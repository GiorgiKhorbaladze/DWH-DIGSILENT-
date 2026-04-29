# -*- coding: utf-8 -*-

import pandas as pd

REQUIRED_COLUMNS = ["name", "P", "Q", "type"]


def transform_dataframe(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(u"CSV-ში აკლია სვეტები: {0}".format(", ".join(missing)))

    out = df.copy()[REQUIRED_COLUMNS]
    out["name"] = out["name"].astype(str).str.strip()
    out["type"] = out["type"].astype(str).str.strip()

    invalid_p = pd.to_numeric(out["P"], errors="coerce").isnull().sum()
    invalid_q = pd.to_numeric(out["Q"], errors="coerce").isnull().sum()

    out["P"] = pd.to_numeric(out["P"], errors="coerce").fillna(0)
    out["Q"] = pd.to_numeric(out["Q"], errors="coerce").fillna(0)

    report = {"invalid_p": int(invalid_p), "invalid_q": int(invalid_q)}
    return out, report
