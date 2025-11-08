"""Automation script for exporting Vanguard performance data.

This module launches a Playwright-controlled browser session, logs into the
Vanguard Personal Investor portal, and downloads the "Performance Details" data
into a structured CSV file. The script mirrors the manual workflow of visiting
https://personal-performance.web.vanguard.com/, navigating to Performance
Details, expanding the "Show More" section, and scraping the tabular data that
becomes visible.

The DOM structure of Vanguard's authenticated pages can change at any time,
so the selectors below are intentionally flexible and include multiple
fallbacks. Review the logs if the script fails, and update selectors as needed.

Example usage from the repository root:

    python scripts/vanguard_performance_export.py \
        --username "YOUR_USER" \
        --password "YOUR_PASSWORD" \
        --output-file data/vanguard_performance.csv

Credentials are read from the command line or environment variables; nothing is
stored on disk. Two-factor authentication prompts (e.g., OTP) will pause the
script and ask you to confirm completion before continuing.
"""
from __future__ import annotations

import argparse
import getpass
import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
from playwright.sync_api import (
    BrowserContext,
    Error,
    Frame,
    Page,
    TimeoutError,
    sync_playwright,
)


LOGGER = logging.getLogger(__name__)

LOGIN_URL = "https://personal-performance.web.vanguard.com/"
PERFORMANCE_DETAILS_KEYWORDS = (
    "Performance",
    "Performance details",
    "Performance Details",
)
SHOW_MORE_KEYWORDS = (
    "Show more",
    "Show More",
)

TABLE_MIN_COLUMNS = 3
DEFAULT_WAIT_TIMEOUT = 30_000


@dataclass
class ScrapeConfig:
    """Configuration for the Vanguard scrape workflow."""

    username: str
    password: str
    output_file: Path
    headless: bool = False
    max_wait_ms: int = DEFAULT_WAIT_TIMEOUT
    store_html_debug: Optional[Path] = None
    pause_on_error: bool = False


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Log into Vanguard Personal Investor and export the Performance "
            "Details table to CSV."
        )
    )
    parser.add_argument("--username", help="Vanguard username; prompts if omitted")
    parser.add_argument(
        "--password",
        help="Vanguard password; prompts securely if omitted",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path("vanguard_performance.csv"),
        help="Destination CSV path (default: vanguard_performance.csv)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser in headless mode (default: False).",
    )
    parser.add_argument(
        "--max-wait-ms",
        type=int,
        default=DEFAULT_WAIT_TIMEOUT,
        help="Maximum wait time for elements to appear (milliseconds).",
    )
    parser.add_argument(
        "--store-html-debug",
        type=Path,
        help="Optional path to write the final page HTML for troubleshooting.",
    )
    parser.add_argument(
        "--pause-on-error",
        action="store_true",
        help=(
            "Keep the browser open if an error occurs so you can inspect the "
            "state before exiting."
        ),
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Configure logging verbosity (default: INFO).",
    )
    return parser


def prompt_credentials(username: Optional[str], password: Optional[str]) -> tuple[str, str]:
    if not username:
        username = input("Vanguard username: ").strip()
    if not password:
        password = getpass.getpass("Vanguard password: ")
    if not username or not password:
        raise ValueError("Username and password are required.")
    return username, password


