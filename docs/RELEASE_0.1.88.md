# Summon Night 3 English v0.1.88

English translation test release for the Japanese PSP edition (NPJH50380).
Includes local builds 0.1.84–0.1.88 since published v0.1.83.

Apply with [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools):
refresh the catalog, select your source ISO, and choose Latest. Manual xdelta
patching is also supported. Only these two routes are published:

| Source ISO | Patch |
| --- | --- |
| Clean Japanese original | SN3-English-v0.1.88.xdelta |
| Published English v0.1.83 | SN3-English-v0.1.83-to-v0.1.88.xdelta |

Changes since v0.1.83:

- Restore Shine Saber's blank spell row as “Crush! L.G.Sword” using proportional
  text. Its old 18-character label exceeded the 16-cell font cache. Check all
  235 nonempty spell names and synchronize the battle-banner lookup.
- Display complete proportional action banners, including “Deadly Strike”.
- Prevent Level Up button icons from overlapping OK, End and Skills hints.
- Fit crafting accessory names as “1-Eye Magatama” and “Arabesque Chm”.
- Match Retreat's button frame and palette to neighboring commands.
- Translate missed default summon-animation names, reward headings and class
  prompts; use proportional discovery text and class equipment captions.
- Retain all earlier published translations and the Berserk Summon crash fix.

Start the game fresh and load an in-game save after patching. Save states
restore older executable and text data. Private saves and game images are not
included.

Validation:

- Both patches are decoded completely and compared against the tested ISO:
  `c022bef990dc7e2af8a94fc08c19649c84d5c11cf21decfbfe2e5ebe7f52ee64`.
- Verify all 3,404 build-input hashes. The final fix changes only existing text
  data and the banner dictionary, with no additional loaded memory or ISO growth.
- Execute the native font allocator for all 235 spell names and reproduce its
  failure with the old label. Verify all 144 banner names plus rejection cases
  at two load addresses (296 cases).
- Fresh-boot Windows PPSSPP 1.20.4 tests with normal in-game saves reproduce the
  old blank row and display the corrected row in Summon Index, including
  switching to Dark Bringer and back. The exact Create Summons casting screen
  was not replayed.
- Earlier checks for builds 0.1.84–0.1.87 are identified separately in the
  gameplay validation. The exact beach reward and class-change scenes were not
  replayed; no Android, hardware-renderer or complete-playthrough claim is made.

The Brave Medal award heading remains untranslated. Translation remains
incomplete and uses AI-assisted machine translation drafted and edited under
the maintainer's direction, without complete human Japanese-to-English review.

Source and target hashes are in BUILD-MANIFEST.json. Versioned SHA256 sums
cover the release payload. The full patch uses a 256 MiB source window to keep
it compact. GitHub's Source code downloads contain tools, English targets and
review records; builders require locally supplied original media and historical
intermediate outputs.

[Report issues](https://github.com/retro-trans/Summon-Night-3/issues) with the
build version, emulator, chapter, steps, screenshot and whether you used an
in-game save or a save state.
