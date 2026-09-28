"""Write the bounded English draft for opening rows 1121 through 1200."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

from dialogue_encoding import control_tokens, encode_dialogue
from prepare_harbor_context import opening_source


TEXT = {
    1121: "Let's hurry to the boat.",
    1122: "...!?",
    1123: "Sorry, but",
    1124: "I can't let you",
    1125: "do that, you see...",
    1126: "Damn it!?",
    1127: "There were still guards",
    1128: "left...",
    1129: "What!?",
    1130: "There were still guards",
    1131: "left...?",
    1132: "If you behave, we won't",
    1133: "take your lives, so why don't you",
    1134: "just surrender quietly?",
    1135: "▲...",
    1136: "Get behind me.",
    1137: "▲,",
    1138: "get behind me.",
    1139: "▲,",
    1140: "get behind me.",
    1141: "!?",
    1142: "I can't let you",
    1143: "do that.",
    1144: "Not on our side, either.",
    1145: "I appreciate your concern,",
    1146: "but...",
    1147: "we can't do that",
    1148: "either.",
    1149: "Not on our side...",
    1150: "Well, it can't be helped...",
    1151: "That's the natural reaction.",
    1152: "Rough them up until",
    1153: "they say they've had enough!",
    1154: "Yeah!!",
    1155: "Huff... huff...",
    1156: "Amazing...",
    1157: "Still want to fight?",
    1158: "Do you still wish to fight?",
    1159: "Urgh...",
    1160: "...Step back.",
    1161: "You're way",
    1162: "out of your league.",
    1163: "Captain...",
    1164: "In that case,",
    1165: "I'll be your opponent now.",
    1166: "You really won't",
    1167: "let us go, will you?",
    1168: "You really won't",
    1169: "let us go, will you?",
    1170: "Yeah, sorry to be selfish, but",
    1171: "we have our own reasons",
    1172: "for this.",
    1173: "And besides... I",
    1174: "love going toe-to-toe with",
    1175: "strong opponents.",
    1176: "Even if my opponent is",
    1177: "a woman.",
    1178: "...!",
    1179: "Ah, come on!",
    1180: "This is taking forever!!",
    1181: "Miss...!",
    1182: "I'll be your opponent next.",
    1183: "Come at me!",
    1184: "You really won't",
    1185: "let us go, will you?",
    1186: "You really won't",
    1187: "let us go, will you?",
    1188: "Sorry, but we have",
    1189: "our own pride to uphold.",
    1190: "If we back down now,",
    1191: "the Kyle family's name",
    1192: "will be disgraced.",
    1193: "Don't underestimate me",
    1194: "just because I'm a woman, or you'll",
    1195: "regret it!",
    1196: "...!",
    1197: "W-what!?",
    1198: "Huh!?",
    1199: "The tide changed!?",
    1200: "Aah!?",
}

NOTES = {
    1121: "Completes preceding rows 1119-1120; female protagonist alternative.",
    1123: "Completes with rows 1124-1125.",
    1124: "Continuation of row 1123.",
    1125: "Completes rows 1123-1124.",
    1127: "Completes with row 1128.",
    1130: "Completes with row 1131; female protagonist alternative.",
    1132: "Completes with rows 1133-1134; the pirate's conditional surrender demand is preserved.",
    1133: "Continuation of row 1132.",
    1134: "Completes rows 1132-1133.",
    1135: "Preserves the runtime pupil-name token ▲ exactly.",
    1136: "Follows the runtime pupil-name address in row 1135.",
    1137: "Preserves the runtime pupil-name token ▲ exactly; male pupil-address variant.",
    1138: "Completes row 1137.",
    1139: "Preserves the runtime pupil-name token ▲ exactly; female pupil-address variant.",
    1140: "Completes row 1139.",
    1142: "Completes with rows 1143-1144.",
    1143: "Continuation of row 1142.",
    1144: "Completes rows 1142-1143.",
    1145: "Completes with rows 1146-1149; polite protagonist alternative.",
    1147: "Continuation of row 1145 after row 1146's hesitation.",
    1148: "Completes rows 1145-1147.",
    1150: "Completes with row 1151.",
    1152: "Completes with row 1153.",
    1160: "Completes with rows 1161-1162.",
    1161: "Continuation of row 1160.",
    1162: "Completes rows 1160-1161.",
    1164: "Completes with row 1165.",
    1166: "Completes with row 1167; male protagonist alternative.",
    1168: "Completes with row 1169; female protagonist alternative.",
    1170: "Completes with rows 1171-1172.",
    1171: "Continuation of row 1170.",
    1172: "Completes rows 1170-1171.",
    1173: "Completes with rows 1174-1175.",
    1174: "Continuation of row 1173.",
    1175: "Completes rows 1173-1174.",
    1176: "Completes with row 1177; opponent's stated gender is preserved.",
    1179: "Completes with row 1180.",
    1182: "Completes with row 1183.",
    1184: "Completes with row 1185; male protagonist alternative.",
    1186: "Completes with row 1187; female protagonist alternative.",
    1188: "Completes with row 1189.",
    1190: "Completes with rows 1191-1192; Kyle family name is locked glossary spelling.",
    1191: "Continuation of row 1190.",
    1192: "Completes rows 1190-1191; family-name idiom means disgrace.",
    1193: "Completes with rows 1194-1195.",
    1194: "Continuation of row 1193.",
    1195: "Completes rows 1193-1194.",
}

UNCERTAINTIES = [
    {
        "opening_rows": [1135, 1136, 1137, 1138, 1139, 1140],
        "kind": "runtime_pupil_token_and_address_variants",
        "finding": "The ▲ runtime token is preserved literally in every source occurrence. Japanese gendered honorific variants are rendered as the same English address because they do not require distinct English equivalents.",
    },
    {
        "opening_rows": [1190, 1191, 1192],
        "kind": "family_honor_idiom",
        "finding": "The source's literal image of the Kyle family name crying is translated as being disgraced, preserving its reputational meaning.",
    },
]


def build_payload():
    resource, rows, data = opening_source()
    translations = {}
    for opening_row in range(1121, 1201):
        row = rows[opening_row]
        source = data[row["source_offset"]:row["source_offset"] + row["source_byte_length"]].decode("cp932")
        text = TEXT[opening_row]
        if control_tokens(text) != control_tokens(source):
            raise ValueError(f"Control tokens differ at opening row {opening_row}")
        if text.count("\u3000") != source.count("\u3000"):
            raise ValueError(f"Full-width spaces differ at opening row {opening_row}")
        encode_dialogue(text, source)
        translations[row["id"]] = {
            "id": row["id"],
            "source_sha256": row["source_sha256"],
            "source_offset": row["source_offset"],
            "source_byte_length": row["source_byte_length"],
            "reference_instructions": row["reference_instructions"],
            "opening_row": opening_row,
            "text": text,
            "status": "draft",
            "notes": NOTES.get(opening_row, "No control tokens; direct dialogue draft."),
        }
    if len(translations) != 80 or set(TEXT) != set(range(1121, 1201)):
        raise ValueError("Slice coverage is incomplete")
    return {
        "resource_id": resource["id"],
        "assigned_range": [1121, 1200],
        "rows_examined": {"ranges_inclusive": [[1101, 1220]], "count": 120},
        "translations": translations,
        "uncertainties": UNCERTAINTIES,
        "new_glossary_requests": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    sample_ids = list(payload["translations"])[0:3] + list(payload["translations"])[-3:]
    sample = [payload["translations"][row_id] for row_id in sample_ids]
    print(json.dumps({"mode": "write" if args.write else "dry-run", "rows": len(payload["translations"]), "uncertainties": payload["uncertainties"], "sample": sample}, ensure_ascii=False, indent=2))
    if args.write:
        output = Path(__file__).with_name("slice_1121.targets.json")
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"wrote": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
