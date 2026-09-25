from contextlib import contextmanager

from google.cloud import bigquery


def main():
    with new_bigquery_client(project="ufc-data-pipeline") as client:
        query = "SELECT 1 AS test_value"
        result = client.query(query).result()
        for row in result:
            print(row)


@contextmanager
def new_bigquery_client(project: str):
    client = bigquery.Client(project=project)
    try:
        yield client
    finally:
        client.close()


if __name__ == "__main__":
    main()
