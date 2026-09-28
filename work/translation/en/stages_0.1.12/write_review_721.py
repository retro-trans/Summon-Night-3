"""Write the independent meaning review for the neighboring opening slices."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from dialogue_encoding import control_tokens, encode_dialogue
from prepare_harbor_context import opening_source


SLICES = (
    ("slice_801.targets.json", 801, 880, 781, 900),
    ("slice_1041.targets.json", 1041, 1120, 1021, 1140),
    ("slice_1201.targets.json", 1201, 1280, 1181, 1300),
)

CORRECTIONS = (
    {
        "target_file": "slice_801.targets.json",
        "source_id": "00:00065:text:00029ea2",
        "opening_row": 804,
        "replacement_text": "Shall we grab 'em and",
        "reason": "The source proposes seizing the suspicious person; the draft's past-tense 'We caught' changes an unperformed proposal into a completed action.",
    },
    {
        "target_file": "slice_801.targets.json",
        "source_id": "00:00065:text:00029eb0",
        "opening_row": 805,
        "replacement_text": "rough 'em up?",
        "reason": "Completes row 804's proposal and preserves the threat to manhandle the person.",
    },
    {
        "target_file": "slice_801.targets.json",
        "source_id": "00:00065:text:0002a0e4",
        "opening_row": 838,
        "replacement_text": "Yes, of course...",
        "reason": "The source is polite assent but supplies no English 'sir' address.",
    },
    {
        "target_file": "slice_1041.targets.json",
        "source_id": "00:00065:text:0002af50",
        "opening_row": 1043,
        "replacement_text": "I'll make sure of it.",
        "reason": "The source asserts that the speaker will manage the escape, rather than making an explicit promise.",
    },
    {
        "target_file": "slice_1041.targets.json",
        "source_id": "00:00065:text:0002af9c",
        "opening_row": 1046,
        "replacement_text": "I'll make sure of it.",
        "reason": "The polite female protagonist counterpart has the same asserted commitment rather than an explicit promise.",
    },
    {
        "target_file": "slice_1201.targets.json",
        "source_id": "00:00065:text:0002bac8",
        "opening_row": 1213,
        "replacement_text": "What's happening,",
        "reason": "Continues through row 1214; source asks what is happening with emphatic 'what on earth,' not a location-specific question.",
    },
    {
        "target_file": "slice_1201.targets.json",
        "source_id": "00:00065:text:0002bade",
        "opening_row": 1214,
        "replacement_text": "on earth...?",
        "reason": "Completes row 1213 and preserves the source's emphatic uncertainty without adding 'here.'",
    },
    {
        "target_file": "slice_1201.targets.json",
        "source_id": "00:00065:text:0002baee",
        "opening_row": 1215,
        "replacement_text": "What's happening,",
        "reason": "Continues through row 1216; female protagonist counterpart has the same source meaning.",
    },
    {
        "target_file": "slice_1201.targets.json",
        "source_id": "00:00065:text:0002bb02",
        "opening_row": 1216,
        "replacement_text": "on earth...?",
        "reason": "Completes row 1215 and preserves the source's emphatic uncertainty without adding 'here.'",
    },
)

UNCERTAINTIES = [
    {
        "opening_rows": [1223, 1224, 1225, 1247, 1249, 1250, 1251, 1252, 1267, 1271, 1272, 1277, 1278, 1279],
        "kind": "runtime_pupil_token_variants",
        "finding": "The reviewed draft retains ▲ in each source row. The Japanese gendered honorific variants have no required distinct English equivalent; token preservation is the correctness condition.",
    },
    {
        "opening_rows": [1231, 1232, 1233, 1234, 1235, 1236],
        "kind": "branch_grouping",
        "finding": "The male and female protagonist recollections use alternative openings that converge on the shared promise-to-protect continuation. The review treats them as alternatives rather than cumulative speech.",
    },
]


def build_payload():
    resource, rows, data = opening_source()
    reviewed_files = []
    reviewed_rows = 0
    for filename, start, end, context_start, context_end in SLICES:
        path = Path(__file__).with_name(filename)
        raw = path.read_bytes()
        draft = json.loads(raw.decode("utf-8"))
        targets = {target["opening_row"]: target for target in draft["translations"].values()}
        if set(targets) != set(range(start, end + 1)) or len(targets) != 80:
            raise ValueError(f"Unexpected coverage in {filename}")
        for opening_row in range(start, end + 1):
            row = rows[opening_row]
            source = data[row["source_offset"]:row["source_offset"] + row["source_byte_length"]].decode("cp932")
            target = targets[opening_row]
            if target["id"] != row["id"] or target["source_sha256"] != row["source_sha256"]:
                raise ValueError(f"Source identity changed in {filename}, row {opening_row}")
            if control_tokens(target["text"]) != control_tokens(source):
                raise ValueError(f"Control tokens changed in {filename}, row {opening_row}")
            encode_dialogue(target["text"], source)
        reviewed_rows += 80
        reviewed_files.append({
            "target_file": filename,
            "target_sha256": hashlib.sha256(raw).hexdigest(),
            "assigned_range": [start, end],
            "rows_examined": {"ranges_inclusive": [[context_start, context_end]], "count": context_end - context_start + 1},
            "target_rows_verified": 80,
        })
    return {
        "schema_version": 1,
        "language": "en",
        "resource_id": resource["id"],
        "reviewer": "independent_slice_721_author",
        "reviewed_files": reviewed_files,
        "total_target_rows_reviewed": reviewed_rows,
        "total_rows_examined": sum(item["rows_examined"]["count"] for item in reviewed_files),
        "required_corrections": list(CORRECTIONS),
        "uncertainties": UNCERTAINTIES,
        "drafts_modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "reviewed_files": payload["reviewed_files"],
        "required_corrections": payload["required_corrections"],
        "uncertainties": payload["uncertainties"],
    }, ensure_ascii=False, indent=2))
    if args.write:
        output = Path(__file__).with_name("review_721.json")
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"wrote": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
