from pathlib import Path

import requests
from dotenv import load_dotenv
import os
import time


class FinanceAPI:
    def __init__(self, base_url, api_key):
        self.api_key = api_key
        # Using the Balance Sheet Statement endpoint to get totalLiabilities
        self.base_url = base_url

    def get_previous_close(self, symbol):
        """
        Fetches the most recent 'totalLiabilities' for a given stock symbol.
        Satisfies the requirement: 'Transformim dhe pasurim real i të dhënave'.
        """
        if not self.api_key:
            return "Missing API Key"

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                quote = data.get("Global Quote", {})
                return quote.get("08. previous close")
            # Construct URL for the specific symbol
            url = f"{self.base_url}{symbol}?limit=1&apikey={self.api_key}"
            print(url)
            response = requests.get(url, timeout=10)


            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Retrieve the specific field we decided on
                    return data[0].get("totalLiabilities", 0)
                else:
                    return "No Data Found"
            else:
                return f"Error {response.status_code}"

        except Exception as e:
            # Trajtim i mungesës së të dhënave ose problemeve të lidhjes
            print(f"API Connection Error for {symbol}: {e}")
            return "Connection Error"