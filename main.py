from __future__ import annotations

import os

from src.dwh_client import DWHClient
from src.export import save_for_windows_desktop
from src.transform import transform_dataframe


def main() -> None:
    api_key = os.getenv("DWH_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("ვერ მოიძებნა DWH_API_KEY გარემოს ცვლადში.")

    client = DWHClient()
    raw_df = client.fetch_csv(api_key)
    transformed = transform_dataframe(raw_df)
    output = save_for_windows_desktop(transformed)
    print(f"ფაილი წარმატებით შეინახა: {output}")


if __name__ == "__main__":
    main()
