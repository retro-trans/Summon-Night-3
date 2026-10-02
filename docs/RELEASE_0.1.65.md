# Summon Night 3 English — v0.1.65

English translation **test release** for the Japanese PSP edition **NPJH50380**.
Includes all published v0.1.55 translations and the UI fixes from local builds
0.1.56 through 0.1.64, plus the 0.1.65 memory fix. Remaining text and full-route testing are incomplete.

## Apply

Use [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools): refresh
the catalog, choose Automatic and select your source ISO. Manual Apply xdelta
and DeltaPatcher also accept these patches. Keep checksum verification enabled.

| Source image | Patch |
|---|---|
| Clean Japanese NPJH50380 | `SN3-English-v0.1.65.xdelta` |
| Published English v0.1.55 | `SN3-English-v0.1.55-to-v0.1.65.xdelta` |

Only these two xdelta patches are included. Local intermediate builds are not
valid sources for the upgrade patch. Use the original patch with the clean
Japanese image instead. No game image or private save is distributed.

Start the new ISO fresh and load an **in-game save**. Emulator save states
retain the previous executable and resources.

## Changes since v0.1.55

- Fix a reproduced Chapter 15 Battle Info crash: the chapter-common script
  now uses a separate loader-owned buffer, preventing it from overwriting
  the expanded Extra Brave Goal table. All 20 chapter scripts fit the buffer.

- Translate Magna and Yard nameplates while preserving their original frames.
- Translate Create Summons, Affinity, Island Map, First Shore and Level Up.
- Align the summon controls and Level Up's Learn Skills hint.
- Translate Charge, indirect-attack commands and Blade Awakening variants.
- Fix the truncated Zip Toast name and display recognized spell banners with
  centered proportional lettering. Fix the Shine Saber spell-list overlap.
- Translate Mujina's alternate names, three spells and description.
- Translate Rewards obtained!, F Aid, all numbered Concept Art items, and
  shared party/battle/support joining messages with proportional lettering.
- Translate Dash!, Fighting Spirit, Guts and Item Throw, including their help
  and mastery effects within the existing description allocation.
- Preserve player-entered names, skill effects, costs, statistics, discovery
  placeholders, event flow and existing crash guards.

## Validation and limits

The completed ISO passes all 16 cumulative regression groups, including native
formatting/staging, bounded rendering and archive/cache consistency checks.
All four newly translated skill-help blocks fit the 54-glyph allocation, and
their names fit the measured card space. Both release patches pass full
decoded-ISO hash verification through Retro Trans Tools.

Fresh-boot PPSSPP 1.20.4 checks cover Continue from a Chapter 15 in-game save,
Extra Brave Goals, equipment Inventory and Summon Index. Screenshots are in
`work/ui/release_0.1.65` and summarized in the release validation records.
A long Extra Brave Goal list label still clips at its edge.
Some Summon Index descriptions remain Japanese.
Exact reward/recruitment, map, casting-banner, Level Up and Learn Skills visual
checks still require matching saves. Full routes, early-chapter and Night Talk
gameplay, puppet shop, room skills, Cooking and save/reload are not exhaustively
tested in this release. Some names and lore terms remain provisional.

This is an **AI-assisted machine translation**, drafted and edited with large
language models under the maintainer's direction. It has not received complete
human Japanese-to-English proofreading.

GitHub's Source code downloads contain tools, English targets and review
records. They are not playable game images. Incremental builders require
locally supplied original media and historical intermediate outputs.

[Report issues](https://github.com/retro-trans/Summon-Night-3/issues) with the
patch version, emulator version, chapter, reproduction steps and screenshot.
State whether you used an in-game save or emulator save state.

Apply this free patch to your own copy. Do not sell the patch or prepatched images.
