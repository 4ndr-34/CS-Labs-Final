import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import pandas as pd
import os
from dotenv import load_dotenv


class Scraper:
    def __init__(self, base_url, headless=True):
        self.base_url = base_url
        self.headless = headless
        self.last_request_time = None

    def _smart_delay(self, seconds=2):
        """Uses datetime to ensure a minimum gap between requests (Assignment Requirement)."""
        if self.last_request_time is not None:
            elapsed = (datetime.datetime.now() - self.last_request_time).total_seconds()
            if elapsed < seconds:
                wait_until = datetime.datetime.now() + datetime.timedelta(seconds=(seconds - elapsed))
                while datetime.datetime.now() < wait_until:
                    pass
        self.last_request_time = datetime.datetime.now()

    def handle_cookies(self, page):
        reject_cookies_button = page.locator('button.reject-all')
        if reject_cookies_button.is_visible() and reject_cookies_button.is_enabled():
            reject_cookies_button.click()


    def fetch_data(self):
        all_rows = []
        headers = []
        excluded_indices = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(self.base_url, timeout=60000)

                while True:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scraping page...")

                    self.handle_cookies(page)

                    page.wait_for_selector("div.table-container table")
                    table = page.query_selector("div.table-container table")

                    # 1. Capture Headers and identify columns to EXCLUDE (Only on Page 1)
                    if not headers:
                        th_elements = table.query_selector_all("thead th")
                        for idx, th in enumerate(th_elements):

                            if th.get_attribute('data-testid-header').strip() == "sparkline" or th.get_attribute('data-testid-header').strip() == "fiftyTwoWeekRange":
                                excluded_indices.append(idx)
                                continue

                            # If it's a valid column, add the cleaned text to headers
                            headers.append(th.inner_text().strip())

                    # 2. Extract Table Rows excluding filtered indices
                    tr_elements = table.query_selector_all("tbody tr")
                    for tr in tr_elements:
                        cells = tr.query_selector_all("td")
                        if not cells:
                            continue

                        filtered_row = [
                            cells[i].inner_text().strip()
                            for i in range(len(cells)) if i not in excluded_indices
                        ]
                        all_rows.append(filtered_row)

                    # 3. Pagination Logic: Find 'Next' button
                    next_btn = page.locator('button[data-testid="next-page-button"]')

                    if next_btn.is_visible() and next_btn.is_enabled():
                        # Get first cell text to detect when page has loaded new data
                        first_val_before = page.locator("tbody tr td").first.inner_text()

                        self._smart_delay(seconds=2)
                        next_btn.click()

                        # Wait for the table data to refresh
                        try:
                            page.wait_for_function(
                                f"val => document.querySelector('tbody tr td').innerText !== '{first_val_before}'",
                                timeout=10000
                            )
                        except:
                            print("Wait timeout: Page may not have changed or last page reached.")
                            break
                    else:
                        print("Next button disabled or missing. Reached end of data.")
                        break

            except Exception as e:
                print(f"Scraping error encountered: {e}")
            finally:
                browser.close()

        # Build and return the final DataFrame
        df = pd.DataFrame(all_rows, columns=headers)
        print(f"Extracted {len(df)} rows.")
        return df
