from warehouse.client import new_bigquery_client


def main():
    with new_bigquery_client(project="ufc-data-pipeline") as client:
        result = get_stored_fighter_records(client)
        print(result)


def get_stored_fighter_records(client) -> dict[str, str]:
    query = (
        "SELECT id, record FROM `ufc-data-pipeline.raw.fighter_profiles` "
        "QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY loaded_at DESC) = 1"
    )

    rows = client.query(query).result()

    fighter_records = {row.id: row.record for row in rows}

    return fighter_records


if __name__ == "__main__":
    main()
