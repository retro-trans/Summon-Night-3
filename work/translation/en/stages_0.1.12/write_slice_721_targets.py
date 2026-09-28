"""Write the bounded English draft for opening rows 721 through 800."""

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
    721: "Come on...",
    722: "Don't say that.",
    723: "Please...",
    724: "I'm not in the mood",
    725: "right now, I told you.",
    726: "Didn't I?!",
    727: "...!",
    728: "Are you feeling sick...?",
    729: "That's what I said...",
    730: "I see...",
    731: "Then I'll",
    732: "go get you",
    733: "something cold to drink.",
    734: "Then I'll",
    735: "go get you",
    736: "something cold to drink.",
    737: "...Yes?",
    738: "Hi.",
    739: "Hello.",
    740: "Oh...",
    741: "I was wondering",
    742: "how you were doing.",
    743: "Let's talk a little.",
    744: "We haven't even",
    745: "properly introduced ourselves.",
    746: "I was wondering",
    747: "how you were doing...",
    748: "Could we talk a little?",
    749: "We haven't even",
    750: "properly introduced ourselves.",
    751: "Not right now...",
    752: "Don't say that.",
    753: "Come on...",
    754: "Don't say that.",
    755: "Please...",
    756: "No...!",
    757: "...!",
    758: "U-um...",
    759: "I'm sorry.",
    760: "I'm just not in the mood...",
    761: "I see...",
    762: "Then I'll",
    763: "go get you",
    764: "something cold to drink.",
    765: "Then I'll",
    766: "go get you",
    767: "something cold to drink.",
    768: "Phew... I said that",
    769: "without thinking and",
    770: "left the room, but...",
    771: "Phew... I said that",
    772: "without thinking and left",
    773: "the room, but...",
    774: "I wonder if they thought",
    775: "I ran away.",
    776: "Still, there is no doubt",
    777: "I was being avoided,",
    778: "that's for sure.",
    779: "It can't be helped...",
    780: "I'll go kill",
    781: "some time.",
    782: "It can't be helped...",
    783: "I'll kill some time,",
    784: "then go back.",
    785: "What should I do...?",
    786: "　Walk around the ship",
    787: "　Go out on deck",
    788: "Hmm?",
    789: "Huh?",
    790: "......",
    791: "Are those Imperial uniforms?",
    792: "On a civilian ship?",
    793: "Why???",
    794: "You there!",
    795: "!?",
    796: "Don't move!",
    797: "Move, and I'll kill you",
    798: "without asking questions!",
    799: "W-wait,",
    800: "calm down!?",
}

NOTES = {
    721: "Completes the preceding plea in row 720.",
    722: "Alternative continuation of the same plea.",
    723: "Completes row 722.",
    724: "Completes with rows 725-726; refusal is emphatic.",
    725: "Continuation of row 724.",
    726: "Completes rows 724-725.",
    731: "Completes with rows 732-733; male protagonist alternative.",
    732: "Continuation of row 731.",
    733: "Completes rows 731-732.",
    734: "Completes with rows 735-736; female protagonist alternative.",
    735: "Continuation of row 734.",
    736: "Completes rows 734-735.",
    741: "Completes with row 742.",
    744: "Completes with row 745.",
    746: "Completes with row 747; female protagonist alternative.",
    749: "Completes with row 750.",
    762: "Completes with rows 763-764; male protagonist alternative.",
    763: "Continuation of row 762.",
    764: "Completes rows 762-763.",
    765: "Completes with rows 766-767; female protagonist alternative.",
    766: "Continuation of row 765.",
    767: "Completes rows 765-766.",
    768: "Completes with rows 769-770; male protagonist internal monologue alternative.",
    769: "Continuation of row 768.",
    770: "Completes rows 768-769.",
    771: "Completes with rows 772-773; female protagonist internal monologue alternative.",
    772: "Continuation of row 771.",
    773: "Completes rows 771-772.",
    774: "Completes with row 775; selected pupil remains gender-neutral.",
    776: "Completes with rows 777-778; avoidance is directed at the protagonist.",
    777: "Continuation of row 776.",
    778: "Completes rows 776-777.",
    780: "Completes with row 781; male protagonist alternative.",
    781: "Completes row 780.",
    782: "Completes with rows 783-784; female protagonist alternative.",
    783: "Continuation of row 782.",
    784: "Completes rows 782-783.",
    786: "Menu option; preserves the source full-width leading space.",
    787: "Menu option; preserves the source full-width leading space.",
    797: "Completes with row 798; the threat is immediate and unconditional.",
    798: "Completes row 797.",
    799: "Completes with row 800; startled plea.",
    800: "Completes row 799.",
}


def build_payload():
    resource, rows, data = opening_source()
    translations = {}
    for opening_row in range(721, 801):
        row = rows[opening_row]
        source = data[row["source_offset"]:row["source_offset"] + row["source_byte_length"]].decode("cp932")
        text = TEXT[opening_row]
        if control_tokens(text) != control_tokens(source):
            raise ValueError(f"Control tokens differ at opening row {opening_row}")
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
    if len(translations) != 80 or set(TEXT) != set(range(721, 801)):
        raise ValueError("Slice coverage is incomplete")
    return {
        "resource_id": resource["id"],
        "assigned_range": [721, 800],
        "rows_examined": {"ranges_inclusive": [[681, 820]], "count": 140},
        "translations": translations,
        "uncertainties": [],
        "new_glossary_requests": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    sample_ids = list(payload["translations"])[0:3] + list(payload["translations"])[-3:]
    sample = [payload["translations"][row_id] for row_id in sample_ids]
    print(json.dumps({"mode": "write" if args.write else "dry-run", "rows": len(payload["translations"]), "sample": sample}, ensure_ascii=False, indent=2))
    if args.write:
        output = Path(__file__).with_name("slice_721.targets.json")
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"wrote": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
