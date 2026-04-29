from __future__ import annotations

import io
from dataclasses import dataclass

import pandas as pd
import requests


@dataclass
class DWHClient:
    base_url: str = "https://reporting.gse.com.ge/api/queries/108/results.csv"
    timeout_seconds: int = 30

    def fetch_csv(self, api_key: str) -> pd.DataFrame:
        if not api_key:
            raise ValueError("API key ცარიელია. მიუთითეთ DWH_API_KEY.")

        try:
            response = requests.get(
                self.base_url,
                params={"api_key": api_key},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise RuntimeError("API მოთხოვნას გაუვიდა დრო (timeout).") from exc
        except requests.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "unknown"
            raise RuntimeError(f"API შეცდომა. HTTP status: {code}") from exc
        except requests.RequestException as exc:
            raise RuntimeError("API მოთხოვნა ვერ შესრულდა ქსელური შეცდომის გამო.") from exc

        try:
            return pd.read_csv(io.StringIO(response.text), encoding="utf-8-sig")
        except Exception as exc:
            raise RuntimeError("მიღებული CSV ვერ წაიკითხა pandas-მა.") from exc
