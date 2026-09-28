import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chapter_source import chapter_source

STARTS = (1120, 1200, 1280, 1360, 1440, 1520, 1600, 1680)
REPLACEMENTS = {
    1131: ("But now I've quit", "Uses the completed-action sense of the source; the present-tense draft changes its timing."),
    1202: ("Well...", "The source is an impressed reaction before the following compliment, not confused surprise."),
}

def build():
    resource, rows, _ = chapter_source(88)
    base = Path("work/translation/en/chapters_0.1.12/0088")
    reviewed = []
    all_rows = {}
    for start in STARTS:
        path = base / f"slice_{start:04d}.targets.json"
        raw = path.read_bytes()
        draft = json.loads(raw)
        by_row = {entry["resource_row"]: entry for entry in draft["translations"].values()}
        all_rows.update(by_row)
        end = min(start + 79, 1710)
        context_end = min(end + 20, 1710)
        reviewed.append({
            "target_file": path.name,
            "reviewed_rows": [[start, end]],
            "context_ranges": [[max(1100, start - 20), context_end]],
            "context_count": context_end - max(1100, start - 20) + 1,
            "assigned_range": draft["assigned_range"],
            "target_sha256": hashlib.sha256(raw).hexdigest(),
        })
    fixes = []
    for number, (text, reason) in REPLACEMENTS.items():
        entry = all_rows[number]
        fixes.append({
            "target_file": f"slice_{(number // 80) * 80:04d}.targets.json",
            "source_id": entry["id"],
            "resource_row": number,
            "replacement_text": text,
            "reason": reason,
        })
    return {
        "resource_id": resource["id"],
        "reviewed_targets": reviewed,
        "required_fixes": fixes,
        "uncertainties": [{"resource_rows": [1344, 1345], "finding": "The target conveys the speaker's refusal to accept responsibility; no change is required, but the English is interpretive because the source is an idiomatic dismissal."}],
        "change_log": [{"version": "0.1.12", "date": "2026-09-27", "change": "Recorded source-context meaning review of Chapter 2 rows 1120–1710 without altering reviewed drafts."}],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build()
    output = Path("work/translation/en/chapters_0.1.12/0088/review_1120_1710.json")
    print(json.dumps({"mode": "write" if args.write else "dry-run", "target": str(output), "reviewed_files": len(payload["reviewed_targets"]), "required_fixes": payload["required_fixes"]}, indent=2))
    if args.write:
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
