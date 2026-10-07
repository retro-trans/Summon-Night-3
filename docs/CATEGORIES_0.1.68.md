# Related UI category translations — 0.1.68

Local test build based on immutable 0.1.67. Published release remains 0.1.65.

The six reports trace to shared summon profiles, map location labels, short
support descriptions, and active/passive/common skill descriptions and mastery
effects. The build translates all 601 remaining Japanese pointer groups in
these selected categories, not merely the six visible examples. It also
reformats 12 existing English help groups to leave room for translated mastery
effects, and translates 24 map labels through 30 native pointer fields.

The selected tables now have no referenced Japanese text: summon profiles
(table 12, slot 12), active skills (28), passive/support skills (31), short
support descriptions (32), and common-skill descriptions/mastery (34).
Unreferenced original text remains in its original pools. Undiscovered-entry
question marks remain intentional. Other categories, including alternate
summon forms, are outside this pass.

Examples include Picolit's apprentice-angel profile, Warning's side/rear attack
description, Unit Summon's level-dependent unit count and mastery effect,
Cheer's HP/critical-rate/damage-reduction effects, and Rocky Shore. Longer map
names use short display forms, with full English names retained in map.json.
Names follow the current character reference: Belfraw, Alieze, Minis. Stora
follows the existing technique glossary. No saved player names are rewritten.

Translations are appended and their audited pointers rebound. Record counts,
numeric fields, costs, level data, original text pools and all previous native
code are preserved. The expanded resident table is synchronized in both bank
and cached master copies. The private chapter-script arena remains writable
and unchanged. The inherited 0.1.67 SELECT/Learn Skills correction is retained.

The independent meaning review covered all 83 profiles and 485 other pointer
groups, including identical-source duplicates. Corrections preserve incoming
damage, adjacency, allied summon ownership, ailments, and the level-gap cap.
Profiles are abbreviated for the two visible 27-cell rows; fuller English is
stored for entries whose display version omits background details.

Uncertainties retained in the records: profile 18 is a deliberately odd quoted
strength/manganese joke, translated literally; Zel is a provisional English
romanization of the Machine World craftsman's name. The original Japanese
listing establishes the name and role, not an official English spelling:
[summon listing](https://w.atwiki.jp/sn3psp/pages/89.html).
Minis follows the user's
[SN6 gallery reference](https://summonnight.fandom.com/wiki/Summon_Night_6:_Lost_Borders/PS_Vita_Gallery).
Native Greek/box stat glyphs are preserved as icons. The concealment skill's
ZOC wording preserves the source's unspecified distinction between emitting
ZOC and ignoring opposing ZOC.

Validation passed on the completed ISO:

- 14 inherited regression groups, including 1,434 equipment cases, 235 spell
  cases, dynamic Pact help and 131,072 relocated glyph-guard cases.
- 254 native help/master formatter cases and 373 shared-staging cases; no
  truncated text, no output-buffer overrun, maximum 54 glyph cells.
- 178 translated skill-name fields fit 16 cells and 108 pixels. All map display
  labels fit 16 cells and 96 pixels.
- 16 native Status formatter combinations, 18 SELECT positioning cases and
  two retained Give Food executions at two load bases.
- 23 bank indexes, synchronized caches, and 5,728 unchanged bank resources.
- Strict PPSSPP 1.20.4 JIT fresh boot using a normal Chapter 15 save. Battle
  menu and Summon Index work; Picolit's two English lines were captured in
  game. IgnoreBadMemAccess is disabled; no save state was used.

Exact early-story map/deployment/Learn Skills screens and battle casting
remain untested without a matching normal save. This is not a full playthrough
or a universal crash-prevention claim.

ISO: work/output/0.1.68/Summon_Night_3_EN_0.1.68.iso

SHA-256: 34744b4267e13813d2c7c84baa7d4aac251779bd16d1f515af2d3e9775d9a3cd
