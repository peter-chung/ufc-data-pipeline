import json
from dataclasses import asdict
from datetime import datetime

from scrapers.ufcstats.event_scraper import run_event_scrape
from scrapers.ufcstats.fighter_scraper import run_fighter_scrape
from warehouse.client import new_bigquery_client
from warehouse.loader import (
    PROJECT,
    load_ufcstats_events,
    load_ufcstats_fighter_profiles,
    load_ufcstats_upcoming_index,
)
from warehouse.reader import (
    get_stored_ufcstats_completed_event_ids,
    get_stored_ufcstats_fighter_records,
)


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with new_bigquery_client(project=PROJECT) as client:
        # Events
        stored_completed_event_ids = get_stored_ufcstats_completed_event_ids(client)
        events, upcoming_index = run_event_scrape(
            stored_completed_event_ids=stored_completed_event_ids
        )
        with open(
            f"data/raw/ufcstats_event_scrape_{timestamp}.json", "w", encoding="utf-8"
        ) as f:
            json.dump([asdict(event) for event in events], f, indent=2)
        load_ufcstats_events(client, events)
        load_ufcstats_upcoming_index(client, upcoming_index)

        # Fighter profiles
        # Fighter ids in events that recently have been completed
        force_fighter_ids = {
            fighter.id
            for event in events
            if event.completed
            for fight in event.fights
            for fighter in (fight.fighter_1, fight.fighter_2)
        }
        stored_fighter_records = get_stored_ufcstats_fighter_records(client)
        fighter_profiles = run_fighter_scrape(
            stored_fighter_records=stored_fighter_records,
            force_fighter_ids=force_fighter_ids,
        )
        with open(
            f"data/raw/ufcstats_fighter_scrape_{timestamp}.json", "w", encoding="utf-8"
        ) as f:
            json.dump([asdict(profile) for profile in fighter_profiles], f, indent=2)
        load_ufcstats_fighter_profiles(client, fighter_profiles)


if __name__ == "__main__":
    main()
