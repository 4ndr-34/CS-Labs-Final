import os
from pathlib import Path

from dotenv import load_dotenv
from modules.scraper import Scraper
from modules.finance_api import FinanceAPI
from modules.data_processor import DataProcessor
from modules.security import SecurityManager


def main():
    current_dir = Path(__file__).resolve().parent
    env_path = current_dir.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    #1. Scrape all stocks from Yahoo Finance Most Ative Stocks
    yahoo_finance_url = os.getenv("BASE_URL")
    page_size = os.getenv("PAGE_SIZE")
    encryption_key = os.getenv("ENCRYPTION_KEY")
    print(f"{yahoo_finance_url}{page_size}")
    scraper = Scraper(f"{yahoo_finance_url}{page_size}")
    raw_df = scraper.fetch_data()

    if raw_df.empty:
        print("No data scraped. Check connection.")
        return

    #2. Process, sort and enrich
    api_client = FinanceAPI(os.getenv("ALPHA_VANTAGE_URL"),os.getenv("ALPHA_VANTAGE_API_KEY"))
    processor = DataProcessor(raw_df)

    # This will sort by price and only call the API for the top 10
    generated_files, top_10_df = processor.process_and_save(api_client)

    print("\n--- Results Preview (Top 5) ---")
    print(top_10_df[['Symbol', 'Price', 'API_Previous_Close']].head())

    print("\n--- Securing Data (AES Encryption) ---")
    security = SecurityManager(encryption_key)

    encrypted_files = []
    for file_path in generated_files:
        enc_p = security.encrypt_file(file_path)
        if enc_p:
            encrypted_files.append(enc_p)

    # --- DEMO: DECRYPTION ---
    if encrypted_files:
        for file in encrypted_files:
            print("\n--- Demo: Restoring Encrypted Data ---")
            security.decrypt_file(file)

    print("\nWorkflow Complete. Check the 'extracted data' folder.")

if __name__ == "__main__":
    main()