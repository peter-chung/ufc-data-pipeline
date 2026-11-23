import traceback

from playwright.sync_api import sync_playwright
from tqdm import tqdm

from scrapers.browser import goto_ufcstats, new_browser
from scrapers.ufcstats.models import Event, Fight, FighterRef, FighterRoundStats
from scrapers.ufcstats.parsing import (
    extract_id_from_href,
    parse_fight_metadata,
    parse_label_value_box,
    parse_stacked_cell,
)

TOTALS_FIELDS = [
    "knockdowns",
    "sig_str",
    "sig_str_pct",
    "total_str",
    "td",
    "td_pct",
    "sub_attempts",
    "reversals",
    "control_time",
]
SIG_STRIKES_FIELDS = [
    "sig_str",
    "sig_str_pct",
    "head_str",
    "body_str",
    "leg_str",
    "distance_str",
    "clinch_str",
    "ground_str",
]

COMPLETED_EVENTS_URL = "http://ufcstats.com/statistics/events/completed?page=all"
UPCOMING_EVENTS_URL = "http://ufcstats.com/statistics/events/upcoming?page=all"


def main(): ...


def scrape_event_index(page, url=COMPLETED_EVENTS_URL) -> list[tuple[str, str, str]]:
    soup = goto_ufcstats(page, url)
    event_links = soup.find_all(
        "a", href=lambda href: href and "/event-details/" in href
    )
    events = []

    for event_link in event_links:
        if url == COMPLETED_EVENTS_URL:
            row = event_link.find_parent("tr")
            is_next = row is not None and row.find(
                "img", src=lambda s: s and "next.png" in s
            )
            if is_next:
                continue

        name = event_link.get_text(strip=True)
        link = event_link["href"]
        event_id = extract_id_from_href(link)

        events.append((event_id, name, link))

    return events


def scrape_event_detail(page, event_id, name, link, completed) -> Event:
    soup = goto_ufcstats(page, link)
    box = soup.find("ul", class_="b-list__box-list")
    box_data = parse_label_value_box(box)

    date_raw = box_data["Date"]
    location_raw = box_data.get("Location")

    table = soup.find("table", class_="b-fight-details__table")
    fights = []

    for row in table.find_all("tr", attrs={"data-link": True}):
        fight_link = row["data-link"]
        fight_id = extract_id_from_href(fight_link)
        tds = row.find_all("td")

        fighter_links = tds[1].find_all("a")
        fighter_1 = FighterRef(
            id=extract_id_from_href(fighter_links[0]["href"]),
            name=fighter_links[0].get_text(strip=True),
            link=fighter_links[0]["href"],
        )
        fighter_2 = FighterRef(
            id=extract_id_from_href(fighter_links[1]["href"]),
            name=fighter_links[1].get_text(strip=True),
            link=fighter_links[1]["href"],
        )

        weight_class = tds[6].get_text(strip=True) or None

        fights.append(
            Fight(
                id=fight_id,
                link=fight_link,
                fighter_1=fighter_1,
                fighter_2=fighter_2,
                weight_class=weight_class,
            )
        )

    return Event(
        id=event_id,
        name=name,
        link=link,
        date_raw=date_raw,
        completed=completed,
        location_raw=location_raw,
        fights=fights,
    )


def _iter_round_rows(table):
    """Yield (round_number, row) for each data row in a stat table.

    Handles both the simple tables (one header + one body, round=None
    throughout) and the per-round tables (a normal header with an empty
    body, then repeated "Round N" marker theads each followed by a tbody
    holding that round's single data row) with the same logic.
    """
    round_number = None

    for child in table.find_all(["thead", "tbody"], recursive=False):
        if child.name == "thead":
            if "b-fight-details__table-row_type_head" in (child.get("class") or []):
                text = child.get_text(strip=True)
                round_number = int("".join(ch for ch in text if ch.isdigit()))
        else:
            row = child.find("tr")
            if row is not None:
                yield round_number, row


def _apply_stat_row(row, field_names, stats_by_fighter_id):
    tds = row.find_all("td")
    fighter_links = tds[0].find_all("a")
    row_fighter_ids = [extract_id_from_href(a["href"]) for a in fighter_links]

    for field_name, td in zip(field_names, tds[1:]):
        value_1, value_2 = parse_stacked_cell(td)
        for fighter_id, value in zip(row_fighter_ids, (value_1, value_2)):
            setattr(stats_by_fighter_id[fighter_id], field_name, value)


