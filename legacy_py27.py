# -*- coding: utf-8 -*-

import os
import csv
import sys
import codecs
import datetime
import urllib2

API_URL = "https://reporting.gse.com.ge/api/queries/108/results.csv?api_key={0}"
REQUIRED_COLUMNS = ["name", "P", "Q", "type"]


def get_api_key():
    return os.getenv("DWH_API_KEY", "").strip()


def fetch_csv_from_api(api_key):
    if not api_key:
        raise ValueError("DWH_API_KEY is not set.")

    url = API_URL.format(api_key)
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req, timeout=30)
        content = response.read()
        return content
    except Exception as exc:
        raise RuntimeError("API fetch failed: {0}".format(exc))


def read_csv_text_to_rows(text_bytes):
    # utf-8-sig removes BOM if exists
    text = text_bytes.decode("utf-8-sig")
    lines = text.splitlines()
    reader = csv.DictReader(lines)
    rows = [row for row in reader]
    return rows, reader.fieldnames


def read_local_csv(path):
    if not os.path.isfile(path):
        raise IOError("File not found: {0}".format(path))

    f = codecs.open(path, "r", "utf-8-sig")
    try:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
        return rows, reader.fieldnames
    finally:
        f.close()


def validate_columns(fieldnames):
    missing = [c for c in REQUIRED_COLUMNS if c not in (fieldnames or [])]
    if missing:
        raise ValueError("Missing required columns: {0}".format(", ".join(missing)))


def to_float_or_zero(value):
    try:
        if value is None:
            return 0.0
        v = str(value).strip()
        if v == "":
            return 0.0
        return float(v)
    except Exception:
        return 0.0


def transform_rows(rows):
    out = []
    invalid_p = 0
    invalid_q = 0

    for row in rows:
        name = str(row.get("name", "")).strip()
        row_type = str(row.get("type", "")).strip()

        p_raw = row.get("P", "")
        q_raw = row.get("Q", "")

        p_val = to_float_or_zero(p_raw)
        q_val = to_float_or_zero(q_raw)

        try:
            if str(p_raw).strip() != "" and float(str(p_raw).strip()) == p_val:
                pass
        except Exception:
            invalid_p += 1

        try:
            if str(q_raw).strip() != "" and float(str(q_raw).strip()) == q_val:
                pass
        except Exception:
            invalid_q += 1

        out.append({"name": name, "P": p_val, "Q": q_val, "type": row_type})

    return out, {"invalid_p": invalid_p, "invalid_q": invalid_q}


def get_desktop_path():
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    if not os.path.isdir(desktop):
        os.makedirs(desktop)
    return desktop


def build_filename():
    today = datetime.datetime.now().strftime("%Y_%m_%d")
    return "DIgSILENT_Table_{0}.csv".format(today)


def write_output(rows):
    output_path = os.path.join(get_desktop_path(), build_filename())
    f = codecs.open(output_path, "w", "utf-8-sig")
    try:
        writer = csv.writer(f)
        writer.writerow(REQUIRED_COLUMNS)
        for row in rows:
            writer.writerow([row["name"], row["P"], row["Q"], row["type"]])
    finally:
        f.close()
    return output_path


def prompt_local_path():
    sys.stdout.write("Enter local CSV path: ")
    sys.stdout.flush()
    return sys.stdin.readline().strip()


def main():
    api_key = get_api_key()
    rows = None
    fieldnames = None
    source = "api"

    try:
        raw = fetch_csv_from_api(api_key)
        rows, fieldnames = read_csv_text_to_rows(raw)
    except Exception as exc:
        print("API call failed ({0}).".format(exc))
        print("Fallback mode: provide local CSV path.")
        local_path = prompt_local_path()
        if not local_path:
            print("No local CSV path provided. Exiting.")
            return
        rows, fieldnames = read_local_csv(local_path)
        source = "local_csv"

    validate_columns(fieldnames)
    transformed, report = transform_rows(rows)
    out_file = write_output(transformed)

    print("Source: {0}".format(source))
    if report["invalid_p"] or report["invalid_q"]:
        print("Invalid values converted to 0.0 (P: {0}, Q: {1})".format(
            report["invalid_p"], report["invalid_q"]))
    print("Saved: {0}".format(out_file))


if __name__ == "__main__":
    main()
