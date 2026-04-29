# -*- coding: utf-8 -*-

import os
from datetime import datetime


def build_output_filename(prefix="DIgSILENT_Table"):
    return "{0}_{1}.csv".format(prefix, datetime.now().strftime("%Y_%m_%d"))


def save_for_windows_desktop(df):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(desktop):
        os.makedirs(desktop)

    out_file = os.path.join(desktop, build_output_filename())
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    return out_file
