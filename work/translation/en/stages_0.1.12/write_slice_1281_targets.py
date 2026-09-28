"""Write the bounded English draft for opening rows 1281 through 1360."""

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
    1281: "Go away!",
    1282: "This one's injured!",
    1283: "Pipoo...",
    1284: "Don't come any closer!",
    1285: "This child is not",
    1286: "your food!!",
    1287: "Mew...",
    1288: "Go away!　Don't you think",
    1289: "bullying someone weaker is",
    1290: "shameful!?",
    1291: "Bweep...",
    1292: "Don't come any closer!!",
    1293: "Please, don't bully this child",
    1294: "anymore!",
    1295: "Kyupii...",
    1296: "Stray summoned beasts!?",
    1297: "And that many,",
    1298: "too...",
    1299: "Bupii...",
    1300: "Don't worry.",
    1301: "I'll protect you",
    1302: "no matter what.",
    1303: "No matter what...",
    1304: "Fumii...",
    1305: "Don't be afraid.",
    1306: "I'll protect you",
    1307: "no matter what.",
    1308: "No matter what...",
    1309: "Bii...",
    1310: "It's all right.",
    1311: "I'll drive those",
    1312: "away for you.",
    1313: "No matter what...",
    1314: "Kyupii...",
    1315: "Don't be afraid.",
    1316: "I'll protect you.",
    1317: "No matter what...",
    1318: "I have to help them!",
    1319: "But...",
    1320: "I don't have a weapon",
    1321: "or a summoning stone.",
    1322: "I have to help them!",
    1323: "But...",
    1324: "I don't have a weapon",
    1325: "or a summoning stone.",
    1326: "Roooar!!",
    1327: "What should I do...?",
    1328: "　I'll help them anyway!",
    1329: "　There's nothing I can do...",
    1330: "...Myaow!?",
    1331: "I'm your opponent!",
    1332: "Get away from ▲",
    1333: "now!",
    1334: "Get away from ▲",
    1335: "now!",
    1336: "Oh...!",
    1337: "Oh...!",
    1338: "Oh...!",
    1339: "Oh...!",
    1340: "Come on, while you can,",
    1341: "run!",
    1342: "Come on, while you can,",
    1343: "hurry and run!",
    1344: "Even without a weapon,",
    1345: "this time...",
    1346: "I'll protect them!!",
    1347: "I'll protect them!!",
    1348: "No...",
    1349: "There's nothing I can do.",
    1350: "No...",
    1351: "Without a weapon,",
    1352: "even if I go out there...",
    1353: "If only I had",
    1354: "a weapon...",
    1355: "If it's a weapon you want...",
    1356: "I have one...",
    1357: "What?",
    1358: "Call me...",
    1359: "Summon me...",
    1360: "If you desire the power",
}

NOTES = {
    1281: "Completes with row 1282; the injured creature remains an unspecified child/creature.",
    1284: "Completes with rows 1285-1286.",
    1285: "Continuation of row 1284.",
    1286: "Completes rows 1284-1285.",
    1288: "Completes with rows 1289-1290; preserves the source full-width internal space.",
    1289: "Continuation of row 1288.",
    1290: "Completes rows 1288-1289.",
    1292: "Completes with rows 1293-1294.",
    1293: "Continuation of row 1292.",
    1294: "Completes rows 1292-1293.",
    1296: "Project-generic rendering of the creature category; terminology remains pending glossary confirmation.",
    1297: "Completes with row 1298.",
    1300: "Completes with rows 1301-1303; first pupil reassurance branch.",
    1301: "Continuation of row 1300.",
    1302: "Completes rows 1300-1301.",
    1305: "Completes with rows 1306-1308; second pupil reassurance branch.",
    1306: "Continuation of row 1305.",
    1307: "Completes rows 1305-1306.",
    1310: "Completes with rows 1311-1313; third pupil reassurance branch.",
    1311: "Continuation of row 1310.",
    1312: "Completes rows 1310-1311.",
    1315: "Completes with rows 1316-1317; fourth pupil reassurance branch.",
    1318: "Completes with rows 1319-1321; male protagonist alternative.",
    1320: "Continuation of row 1318 after row 1319's hesitation.",
    1321: "Completes rows 1318-1320.",
    1322: "Completes with rows 1323-1325; female protagonist alternative.",
    1324: "Continuation of row 1322 after row 1323's hesitation.",
    1325: "Completes rows 1322-1324.",
    1327: "Choice prompt; full alternatives follow in rows 1328-1329.",
    1328: "Choice text; preserves source full-width leading space.",
    1329: "Choice text; preserves source full-width leading space.",
    1331: "Completes with gender-specific runtime pupil-name branches in rows 1332-1335.",
    1332: "Completes with row 1333; preserves runtime pupil-name token ▲ in its source row.",
    1333: "Completes row 1332.",
    1334: "Completes with row 1335; preserves runtime pupil-name token ▲ in its source row.",
    1335: "Completes row 1334.",
    1340: "Completes with row 1341; male protagonist alternative.",
    1342: "Completes with row 1343; female protagonist alternative.",
    1344: "Completes with rows 1345-1347; the referent remains gender-neutral.",
    1345: "Continuation of row 1344.",
    1346: "Completes rows 1344-1345; male protagonist alternative.",
    1347: "Completes rows 1344-1345; female protagonist alternative.",
    1348: "Completes with row 1349; resigned player-choice branch.",
    1350: "Completes with rows 1351-1352; female protagonist alternative.",
    1351: "Continuation of row 1350.",
    1353: "Completes with row 1354.",
    1355: "Completes with row 1356; unknown speaker remains unnamed.",
    1358: "Completes with out-of-slice rows 1359-1362.",
    1359: "Completes with out-of-slice rows 1360-1362.",
    1360: "Continues through contextual rows 1361-1362.",
}

UNCERTAINTIES = [
    {
        "opening_rows": [1296, 1297, 1298],
        "kind": "creature_category_term",
        "finding": "No project glossary entry establishes an English term for this generic category. 'Stray summoned beasts' retains both its unbound/stray sense and its summoned-creature category without claiming an official term.",
    },
    {
        "opening_rows": [1332, 1333, 1334, 1335],
        "kind": "runtime_pupil_token_and_address_variants",
        "finding": "The ▲ token is preserved literally. The Japanese -kun/-chan variants are rendered as the same token-only English address because no gendered English title is required.",
    },
]


def build_payload():
    resource, rows, data = opening_source()
    translations = {}
    for opening_row in range(1281, 1361):
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
    if len(translations) != 80 or set(TEXT) != set(range(1281, 1361)):
        raise ValueError("Slice coverage is incomplete")
    return {
        "resource_id": resource["id"],
        "assigned_range": [1281, 1360],
        "rows_examined": {"ranges_inclusive": [[1261, 1380]], "count": 120},
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
        output = Path(__file__).with_name("slice_1281.targets.json")
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"wrote": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
