"""Playwright browser lifecycle and ESPN page-navigation helpers.

Generic Chromium launch/close management (`new_browser`) plus the
ESPN-specific wait strategy for reading their embedded client-state
object (`goto_espn`), used by every scraper module that needs a page.
"""

import random
import time
import traceback
from contextlib import contextmanager

from bs4 import BeautifulSoup
from playwright.sync_api import (
    Playwright,
)
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import (
    sync_playwright,
)

MAX_RETRY_ATTEMPTS = 3


def main():
    # with sync_playwright() as playwright:
    #     with new_browser(playwright) as browser:
    #         url = "https://www.espn.com/mma/schedule/_/league/ufc"
    #         page = browser.new_page()

    #         content = goto_espn(page, url)
    #         print(content)

    with sync_playwright() as playwright:
        with new_browser(playwright) as browser:
            url = "http://ufcstats.com/fighter-details/262d32ebda89efc4"
            page = browser.new_page()

            content = goto_ufcstats(page, url)
            print(content)


@contextmanager
def new_browser(playwright: Playwright, headless: bool = True):
    browser = playwright.chromium.launch(headless=headless)
    try:
        yield browser
    finally:
        browser.close()


def goto_espn(page, url):
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


def goto_ufcstats(page, url, wait_selector="table", timeout_ms=20000):
    last_error = None

    for _ in range(MAX_RETRY_ATTEMPTS):
        delay_in_seconds = random.uniform(1, 3)
        try:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector(wait_selector, timeout=timeout_ms)
        except PlaywrightTimeoutError as e:
            print(e)
            last_error = e
            traceback.print_exc()
        else:
            return BeautifulSoup(page.content(), "lxml")
        finally:
            # rate limit
            time.sleep(delay_in_seconds)

    raise last_error


if __name__ == "__main__":
    main()
