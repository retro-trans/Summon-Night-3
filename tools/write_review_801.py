"""Write a source-grounded meaning review for the assigned stage drafts."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from prepare_harbor_context import opening_source


STAGES = Path("work/translation/en/stages_0.1.12")
REVIEWS = [
    {
        "target_file": "slice_641.targets.json",
        "reviewed_rows": [[641, 720]],
        "context_ranges": [[621, 740]],
        "context_count": 120,
    },
    {
        "target_file": "slice_881.targets.json",
        "reviewed_rows": [[881, 960]],
        "context_ranges": [[861, 980]],
        "context_count": 120,
    },
    {
        "target_file": "slice_1281.targets.json",
        "reviewed_rows": [[1281, 1360]],
        "context_ranges": [[1261, 1360]],
        "context_count": 100,
    },
    {
        "target_file": "slice_1361.targets.json",
        "reviewed_rows": [[1361, 1427]],
        "context_ranges": [[1341, 1427]],
        "context_count": 87,
    },
]

FIXES = [
    {
        "target_file": "slice_881.targets.json",
        "source_id": "00:00065:text:0002a412",
        "opening_row": 884,
        "replacement_text": "Leaving the mansion and",
        "reason": "Restores the source's coordinated thought with rows 885-886; the existing phrase incorrectly made living with strangers sound like the purpose of leaving.",
    },
    {
        "target_file": "slice_881.targets.json",
        "source_id": "00:00065:text:0002a41e",
        "opening_row": 885,
        "replacement_text": "living with strangers",
        "reason": "Completes the corrected coordinated thought with row 884; the living action belongs in the full source sentence.",
    },
    {
        "target_file": "slice_1361.targets.json",
        "source_id": "00:00065:text:0002c46e",
        "opening_row": 1361,
        "replacement_text": "to survive,",
        "reason": "Rows 1360-1362 currently repeat the conditional. This completes the source meaning as 'If you desire the power to survive, draw me!!'.",
    },
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review():
    resource, rows, _ = opening_source()
    source_by_id = {row["id"]: row for row in rows}
    targets = {}
    reviewed = []
    for item in REVIEWS:
        path = STAGES / item["target_file"]
        target = json.loads(path.read_text(encoding="utf-8"))
        targets[item["target_file"]] = target
        reviewed.append({
            **item,
            "assigned_range": target["assigned_range"],
            "target_sha256": sha256(path),
        })
    for fix in FIXES:
        source = source_by_id[fix["source_id"]]
        if source["id"] != fix["source_id"]:
            raise ValueError("Source ID lookup failed")
        if fix["opening_row"] != rows.index(source):
            raise ValueError("Opening-row mismatch")
        if fix["source_id"] not in targets[fix["target_file"]]["translations"]:
            raise ValueError("Fix source ID not found in reviewed target")
    return {
        "resource_id": resource["id"],
        "reviewed_targets": reviewed,
        "required_fixes": FIXES,
        "uncertainties": [
            {
                "opening_rows": [1378, 1381],
                "finding": "The sword's speaking entity remains unnamed in this context; no identity or gender is inferred from the target.",
            },
        ],
        "change_log": [
            {
                "version": "0.1.12",
                "date": "2026-09-27",
                "change": "Recorded independent source-context meaning review of slices 641, 881, 1281, and 1361 without changing the reviewed drafts.",
            }
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = review()
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": str(STAGES / "review_801.json"),
        "reviewed_targets": output["reviewed_targets"],
        "required_fixes": output["required_fixes"],
        "uncertainties": output["uncertainties"],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = STAGES / "review_801.json"
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing review: {destination}")
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
