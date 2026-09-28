"""Create the English draft for opening rows 881-960.

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
    881: "!?",
    882: "Just like I thought...",
    883: "I shouldn't have done this.",
    884: "Leaving the mansion",
    885: "to live with strangers",
    886: "...",
    887: "...No, that's not it.",
    888: "It's not that I'm lonely...",
    889: "I've always",
    890: "been fine on my own.",
    891: "I'm not worried...",
    892: "I'm not",
    893: "lonely at all!",
    894: "Feeling homesick...",
    895: "I'm not",
    896: "a child...",
    897: "anymore...",
    898: "No...",
    899: "I mustn't",
    900: "cry...",
    901: "But...",
    902: "Sniff... sob...",
    903: "...",
    904: "Of course.",
    905: "They're still",
    906: "just a child.",
    907: "Traveling suddenly",
    908: "with a grown-up they don't know—",
    909: "of course they'd be scared.",
    910: "And yet I",
    911: "never even",
    912: "realized that...",
    913: "That's right...",
    914: "They're still",
    915: "just a child.",
    916: "Traveling suddenly with",
    917: "a grown-up they don't know—how could they",
    918: "not be scared...?",
    919: "And yet I never",
    920: "realized that",
    921: "for them...",
    922: "...!?",
    923: "Aah!?",
    924: "Aah!?",
    925: "Eek!?",
    926: "Eek!?",
    927: "Are you okay!?",
    928: "Are you okay!?",
    929: "Ah...",
    930: "Ah...",
    931: "Ah...",
    932: "Ah...",
    933: "That was cannon fire.",
    934: "Don't tell me...!?",
    935: "Whoo-hoo!",
    936: "Kaboom! Direct hit♪",
    937: "Nice shot, Sonolar.",
    938: "You shattered only the mast",
    939: "with one shot.",
    940: "Hey, Scarrel.",
    941: "Don't praise her",
    942: "too much.",
    943: "Like last time,",
    944: "she'll get carried away again",
    945: "and sink our prey.",
    946: "Boo, boo!",
    947: "Big Bro, you're bringing up",
    948: "that old story again.",
    949: "Guest, the goods we're after",
    950: "are definitely aboard",
    951: "that ship?",
    952: "Yes, without a doubt.",
    953: "But why go to all the trouble of",
    954: "disguising it as a passenger liner",
    955: "to transport it?",
    956: "Given what it is,",
    957: "they want to move it",
    958: "in secret, I suppose.",
    959: "Still, the fact they let us",
    960: "find them makes them pretty",
}


def scene_note(row_number):
    if row_number <= 903:
        return "Cabin reflection branch; no control tokens."
    if row_number <= 921:
        return "Protagonist's reflection; no control tokens."
    if row_number <= 934:
        return "Attack reaction branch; no control tokens."
    if row_number <= 948:
        return "Pirate crew dialogue; locked names Sonolar and Scarrel; no control tokens."
    if row_number <= 958:
        return "Pirate crew dialogue; generic guest remains unnamed."
    return "Pirate crew dialogue; source sentence continues into row 961 outside this slice."


def draft():
    resource, rows, data = opening_source()
    expected = set(range(881, 961))
    if set(TARGETS) != expected:
        raise ValueError("Target row mapping must contain exactly rows 881-960")
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
        "assigned_range": [881, 960],
        "rows_examined": {"ranges_inclusive": [[821, 1040]], "count": 220},
        "translations": translations,
        "uncertainties": [],
        "new_glossary_requests": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = draft()
    samples = [882, 887, 904, 916, 936, 949, 959]
    by_row = {value["opening_row"]: value for value in output["translations"].values()}
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": "work/translation/en/stages_0.1.12/slice_881.targets.json",
        "translation_count": len(output["translations"]),
        "samples": [by_row[row] for row in samples],
        "new_glossary_requests": output["new_glossary_requests"],
    }, ensure_ascii=False, indent=2))
    if args.write:
        destination = Path("work/translation/en/stages_0.1.12/slice_881.targets.json")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing target: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
