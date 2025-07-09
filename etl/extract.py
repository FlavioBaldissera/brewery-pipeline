import requests
import json
import os

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


BRONZE_PATH = "/opt/airflow/data_lake/bronze"


def fetch_page(page: int):
    url = f"https://api.openbrewerydb.org/v1/breweries?page={page}&per_page=50"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to fetch page {page}: {e}")
        return []
    

def extract_breweries(max_page: int = 5):
    os.makedirs(BRONZE_PATH, exist_ok=True)

    breweries = []
    page = 1

    def fetch_until_empty():
        nonlocal page
        while True:
            data = fetch_page(page)
            if not data:
                break
            breweries.extend(data)
            page += 1

    if max_page is not None:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(fetch_page, range(1, max_page + 1)))
            breweries = [brewery for page_data in results for brewery in page_data]
    else:
        fetch_until_empty()

    if not breweries:
        raise ValueError("No data was extracted from the API.")

    filename = f"{BRONZE_PATH}/breweries_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, "w") as f:
        json.dump(breweries, f, indent=2)

    print(f"Extraction completed with {len(breweries)} records.")