# Retro Trans public verification: 0.1.52

The public release at https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.52
was tested with Retro Trans 0.3.1 and a fresh local catalog cache.

- The central catalog includes v0.1.52 after successful targeted refresh run
  https://github.com/retro-trans/retro-trans-tools/actions/runs/36659530017 .
- The clean Japanese source is recognized, with a direct Latest route to 0.1.52.
- The published 0.1.41 ISO is recognized, with a direct upgrade route to 0.1.52.
- The real public upgrade asset was downloaded and applied through Automatic
  mode's engine. The output was recognized as 0.1.52 and matched all
  1,676,666,880 bytes by SHA-256:
  `cfb7e7171e87b528ac91ea345c3ac37853eb345b3486fffd2c0a47c99b2f38f7`.
- All 11 GitHub assets match their corresponding local SHA-256 hashes.

The canonical SHA256SUMS.txt covers the manifest, validation report and four
patches, which are the files downloaded by the catalog importer. Versioned
checksum lists also cover README and changelog documents. No patch or build
manifest was replaced during catalog registration.

Evidence: `work/ui/cooking_title_0.1.52/automatic-validation.json`.
Reproduction: `tools/verify_retro_trans_live_052.py --out <fresh-directory>`.
This is an ISO/catalog/engine test, not a GUI or CHD test. Gameplay limitations
remain those in RELEASE_0.1.52.md. The immutable release tag points to source
commit `1df372420f4dae509fc63eeec73f1350867dec82`; this post-publication report
is a later repository update.

## Release asset cleanup, 2026-09-30

The original publication checks above describe the initial four-patch package.
The release now retains only the original patch and the preceding published
release upgrade (v0.1.41). The v0.1.42 and v0.1.51 upgrade assets are withdrawn;
their catalog identities remain recorded as withdrawn. The two retained patches
and target ISO are unchanged. Release metadata and checksum lists are updated.

All nine remaining public assets match the prepared package by size and
SHA-256. The targeted catalog validation passed after withdrawal:
https://github.com/retro-trans/retro-trans-tools/actions/runs/36661548093 .
The release cleanup preserves the earlier retained-patch round-trip evidence.
