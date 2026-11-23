import re

from warehouse.client import new_bigquery_client


def main():
    with new_bigquery_client(project="ufc-data-pipeline") as client:
        result = get_stored_ufcstats_fighter_records(client)
        print(result)


def get_stored_ufcstats_fighter_records(client) -> dict[str, str]:
    query = (
        "SELECT id, career_record_raw FROM `ufc-data-pipeline.raw.ufcstats_fighter_profiles` "
        "QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY loaded_at DESC) = 1"
    )

    rows = client.query(query).result()
    fighter_records = {
        row.id: re.sub(r"\s*\(\d+\s*NC\)", "", row.career_record_raw or "")
        for row in rows
    }

    return fighter_records


def get_stored_ufcstats_completed_event_ids(client) -> set[str]:
    query = (
        "SELECT DISTINCT id FROM `ufc-data-pipeline.raw.ufcstats_events` "
        "WHERE completed = TRUE AND ARRAY_LENGTH(fights) > 0"
    )

    rows = client.query(query).result()

    return {row.id for row in rows}


if __name__ == "__main__":
    main()
