"""Write the bounded English draft for opening rows 961 through 1040."""

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
    961: "stupid, though...",
    962: "But the fact remains that",
    963: "they have a security unit",
    964: "guarding them.",
    965: "Fine by me.",
    966: "It wouldn't be any fun",
    967: "without a challenge...",
    968: "All right!",
    969: "We'll keep them pinned down",
    970: "with cannon fire and go full speed ahead.",
    971: "Once we're alongside, we'll",
    972: "storm the ship!!",
    973: "Yeah!!",
    974: "No doubt about it.",
    975: "That's a pirate flag.",
    976: "No doubt about it.",
    977: "That's a pirate flag.",
    978: "Pirates!?",
    979: "Pirates!?",
    980: "Pirates?!",
    981: "...!?",
    982: "Don't worry.　This ship has",
    983: "security soldiers on board.",
    984: "They won't take us so easily...",
    985: "It's all right.　This ship has",
    986: "security soldiers on board.",
    987: "They can't take us that easily...",
    988: "!?",
    989: "!?",
    990: "!?",
    991: "!?",
    992: "Looks like it won't be",
    993: "that simple after all.",
    994: "Maybe it won't be",
    995: "that simple after all.",
    996: "Hey, what are we supposed to do?",
    997: "Hey!?",
    998: "This is no time to",
    999: "stay calm, is it?!",
    1000: "H-hey!",
    1001: "Do something!?",
    1002: "What should I do...?",
    1003: "I need to...",
    1004: "　There's only one thing to do: act.",
    1005: "　Let's proceed cautiously.",
    1006: "I need to...",
    1007: "　There's only one thing to do: act.",
    1008: "　Let's see what happens.",
    1009: "If it comes to this,",
    1010: "we need to strike first.",
    1011: "Before the pirates get",
    1012: "here, we'll use a boat",
    1013: "to get away.",
    1014: "At a time like this,",
    1015: "we have to act.",
    1016: "Before the pirates get",
    1017: "here, let's use a boat",
    1018: "to get away.",
    1019: "For now, we should",
    1020: "wait and see.",
    1021: "We shouldn't do anything",
    1022: "that might provoke them",
    1023: "carelessly.",
    1024: "For now, let's",
    1025: "wait and see.",
    1026: "Carelessly provoking them",
    1027: "would only be more dangerous,",
    1028: "after all.",
    1029: "...",
    1030: "...",
    1031: "...",
    1032: "...",
    1033: "It's all right.",
    1034: "I used to be a soldier.",
    1035: "If it comes down to it, I'll protect you",
    1036: "and get us out of here.",
    1037: "I'll make sure of it.",
    1038: "Don't worry.",
    1039: "I may not look it, but",
    1040: "I used to be a soldier.",
}

NOTES = {
    961: "Completes the preceding assessment in rows 959-960.",
    962: "Completes with rows 963-964; the armed force remains generic.",
    963: "Continuation of row 962.",
    964: "Completes rows 962-963.",
    966: "Completes with row 967.",
    969: "Completes with row 970; cannon fire is used to keep the target at bay.",
    970: "Completes row 969.",
    971: "Completes with row 972; boarding attack follows coming alongside.",
    972: "Completes row 971.",
    982: "Completes with rows 983-984; preserves the source full-width internal space.",
    983: "Continuation of row 982.",
    984: "Completes rows 982-983.",
    985: "Completes with rows 986-987; preserves the source full-width internal space.",
    986: "Continuation of row 985.",
    987: "Completes rows 985-986.",
    992: "Completes with row 993.",
    994: "Completes with row 995; this variation preserves the added uncertainty.",
    998: "Completes with row 999.",
    1003: "Male protagonist choice prompt; choices follow in rows 1004-1005.",
    1004: "Male protagonist choice; preserves source full-width leading space.",
    1005: "Male protagonist choice; preserves source full-width leading space.",
    1006: "Female protagonist choice prompt; choices follow in rows 1007-1008.",
    1007: "Female protagonist choice; preserves source full-width leading space.",
    1008: "Female protagonist choice; preserves source full-width leading space.",
    1009: "Completes with row 1010; decisive male protagonist branch.",
    1011: "Completes with rows 1012-1013.",
    1012: "Continuation of row 1011.",
    1013: "Completes rows 1011-1012.",
    1014: "Completes with row 1015; decisive female protagonist branch.",
    1016: "Completes with rows 1017-1018.",
    1017: "Continuation of row 1016.",
    1018: "Completes rows 1016-1017.",
    1019: "Completes with row 1020; cautious male protagonist branch.",
    1021: "Completes with rows 1022-1023.",
    1022: "Continuation of row 1021.",
    1023: "Completes rows 1021-1022.",
    1024: "Completes with row 1025; cautious female protagonist branch.",
    1026: "Completes with rows 1027-1028.",
    1027: "Continuation of row 1026.",
    1028: "Completes rows 1026-1027.",
    1033: "Male protagonist reassurance sequence continues through row 1037.",
    1035: "Completes with rows 1036-1037.",
    1036: "Continuation of row 1035.",
    1037: "Completes rows 1035-1036.",
    1038: "Female protagonist reassurance sequence continues through context row 1046.",
    1039: "Completes with row 1040 and out-of-slice continuation rows 1041-1043.",
    1040: "Completes rows 1039 and starts the out-of-slice continuation.",
}


def build_payload():
    resource, rows, data = opening_source()
    translations = {}
    for opening_row in range(961, 1041):
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
    if len(translations) != 80 or set(TEXT) != set(range(961, 1041)):
        raise ValueError("Slice coverage is incomplete")
    return {
        "resource_id": resource["id"],
        "assigned_range": [961, 1040],
        "rows_examined": {"ranges_inclusive": [[941, 1060]], "count": 120},
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
        output = Path(__file__).with_name("slice_961.targets.json")
        if output.exists():
            raise FileExistsError(output)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"wrote": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
