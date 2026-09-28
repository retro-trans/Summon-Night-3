import argparse
import hashlib
import json
from pathlib import Path

STARTS = (1600, 1680, 1760, 1840, 1920, 2000, 2080, 2160, 2240)

def build():
    base = Path("work/translation/en/chapters_0.1.12/0111")
    reviewed = []
    fixes = []
    for start in STARTS:
        path = base / f"slice_{start:04d}.targets.json"
        raw = path.read_bytes()
        payload = json.loads(raw)
        end = min(start + 79, 2318)
        context_start, context_end = max(1580, start - 20), min(2318, end + 20)
        reviewed.append({
            "target_file": path.name,
            "reviewed_rows": [[start, end]],
            "context_ranges": [[context_start, context_end]],
            "context_count": context_end - context_start + 1,
            "assigned_range": payload["assigned_range"],
            "target_sha256": hashlib.sha256(raw).hexdigest(),
        })
        for entry in payload["translations"].values():
            text = entry["text"]
            if "Farzen" in text or "Yaffa" in text:
                corrected = text.replace("Farzen", "Falzen").replace("Yaffa", "Yafha")
                fixes.append({
                    "target_file": path.name,
                    "source_id": entry["id"],
                    "resource_row": entry["resource_row"],
                    "replacement_text": corrected,
                    "reason": "Uses the locked glossary spelling for this named Guardian.",
                })
    return {
        "resource_id": "00:00111",
        "reviewed_targets": reviewed,
        "required_fixes": fixes,
        "uncertainties": [{
            "resource_rows": [2045, 2057, 2070, 2082],
            "finding": "The English keeps the source's species-level contrast without assigning unsupported individual pronouns to the Guardians."
        }],
        "change_log": [{
            "version": "0.1.12",
            "date": "2026-09-27",
            "change": "Recorded semantic source-context review of Chapter 3 rows 1600–2318 without changing reviewed drafts."
        }]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build()
    output = Path("work/translation/en/chapters_0.1.12/0111/review_1600_2318.json")
    print(json.dumps({"mode": "write" if args.write else "dry-run", "target": str(output), "reviewed_files": len(payload["reviewed_targets"]), "required_fix_count": len(payload["required_fixes"]), "samples": payload["required_fixes"][:4]}, indent=2))
    if args.write:
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
