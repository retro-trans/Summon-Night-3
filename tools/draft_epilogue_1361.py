"""Create the English draft for the final opening rows 1361-1427."""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from dialogue_encoding import control_tokens
from prepare_harbor_context import opening_source


TARGETS = {
    1361: "if you desire it,",
    1362: "draw me!!",
    1363: "A sword...?",
    1364: "A sword in my hand!?",
    1365: "No way...",
    1366: "A sword in my hand!?",
    1367: "Grrr...",
    1368: "I can feel it! I know it!",
    1369: "With this sword...",
    1370: "I can beat them!",
    1371: "Power...",
    1372: "is flowing into me...",
    1373: "With this sword...",
    1374: "I can win!",
    1375: "Eeeek!?",
    1376: "!?",
    1377: "The sword... disappeared...",
    1378: "Whenever you desire power,",
    1379: "call upon me.",
    1380: "I am with",
    1381: "your heart...",
    1382: "What was that...?",
    1383: "Just now...?",
    1384: "What was that...?",
    1385: "Just now...?",
    1386: "But thanks to it,",
    1387: "we were saved...",
    1388: "Teacher...",
    1389: "Teacher...",
    1390: "Teacher...",
    1391: "Teacher...",
    1392: "Ah... yes.",
    1393: "Are you okay?",
    1394: "Are you okay?",
    1395: "Are you hurt",
    1396: "anywhere?",
    1397: "Sniff...",
    1398: "Sniff...",
    1399: "Sniff...",
    1400: "Sniff...",
    1401: "Waaahhh!!",
    1402: "Waaahhh!!",
    1403: "Waaahhh!!",
    1404: "Waaahhh!!",
    1405: "From here...",
    1406: "everything began.",
    1407: "On an unfamiliar island,",
    1408: "what awaited us",
    1409: "were unimaginable days.",
    1410: "But at the time, I",
    1411: "didn't know that yet.",
    1412: "With my sobbing pupil before me,",
    1413: "all I could do was stand there helplessly.",
    1414: "I still...",
    1415: "didn't know...",
    1416: "From here...",
    1417: "everything began...",
    1418: "On an unfamiliar island,",
    1419: "what awaited us",
    1420: "were unimaginable days.",
    1421: "But at the time, I",
    1422: "didn't know that.",
    1423: "I was too busy",
    1424: "comforting my sobbing pupil",
    1425: "to do anything else...",
    1426: "I still...",
    1427: "didn't know...",
}


def scene_note(row_number):
    if row_number <= 1381:
        return "Summoned sword sequence; no control tokens."
    if row_number <= 1404:
        return "Immediate aftermath; unnamed pupils remain unnamed."
    return "Opening narration; no control tokens."


def draft():
    resource, rows, data = opening_source()
    expected = set(range(1361, 1428))
    if set(TARGETS) != expected:
        raise ValueError("Target row mapping must contain exactly rows 1361-1427")
    translations = {}
    for number in sorted(expected):
        row = rows[number]
        source_text = data[
            row["source_offset"]:row["source_offset"] + row["source_byte_length"]
        ].decode("cp932")
        target_text = TARGETS[number]
        if control_tokens(source_text) != control_tokens(target_text):
            raise ValueError(f"Control token mismatch at row {number}")
        translations[row["id"]] = {
            "id": row["id"],
            "source_sha256": row["source_sha256"],
            "source_offset": row["source_offset"],
            "source_byte_length": row["source_byte_length"],
            "reference_instructions": row["reference_instructions"],
            "opening_row": number,
            "text": target_text,
            "status": "draft",
            "notes": scene_note(number),
        }
    return {
        "resource_id": resource["id"],
        "assigned_range": [1361, 1427],
        "rows_examined": {"ranges_inclusive": [[1341, 1427]], "count": 87},
        "translations": translations,
        "uncertainties": [],
        "new_glossary_requests": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = draft()
    samples = [1361, 1364, 1368, 1378, 1395, 1405, 1423]
    by_row = {value["opening_row"]: value for value in output["translations"].values()}
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": "work/translation/en/stages_0.1.12/slice_1361.targets.json",
        "translation_count": len(output["translations"]),
        "samples": [by_row[row] for row in samples],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = Path("work/translation/en/stages_0.1.12/slice_1361.targets.json")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
