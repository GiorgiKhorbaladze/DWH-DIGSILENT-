from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def build_output_filename(prefix: str = "DIgSILENT_Table") -> str:
    return f"{prefix}_{datetime.now().strftime('%Y_%m_%d')}.csv"


def save_for_colab(df: pd.DataFrame, output_dir: str = "/content/output") -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    out_file = path / build_output_filename()
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    return out_file


def save_for_windows_desktop(df: pd.DataFrame) -> Path:
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    out_file = desktop / build_output_filename()
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    return out_file
