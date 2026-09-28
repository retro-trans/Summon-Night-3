"""Preview or apply the 0.1.12 release-documentation update."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "translation_status.json"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
BUILD = ROOT / "docs" / "BUILD_0.1.12.md"

BUILD_TEXT = """# Build 0.1.12 — three chapter story translation candidate

This candidate extends the reviewed English story text through the opening,
Chapter 2, and Chapter 3. It covers **6,174** story fragments: 1,428 in the
opening script, 1,711 in Chapter 2, 2,319 in Chapter 3, and 716 fragments in
18 chapter-specific night-talk resources. This adds 5,533 story fragments to
the 0.1.11 build selection.

## Scope and validation

- No scoped story rows are excluded. The opening script, both chapter-main
  unique tails, and all 18 selected night-talk resources have accepted meaning
  review records.
- Twenty chapter/compiler static validations pass. They preserve source pools,
  earlier translations, branches, direct menus, conditional rows, control
  tokens, relocation data, and simulated dialogue groups.
- The shared UI/library prefix and later chapters are outside this build's story
  scope. This is not a claim that all game dialogue or all interface text is
  translated.
- Earlier UI changes, artwork, audio, and their original resources are retained.

## QA status and limits

Final QA is pending. The candidate must not be described as runtime-complete:
agent 801's final QA remains outstanding, and no full playthrough of all three
chapters has been performed. Runtime checks still need to cover story flow,
branches, layout, substitutions, save/load behavior, and regressions.

Some portrait nameplates for newly introduced characters may still be Japanese.
This release does not translate all UI, graphics, or later-game text.

Next unused version: **0.1.13**.
"""

README_STATUS = """Status: **0.1.12 is a three-chapter story translation candidate** with
6,174 reviewed story fragments: the complete 1,428-row opening script, Chapter
2, Chapter 3, and 18 chapter-specific night-talk resources. It adds 5,533 story
fragments to 0.1.11. All scoped story rows are covered and 20 chapter/compiler
static validations pass.

Final QA is pending, including agent 801's final pass; no complete three-chapter
playthrough has been performed. Do not treat this candidate as runtime-complete.
The shared UI/library prefix, later chapters, and most interface work remain
outside this story scope. Earlier artwork, audio, and UI changes are retained;
portrait nameplates for newly introduced characters may still be Japanese. See
[build notes and limits](docs/BUILD_0.1.12.md). The next unused version is
**0.1.13**.

"""

CHANGELOG_ENTRY = """## 0.1.12 — three chapter story translation candidate, 2026-09-27

- Added 5,533 reviewed story fragments to the previous selection, bringing the
  bounded opening/Chapter 2/Chapter 3 story scope to 6,174 fragments.
- Covered all 1,428 opening rows, the 1,711-row Chapter 2 unique tail, the
  2,319-row Chapter 3 unique tail, and 716 rows across 18 chapter-specific
  night-talk resources. No rows are excluded from this scoped story set.
- Accepted meaning reviews and passed 20 chapter/compiler static validations,
  including branches, direct menus, conditional rows, control tokens,
  relocation, prior translations, and source-pool preservation.
- Retained earlier UI, artwork, and audio. Newly introduced portrait nameplates
  may remain Japanese; this does not claim that all UI is translated.
- Final QA, including agent 801's pass, is pending. No full playthrough of all
  three chapters has been performed, so runtime-complete status is not claimed.
  Next: 0.1.13.

"""

def planned_status():
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    status["updated_on"] = "2026-09-27"
    status["latest_build"] = "0.1.12"
    status["latest_build_kind"] = "Three-chapter story translation candidate; final QA pending"
    status["next_build_version"] = "0.1.13"
    status["coverage_counts_baseline"] = "0.1.12 covers 6,174 scoped story fragments across the complete opening, Chapter 2, Chapter 3, and 18 chapter-specific night-talk resources; 5,533 are new versus 0.1.11."
    status["latest_candidate"] = {
        "acceptance": "static_verified_pending_final_qa",
        "candidate_sha256": None,
        "qa_report": "docs/BUILD_0.1.12.md",
        "inserted_story_fragments": 6174,
        "new_story_fragments_vs_0_1_11": 5533,
        "runtime_verified": False,
        "visual_verified": False,
        "scope_limit": "Complete opening, Chapter 2, Chapter 3, and 18 chapter-specific night-talk resources. Shared UI/library text, later chapters, most interface work, and some new-character portrait nameplates remain outside scope.",
        "runtime_status": "Final QA pending agent 801; no full three-chapter playthrough.",
        "static_validation_reports": 20,
        "story_coverage": {
            "opening_00_00065": 1428,
            "chapter2_main_00_00088": 1711,
            "chapter3_main_00_00111": 2319,
            "chapter_specific_nighttalk_resources": 18,
            "chapter2_nighttalk_fragments": 426,
            "chapter3_nighttalk_fragments": 290,
            "total_story_fragments": 6174,
            "excluded_scoped_story_rows": 0
        }
    }
    status["release_0_1_12"] = {
        "status": "candidate_static_verified_final_qa_pending",
        "meaning_reviews": "accepted",
        "static_validations_passed": 20,
        "runtime_complete": False,
        "full_three_chapter_playthrough": False,
        "retained": ["earlier UI", "original artwork", "original audio"],
        "known_limits": ["Some portrait nameplates for newly introduced characters may remain Japanese.", "This release does not claim complete interface translation.", "Shared UI/library text and later chapters remain outside the scoped story coverage."]
    }
    status["runtime"]["latest_build_runtime_verified"] = False
    status["runtime"]["latest_build_runtime_scope"] = "0.1.12 is statically verified only. Final QA is pending agent 801, and no complete opening/Chapter 2/Chapter 3 playthrough has been performed."
    status["script_pools"]["story_translation_0_1_12"] = {
        "scoped_fragments": 6174,
        "new_vs_0_1_11": 5533,
        "meaning_reviews_accepted": True,
        "excluded_scoped_story_rows": 0,
        "static_validations_passed": 20,
        "runtime_complete": False
    }
    return status

def desired_files():
    current_readme = README.read_text(encoding="utf-8")
    old_status = "Status: **test ISO 0.1.11"
    current_status = "Status: **0.1.12 is a three-chapter story translation candidate**"
    start = current_readme.index(old_status if old_status in current_readme else current_status)
    end = current_readme.index("The rescan also found", start)
    new_readme = current_readme[:start] + README_STATUS + current_readme[end:]
    current_changelog = CHANGELOG.read_text(encoding="utf-8")
    marker = "# Changelog\n\n"
    assert current_changelog.startswith(marker)
    new_changelog = current_changelog if current_changelog.startswith(marker + CHANGELOG_ENTRY) else marker + CHANGELOG_ENTRY + current_changelog[len(marker):]
    return {
        STATUS: json.dumps(planned_status(), ensure_ascii=False, indent=2) + "\n",
        README: new_readme,
        CHANGELOG: new_changelog,
        BUILD: BUILD_TEXT,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    files = desired_files()
    changed = [str(path.relative_to(ROOT)) for path, content in files.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    print(json.dumps({"mode": "write" if args.write else "dry-run", "changed_files": changed, "story_fragments": 6174, "new_vs_0_1_11": 5533, "runtime_complete": False}, ensure_ascii=False))
    if args.write:
        for path, content in files.items():
            path.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    main()
