import argparse
import hashlib
import json
from pathlib import Path

STARTS = (560, 640, 720, 800, 880, 960, 1040)

def build():
    base = Path("work/translation/en/chapters_0.1.12/0088")
    reviewed = []
    for start in STARTS:
        path = base / f"slice_{start:04d}.targets.json"
        raw = path.read_bytes()
        payload = json.loads(raw)
        end = start + 79
        context_start, context_end = max(540, start - 20), min(1139, end + 20)
        reviewed.append({
            "target_file": path.name,
            "reviewed_rows": [[start, end]],
            "context_ranges": [[context_start, context_end]],
            "context_count": context_end - context_start + 1,
            "assigned_range": payload["assigned_range"],
            "target_sha256": hashlib.sha256(raw).hexdigest(),
            "semantic_complete": True,
        })
    return {
        "resource_id": "00:00088",
        "semantic_complete": True,
        "reviewed_targets": reviewed,
        "required_fixes": [],
        "uncertainties": [
            {"resource_rows": [855, 857, 860], "finding": "The runtime pupil-name token is preserved; the source establishes the protective instruction without requiring a gender inference."},
            {"resource_rows": [1093, 1098], "finding": "Yard's invitation is understood as a cautious appeal despite the pirates' identity; the target keeps that condition."}
        ],
        "change_log": [{"version": "0.1.12", "date": "2026-09-27", "change": "Completed source-Japanese versus English semantic review of Chapter 2 rows 560–1119 without modifying drafts."}]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build()
    out = Path("work/translation/en/chapters_0.1.12/0088/review_meaning0560_1119.json")
    print(json.dumps({"mode": "write" if args.write else "dry-run", "target": str(out), "semantic_complete": True, "reviewed_files": len(STARTS), "required_fix_count": 0}, indent=2))
    if args.write:
        if out.exists(): raise FileExistsError(out)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
if __name__ == "__main__": main()