def scrape_fight_detail(page, fight: Fight) -> None:
    soup = goto_ufcstats(page, fight.link, wait_selector=".b-fight-details__persons")

    content = soup.find("div", class_="b-fight-details__content")
    metadata = parse_fight_metadata(content)
    fight.method = metadata.get("Method")
    fight.finish_round = metadata.get("Round")
    fight.finish_time = metadata.get("Time")
    fight.time_format = metadata.get("Time format")
    fight.referee = metadata.get("Referee")
    fight.details = metadata.get("Details")

    for person in soup.find_all("div", class_="b-fight-details__person"):
        status_tag = person.find("i", class_="b-fight-details__person-status")
        link_tag = person.find("a", class_="b-fight-details__person-link")
        if status_tag is None or link_tag is None:
            continue

        person_id = extract_id_from_href(link_tag["href"])
        status = status_tag.get_text(strip=True)

        if person_id == fight.fighter_1.id:
            fight.fighter_1_result = status
        elif person_id == fight.fighter_2.id:
            fight.fighter_2_result = status

    tables = soup.find_all("table")

    fighter_1_stats_by_round = {}
    fighter_2_stats_by_round = {}

    if len(tables) < 4:
        fight.fighter_1_stats = []
        fight.fighter_2_stats = []
        return

    (
        totals_table,
        totals_per_round_table,
        sig_strikes_table,
        sig_strikes_per_round_table,
    ) = tables[:4]

    def stats_for_round(round_number):
        if round_number not in fighter_1_stats_by_round:
            fighter_1_stats_by_round[round_number] = FighterRoundStats(
                round=round_number
            )
            fighter_2_stats_by_round[round_number] = FighterRoundStats(
                round=round_number
            )
        return {
            fight.fighter_1.id: fighter_1_stats_by_round[round_number],
            fight.fighter_2.id: fighter_2_stats_by_round[round_number],
        }

    for table, field_names in (
        (totals_table, TOTALS_FIELDS),
        (totals_per_round_table, TOTALS_FIELDS),
        (sig_strikes_table, SIG_STRIKES_FIELDS),
        (sig_strikes_per_round_table, SIG_STRIKES_FIELDS),
    ):
        for round_number, row in _iter_round_rows(table):
            _apply_stat_row(row, field_names, stats_for_round(round_number))

    fight.fighter_1_stats = list(fighter_1_stats_by_round.values())
    fight.fighter_2_stats = list(fighter_2_stats_by_round.values())


def run_event_scrape(
    headless=True, limit=None, stored_completed_event_ids: set[str] | None = None
) -> tuple[list[Event], list[tuple[str, str, str]]]:
    """Returns (events, upcoming_index).

    upcoming_index is every (event_id, name, link) on ufcstats' upcoming-events
    page this run, including events whose detail page failed to scrape. It's
    the source of truth for "still on the schedule" (see stg_events.event_status).
    """
    stored_completed_event_ids = stored_completed_event_ids or set()
    with sync_playwright() as playwright:
        with new_browser(playwright, headless=headless) as browser:
            page = browser.new_page()
            completed_index = scrape_event_index(page, COMPLETED_EVENTS_URL)
            upcoming_index = scrape_event_index(page, UPCOMING_EVENTS_URL)

            completed_to_scrape = [
                (event_id, name, link)
                for event_id, name, link in completed_index
                if event_id not in stored_completed_event_ids
            ]
            if limit is not None:
                completed_to_scrape = completed_to_scrape[:limit]

            targets = [(*item, True) for item in completed_to_scrape] + [
                (*item, False) for item in upcoming_index
            ]

            events = []
            print("Event scrape started")
            for event_id, name, link, completed in tqdm(targets):
                try:
                    event = scrape_event_detail(page, event_id, name, link, completed)
                    if completed:
                        for fight in event.fights:
                            scrape_fight_detail(page, fight)
                    events.append(event)
                except Exception:
                    tqdm.write(f"Failed on event: {name} ({event_id})")
                    traceback.print_exc()
            print("Event scrape completed")

            return events, upcoming_index


if __name__ == "__main__":
    main()
