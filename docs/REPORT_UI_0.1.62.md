# Awakening and Mujina — local 0.1.62

This test build extends immutable 0.1.61. It translates the four Blade
Awakening skill records and their help, Mujina's Ponta-kun and Chagama name
variants, the Soot Drop, Soot Strike and Twin Dark Strike spells, and Mujina's
two-row lore. The base name Mujina was already translated.

The full awakening explanation is: release the sword's power to awaken;
immunity to all ailments and possession; Berserk Summoning becomes available.
Its compact help reads `Awaken; ailment immunity.` / `No poss.; Berserk Summon OK`.
The name identifies the sword mechanic, and `poss.` means possession.

Mujina is a tanuki yokai who loves dancing, throws rowdy feasts every night,
and is famous for hating baths. The compact lore reads `Dancing tanuki yokai; noisy`
/ `night feasts. Hates baths.` The profile's fame is implicit in this compact
description. The full meaning and source are retained in the translation file.
The hidden question-mark fields and discovery conditions are preserved.

The Set Name hint becomes **Set** with an icon at x424 and proportional text
at x440. Its measured right edge is x473 on the 480-pixel screen. Only this
mode's anchors change. The earlier Create Summons and Affinity artwork fixes
are inherited, along with the Zip Toast and other previous local fixes.

All new strings are appended; only selected table pointers are updated.
Original strings, statistics, costs and unlock fields are preserved. Both
resident copies of the static tables are synchronized. No font pools grow.
The exact-name banner allowlist gains the six distinct new skill/spell names;
unknown and player-entered text retain native behavior.

## Validation

- All 14 inherited ISO regression groups pass.
- Actual candidate code passes 480 banner-wrapper cases, 96 binding cases,
  and 210 centered font-pixel cases at two load bases.
- Five appended two-row descriptions pass guarded native staging: the lore
  uses 53 glyph objects, the awakening help uses 52; the pool holds 54.
- The native mode-selection and coordinate instructions produce the new
  Set positions and preserve the other five tested modes.
- Archive verification checks all 23 indexes and preserves 5,728 unchanged
  bank resources. Input hashes are verified before and after building.
- Retro Trans Tools validates the local 0.1.55-to-0.1.62 patch and decodes it
  to the exact target ISO hash.
- Fresh-boot PPSSPP 1.20.4 loads the copied normal Chapter 15 battle save.
  Mujina's index list and spell page show the translated name, all three
  spells and both lore rows without clipping or a memory fault. No save state
  is used. The exact awakening and Create Summons Set states remain pending
  matching saves; their native instructions and bounds pass the checks above.

This is a local test build. Native graphics calls use boundary stubs in the
instruction-level checks; a pass is not a full-game stability guarantee.
Exact awakening availability and the Create Summons Set screen require saves
with those states accessible. Runtime evidence is saved under
`work/ui/report_0.1.62/runtime`.

ISO SHA256: `14c2444b0256d8e3314a8dd2c510cacd4eac96e3e39cd031c02135754ff5b8be`.

References: [Mujina and its spells](https://w.atwiki.jp/sn3psp/pages/94.html),
[Blade Awakening](https://w.atwiki.jp/sn3psp/pages/108.html).
