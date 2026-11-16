from dataclasses import asdict
from datetime import datetime, timezone

from google.cloud import bigquery

from scrapers.ufcstats.models import Event as UfcstatsEvent
from scrapers.ufcstats.models import FighterProfile as UfcstatsFighterProfile
from warehouse.client import new_bigquery_client
from warehouse.schemas import (
    UFCSTATS_EVENT_SCHEMA,
    UFCSTATS_FIGHTER_PROFILE_SCHEMA,
)

PROJECT = "ufc-data-pipeline"

UFCSTATS_EVENTS_TABLE = f"{PROJECT}.raw.ufcstats_events"
UFCSTATS_FIGHTER_PROFILES_TABLE = f"{PROJECT}.raw.ufcstats_fighter_profiles"


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
