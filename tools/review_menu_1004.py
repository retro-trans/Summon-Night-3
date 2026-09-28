"""Record layout-safe, meaning-checked replacements for two action menu labels."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from prepare_harbor_context import opening_source


TARGET = Path("work/translation/en/stages_0.1.12/slice_961.targets.json")
OUTPUT = Path("work/translation/en/stages_0.1.12/menu_review.json")
REPLACEMENTS = {
    1004: "　All I can do is act!",
    1007: "　All I can do is act!",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review():
    _, rows, _ = opening_source()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    by_row = {value["opening_row"]: value for value in payload["translations"].values()}
    corrections = {}
    for number, text in REPLACEMENTS.items():
        row = rows[number]
        corrections[row["id"]] = {
            "opening_row": number,
            "source_sha256": row["source_sha256"],
            "current_text": by_row[number]["text"],
            "approved_replacement_text": text,
            "rationale": "Conveys the source's decisive-action choice while fitting the 31-cell menu limit.",
        }
    contrast_checks = {}
    for number, explanation in {
        1005: "Retain: this is the cautious-proceed alternative to immediate action.",
        1008: "Retain: this is the wait-and-observe alternative to immediate action.",
    }.items():
        row = rows[number]
        contrast_checks[row["id"]] = {
            "opening_row": number,
            "source_sha256": row["source_sha256"],
            "current_text": by_row[number]["text"],
            "finding": explanation,
        }
    return {
        "resource_id": "00:00065",
        "review_type": "menu_layout_meaning_review",
        "reviewed_target_file": str(TARGET).replace("\\", "/"),
        "reviewed_target_file_sha256": sha256(TARGET),
        "rows_examined": {"ranges_inclusive": [[996, 1018]], "count": 23},
        "approved_replacements": corrections,
        "verified_unchanged_choices": contrast_checks,
        "uncertainties": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = review()
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": str(OUTPUT).replace("\\", "/"),
        "approved_replacements": output["approved_replacements"],
        "verified_unchanged_choices": output["verified_unchanged_choices"],
    }, ensure_ascii=False, indent=2))
    if args.write:
        if OUTPUT.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {OUTPUT}")
        OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
