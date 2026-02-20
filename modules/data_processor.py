import time
from datetime import datetime
from pathlib import Path


class DataProcessor:
    def __init__(self, dataframe):
        self.df = dataframe

    def _clean_price(self, price_str):
        """Converts string prices like '1,250.50' to float."""
        try:
            clean_str = ''.join(c for c in str(price_str) if c.isdigit() or c == '.')
            return float(clean_str)
        except (ValueError, TypeError):
            return 0.0

    def process_and_save(self, api_client):
        """
        Sorts, enriches top 20, splits the dataframe, and saves two timestamped CSVs.
        """
        # 1. Setup the Directory (outside of modules)
        # __file__ is inside 'modules', so .parent.parent is the root
        root_dir = Path(__file__).resolve().parent.parent
        output_dir = root_dir / "extracted data"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 2. Clean and Sort
        print("Cleaning data and identifying top 20 expensive stocks...")
        self.df['Numeric_Price'] = self.df['Price'].apply(self._clean_price)
        sorted_df = self.df.sort_values(by='Numeric_Price', ascending=False).copy()

        # 3. Split the Dataframe
        top_20 = sorted_df.head(20).copy()
        rest_of_df = sorted_df.iloc[20:].copy()

        # 4. Enrich only the Top 20
        previous_closes = []
        for symbol in top_20['Symbol']:
            print(f"Fetching API data for {symbol}...")
            prev_close = api_client.get_previous_close(symbol)
            previous_closes.append(prev_close)
            time.sleep(1.5)  # Alpha Vantage rate limit protection

        top_20['API_Previous_Close'] = previous_closes

        # 5. Save the CSVs
        top_20_path = output_dir / f"top_expensive_stocks_{timestamp}.csv"
        rest_path = output_dir / f"remaining_stocks_{timestamp}.csv"

        # Cleanup helper columns before saving
        top_20.drop(columns=['Numeric_Price'], inplace=True)
        rest_of_df.drop(columns=['Numeric_Price'], inplace=True)

        top_20.to_csv(top_20_path, index=False)
        rest_of_df.to_csv(rest_path, index=False)

        print(f"Success! Files created in: {output_dir}")
        print(f"1. {top_20_path.name}")
        print(f"2. {rest_path.name}")

        return top_20