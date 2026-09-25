from dataclasses import asdict
from datetime import datetime, timezone

from google.cloud import bigquery

from scrapers.event_scraper import run_event_scrape
from scrapers.fighter_scraper import run_fighter_scrape
from scrapers.models import Event, FighterProfile
from warehouse.client import new_bigquery_client
from warehouse.schemas import EVENT_SCHEMA, FIGHTER_PROFILE_SCHEMA

PROJECT = "ufc-data-pipeline"
EVENTS_TABLE = f"{PROJECT}.raw.events"
FIGHTER_PROFILES_TABLE = f"{PROJECT}.raw.fighter_profiles"


def main():
    urls = [
        "https://www.espn.com/mma/fighter/stats/_/id/5120301/joshua-van",
        "https://www.espn.com/mma/fighter/stats/_/id/4419372/arman-tsarukyan",
    ]
    events = run_event_scrape(limit=2)
    fighter_profiles = run_fighter_scrape(urls=urls)

    with new_bigquery_client(project=PROJECT) as client:
        load_events(client, events)
        load_fighter_profiles(client, fighter_profiles)


def load_events(client, events: list[Event]) -> None:
    loaded_at = datetime.now(timezone.utc).isoformat()
    rows = [{**asdict(event), "loaded_at": loaded_at} for event in events]

    job_config = bigquery.LoadJobConfig(
        schema=EVENT_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(rows, EVENTS_TABLE, job_config=job_config)
    job.result()


def load_fighter_profiles(client, profiles: list[FighterProfile]):
    loaded_at = datetime.now(timezone.utc).isoformat()
    rows = [{**asdict(profile), "loaded_at": loaded_at} for profile in profiles]

    job_config = bigquery.LoadJobConfig(
        schema=FIGHTER_PROFILE_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(
        rows, FIGHTER_PROFILES_TABLE, job_config=job_config
    )
    job.result()


if __name__ == "__main__":
    main()
