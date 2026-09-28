"""Create the English draft for opening rows 1201-1280.

Run without --write to validate source alignment and preview sample targets.
"""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from dialogue_encoding import control_tokens
from prepare_harbor_context import opening_source


TARGETS = {
    1201: "No...?",
    1202: "It was just",
    1203: "so sunny a moment ago...",
    1204: "No...?",
    1205: "It was just",
    1206: "so sunny a moment ago...",
    1207: "No...?",
    1208: "It was just",
    1209: "so sunny a moment ago...",
    1210: "No...?",
    1211: "It was just",
    1212: "so sunny a moment ago...",
    1213: "What's happening",
    1214: "here...?",
    1215: "What's happening",
    1216: "here...?",
    1217: "Ugh!?",
    1218: "Ugh!?",
    1219: "Aaaah!?",
    1220: "Aaaah!?",
    1221: "Eek!?",
    1222: "Eek!?",
    1223: "▲!?",
    1224: "▲!?",
    1225: "▲!?",
    1226: "Hey, that's too dangerous!",
    1227: "Wait!",
    1228: "If you jump in",
    1229: "now...",
    1230: "...!!",
    1231: "I promised",
    1232: "them...",
    1233: "I made a promise",
    1234: "to them...",
    1235: "I'd protect them.",
    1236: "And yet...",
    1237: "Ghh...",
    1238: "I can't breathe...",
    1239: "Ah...",
    1240: "If only I had more strength...",
    1241: "Ah, if only I...",
    1242: "had more strength,",
    1243: "enough strength",
    1244: "to protect them...",
    1245: "if only I had it...",
    1246: "I'm sorry...",
    1247: "▲...",
    1248: "I'm sorry...",
    1249: "▲...",
    1250: "▲...",
    1251: "▲...",
    1252: "▲...",
    1253: "Do you",
    1254: "desire power...?",
    1255: "Huh?",
    1256: "Then take me in hand.",
    1257: "If you wish to live,",
    1258: "inherit me.",
    1259: "Live...",
    1260: "Come, reach out",
    1261: "and seize it!!",
    1262: "......!?",
    1263: "That's right...",
    1264: "I was trying to",
    1265: "save them when I fell into the sea...",
    1266: "That's right!?",
    1267: "What about ▲...?",
    1268: "That's right!",
    1269: "I was trying to",
    1270: "save them when I fell into the sea...",
    1271: "What about ▲!?",
    1272: "What about ▲!?",
    1273: "D-don't come any closer!!",
    1274: "D-don't come any closer!!",
    1275: "Nooo!!",
    1276: "Nooo!!",
    1277: "▲!?",
    1278: "▲!?",
    1279: "▲!?",
    1280: "Grrr...",
}


def scene_note(row_number):
    if row_number <= 1216:
        return "Storm reaction branch; no control tokens."
    if row_number <= 1229:
        return "Shipwreck reaction branch; pupil-name tokens retained without literal honorifics."
    if row_number <= 1252:
        return "Shipwreck reflection branch; pupil-name tokens retained without inferred gender."
    if row_number <= 1262:
        return "Mysterious voice; no control tokens."
    if row_number <= 1279:
        return "Shipwreck recollection branch; pupil-name tokens retained without literal honorifics."
    return "Creature sound at the slice boundary; no control tokens."


def draft():
    resource, rows, data = opening_source()
    expected = set(range(1201, 1281))
    if set(TARGETS) != expected:
        raise ValueError("Target row mapping must contain exactly rows 1201-1280")
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
        "assigned_range": [1201, 1280],
        "rows_examined": {"ranges_inclusive": [[1181, 1340]], "count": 160},
        "translations": translations,
        "uncertainties": [],
        "new_glossary_requests": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = draft()
    samples = [1201, 1223, 1231, 1241, 1256, 1267, 1280]
    by_row = {value["opening_row"]: value for value in output["translations"].values()}
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": "work/translation/en/stages_0.1.12/slice_1201.targets.json",
        "translation_count": len(output["translations"]),
        "samples": [by_row[row] for row in samples],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = Path("work/translation/en/stages_0.1.12/slice_1201.targets.json")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
