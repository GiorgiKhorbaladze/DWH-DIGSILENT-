from __future__ import annotations

import os

from src.dwh_client import DWHClient
from src.export import save_for_windows_desktop
from src.transform import transform_dataframe


def fetch_with_fallback(client: DWHClient):
    api_key = os.getenv("DWH_API_KEY", "").strip()
    try:
        df = client.fetch_csv(api_key)
        return df, "api"
    except Exception as api_error:
        print("API-დან წამოღება ვერ შესრულდა:")
        print("  - {}".format(api_error))
        local_path = input("შეიყვანეთ ლოკალური CSV ფაილის სრული გზა fallback რეჟიმისთვის: ").strip()
        if not local_path:
            raise SystemExit("CSV ფაილის გზა არ არის მითითებული. პროგრამა დასრულდა.")
        df = client.read_local_csv(local_path)
        return df, "local_csv"


def main() -> None:
    client = DWHClient()
    raw_df, source = fetch_with_fallback(client)

    transformed, report = transform_dataframe(raw_df)
    if report["invalid_p"] or report["invalid_q"]:
        print(
            "გაფრთხილება: არავალიდური P/Q მნიშვნელობები ნულად გარდაიქმნა "
            "(P: {}, Q: {}).".format(report["invalid_p"], report["invalid_q"])
        )

    output = save_for_windows_desktop(transformed)
    print("მონაცემთა წყარო: {}".format(source))
    print("ფაილი წარმატებით შეინახა: {}".format(output))


if __name__ == "__main__":
    main()
