import pandas as pd


class DataProcessor:
    def __init__(self, dataframe):
        self.df = dataframe

    def add_liabilities(self, api_client):
        """
        Loops through the dataframe and fetches liabilities for each symbol.
        Note: We use a small delay or limit for testing to respect API rates.
        """
        print("Starting API Enrichment...")

        # We create a map to store results to avoid duplicate API calls for the same symbol
        liabilities_cache = {}

        def fetch_val(symbol):
            if symbol not in liabilities_cache:
                liabilities_cache[symbol] = api_client.get_total_liabilities(symbol)
            return liabilities_cache[symbol]

        # Apply the API call to the Symbol column
        # .head(20) is recommended for testing if you have a free API limit
        self.df['Total_Liabilities'] = self.df['Symbol'].apply(fetch_val)

        return self.df