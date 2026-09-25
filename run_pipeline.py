import json
from dataclasses import asdict
from datetime import datetime

from scrapers.event_scraper import run_event_scrape
from scrapers.fighter_scraper import run_fighter_scrape
from scrapers.models import Event
from warehouse.client import new_bigquery_client
from warehouse.loader import PROJECT, load_events, load_fighter_profiles
from warehouse.reader import get_stored_fighter_records


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # REMOVE LIMIT FOR FULL RUN
    events = run_event_scrape()
    with open(f"data/raw/event_scrape_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump([asdict(event) for event in events], f, indent=2)

    fighters_by_id = _extract_fighter_records(events)

    with new_bigquery_client(project=PROJECT) as client:
        stored_records = get_stored_fighter_records(client)

        urls_to_scrape = [
            url
            for fighter_id, (url, record) in fighters_by_id.items()
            if stored_records.get(fighter_id) != record
        ]

        # REMOVE LIMIT FOR FULL RUN
        fighter_profiles = run_fighter_scrape(urls_to_scrape)
        with open(
            f"data/raw/fighter_profiles_scrape_{timestamp}.json", "w", encoding="utf-8"
        ) as f:
            json.dump([asdict(profile) for profile in fighter_profiles], f, indent=2)

        load_events(client, events)
        load_fighter_profiles(client, fighter_profiles)


def _extract_fighter_records(events: list[Event]) -> dict[str, tuple[str, str]]:
    fighters_by_id = {
        fighter.id: (
            fighter.link.replace("/mma/fighter/_/", "/mma/fighter/stats/_/"),
            fighter.record,
        )
        for event in events
        for fight in event.fights
        for fighter in (fight.fighter_1, fight.fighter_2)
        if fighter.link
    }
    return fighters_by_id


if __name__ == "__main__":
    main()
