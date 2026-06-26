import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import polars as pl

from fdm.alerts.fatigue import fatigue_warnings
from fdm.ingestion.roster import load_roster

ROSTER_PATH = REPO_ROOT / "template.xlsx"
OUTPUT_PATH = REPO_ROOT / "data" / "fatigue_warnings.csv"


def main():
    roster = load_roster(ROSTER_PATH)
    warnings = fatigue_warnings(roster)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    warnings.write_csv(OUTPUT_PATH)

    counts = warnings.group_by("warning_type", "severity").len().sort("warning_type", "severity")
    with pl.Config(tbl_rows=20, fmt_str_lengths=90, tbl_width_chars=240):
        print(counts)
        print(warnings.head(15))
    print(f"\n{warnings.height} warnings written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
