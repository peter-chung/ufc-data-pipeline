import traceback

from playwright.sync_api import sync_playwright
from tqdm import tqdm

from scrapers.browser import goto_ufcstats, new_browser
from scrapers.ufcstats.models import FighterProfile, FightHistoryEntry
from scrapers.ufcstats.parsing import (
    extract_id_from_href,
    parse_label_value_box,
    parse_stacked_cell,
)

FIGHTERS_URL_TEMPLATE = "http://ufcstats.com/statistics/fighters?char={letter}&page=all"


def scrape_fighter_index(page, letter: str) -> list[tuple[str, str, str, str, str]]:
    url = FIGHTERS_URL_TEMPLATE.format(letter=letter)
    soup = goto_ufcstats(page, url)
    rows = soup.find_all("tr", class_="b-statistics__table-row")
    fighters = []

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 10:
            continue

        link_tag = tds[0].find("a")
        if link_tag is None:
            continue

        first_name = tds[0].get_text(strip=True)
        last_name = tds[1].get_text(strip=True)
        link = link_tag["href"]
        fighter_id = extract_id_from_href(link)

        wins = tds[7].get_text(strip=True)
        losses = tds[8].get_text(strip=True)
        draws = tds[9].get_text(strip=True)
        record = f"{wins}-{losses}-{draws}"

        fighters.append((fighter_id, first_name, last_name, link, record))

    return fighters


def scrape_fighter_detail(
    page, fighter_id: str, first_name: str, last_name: str, link: str
) -> FighterProfile:
    soup = goto_ufcstats(page, link)
    nickname_tag = soup.find("p", class_="b-content__Nickname")
    nickname = nickname_tag.get_text(strip=True) if nickname_tag else None

    bio_box = soup.find("div", class_="b-list__info-box_style_small-width")
    bio_data = parse_label_value_box(bio_box)
    height = bio_data.get("Height")
    weight = bio_data.get("Weight")
    reach = bio_data.get("Reach")
    stance = bio_data.get("STANCE")
    dob = bio_data.get("DOB")

    career_box = soup.find("div", class_="b-list__info-box_style_middle-width")
    career_data = parse_label_value_box(career_box)
    slpm = career_data.get("SLpM")
    str_acc = career_data.get("Str. Acc.")
    sapm = career_data.get("SApM")
    str_def = career_data.get("Str. Def")
    td_avg = career_data.get("TD Avg.")
    td_acc = career_data.get("TD Acc.")
    td_def = career_data.get("TD Def.")
    sub_avg = career_data.get("Sub. Avg.")

    title = soup.find("h2", class_="b-content__title")
    record_tag = title.find("span", class_="b-content__title-record")
    career_record_raw = (
        record_tag.get_text(strip=True).removeprefix("Record:").strip()
        if record_tag
        else None
    )

    table = soup.find("table", class_="b-fight-details__table")
    fight_history = []

    for row in table.find_all("tr", attrs={"data-link": True}):
        fight_link = row["data-link"]
        fight_id = extract_id_from_href(fight_link)
        tds = row.find_all("td")

        fighter_links = tds[1].find_all("a")
        ids = [extract_id_from_href(a["href"]) for a in fighter_links]
        self_index = ids.index(fighter_id) if fighter_id in ids else 0
        opponent_index = 1 - self_index

        kd_values = parse_stacked_cell(tds[2])
        str_values = parse_stacked_cell(tds[3])
        td_values = parse_stacked_cell(tds[4])
        sub_values = parse_stacked_cell(tds[5])

        event_values = parse_stacked_cell(tds[6])
        event_link_tag = tds[6].find("a")
        method_values = parse_stacked_cell(tds[7])

        fight_history.append(
            FightHistoryEntry(
                fight_id=fight_id,
                fight_link=fight_link,
                opponent_id=ids[opponent_index],
                opponent_name=fighter_links[opponent_index].get_text(strip=True),
                opponent_link=fighter_links[opponent_index]["href"],
                event_name=event_values[0],
                event_link=event_link_tag["href"] if event_link_tag else None,
                event_date_raw=event_values[1],
                result=tds[0].get_text(strip=True),
                knockdowns=kd_values[self_index],
                sig_str=str_values[self_index],
                td=td_values[self_index],
                sub_attempts=sub_values[self_index],
                method=method_values[0],
                method_detail=method_values[1],
                finish_round=tds[8].get_text(strip=True),
                finish_time=tds[9].get_text(strip=True),
            )
        )

    return FighterProfile(
        id=fighter_id,
        first_name=first_name,
        last_name=last_name,
        link=link,
        nickname=nickname,
        height=height,
        weight=weight,
        reach=reach,
        stance=stance,
        dob=dob,
        slpm=slpm,
        str_acc=str_acc,
        sapm=sapm,
        str_def=str_def,
        td_avg=td_avg,
        td_acc=td_acc,
        td_def=td_def,
        sub_avg=sub_avg,
        career_record_raw=career_record_raw,
        fight_history=fight_history,
    )


LETTERS = "abcdefghijklmnopqrstuvwxyz"


def run_fighter_scrape(
    headless=True,
    limit=None,
    stored_fighter_records: dict[str, str] | None = None,
    force_fighter_ids: set[str] | None = None,
) -> list[FighterProfile]:
    stored_fighter_records = stored_fighter_records or {}
    force_fighter_ids = force_fighter_ids or set()
    with sync_playwright() as playwright:
        with new_browser(playwright, headless=headless) as browser:
            page = browser.new_page()
            index = []
            for letter in LETTERS:
                index.extend(scrape_fighter_index(page, letter))

            to_scrape = [
                (fighter_id, first_name, last_name, link)
                for fighter_id, first_name, last_name, link, record in index
                if stored_fighter_records.get(fighter_id) != record
                or fighter_id in force_fighter_ids
            ]
            target = to_scrape if limit is None else to_scrape[:limit]

            fighter_profiles = []
            print("Fighter scrape started")
            for fighter_id, first_name, last_name, link in tqdm(target):
                try:
                    profile = scrape_fighter_detail(
                        page, fighter_id, first_name, last_name, link
                    )
                    fighter_profiles.append(profile)
                except Exception:
                    tqdm.write(
                        f"Failed on fighter: {first_name} {last_name} ({fighter_id})"
                    )
                    traceback.print_exc()
            print("Fighter scrape completed")

            return fighter_profiles
