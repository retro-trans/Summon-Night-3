# Sonolar nameplates — 0.1.38

The pictured Japanese label is Sonolar. This version translates the ordinary
portrait label (`02:00915`, children 3/4) and the separate battle label
(`02:01099`, children 1/2). Each has a main text layer and a matching shadow.
The selected `work/glossary/character_reference_sn6_vita.json` supplies the spelling.

Built on immutable 0.1.37. Its blue Night Talk nameplate and dialogue reflow are
retained. This is a local test build; it has not been published to GitHub.

## Validation

The input resource and layer hashes are bound in `targets.json`. Every imported
sprite retains its native dimensions (144×32 ordinary, 88×24 battle) and palette.
The generated lettering is downsampled without changing its aspect ratio.
The shadow uses the same alpha silhouette and the original shadow color.
Both imported text sprites were visually inspected at native size.

The importer checks every other portrait/expression child for byte equality and
verifies compression round trips. The ISO builder checks file extents, all 23
archive indexes, resident caches, all replacement payloads and all untouched
bank resources. The executable and scripts are unchanged from 0.1.37.

The pictured scene has not been replayed in-game. Night Talk's separate pending
playthrough check from 0.1.37 remains pending; this nameplate update does not
claim to complete that check.

## Artifacts

- `work/output/0.1.38/Summon_Night_3_EN_0.1.38.iso`
- `work/output/0.1.38/manifest.json`
- `work/ui/sonolar_0.1.38/sonolar_generated.png`: lettering generated with the built-in imagegen tool.
- `work/ui/sonolar_0.1.38/sonolar_915_3_native.png`: ordinary portrait label.
- `work/ui/sonolar_0.1.38/sonolar_1099_1_native.png`: battle label.
- `work/translation/en/sonolar_0.1.38/generation.json`: exact prompt and import method.
- `work/translation/en/sonolar_0.1.38/targets.json`: source hashes and import bounds.

Rebuild with `tools/build_sonolar_038.py --write --destination work/scratch/sonolar_rebuild038`
using the project Python runtime and a new destination directory.

Final build: 5,727 untouched bank resources verified.

ISO SHA-256: `72be0148cb7d1c6dbb8d8ed1122347dc1275fc2702b19935c034cb207a8eb5ef`.
