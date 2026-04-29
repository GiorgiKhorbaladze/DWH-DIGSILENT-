from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ["name", "P", "Q", "type"]


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"CSV-ში აკლია სვეტები: {', '.join(missing)}")

    out = df.copy()
    out = out[REQUIRED_COLUMNS]

    out["name"] = out["name"].astype(str).str.strip()
    out["type"] = out["type"].astype(str).str.strip()

    # 1.py-ს პრაქტიკული ლოგიკის შენარჩუნება: P/Q იყოს რიცხვითი და არავალიდური მნიშვნელობები -> 0
    out["P"] = pd.to_numeric(out["P"], errors="coerce").fillna(0)
    out["Q"] = pd.to_numeric(out["Q"], errors="coerce").fillna(0)

    return out
