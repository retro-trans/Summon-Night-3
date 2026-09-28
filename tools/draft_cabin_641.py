"""Create the English draft for opening rows 641-720.

Run without --write to validate source alignment and preview sample targets.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dialogue_encoding import control_tokens
from prepare_harbor_context import opening_source


TARGETS = {
    641: "...It's open!",
    642: "Hey.",
    643: "Hello.",
    644: "Oh, it's you.",
    645: "I was wondering",
    646: "how you were doing.",
    647: "Let's talk a little.",
    648: "We haven't even properly",
    649: "introduced ourselves.",
    650: "I was wondering",
    651: "how you were doing...",
    652: "Would you like to talk a little?",
    653: "We haven't even properly",
    654: "introduced ourselves.",
    655: "...No.",
    656: "Don't say that.",
    657: "Come on...",
    658: "Please don't say that.",
    659: "Okay...?",
    660: "I said no!",
    661: "Just leave me alone!",
    662: "...!",
    663: "I feel sick.",
    664: "My stomach's upset,",
    665: "and I don't want to talk...",
    666: "I see...",
    667: "Then I'll",
    668: "go get you something cold",
    669: "to drink.",
    670: "Then I'll",
    671: "go get you something cold",
    672: "to drink, okay?",
    673: "...Fine.",
    674: "Hey.",
    675: "Hello.",
    676: "What can I do for you?",
    677: "I was wondering",
    678: "how you were doing.",
    679: "Let's talk a little.",
    680: "We haven't even properly",
    681: "introduced ourselves.",
    682: "I was wondering",
    683: "how you were doing...",
    684: "Would you like to talk a little?",
    685: "We haven't even properly",
    686: "introduced ourselves.",
    687: "No, thank you.",
    688: "Don't say that.",
    689: "Come on...",
    690: "Please don't say that.",
    691: "Okay...?",
    692: "I told you no,",
    693: "didn't I?!",
    694: "...!",
    695: "...Sorry.",
    696: "I'm not used to ships,",
    697: "so I feel sick...",
    698: "I see...",
    699: "Then I'll",
    700: "go get you something cold",
    701: "to drink.",
    702: "Then I'll",
    703: "go get you something cold",
    704: "to drink, okay?",
    705: "...Please do.",
    706: "Hey.",
    707: "Hello.",
    708: "What do you want?",
    709: "I was wondering",
    710: "how you were doing.",
    711: "Let's talk a little.",
    712: "We haven't even properly",
    713: "introduced ourselves.",
    714: "I was wondering",
    715: "how you were doing...",
    716: "Would you like to talk a little?",
    717: "We haven't even properly",
    718: "introduced ourselves.",
    719: "I'm not in the mood.",
    720: "Don't say that.",
}


def branch_note(row_number):
    if row_number <= 673:
        return "Nup cabin branch; no control tokens."
    if row_number <= 705:
        return "Will cabin branch; no control tokens."
    return "Belfrau cabin branch; no control tokens."


def draft():
    resource, rows, data = opening_source()
    expected = set(range(641, 721))
    if set(TARGETS) != expected:
        raise ValueError("Target row mapping must contain exactly rows 641-720")
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
            "notes": branch_note(number),
        }
    return {
        "resource_id": resource["id"],
        "assigned_range": [641, 720],
        "rows_examined": {"ranges_inclusive": [[621, 740]], "count": 120},
        "translations": translations,
        "uncertainties": [],
        "new_glossary_requests": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = draft()
    samples = [641, 663, 676, 696, 708, 719]
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": "work/translation/en/stages_0.1.12/slice_641.targets.json",
        "translation_count": len(output["translations"]),
        "samples": [output["translations"][next(key for key, value in output["translations"].items()
                                                   if value["opening_row"] == row)] for row in samples],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = Path("work/translation/en/stages_0.1.12/slice_641.targets.json")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