def log_in(context: BrowserContext, page: Page, config: ScrapeConfig) -> Page:
    LOGGER.info("Navigating to Vanguard login page")
    page.goto(LOGIN_URL, wait_until="domcontentloaded")

    LOGGER.debug("Allowing login page to fully initialize before locating inputs")
    page.wait_for_timeout(2_000)

    username_selectors = [
        'input[name="USER"]',
        'input[name="USERNAME"]',
        'input[name="USER_ID"]',
        'input[id="username"]',
        'input[id="UserID"]',
        'input[autocomplete="username"]',
        'input[type="text"]',
    ]
    password_selectors = [
        'input[name="PASSWORD"]',
        'input[name="PASSWORD1"]',
        'input[id="password"]',
        'input[autocomplete="current-password"]',
        'input[type="password"]',
    ]

    login_frame = wait_for_frame_with_selectors(
        page,
        username_selectors,
        config.max_wait_ms,
    )

    fill_first_available(login_frame, username_selectors, config.username)
    fill_first_available(login_frame, password_selectors, config.password)

    submit_selectors = [
        'button[type="submit"]',
        'button[name="login"]',
        'button:has-text("Log on")',
        'button:has-text("Log On")',
        'button:has-text("Sign in")',
        'button:has-text("Sign On")',
        'input[type="submit"]',
    ]
    existing_pages = set(context.pages)
    click_first_available(login_frame, submit_selectors)

    LOGGER.info("Waiting for post-login navigation")
    page = wait_for_authentication(context, page, existing_pages, config)
    page.wait_for_load_state("networkidle", timeout=config.max_wait_ms)

    if requires_two_factor(page):
        LOGGER.warning(
            "Two-factor authentication detected. Complete verification in the "
            "browser window, then press Enter to continue."
        )
        input("Press Enter after completing multi-factor authentication...")
        page.wait_for_load_state("networkidle", timeout=config.max_wait_ms)

    return page


def requires_two_factor(page: Page) -> bool:
    two_factor_markers = [
        "verification",
        "two-factor",
        "multi-factor",
        "security code",
        "one-time password",
    ]
    try:
        body_locator = page.locator("body")
        page_text = body_locator.inner_text(timeout=5_000).lower()
    except Error:
        page_text = page.content().lower()
    return any(marker in page_text for marker in two_factor_markers)


def wait_for_frame_with_selectors(
    page: Page, selectors: Iterable[str], timeout_ms: int
) -> Frame:
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        frames = [page.main_frame, *page.frames]
        for frame in frames:
            if frame is None:
                continue
            for selector in selectors:
                try:
                    locator = frame.locator(selector)
                    if locator.count() > 0:
                        return frame
                except Error:
                    continue
        page.wait_for_timeout(250)
    raise TimeoutError(
        "Timed out waiting for login inputs to become available. Update selectors."
    )


def wait_for_authentication(
    context: BrowserContext,
    current_page: Page,
    existing_pages: set[Page],
    config: ScrapeConfig,
) -> Page:
    deadline = time.monotonic() + config.max_wait_ms / 1000
    auth_pattern = re.compile(r"personal-performance", re.IGNORECASE)

    def is_authenticated(target_page: Page) -> bool:
        if auth_pattern.search(target_page.url) and "logon" not in target_page.url.lower():
            return True
        try:
            text = target_page.locator("body").inner_text(timeout=2_000)
        except Error:
            return False
        lowered = text.lower()
        return "log off" in lowered or "sign out" in lowered or "performance" in lowered

    while time.monotonic() < deadline:
        for candidate in context.pages:
            if candidate not in existing_pages and candidate.url:
                try:
                    candidate.wait_for_load_state(
                        "domcontentloaded", timeout=config.max_wait_ms
                    )
                except TimeoutError:
                    continue
                if is_authenticated(candidate):
                    return candidate

        if is_authenticated(current_page):
            return current_page

        current_page.wait_for_timeout(250)

    raise TimeoutError("Login did not complete before timeout. Check credentials or MFA.")


def ensure_performance_page(page: Page, timeout_ms: int) -> None:
    auth_pattern = re.compile(r"personal-performance", re.IGNORECASE)
    if auth_pattern.search(page.url):
        return

    try:
        page.wait_for_url(auth_pattern, timeout=timeout_ms)
    except TimeoutError:
        page.goto(LOGIN_URL, wait_until="networkidle")
        page.wait_for_url(auth_pattern, timeout=timeout_ms)


def fill_first_available(frame: Frame, selectors: Iterable[str], value: str) -> None:
    for selector in selectors:
        locator = frame.locator(selector)
        if locator.count() > 0:
            LOGGER.debug("Filling selector %s", selector)
            locator.first.fill(value, timeout=5_000)
            return
    raise RuntimeError(f"Unable to find an input matching selectors: {selectors}")


