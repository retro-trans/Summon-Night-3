"""Create the 0.1.12 ship-scene glossary from supplied evidence."""

import argparse
import json
from pathlib import Path


ROSTER = "https://summonnight.wiki.gg/wiki/Summon_Night_3"
GALLERY = "https://summonnight.fandom.com/wiki/Summon_Night_3/PSP_Gallery"
REN0TE_12 = "https://renote.net/articles/17584/page/12"
REN0TE_13 = "https://renote.net/articles/17584/page/13"
REN0TE_16 = "https://renote.net/articles/17584/page/16"
ATWIKI_56 = "https://w.atwiki.jp/sn3psp/pages/56.html"
ATWIKI_57 = "https://w.atwiki.jp/sn3psp/pages/57.html"


def unknown_nickname():
    return {"value": None, "status": "No distinct nickname established by the supplied evidence."}


def roster_evidence():
    return [
        {
            "url": ROSTER,
            "supports": ["locked_wiki_name"],
            "retrieval_note": "Direct page returned 403; roster spelling was retrieved through search cache.",
        },
        {
            "url": GALLERY,
            "supports": ["fallback_name_comparison"],
            "notes": "Fallback spellings do not override the locked Wiki.gg roster names.",
        },
    ]


def entry(identifier, name, gender, personality, role, profile_url, profile_supports, notes=None, full_name=None):
    result = {
        "id": identifier,
        "category": "character",
        "name": name,
        "target_name": name,
        "nickname": unknown_nickname(),
        "gender": gender,
        "gender_evidence": profile_url if gender is not None else "Not supplied by the evidence sources used for this entry.",
        "personality": personality,
        "role": role,
        "confidence": "high_for_locked_name_and_profile_summary",
        "evidence": roster_evidence() + [{"url": profile_url, "supports": profile_supports}],
    }
    if full_name:
        result["full_name"] = full_name
    if notes:
        result["notes"] = notes
    return result


def glossary():
    entries = [
        entry(
            "character.kyle",
            "Kyle",
            "male",
            "Dependable and boisterous.",
            "Pirate captain of the third pirate group.",
            REN0TE_12,
            ["gender", "personality", "pirate_captain_role", "third_group"],
        ),
        entry(
            "character.sonolar",
            "Sonolar",
            "female",
            "Energetic, rough-spoken, and kind.",
            "Pirate gunner.",
            REN0TE_12,
            ["gender", "personality", "gunner_role"],
            "Calls Kyle 'Bro'; this is an address and must not be treated as evidence that they are biological siblings.",
        ),
        entry(
            "character.scarrel",
            "Scarrel",
            "male",
            "Cheerful and teasing; cool and analytical.",
            "Pirate navigator and adviser.",
            REN0TE_12,
            ["gender", "personality", "navigator_role", "adviser_role", "friendship_with_yard"],
            "Uses feminine speech despite being male. Childhood friend of Yard.",
        ),
        entry(
            "character.yard_grenaze",
            "Yard",
            "male",
            "Polite and serious.",
            "Guest summoner; formerly affiliated with the Colorless Faction.",
            REN0TE_13,
            ["full_name", "gender", "personality", "guest_summoner_role", "former_colorless_faction"],
            "Full name: Yard Grenaze.",
            "Yard Grenaze",
        ),
        entry(
            "character.azlier_levinoss",
            "Azlier",
            "female",
            None,
            "Captain in the Imperial Naval Sixth Unit; academy classmate of the protagonist.",
            ATWIKI_56,
            ["full_name", "gender", "captain_role", "imperial_naval_sixth_unit", "academy_classmate_role"],
            "Full name: Azlier Levinoss. No personality profile was supplied. Fallback sources use discrepant spellings that do not override Wiki.gg.",
            "Azlier Levinoss",
        ),
        entry(
            "character.galleor",
            "Galleor",
            None,
            "Loyal and honorable.",
            "Deputy.",
            ATWIKI_57,
            ["personality", "deputy_role"],
            "Gender was not supplied. Fallback sources use a discrepant spelling that does not override Wiki.gg.",
        ),
        entry(
            "character.vijue",
            "Vijue",
            None,
            "Cruel and self-centered.",
            "Military member of the Sixth Naval Unit.",
            REN0TE_16,
            ["personality", "military_role", "sixth_naval_unit"],
            "Gender was not supplied.",
        ),
    ]
    return {
        "schema_version": 1,
        "language": "en",
        "status": "ship_scene_cast_evidence_compiled",
        "name_policy": "Wiki.gg roster names are locked. Fallback gallery spellings are evidence only and do not override them.",
        "entries": entries,
        "do_not_touch_after_normalization": ["Kyle", "Sonolar", "Scarrel", "Yard", "Azlier", "Galleor", "Vijue"],
        "change_log": [
            {
                "version": "0.1.12",
                "date": "2026-09-27",
                "change": "Added evidence-grounded ship-scene cast glossary without modifying earlier glossaries.",
            }
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = glossary()
    destination = Path("work/glossary/ship_0.1.12.json")
    print(json.dumps({
        "mode": "write" if args.write else "dry-run",
        "target": str(destination),
        "entry_count": len(output["entries"]),
        "locked_names": output["do_not_touch_after_normalization"],
        "sample_entries": output["entries"][:2],
    }, ensure_ascii=False, indent=2))
    if args.write:
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing glossary: {destination}")
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
