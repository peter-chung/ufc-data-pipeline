"""One-time backfill: re-scrape every completed event so fights are stored in
corner order (fighter_1 = red, fighter_2 = blue).

Fights scraped before the fix have the winner as fighter_1 (the event page's
order). stg_events keeps each event's latest load, so reloading the events
replaces the old rows without touching anything else.

About 800 event pages + ~9,000 fight pages at ufcstats' rate limit: several
hours. Events are loaded in batches as it goes, so an interruption loses at
most one batch. To resume, rerun with the --started-at value printed at the
start; events already reloaded since then are skipped.

    python rescrape_completed_events.py
    python rescrape_completed_events.py --started-at 2026-11-24T05:00:00+00:00
    python rescrape_completed_events.py --limit 3     # quick trial run
"""

import argparse
import traceback
from datetime import datetime, timezone

from google.cloud import bigquery
from playwright.sync_api import sync_playwright
from tqdm import tqdm

from scrapers.browser import new_browser
from scrapers.ufcstats.event_scraper import (
    COMPLETED_EVENTS_URL,
    scrape_event_detail,
    scrape_event_index,
    scrape_fight_detail,
)
from warehouse.client import new_bigquery_client
from warehouse.loader import PROJECT, UFCSTATS_EVENTS_TABLE, load_ufcstats_events

BATCH_SIZE = 20


def get_event_ids_reloaded_since(client, started_at: str) -> set[str]:
    query = f"""
        SELECT id
        FROM `{UFCSTATS_EVENTS_TABLE}`
        WHERE completed
        GROUP BY id
        HAVING MAX(SAFE_CAST(loaded_at AS TIMESTAMP)) >= @started_at
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("started_at", "TIMESTAMP", started_at)
        ]
    )
    return {row.id for row in client.query(query, job_config=job_config).result()}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--started-at",
        help="ISO timestamp of the original run, to resume it (skips events reloaded since)",
    )
    parser.add_argument("--limit", type=int, help="only re-scrape this many events")
    args = parser.parse_args()

    started_at = args.started_at or datetime.now(timezone.utc).isoformat()
    print(f"Started at {started_at}")
    print(f"To resume after an interruption: --started-at {started_at}")

    with new_bigquery_client(project=PROJECT) as client:
        already_done = get_event_ids_reloaded_since(client, started_at)

        with sync_playwright() as playwright:
            with new_browser(playwright) as browser:
                page = browser.new_page()
                completed_index = scrape_event_index(page, COMPLETED_EVENTS_URL)
                targets = [item for item in completed_index if item[0] not in already_done]
                if args.limit is not None:
                    targets = targets[: args.limit]

                print(
                    f"{len(completed_index)} completed events, "
                    f"{len(already_done)} already reloaded, {len(targets)} to go"
                )

                batch, loaded, failed = [], 0, []
                for event_id, name, link in tqdm(targets):
                    try:
                        event = scrape_event_detail(page, event_id, name, link, True)
                        for fight in event.fights:
                            scrape_fight_detail(page, fight)
                        batch.append(event)
                    except Exception:
                        tqdm.write(f"Failed on event: {name} ({event_id})")
                        traceback.print_exc()
                        failed.append(f"{name} ({event_id})")

                    if len(batch) >= BATCH_SIZE:
                        load_ufcstats_events(client, batch)
                        loaded += len(batch)
                        batch = []

                if batch:
                    load_ufcstats_events(client, batch)
                    loaded += len(batch)

    print(f"Reloaded {loaded} events")
    if failed:
        print(f"{len(failed)} failed (rerun with --started-at to retry them):")
        for item in failed:
            print(f"  {item}")


if __name__ == "__main__":
    main()
