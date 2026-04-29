from __future__ import annotations

import os
from getpass import getpass

from src.dwh_client import DWHClient
from src.export import save_for_colab
from src.transform import transform_dataframe


def get_api_key_colab_safe() -> str:
    key = os.getenv("DWH_API_KEY", "").strip()
    if key:
        return key

    try:
        from google.colab import userdata  # type: ignore

        key = (userdata.get("DWH_API_KEY") or "").strip()
        if key:
            return key
    except Exception:
        pass

    key = getpass("შეიყვანეთ DWH_API_KEY: ").strip()
    if not key:
        raise ValueError("API key აუცილებელია.")
    return key


def run_colab_flow() -> None:
    api_key = get_api_key_colab_safe()
    client = DWHClient()

    raw_df = client.fetch_csv(api_key)
    print("საწყისი მონაცემების პირველი 5 ჩანაწერი:")
    print(raw_df.head(5))

    transformed = transform_dataframe(raw_df)
    output_path = save_for_colab(transformed)
    print(f"შედეგი შენახულია: {output_path}")

    try:
        from google.colab import files  # type: ignore

        files.download(str(output_path))
    except Exception:
        print("google.colab.files.download ვერ გაეშვა (არ არის Colab გარემო).")


if __name__ == "__main__":
    run_colab_flow()
