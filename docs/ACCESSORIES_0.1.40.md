# Accessory text and Deployment — 0.1.40

Local test build based on 0.1.39; not published to GitHub.

## Changes

- Finish all 25 remaining Japanese accessory names in static table 17,
  including All-Purpose Pot, Titanium Screw, Lucky Ring and Pirate Flag.
  Shared table pointers update the Combine list and other item-name consumers.
- Translate 17 shared item-effect fragments. The pictured effect now reads
  `DF+3 Blind Proof`, with the native stat symbols and spacing retained.
- Use M/O/S/B/N for the fixed single-cell Machine/Oni/Spirit/Beast/Null labels.
- Correct two Deployment branch references which bypassed the existing
  `Learn Skills` translation, and one missed branch for `Key Item`.
- Prevent pre-existing scratch-buffer corruption from long ailment names.
  Groups of three or more effects use scoped compact forms: Stone, Chrm, Rge,
  Psn, Para, Bld, Seal and Sleep. Other screens and single effects retain
  their existing names. Numeric effects and combination recipes are unchanged.

## Verification

- Execute the game's native accessory formatter and writers for all 120
  nonempty records, with and without the key-item flag: 240 cases.
  Guard output buffers, enforce writer concatenation limits, decode strictly,
  check line length and total output allocation, and reject untranslated kana/kanji.
- All 23 bank indexes parse; 5,728 unrelated resources remain byte-identical.
  The static table and resident cache agree. Previous build inputs retain hashes.
- Fresh isolated PPSSPP boot and copied first-battle save load succeed.
  Deployment status and shortcut layout look correct for this early save.
- The available save has combination recipes and skill learning locked, so
  the exact unlocked screens in the user's screenshots are **not visually verified**.
- Some complex item descriptions still generate more than two lines; all
  fit the native memory allocation, but their full visual layout is not certified.
  `work/ui/accessories_0.1.40/verification.json` lists those cases, including
  synthetic key-item combinations used to exercise both branches.

## Build

`python tools/build_accessories_040.py --write --destination work/output/0.1.40`

Output: `work/output/0.1.40/Summon_Night_3_EN_0.1.40.iso`

SHA-256: `6ff9a6321606c922d66582e5baf101ebc50acce6cbac929058e8c1be9bf66cf9`

Start the new ISO and load an in-game save. An old emulator save state can
restore old executable data and translated text.