def click_first_available(frame: Frame, selectors: Iterable[str]) -> None:
    for selector in selectors:
        locator = frame.locator(selector)
        if locator.count() > 0:
            LOGGER.debug("Clicking selector %s", selector)
            locator.first.click(timeout=5_000)
            return
    raise RuntimeError(f"Unable to find a clickable element matching {selectors}")


def navigate_to_performance_details(page: Page, config: ScrapeConfig) -> None:
    LOGGER.info("Navigating to Performance Details")
    ensure_performance_page(page, config.max_wait_ms)
    if not re.search(r"personal-performance", page.url, re.IGNORECASE):
        for keyword in PERFORMANCE_DETAILS_KEYWORDS:
            try:
                locator = page.get_by_role("link", name=keyword, exact=False)
                if locator.count() > 0:
                    locator.first.click(timeout=5_000)
                    break
            except (Error, TimeoutError):
                continue
        else:
            # Fall back to text matching anywhere on the page.
            for keyword in PERFORMANCE_DETAILS_KEYWORDS:
                try:
                    page.locator(f"text={keyword}").first.click(timeout=5_000)
                    break
                except (Error, TimeoutError):
                    continue
            else:
                raise RuntimeError(
                    "Unable to locate the Performance Details section. Update selectors."
                )

        page.wait_for_load_state("networkidle", timeout=config.max_wait_ms)
        ensure_performance_page(page, config.max_wait_ms)

    LOGGER.info("Expanding 'Show More' section if available")
    for keyword in SHOW_MORE_KEYWORDS:
        try:
            locator = page.get_by_role("button", name=keyword, exact=False)
            if locator.count() > 0:
                locator.first.click()
                break
        except (Error, TimeoutError):
            continue
    else:
        try:
            page.locator("text=Show More").first.click(timeout=5_000)
        except (Error, TimeoutError):
            LOGGER.warning("'Show More' button not found; continuing without expanding.")

    page.wait_for_load_state("networkidle", timeout=config.max_wait_ms)


def extract_tables(page: Page, config: ScrapeConfig) -> pd.DataFrame:
    LOGGER.info("Extracting performance tables from the page HTML")
    html = page.content()

    if config.store_html_debug:
        config.store_html_debug.write_text(html, encoding="utf-8")
        LOGGER.info("Wrote debug HTML to %s", config.store_html_debug)

    tables = pd.read_html(html)
    if not tables:
        raise RuntimeError("No HTML tables were detected on the page.")

    LOGGER.debug("Found %d tables", len(tables))
    # Choose the widest table assuming that's the primary data grid.
    tables = [df for df in tables if df.shape[1] >= TABLE_MIN_COLUMNS]
    if not tables:
        raise RuntimeError("No tables met the minimum column requirement.")

    table = max(tables, key=lambda df: df.shape[1] * df.shape[0])
    LOGGER.info(
        "Selected table with %d rows and %d columns", table.shape[0], table.shape[1]
    )
    return table


def run(config: ScrapeConfig) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=config.headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            page = log_in(context, page, config)
            navigate_to_performance_details(page, config)
            table = extract_tables(page, config)
        except Exception as exc:
            if config.pause_on_error:
                LOGGER.error(
                    "Encountered an error. Leaving browser open for inspection: %s",
                    exc,
                )
                input("Press Enter after reviewing the browser window to exit...")
            raise
        finally:
            context.close()
            browser.close()

    config.output_file.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(config.output_file, index=False)
    LOGGER.info("Wrote performance data to %s", config.output_file)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    LOGGER.setLevel(log_level)

    username, password = prompt_credentials(args.username, args.password)

    config = ScrapeConfig(
        username=username,
        password=password,
        output_file=args.output_file,
        headless=args.headless,
        max_wait_ms=args.max_wait_ms,
        store_html_debug=args.store_html_debug,
        pause_on_error=args.pause_on_error,
    )

    try:
        run(config)
    except Exception as exc:  # noqa: BLE001 - surface readable error to user
        LOGGER.error("Scrape failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
