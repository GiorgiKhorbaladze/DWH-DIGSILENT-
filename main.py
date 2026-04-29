# -*- coding: utf-8 -*-

import os

from src.dwh_client import DWHClient
from src.export import save_for_windows_desktop
from src.transform import transform_dataframe


try:
    input_func = raw_input  # Python 2
except NameError:
    input_func = input


def fetch_with_fallback(client):
    api_key = os.getenv("DWH_API_KEY", "").strip()
    try:
        df = client.fetch_csv(api_key)
        return df, "api"
    except Exception as api_error:
        print(u"API-დან წამოღება ვერ შესრულდა:")
        print(u"  - {0}".format(api_error))
        local_path = input_func(u"შეიყვანეთ ლოკალური CSV ფაილის სრული გზა fallback რეჟიმისთვის: ").strip()
        if not local_path:
            raise SystemExit(u"CSV ფაილის გზა არ არის მითითებული. პროგრამა დასრულდა.")
        df = client.read_local_csv(local_path)
        return df, "local_csv"


def main():
    client = DWHClient()
    raw_df, source = fetch_with_fallback(client)

    transformed, report = transform_dataframe(raw_df)
    if report["invalid_p"] or report["invalid_q"]:
        print(
            u"გაფრთხილება: არავალიდური P/Q მნიშვნელობები ნულად გარდაიქმნა (P: {0}, Q: {1}).".format(
                report["invalid_p"], report["invalid_q"]
            )
        )

    output = save_for_windows_desktop(transformed)
    print(u"მონაცემთა წყარო: {0}".format(source))
    print(u"ფაილი წარმატებით შეინახა: {0}".format(output))


if __name__ == "__main__":
    main()
