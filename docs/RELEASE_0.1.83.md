# Summon Night 3 English v0.1.83

English translation test release for the Japanese PSP edition (NPJH50380).
Includes both local fixes since the last published release, v0.1.81.

Apply with [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools):
refresh the catalog, select your source ISO, and choose Latest. Manual xdelta
patching is also supported. Only these two routes are published:

| Source ISO | Patch |
| --- | --- |
| Clean Japanese original | SN3-English-v0.1.83.xdelta |
| Published English v0.1.81 | SN3-English-v0.1.81-to-v0.1.83.xdelta |

Changes since v0.1.81:

- Fix the crash after Berserk Summon destroys a Summonite Stone. The old
  52-character notification overran a native 31-entry character list. The full
  notification now fits; eight related oversized battle warnings are fixed too.
- Fix the first two blank Equip Type rows. Both consumers now use independent
  captions, covering all 150 attack/weapon combinations. Greatsword is shortened
  to Greatswd only in composite captions to fit the existing text cache.
- Preserve player-entered names, combat rules and save formats. Includes all
  earlier published translation and UI fixes.

Start the game fresh and load an in-game save after patching. Save states restore
the old executable, text and any interrupted renderer state. Private recovery
saves are not included in this public release. No game ISO is distributed.

Validation:

- Both patches are decoded completely and compared against the tested ISO:
  `6cac982807c5cb6672fbbb74e166f973352ac7d30375fe4ccfee48d41babb5e6`.
- All 3,358 build-input hashes are verified. The final notification fix changes
  only existing English literals relative to local build 0.1.82; code,
  relocations and every other ISO file remain unchanged.
- The native binder reproduces the reported invalid write and passes 56 fixed
  cases at two load addresses, including the 31-character limit. All 27 audited
  notification strings are checked after a fresh boot.
- Windows PPSSPP 1.20.4, JIT, software graphics and strict memory checks: the
  supplied 0.1.81 state reproduces the crash. After narrowly repairing its text
  renderer, the complete message displays, confirming returns to battle, and a
  normal Suspend save completes. A separate fresh 0.1.83 boot loads that normal
  Suspend save and resumes the battle. Only one emulator is used at a time.
- Earlier 0.1.82 checks cover 616 equipment-consumer cases at two load addresses,
  neighboring-buffer guards and fresh-save Rexx/Kyuuma equipment pages, including
  switching back to Rexx. These earlier checks are identified separately in
  GAMEPLAY-VALIDATION-v0.1.83.json.

The complete Berserk cast was not repeated from a normal save in the final run;
its exact aftermath was replayed from the supplied state, with fresh-loaded
text and normal-save continuation checked separately. No direct Android,
hardware-renderer or full-game playthrough test was performed. Audio was enabled
but playback was not independently validated.

This is an **AI-assisted machine translation**, drafted and edited with large
language models under the maintainer's direction. Translation remains incomplete
and has not received complete human Japanese-to-English proofreading.

Source and target hashes are in BUILD-MANIFEST.json. SHA256SUMS-v0.1.83.txt covers
the release payload. The full patch uses a 256 MiB source window to keep it compact.
GitHub's Source code downloads contain tools, English targets and review records,
not playable game images. Builders require locally supplied original media and
historical intermediate outputs.

[Report issues](https://github.com/retro-trans/Summon-Night-3/issues) with the
build version, emulator, chapter, steps, screenshot and whether you used an
in-game save or a save state. Apply to your own copy; do not sell patched copies.
