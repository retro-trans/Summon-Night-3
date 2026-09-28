# Translating Summon Night 3

English targets and source identities live under `work/translation/en/`.
Resolve Japanese from your own game image. A source hash identifies the
original string; never replace it with the hash of an edited translation.

1. Find the category and versioned targets. Read review and layout notes;
   resolve neighboring source lines for dialogue context.
2. Check `work/glossary/`, especially `character_reference_sn6_vita.json`.
   Preserve short names and player-entered protagonist names.
3. Draft the full meaning. Preserve control tokens, speaker expressions and
   substitutions. Do not cut text to fit an original byte budget.
4. Review meaning, then fit the actual renderer. Dialogue and menus have
   different limits; use the corresponding verifier.
5. Create new versioned inputs. Do not rewrite published manifest inputs.
   Preview a data-writing script before `--write`.
6. Check source hashes, references, terminators and layout. Test a fresh launch
   with an in-game save, save screenshots and record untested paths.
7. Update `CHANGELOG.md` with the change and its limitations.

Examples: `tools/menu_enemy_035.py`, `tools/verify_menu_enemy_035.py`, and
`docs/BATTLE_DIALOGUE_0.1.24.md`.

Build tools currently require historical local outputs and extracted resources
that are not in Git. A clean clone supports reviewing and editing the English;
reproducing the incremental build chain also requires your own image,
dependencies and intermediate artifacts. Use the release patch to play.

Report bugs with patch/emulator versions, chapter, reproduction steps,
screenshot and save-loading method. Do not upload game images or full
Japanese script dumps.
