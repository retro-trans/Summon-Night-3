# Summon Night 3 English v0.1.81

English translation test release for the Japanese PSP edition (NPJH50380).
Includes all changes since the last published release, v0.1.77; versions
0.1.78–0.1.80 were local test builds.

Apply with [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools):
refresh the catalog, select your source ISO, and choose Latest. Manual xdelta
patching is also supported. Only these two patch routes are published:

| Source ISO | Patch |
| --- | --- |
| Clean Japanese original | SN3-English-v0.1.81.xdelta |
| Published English v0.1.77 | SN3-English-v0.1.77-to-v0.1.81.xdelta |

Start the game fresh and load an in-game save after patching. Save states retain
the old executable in memory. Source and target hashes are in BUILD-MANIFEST.json;
SHA256SUMS-v0.1.81.txt covers the release payload. No game ISO or private save is
distributed. The full patch uses a 256 MiB source window to avoid the oversized
patch produced by the previous encoder settings.

Changes since v0.1.77:

- Remove black Japanese masks behind selected Options labels.
- Restore Chapter 7 Night Talks titles, preserve proportional title lettering,
  and separate the footer controls.
- Translate related attack-skill names and descriptions, fortune messages,
  equipment types and range descriptions, location plaques and speaker graphics.
- Translate Learn Skills warnings and use variable-width popup lettering;
  restore missing skill-card names when the texture strip pool fills.
- Translate default summon-name labels and battle banners while preserving
  custom names. Reflow proficiency help and fix Replay help errors, chapter
  labels and truncated Brave Orders.
- Align the Assist triangle icon with its caption and use variable-width
  lettering in the required-member INFO list, including Protagonist and
  Magna / Toris.

Validation:

- Both patches are decoded completely and compared with the tested v0.1.81 ISO:
  `1e574f8ec2ed2917a2ee90b7c75427a6acb2ecca64727ca1215a3c683f2f89a8`.
- All 3,350 recorded build-input hashes are checked. Final asset checks cover
  relocated Assist icon and member-list paths at two load bases, buffer guards,
  custom names, inherited code/data and unchanged remaining ISO files.
- Fresh boot and in-game save checks in Windows PPSSPP 1.20.4 confirm Sky Torrent
  and Heaven's Net INFO layouts and the shared Assist help renderer. A live trace
  confirms execution of the new icon helper. Only one emulator was used.
- Earlier local builds supplied fresh-save checks for Options, Night Talks,
  Learn Skills, proficiency and Replay; their reports are identified separately
  in GAMEPLAY-VALIDATION-v0.1.81.json.

The shared Assist widgets were checked in the Summon Index; the exact supplied
battle sequence was not replayed. No direct Android test or full-game playthrough
was performed. Audio was enabled but playback was not independently validated.
Translation is machine assisted and remains incomplete; it has not received a
complete human Japanese proofreading pass.

Report issues at [Summon Night 3 issues](https://github.com/retro-trans/Summon-Night-3/issues)
with the build version, emulator, chapter, steps and screenshot, and whether you
used an in-game save or a save state. Apply to your own copy; do not sell patched
game copies.
