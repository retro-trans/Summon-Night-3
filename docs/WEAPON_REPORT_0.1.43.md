# Ishlar weapon report — 0.1.43

The screenshot showed untranslated text in the weapon heading, special
attack, adjacent-target help and Ishlar unit name. These are static table
entries, independent of translated battle dialogue.

## Changes

- Table 15, weapon record 60: Generasneil (project transliteration; no
  official English spelling established).
- Table 25, attack 156: Fell Wildfire, a compact localization of the evil
  sword / fierce spreading fire title. Attack 159: Tyrant's Rampage,
  covering the associated awakened sword art.
- All 16 identical sword-only adjacent-target help entries now read:
  “Sword-only special attack.” / “Hits one adjacent target.”
- Character label 0x77b2, both identity rows 228/229: Ishlar, following the
  user-selected SN6 Vita gallery glossary. Other names, including player
  protagonist names, are unchanged.
- Weapon heading call 0x86248 now uses the already-existing 0x34cbfc VWF
  wrapper, also used by the magic heading. Runtime tracing established
  the original native call at 0x1cbee0 with caller return 0x86250.
  The existing JAL relocation is retained; null/unallocated objects still
  use the native fallback. No new renderer allocation is introduced.

Gameplay fields, attack-level inheritance, MP costs and weapon stats are
unchanged. Names and help are appended with explicit terminators. Both
resident and bank copies of the affected tables are rebuilt together.

## Verification

- All 19 static text targets verified through their real pointer fields.
- 16 descriptions pass native MIPS staging-copy execution with guards;
  each has at most 27 cells per line and 54 total glyphs.
- Eight VWF dispatch cases cover two relocated load bases and null,
  missing-allocation and normal-text branches.
- All ten Brave Goals title/help regression cases still pass.
- ISO filesystem, all 23 indexes, 5,727 unaffected bank resources and all
  historical/current build input hashes verified.
- Both xdelta patches reconstruct the final target hash recorded in the
  build manifest and XDELTA-VALIDATION.json.

Runtime captures and exact tested scope are recorded separately in
work/ui/weapon_report_0.1.43/runtime.json. Other characters' untranslated
skills and remaining sword-art names are outside this report's changes.
The awakened Tyrant's Rampage entry has static verification; its awakened
in-game screen has not been exercised.

This is a local test build, not a GitHub release. Restart the patched game
and load the normal in-game save; older PPSSPP states preserve older data.
