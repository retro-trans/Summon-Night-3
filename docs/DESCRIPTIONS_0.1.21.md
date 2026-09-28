# Spell descriptions — 0.1.21

Built on 0.1.20. ISO SHA-256:
`e334fb7cbf31da3e6b52944268cdb73100c1e0f52730cf415209a6bd5a7d2022`.

The reported Drill Hurricane line means **Attack — Power: 38; Target: Single**.
It now displays **ATK Pwr:38 Single**, with the existing proportional font.

## Coverage

- All 235 populated spell records produce English effect descriptions.
- 18 shared executable literals cover attacks, healing, ailments, possession,
  unit summoning, target areas, Favorites Only and Assist Only/button help.
- All 12 custom spell-description groups are translated, including their
  continuation lines (19 source rows).
- All 30 possession-effect descriptions are translated. Existing names and
  numerical effects remain unchanged.
- Both copies of the shared tables are updated: 02:3 and resident 00:44/7.
- Existing proportional rendering and the five 0.1.17 crash fixes are retained.

This is the selected-spell effect-description category. It does not claim that
all creature lore, equipment, skills, dialogue, or other descriptions in the game
are translated. The separate equipment-fragment review is a draft, not applied
by this release.

## Compact notation

The native panel supports two visible lines of 27 cells and a 54-glyph pool.
The longest descriptions require abbreviations even with proportional spacing.

| Display | Meaning |
| --- | --- |
| ATK Pwr | Attack power |
| Ail / ail. | Ailment |
| Poss. | Possession |
| Med. / Lrg. | Medium / large target area |
| V / H | Vertical / horizontal target pattern |
| H1 adj | Height-one platform; effect includes adjacent cells |
| Phys.break | Physical attacks can destroy the platform |
| ex.Cheer/Chg/Stl | Except Cheer, Charge, and Stealth |
| M / O / S / B | Machine / Oni / Spirit / Beast affinity |
| Res | Resistance |
| rest-20% | The other three listed elemental affinities have -20% resistance |

The three anti-effect platforms preserve their height, adjacency, ailment or
possession effect, physical destructibility, and named exceptions. Full meanings
are retained in the reviewed translation files. Trip Vision retains the source's
literal “varies by screen”; its precise intended context is not established.
Cross H2 and V/H3 retain source geometry notation rather than guessing a shape.

## Verification

Executed the game's original spell-description formatter and string writer for
all 235 populated records. The bounded MIPS interpreter executes branches and
delay slots; only memset, U16 copy/length, and numeric conversion are boundary
stubs. It checks assembled strings, temporary concatenation capacity, output
buffer guards, two-line/27-cell limits, total 54-glyph capacity, and no remaining
Japanese in these effect descriptions. All cases pass. This is not a whole-PSP
emulator or a substitute for rendering checks.

Seven alternate branch-entry HI16 instructions needed the same relocation as
their shared LO16 consumers. The native-formatter tests caught these paths;
the real emulator then verified every relocated pointer, including those seven.
The five-cell ailment prefix is changed in place to avoid an unproven shared
HI16 relocation. Controller glyphs and runtime values are preserved.

Freshly launched the final candidate in an isolated PPSSPP 1.20.4 instance and
loaded a copied in-game battle save, without a save state. Verified Battle Prep,
Dritol's detail page, Drill Blow (12), Drill Rush (24), and Drill Hurricane (38).
Text is proportional and fits. Screenshots and validation are in
`work/ui/descriptions_0.1.21/runtime`.

Read-only live checks verified 18 executable literals, 17 relocation references,
seven alternate branch entries, all 42 resident table-description groups, and
all five preserved crash-fix spans. All 23 bank indexes, the resident mirror,
5,728 untouched bank resources, unrelated ISO files, and historical input
hashes passed static checks. Native font/spacing code is unchanged from 0.1.20.

Visual testing used the software renderer at 1x and the spells available in the
copied save. Other spells received formatter and live table checks. Hardware
rendering and original PSP hardware were not tested.
