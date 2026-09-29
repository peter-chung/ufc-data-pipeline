import json
import traceback
from dataclasses import asdict
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from tqdm import tqdm

from scrapers.browser import goto_espn, new_browser
from scrapers.models import Event, Fight, Fighter, Venue

BASE_URL = "https://www.espn.com"


def main():
    events = run_event_scrape()

    with open("data/raw/event_scrape.json", "w", encoding="utf-8") as f:
        json.dump([asdict(event) for event in events], f, indent=2)


def _parse_fighter(raw: dict) -> Fighter:
    stats = raw.get("stats", {})
    raw_age = stats.get("age")
    fighter = Fighter(
        # identity (always required)
        id=raw["id"],
        first_name=raw["frstNm"],
        # identity (optional)
        last_name=raw.get("lstNm"),
        link=raw.get("lnk"),
        country=raw.get("country"),
        flag=raw.get("flag"),
        gender=raw.get("gndr"),
        head_img=raw.get("hdsht"),
        body_img=raw.get("bdyImg"),
        # physical stats (optional)
        height=stats.get("ht"),
        weight=stats.get("wt"),
        reach=stats.get("rch"),
        stance=stats.get("stnce"),
        age=raw_age if isinstance(raw_age, int) else None,
        # performance stats (optional)
        record=raw.get("rec"),
        sig_str_lpm=stats.get("sigstrklpm"),
        sig_str_acc=stats.get("sigstrkacc"),
        td_avg=stats.get("tdavg"),
        td_acc=stats.get("tdacc"),
        sub_avg=stats.get("subavg"),
        is_pre=stats.get("isPre"),
        is_win=raw.get("isWin"),
    )

    return fighter


def _parse_fight(raw: dict, card_segment: str) -> Fight:
    status = raw.get("status") or {}
    decision = raw.get("dec") or {}
    networks = raw.get("ntwrks") or {}
    fight = Fight(
        # matchup (always required)
        id=raw["id"],
        fighter_1=_parse_fighter(raw["awy"]),
        fighter_2=_parse_fighter(raw["hme"]),
        card_segment=card_segment,
        # fight details (optional)
        note=raw.get("nte"),
        date_time=raw.get("dt"),
        # broadcast / status (optional)
        networks=networks.get("nm"),
        status=status.get("state"),
        status_detail=status.get("det"),
        round_number=status.get("rd"),
        finish_time=status.get("dspClk"),
        method=decision.get("det"),
        method_short=decision.get("shrtDspNm"),
    )

    return fight


def _parse_venue(raw: dict) -> Venue:
    address = raw["address"]
    venue = Venue(
        id=raw["id"],
        name=raw["fullName"],
        city=address["city"],
        country=address["country"],
        state=address.get("state"),
        address=address.get("address1"),
    )

    return venue


def _parse_event(raw: dict) -> Event:
    event = Event(
        id=raw["id"],
        name=raw["name"],
        link=raw["link"],
        date=raw["date"],
        status=raw["status"]["state"],
        status_detail=raw["status"]["detail"],
        completed=raw["completed"],
        is_postponed_or_canceled=raw["isPostponedOrCanceled"],
        venue=_parse_venue(raw["venue"]),
    )

    return event


def scrape_events(page) -> list[Event]:
    schedule_url = f"{BASE_URL}/mma/schedule/_/league/ufc"
    response = goto_espn(page, schedule_url)
    events_by_date = response["page"]["content"]["events"]
    parsed_events = []

    for event_group in events_by_date.values():
        for event_data in event_group:
            parsed_events.append(_parse_event(event_data))

    return parsed_events


def scrape_event_fights(page, event: Event) -> None:
    event_url = urljoin(BASE_URL, event.link)
    response = goto_espn(page, event_url)
    gamepackage = response["page"]["content"]["gamepackage"]
    event.short_name = gamepackage["hdr"]["evt"]["snm"]
    card_segments = gamepackage.get("cardSegs")

    if not card_segments:
        return

    fights = []

    for card_segment in card_segments:
        for fight in card_segment["mtchs"]:
            try:
                fights.append(_parse_fight(fight, card_segment["hdr"]))
            except Exception:
                tqdm.write(f"Failed on fight id: {fight.get('id')}")
                traceback.print_exc()

    event.fights = fights


def run_event_scrape(
    headless=True, limit=None, stored_completed_event_ids: set[str] | None = None
) -> list[Event]:
    stored_completed_event_ids = stored_completed_event_ids or set()
    with sync_playwright() as playwright:
        with new_browser(playwright, headless=headless) as browser:
            page = browser.new_page()
            events = scrape_events(page)

            events_to_scrape = [
                event
                for event in events
                if not (event.completed and event.id in stored_completed_event_ids)
            ]
            target_events = (
                events_to_scrape if limit is None else events_to_scrape[:limit]
            )

            print("Event scrape started")
            for event in tqdm(target_events):
                try:
                    scrape_event_fights(page, event)
                except Exception:
                    tqdm.write(f"Failed on event: {event.name} ({event.id})")
                    traceback.print_exc()
            print("Event scrape completed")

            return target_events


if __name__ == "__main__":
    main()
