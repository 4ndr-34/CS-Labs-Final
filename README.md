# Financial Data Extraction and Security Pipeline

## Project Overview
This project is an automated financial data pipeline designed to extract, process, and secure market information from Yahoo Finance. It integrates web scraping, external API enrichment, and symmetric AES encryption into a structured architecture. The system identifies high-value stocks, enriches them with historical closing data, and ensures the results are stored in an encrypted format.

---

## Technical Architecture
The system is divided into four functional modules to ensure separation of concerns:

* **Scraper Module**: Uses Playwright to navigate Yahoo Finance, handling dynamic content and multi-page pagination. It implements dynamic filtering to remove non-numerical columns such as graphical sparklines.
* **API Client Module**: Interfaces with the Alpha Vantage API to retrieve the "Previous Close" attribute for specific stock symbols.
* **Data Processor Module**: Performs data cleaning, converts string-based currency to numerical floats, and splits the dataset into high-priority (expensive) and secondary stock lists.
* **Security Module**: Implements AES-128 bit encryption using the Fernet (cryptography) library. It manages directory organization and persistent key storage.



---

## Security Implementation
The project satisfies advanced security requirements through the following mechanisms:

* **Symmetric Encryption**: All extracted CSV files are converted into `.enc` binary files using the Fernet symmetric encryption standard.
* **Dynamic Key Management**: The system automatically detects missing or empty encryption keys in the `.env` file. It generates a new key upon first execution and persists it to the environment file to allow for future decryption.
* **Data at Rest Protection**: Once a file is processed and encrypted, the original plain-text CSV is deleted from the disk to prevent unauthorized access.
* **Sub-directory Isolation**: The system maintains a strict directory structure, separating encrypted assets from restored (decrypted) files.



---

## Data Workflow
1.  **Extraction**: The Scraper retrieves all "Most Active" stocks (300+ entries) across multiple pages.
2.  **Transformation**: The Processor cleans the "Price" column and identifies the top 10 most expensive stocks.
3.  **Enrichment**: The API Client fetches the "Previous Close" for the top 10 stocks to provide a comparison against current prices.
4.  **Storage**: The data is split into two timestamped CSV files.
5.  **Securing**: Both files are encrypted and moved to the `/extracted data/encrypted/` directory.

---
## API Limitations and Usage
The project utilizes the Alpha Vantage free tier for financial data enrichment. Please note the following:
* **Rate Limits**: Alpha Vantage currently allows a maximum of **25 requests per day**.
* **Optimization Strategy**: To ensure the application remains functional within these limits, the `DataProcessor` is configured to only enrich the top 10 most expensive stocks. This avoids hitting the daily quota while still satisfying the requirements for data integration.

---
# Installation and Usage

## Environment Management
The project uses a Python virtual environment (`.venv`) to isolate dependencies. 

### Benefits:
- **Consistency**: Ensures the project runs with the exact versions listed in `requirements.txt`.
- **Cleanliness**: Keeps your global Python installation free of project-specific packages like Playwright or Cryptography.

### Setup Instructions:
1. Create the environment:
   ```bash
   python -m venv .venv
   ```
### Prerequisites
* Python 3.10+
* Playwright
* Pandas
* Cryptography
* Python-dotenv

### Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Install Playwright browser:
    ```bash
    python -m playwright install chromium
    ```
3.  Create a `.env` file in the root directory with the following variables:
    * `ALPHA_VANTAGE_KEY`: Your Alpha Vantage API Key
    * `BASE_URL`: https://finance.yahoo.com/markets/stocks/most-active/?start=0&count=
    * `PAGE_SIZE`: 100
    * `ENCRYPTION_KEY`: (Leave empty for initial auto-generation)

### Execution
Run the main orchestrator:
```bash
python modules/main.py
```
