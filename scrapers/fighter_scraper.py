import json
import traceback
from dataclasses import asdict

from playwright.sync_api import sync_playwright
from tqdm import tqdm

from scrapers.browser import new_browser, goto_espn
from scrapers.models import FighterProfile, FightHistoryRow, StatColumn, StatValue


def main():
    urls = [
        "https://www.espn.com/mma/fighter/stats/_/id/5120301/joshua-van",
        "https://www.espn.com/mma/fighter/stats/_/id/4419372/arman-tsarukyan",
    ]
    fighter_profiles = run_fighter_scrape(urls)
    with open("data/raw/fighter_scrape.json", "w", encoding="utf-8") as f:
        json.dump([asdict(profile) for profile in fighter_profiles], f, indent=2)


def scrape_fighter_profile(page, url) -> FighterProfile:
    response = goto_espn(page, url)
    return _parse_fighter_profile(response["page"]["content"]["player"])


def _parse_fighter_profile(raw: dict) -> FighterProfile:
    bio = raw["plyrHdr"]["ath"]
    career_stats = {
        entry["lbl"]: entry["val"] for entry in raw["plyrHdr"]["statsBlck"]["vals"]
    }

    fighter_profile = FighterProfile(
        # identity
        id=raw["playerId"],
        first_name=bio["fNm"],
        last_name=bio.get("lNm"),
        nickname=bio.get("ncknm"),
        country=bio.get("cntry"),
        country_code=bio.get("cntryShrt"),
        team=bio.get("tm"),
        head_img=bio.get("img"),
        flag=bio.get("logo"),
        # physical / bio
        dob=bio.get("dob"),
        dob_raw=bio.get("dobRaw"),
        gender=bio.get("gndr"),
        height=bio.get("htOnly"),
        height_weight=bio.get("htwt"),
        reach=bio.get("rch"),
        stance=bio.get("stnc"),
        weight_class=bio.get("wghtclss"),
        weight_class_short=bio.get("wghtclssshrt"),
        # career totals
        record=career_stats.get("W-L-D"),
        tko_record=career_stats.get("(T)KO"),
        sub_record=career_stats.get("SUB"),
    )

    _apply_fight_history(fighter_profile, raw)

    return fighter_profile


def _apply_fight_history(fighter_profile: FighterProfile, raw: dict) -> None:
    tables = raw["stat"]["tbl"]
    # match based on category of striking, clinch, ground
    for table in tables:
        match table["ttl"].strip().lower():
            case "striking":
                fighter_profile.striking_columns = [
                    StatColumn(abbreviation=c["data"], name=c["ttl"]) for c in table["col"]
                ]
                fighter_profile.striking_history = [
                    _parse_fight_history_row(row, table["col"]) for row in table["row"]
                ]
            case "clinch":
                fighter_profile.clinch_columns = [
                    StatColumn(abbreviation=c["data"], name=c["ttl"]) for c in table["col"]
                ]
                fighter_profile.clinch_history = [
                    _parse_fight_history_row(row, table["col"]) for row in table["row"]
                ]
            case "ground":
                fighter_profile.ground_columns = [
                    StatColumn(abbreviation=c["data"], name=c["ttl"]) for c in table["col"]
                ]
                fighter_profile.ground_history = [
                    _parse_fight_history_row(row, table["col"]) for row in table["row"]
                ]
            case _:
                raise ValueError(f"Unknown stat table type: {table['ttl']!r}")


def _parse_fight_history_row(raw: list, columns: list) -> FightHistoryRow:
    fight_history_row = FightHistoryRow(
        date=raw[0].get("dte"),
        opponent_name=raw[1].get("txt"),
        opponent_link=raw[1].get("url"),
        event_name=raw[2].get("nm"),
        event_link=raw[2].get("lnk"),
        result=raw[3].get("rslt"),
        stats=[
            StatValue(abbreviation=column["data"], value=value)
            for column, value in zip(columns, raw[4:])
        ],
    )

    return fight_history_row


def run_fighter_scrape(
    urls: list[str], headless=True, limit=None
) -> list[FighterProfile]:
    with sync_playwright() as playwright:
        with new_browser(playwright, headless=headless) as browser:
            page = browser.new_page()
            target_urls = urls if limit is None else urls[:limit]

            fighter_profiles = []
            print("Fighter scrape started")
            for url in tqdm(target_urls):
                try:
                    fighter_profiles.append(scrape_fighter_profile(page, url))
                except Exception:
                    tqdm.write(f"Failed on fighter url: {url}")
                    traceback.print_exc()
            print("Fighter scrape completed")
    return fighter_profiles


if __name__ == "__main__":
    main()
