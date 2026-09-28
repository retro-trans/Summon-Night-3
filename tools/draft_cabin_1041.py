"""Draft and validate opening rows 1041-1120 without altering game resources."""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from dialogue_encoding import control_tokens
from prepare_harbor_context import opening_source


TARGETS = {
    1041: "If it comes to it, I'll protect you",
    1042: "and get you out of here.",
    1043: "I promise.",
    1044: "If it comes to it, I'll protect you",
    1045: "and get you out of here.",
    1046: "I promise.",
    1047: "Really?",
    1048: "Really?",
    1049: "Really?",
    1050: "Really?",
    1051: "Yeah, I promise.",
    1052: "Yes, I promise!",
    1053: "...Okay.",
    1054: "...Okay.",
    1055: "...Okay.",
    1056: "...Okay.",
    1057: "Take this!!",
    1058: "Gah!?",
    1059: "Hey, you lot,",
    1060: "you're backing down already?",
    1061: "Ugh...",
    1062: "If you don't have the stomach for it,",
    1063: "get lost, now!",
    1064: "Don't run away!!",
    1065: "Don't run away!",
    1066: "!?",
    1067: "If you run away now,",
    1068: "who will protect",
    1069: "this ship!?",
    1070: "...!?",
    1071: "Hoh... Finally,",
    1072: "someone with some guts.",
    1073: "You're quite a brave",
    1074: "young lady, but...",
    1075: "Since you said that,",
    1076: "you aren't going to let it",
    1077: "be all talk, are you?",
    1078: "▲...",
    1079: "Get behind me,",
    1080: "▲.",
    1081: "Get behind me,",
    1082: "▲.",
    1083: "Get behind me!",
    1084: "!?",
    1085: "If you won't",
    1086: "give up!",
    1087: "If you won't",
    1088: "give up,",
    1089: "then I have no choice.",
    1090: "I'll take you on.",
    1091: "Ha ha ha ha!",
    1092: "All right,",
    1093: "I like people who make it simple!",
    1094: "Men!",
    1095: "Out of respect,",
    1096: "give her a fight!",
    1097: "Yeah!!",
    1098: "Eek!?",
    1099: "Tch...",
    1100: "What a pathetic bunch.",
    1101: "Boss!",
    1102: "There's an Imperial soldier",
    1103: "over there!",
    1104: "All right, men!",
    1105: "The prey's over there!",
    1106: "Yeah!!",
    1107: "We managed to",
    1108: "slip by them.",
    1109: "It seems we managed",
    1110: "to slip by them.",
    1111: "after all.",
    1112: "...",
    1113: "...",
    1114: "...",
    1115: "...",
    1116: "Come on, while we can,",
    1117: "let's hurry to",
    1118: "the boat.",
    1119: "Come on, while we can,",
    1120: "let's hurry to the boat",
}


def notes(row):
    if 1041 <= row <= 1046:
        return "Aty's reassurance continues from row 1039; no source control tokens."
    if 1047 <= row <= 1056:
        return "Selected-pupil response branch; no source control tokens."
    if 1078 <= row <= 1082:
        return "Preserves the runtime pupil-name token ▲ exactly."
    if 1119 <= row <= 1120:
        return "Aty branch; the source sentence completes at out-of-slice row 1121."
    return "No source control tokens."


def draft():
    resource, rows, data = opening_source()
    expected = set(range(1041, 1121))
    if set(TARGETS) != expected:
        raise ValueError("Target mapping must contain exactly rows 1041-1120")
    translations = {}
    for number in sorted(expected):
        row = rows[number]
        source_text = data[row["source_offset"]:row["source_offset"] + row["source_byte_length"]].decode("cp932")
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
            "notes": notes(number),
        }
    return {
        "resource_id": resource["id"],
        "assigned_range": [1041, 1120],
        "rows_examined": {"ranges_inclusive": [[961, 1180]], "count": 220},
        "translations": translations,
        "uncertainties": [
            {"opening_rows": [1078, 1083], "finding": "The three name-address branches are reconstructed from adjacent VM references; each ▲ token is preserved exactly, while Japanese honorifics are omitted in natural English."},
            {"opening_rows": [1119, 1120], "finding": "Aty's route continues with row 1121 outside this assigned slice; the translated fragment deliberately has no terminal punctuation."},
        ],
        "new_glossary_requests": [],
        "change_log": [
            {"version": "0.1.12", "date": "2026-09-27", "change": "Added draft English translations for opening rows 1041-1120 after examining rows 961-1180; no game resources or other translation files were modified."}
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = draft()
    by_row = {value["opening_row"]: value for value in output["translations"].values()}
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": "work/translation/en/stages_0.1.12/slice_1041.targets.json",
        "translation_count": len(output["translations"]),
        "samples": [by_row[row] for row in [1041, 1046, 1067, 1078, 1080, 1096, 1119, 1120]],
        "uncertainties": output["uncertainties"],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = Path("work/translation/en/stages_0.1.12/slice_1041.targets.json")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {destination}")
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
