import os
from pathlib import Path

from dotenv import load_dotenv
from modules.scraper import Scraper
from modules.finance_api import FinanceAPI
from modules.data_processor import DataProcessor


def main():
    current_dir = Path(__file__).resolve().parent
    env_path = current_dir.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("ALPHA_VANTAGE_KEY")

    # PHASE 1: Scrape all stocks
    yahoo_finance_url = os.getenv("BASE_URL")
    page_size = os.getenv("PAGE_SIZE")
    scraper = Scraper(f"{yahoo_finance_url}{page_size}")
    raw_df = scraper.fetch_data()

    if raw_df.empty:
        print("No data scraped. Check connection.")
        return

    # PHASE 2: Process, Sort, and Enrich
    api_client = FinanceAPI(os.getenv("ALPHA_VANTAGE_URL"),os.getenv("ALPHA_VANTAGE_API_KEY"))
    processor = DataProcessor(raw_df)

    # This will sort by price and only call the API for the top 20
    final_top_20 = processor.process_and_save(api_client)

    print("\n--- Results Preview (Top 5) ---")
    print(final_top_20[['Symbol', 'Price', 'API_Previous_Close']].head())


if __name__ == "__main__":
    main()