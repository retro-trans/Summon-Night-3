# Release 0.1.41 — cumulative interface and dialogue fixes

Published from the verified local 0.1.41 image. This release includes the
previously local 0.1.37–0.1.40 changes and keeps the earlier Chapter 1–8 scope.
It is an incomplete translation and an ongoing test build.

## Changes since 0.1.36

- Reflow 1,348 Night Talk groups in 76 scene resources to two lines per page,
  identified by native display modes 4/5; translate 19 blue nameplates.
  See [Night Talk](NIGHT_TALK_0.1.37.md).
- Translate Sonolar's ordinary and battle nameplates, using the selected name
  reference. See [nameplates](SONOLAR_0.1.38.md).
- Remove the repeated request to hurry to the boat in Aty's Chapter 1 line.
  See [dialogue correction](REPETITION_0.1.39.md).
- Translate 25 remaining accessory names and shared equipment-effect wording;
  fix Learn Skills/Key Item branch references and bound long ailment groups.
  See [accessories](ACCESSORIES_0.1.40.md).
- Translate Learn Skills, Common/Unique tabs, controls and 31 skill names;
  add scoped VWF and shorten Pact names; wrap crafting help between affinities.
  See [Learn Skills](SKILLS_0.1.41.md).

## Verification and limits

The incremental builders check archive indexes, changed records, untouched
resources and resident table copies. Additional checks cover 240 native item
formatter cases, 15 Pact name cases, 31 Pact description cases and 108 relocated
VWF executions. Version 0.1.41 passed a fresh PPSSPP boot. Version 0.1.40 also
loaded a copied early-battle save and displayed the Deployment layout.

The unlocked Learn Skills report came from another user without a save.
That exact screen, normal Night Talk playthroughs and the corrected Chapter 1
scene have not been verified in gameplay. Some unique skill names/descriptions
remain untranslated. Complex accessory descriptions can exceed two lines;
visual layout for these remains pending. No full route or PSP hardware testing
is claimed. AI-assisted review does not represent human proofreading totals.

## Release contract

`tools/package_release_041.py --write` verifies the target ISO and all 1,062
recorded build inputs, then uses the published Retro Trans 0.3.1 library
(commit `b90feb1df59324dfda96b81ad32eecad4deae867`) to build and fully decode:

- `SN3-English-v0.1.41.xdelta`: original Japanese NPJH50380 ISO.
- `SN3-English-v0.1.36-to-v0.1.41.xdelta`: exact published English 0.1.36 ISO.

Both outputs must be 1,672,138,752 bytes with SHA-256
`56dd6bac4296cb25467dde3d1536928fed42f977f5cce4ed8d6ea79cb5b8e4fa`.
`BUILD-MANIFEST.json`, `VALIDATION.json` and `SHA256SUMS.txt` use the canonical
Retro Trans release contract. Full and upgrade patches produce the same image.
The source commit is recorded when packaging; game images are never uploaded.

Historical per-build reports describe their local-test status at the time.
This cumulative release does not change their recorded inputs or expand their
runtime verification claims. Start the new ISO fresh and use an in-game save.
