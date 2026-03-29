import os
import time
from urllib.parse import quote

import requests
from dotenv import load_dotenv


load_dotenv()


class AirtableClient:
    """
    Small Airtable client for reading all records from one table.
    """

    def __init__(self) -> None:
        self.pat = os.getenv("AIRTABLE_PAT", "").strip()
        self.base_id = os.getenv("AIRTABLE_BASE_ID", "").strip()
        self.table_id = os.getenv("AIRTABLE_TABLE_ID", "").strip()
        self.view_name = os.getenv("AIRTABLE_VIEW_NAME", "").strip()

        if not self.pat:
            raise ValueError("AIRTABLE_PAT is missing from .env")
        if not self.base_id:
            raise ValueError("AIRTABLE_BASE_ID is missing from .env")
        if not self.table_id:
            raise ValueError("AIRTABLE_TABLE_ID is missing from .env")

        encoded_table_id = quote(self.table_id, safe="")
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{encoded_table_id}"

        self.headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json",
        }

    def get_status(self) -> dict:
        return {
            "pat_loaded": bool(self.pat),
            "base_id": self.base_id,
            "table_id": self.table_id,
            "view_name": self.view_name,
            "base_url": self.base_url,
        }

    def status(self) -> dict:
        return self.get_status()

    def get_all_records(self) -> list[dict]:
        all_records = []
        offset = ""

        while True:
            params = {}

            if offset:
                params["offset"] = offset

            if self.view_name:
                params["view"] = self.view_name

            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 429:
                time.sleep(1)
                continue

            response.raise_for_status()
            payload = response.json()

            records = payload.get("records", [])
            all_records.extend(records)

            offset = payload.get("offset", "")
            if not offset:
                break

        return all_records
