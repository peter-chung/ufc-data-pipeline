from dataclasses import asdict
from datetime import datetime, timezone

from google.cloud import bigquery

from scrapers.ufcstats.models import Event as UfcstatsEvent
from scrapers.ufcstats.models import FighterProfile as UfcstatsFighterProfile
from warehouse.client import new_bigquery_client
from warehouse.schemas import (
    UFCSTATS_EVENT_SCHEMA,
    UFCSTATS_FIGHTER_PROFILE_SCHEMA,
    UFCSTATS_UPCOMING_INDEX_SCHEMA,
)

PROJECT = "ufc-data-pipeline"

UFCSTATS_EVENTS_TABLE = f"{PROJECT}.raw.ufcstats_events"
UFCSTATS_FIGHTER_PROFILES_TABLE = f"{PROJECT}.raw.ufcstats_fighter_profiles"
UFCSTATS_UPCOMING_INDEX_TABLE = f"{PROJECT}.raw.ufcstats_upcoming_index"


def load_ufcstats_upcoming_index(
    client, upcoming_index: list[tuple[str, str, str]]
) -> None:
    """Snapshot of ufcstats' upcoming-events page for this run.

    An empty page almost certainly means a scrape problem, not "every card was
    cancelled", so it isn't saved: an empty snapshot would mark every upcoming
    event as cancelled in stg_events.
    """
    if not upcoming_index:
        print("Upcoming index is empty; not saving a snapshot")
        return

    loaded_at = datetime.now(timezone.utc).isoformat()
    rows = [
        {"id": event_id, "name": name, "loaded_at": loaded_at}
        for event_id, name, _link in upcoming_index
    ]

    job_config = bigquery.LoadJobConfig(
        schema=UFCSTATS_UPCOMING_INDEX_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_json(
        rows, UFCSTATS_UPCOMING_INDEX_TABLE, job_config=job_config
    )
    job.result()


def load_ufcstats_events(client, events: list[UfcstatsEvent]) -> None:
    loaded_at = datetime.now(timezone.utc).isoformat()
    rows = [{**asdict(event), "loaded_at": loaded_at} for event in events]

    job_config = bigquery.LoadJobConfig(
        schema=UFCSTATS_EVENT_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
    )

    job = client.load_table_from_json(
        rows, UFCSTATS_EVENTS_TABLE, job_config=job_config
    )
    job.result()


def load_ufcstats_fighter_profiles(
    client, profiles: list[UfcstatsFighterProfile]
) -> None:
    loaded_at = datetime.now(timezone.utc).isoformat()
    rows = [{**asdict(profile), "loaded_at": loaded_at} for profile in profiles]

    job_config = bigquery.LoadJobConfig(
        schema=UFCSTATS_FIGHTER_PROFILE_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
    )

    job = client.load_table_from_json(
        rows, UFCSTATS_FIGHTER_PROFILES_TABLE, job_config=job_config
    )
    job.result()
