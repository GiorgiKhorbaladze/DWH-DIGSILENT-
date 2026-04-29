# -*- coding: utf-8 -*-

import io

import pandas as pd
import requests


class DWHClient(object):
    def __init__(self, base_url=None, timeout_seconds=30):
        self.base_url = base_url or "https://reporting.gse.com.ge/api/queries/108/results.csv"
        self.timeout_seconds = timeout_seconds

    def fetch_csv(self, api_key):
        if not api_key:
            raise ValueError(
                u"DWH_API_KEY არ არის დაყენებული.\n"
                u"CMD (current window): set DWH_API_KEY=...\n"
                u"PowerShell (current session): $env:DWH_API_KEY=\"...\"\n"
                u"PowerShell (persist): setx DWH_API_KEY \"...\""
            )

        try:
            response = requests.get(
                self.base_url,
                params={"api_key": api_key},
                timeout=self.timeout_seconds,
            )
        except requests.exceptions.ConnectionError:
            raise RuntimeError(u"ქსელური/DNS შეცდომა: DWH API ჰოსტი მიუწვდომელია ამ მანქანიდან.")
        except requests.Timeout:
            raise RuntimeError(u"API მოთხოვნას გაუვიდა დრო (timeout).")
        except requests.RequestException:
            raise RuntimeError(u"API მოთხოვნა ვერ შესრულდა ქსელური შეცდომის გამო.")

        if response.status_code in (401, 403):
            raise RuntimeError(
                u"წვდომა აკრძალულია (HTTP {0}). შეამოწმეთ DWH_API_KEY.".format(response.status_code)
            )
        if not response.ok:
            raise RuntimeError(u"API შეცდომა. HTTP status: {0}".format(response.status_code))

        try:
            return pd.read_csv(io.BytesIO(response.content), encoding="utf-8-sig")
        except Exception:
            raise RuntimeError(u"მიღებული CSV ვერ წაიკითხა pandas-მა.")

    @staticmethod
    def read_local_csv(path):
        try:
            return pd.read_csv(path, encoding="utf-8-sig")
        except IOError:
            raise IOError(u"ფაილი ვერ მოიძებნა ან ვერ გაიხსნა: {0}".format(path))
        except Exception:
            raise RuntimeError(u"CSV ვერ წაიკითხა pandas-მა: {0}".format(path))
