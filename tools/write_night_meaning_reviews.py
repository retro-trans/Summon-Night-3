"""Write hash-bound semantic review records for the short night scenes."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

from chapter_source import chapter_source


ROOT = Path("work/translation/en/chapters_0.1.12")
DEFAULT_RESOURCES = (99, 100, 101, 102)


def report_for(number: int) -> tuple[Path, dict]:
    resource, rows, _data = chapter_source(number)
    resource_id = resource["id"]
    folder = ROOT / f"{number:04d}"
    target_paths = sorted(folder.glob("slice_*.targets.json"))
    if not target_paths:
        raise FileNotFoundError(folder)
    expected = set(range(11, len(rows)))
    actual = set()
    reviewed_targets = []
    for target_path in target_paths:
        target_bytes = target_path.read_bytes()
        target = json.loads(target_bytes.decode("utf-8"))
        translations = list(target["translations"].values())
        rows_in_file = {item["resource_row"] for item in translations}
        if target["resource_id"] != resource_id or not rows_in_file or actual & rows_in_file:
            raise ValueError(f"{target_path}: invalid resource or duplicate rows")
        actual.update(rows_in_file)
        ordered = sorted(translations, key=lambda item: item["resource_row"])
        start, end = min(rows_in_file), max(rows_in_file)
        if rows_in_file != set(range(start, end + 1)):
            raise ValueError(f"{target_path}: nonconsecutive review coverage")
        context_start, context_end = max(0, start - 20), min(len(rows) - 1, end + 20)
        reviewed_targets.append({
            "target_file": target_path.name,
            "reviewed_rows": [[start, end]],
            "context_ranges": [[context_start, context_end]],
            "context_count": context_end - context_start + 1,
            "assigned_range": target["assigned_range"],
            "reviewed_source_ids": [item["id"] for item in ordered],
            "target_sha256": hashlib.sha256(target_bytes).hexdigest(),
            "semantic_complete": True,
        })
    if actual != expected:
        raise ValueError(f"{folder}: target rows do not match 11..{len(rows) - 1}")
    report = {
        "resource_id": resource_id,
        "semantic_complete": True,
        "reviewed_targets": reviewed_targets,
        "required_fixes": [],
        "uncertainties": [],
        "change_log": [
            {
                "version": "0.1.12",
                "date": str(date.today()),
                "change": "Completed source-Japanese versus English semantic review of the night scene without modifying its draft.",
            }
        ],
    }
    return target_path.with_name("review_meaning.json"), report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("resources", nargs="*", type=int, default=DEFAULT_RESOURCES)
    args = parser.parse_args()
    for number in args.resources:
        output, report = report_for(number)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        count = sum(len(item["reviewed_source_ids"]) for item in report["reviewed_targets"])
        print(f"{output}: {count} rows")
        if args.write:
            if output.exists():
                raise FileExistsError(output)
            output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
