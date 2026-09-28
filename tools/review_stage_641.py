"""Record a meaning-only review of the three preceding opening slices."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from prepare_harbor_context import opening_source


ROOT = Path("work/translation/en/stages_0.1.12")
SLICES = [
    ("slice_721.targets.json", [721, 800], [[701, 821]]),
    ("slice_961.targets.json", [961, 1040], [[941, 1061]]),
    ("slice_1121.targets.json", [1121, 1200], [[1101, 1221]]),
]
SUGGESTIONS = {
    728: {
        "suggested_text": "I don't feel well...",
        "rationale": "The source is a statement by the pupil, not a question asked by the teacher.",
    },
    729: {
        "suggested_text": "That's why...",
        "rationale": "Completes the pupil's explanation that they feel unwell; the current text reverses the exchange's meaning.",
    },
    982: {
        "suggested_text": "Don't worry.\u3000This ship should have",
        "rationale": "The source expresses expectation that security soldiers ought to be aboard, rather than certainty that they are.",
    },
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_range(ranges):
    return sum(end - start + 1 for start, end in ranges)


def review():
    _, rows, _ = opening_source()
    by_number = {number: row for number, row in enumerate(rows)}
    reviewed = []
    source_to_file = {}
    for filename, assigned_range, examined_ranges in SLICES:
        path = ROOT / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        translations = payload["translations"]
        opening_rows = sorted(value["opening_row"] for value in translations.values())
        expected = list(range(assigned_range[0], assigned_range[1] + 1))
        if opening_rows != expected:
            raise ValueError(f"Unexpected row set in {path}")
        reviewed.append({
            "target_file": str(path).replace("\\", "/"),
            "target_file_sha256": sha256(path),
            "assigned_range": assigned_range,
            "translation_count": len(translations),
            "rows_examined": {
                "ranges_inclusive": examined_ranges,
                "count": count_range(examined_ranges),
            },
        })
        for source_id, value in translations.items():
            source_to_file[source_id] = str(path).replace("\\", "/")
    corrections = {}
    for number, suggestion in SUGGESTIONS.items():
        row = by_number[number]
        source_id = row["id"]
        corrections[source_id] = {
            "opening_row": number,
            "source_sha256": row["source_sha256"],
            "target_file": source_to_file[source_id],
            **suggestion,
        }
    return {
        "resource_id": "00:00065",
        "review_type": "independent_meaning_review",
        "reviewed_slices": reviewed,
        "required_corrections": corrections,
        "uncertainties": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = review()
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": "work/translation/en/stages_0.1.12/review_641.json",
        "reviewed": output["reviewed_slices"],
        "required_corrections": output["required_corrections"],
        "uncertainties": output["uncertainties"],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = ROOT / "review_641.json"
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {destination}")
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
