# 0.1.13 — Battle UI draft

Final build scope: 161 executable roots and six choice tails; 310 shared table
strings; 13 tutorial pages; all 55 distinct encounter text sprites, with 611
matching uses across 80 packs. Earlier draft exclusions below are historical;
review overlays and the final artwork catalog are authoritative. Forty-six
unproven executable records remain excluded. See docs/BATTLE_0.1.13.md.

- Added executable drafts for deployment, actions, confirmations, encounter labels, victory and defeat conditions, status effects, and battle setup.
- Added static-table drafts for status labels, base attack modes and range text, tutorial navigation, and directly translatable Brave Battle objectives.
- Kept named skills, item names, and 76 named or multi-line Brave Battle condition rows out of this batch pending glossary and meaning review.
- No source executable, archive, ISO, or build output was changed.
- Added `tools/battle_table_patch.py`, a dry-run-only pure planner for 0.1.12 that relocates reviewed, directly referenced table strings in both shared copies using two-byte display encoding.
- Added `meaning_review.json` with independent executable review notes, compact attack-label variants, corrections for mixed-language objective drafts, and the previously excluded Brave Battle condition translations.
- Updated the table planner to relocate every unowned continuation in a direct-pointer-led pool group through the next referenced string; reviewed tails are translated and unknown tails remain raw.
- Normalized current battle drafts and review overlays to the Wiki.gg spellings Vijue, Ishlar, Ordreik, Heinel Copse, and VAR-Xe-LD; the exact-match normalizer excludes unrelated text such as "Island Residents."
- Added the source-verified Pact Ritual tutorial example and battle-scoped glossary records for Heinel Copse, VAR-Xe-LD, Ishlar, and Ordreik Servolt.
- Finalized exact-word battle-name normalization, including Azlier, Sonolar, Galleor, Phlaiz, and Cunnon. The frozen build-input manifest records the relevant target, review, glossary, and normalizer hashes.
