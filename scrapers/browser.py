"""Playwright browser lifecycle and ESPN page-navigation helpers.

Generic Chromium launch/close management (`new_browser`) plus the
ESPN-specific wait strategy for reading their embedded client-state
object (`goto_espn`), used by every scraper module that needs a page.
"""

import time
import random
import traceback
from contextlib import contextmanager
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Playwright,
)


MAX_RETRY_ATTEMPTS = 3


def main():
    """Smoke-test entry point: fetch the ESPN schedule page's raw data."""
    with sync_playwright() as playwright:
        with new_browser(playwright) as browser:
            url = "https://www.espn.com/mma/schedule/_/league/ufc"
            page = browser.new_page()

            content = goto_espn(page, url)
            print(content)


@contextmanager
def new_browser(playwright: Playwright, headless: bool = True):
    """Launch a Chromium browser and guarantee it closes on exit.

    Args:
        playwright: An active Playwright driver instance (from
            ``sync_playwright()``).
        headless: Whether to run without a visible browser window.

    Yields:
        Browser: The launched browser instance.
    """
    browser = playwright.chromium.launch(headless=headless)
    try:
        yield browser
    finally:
        browser.close()


def goto_espn(page, url):
    """Navigate to an ESPN page and return its embedded client-state data.

    ESPN's pages never reach Playwright's "networkidle" wait condition
    (continuous ad/analytics traffic), so this waits for the DOM only,
    then polls for ``window.__espnfitt__`` to be populated by ESPN's
    client-side JS before reading it.

    Args:
        page: The Playwright page to navigate.
        url: The ESPN URL to load.

    Returns:
        dict: The parsed contents of ``window.__espnfitt__``.
    """
    last_error = None

    for _ in range(MAX_RETRY_ATTEMPTS):
        delay_in_seconds = random.uniform(1, 3)
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function("() => window.__espnfitt__ != null")
            data = page.evaluate("() => window.__espnfitt__")
        except PlaywrightTimeoutError as e:
            print(e)
            last_error = e
            traceback.print_exc()
        else:
            return data
        finally:
            # rate limit
            time.sleep(delay_in_seconds)

    raise last_error


if __name__ == "__main__":
    main()
