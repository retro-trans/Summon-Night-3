# Retro Trans public verification: 0.1.54

The [published release](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.54)
was tested through Retro Trans 0.3.1 with a fresh catalog/download cache.

- [Targeted catalog validation](https://github.com/retro-trans/retro-trans-tools/actions/runs/36800735181) passed.
- The clean Japanese ISO has a direct Latest route to v0.1.54.
- Published v0.1.52 is recognized and has a direct upgrade route to v0.1.54.
- The public upgrade asset was downloaded and applied through the Automatic engine.
- Its complete 1,676,941,312-byte output is recognized as v0.1.54 and matches
  SHA-256 cdf3899bb3aeec87e03cc979b203c56edcbcd1b270036397dfdd37b00488b8c5.
- All nine public assets match their local size and SHA-256.
- The release contains exactly two xdelta files: original-to-current and
  preceding-published-release v0.1.52-to-current.

The canonical SHA256SUMS.txt covers only the manifest, validation report and
patches downloaded by the importer. The versioned checksum lists additionally
cover the README and changelog. Patch bytes and target ISO were unchanged by
the checksum-list correction during registration.

Evidence: work/ui/story_0.1.54/automatic-validation.json and
work/ui/story_0.1.54/publication-validation.json.
Reproduce with tools/verify_retro_trans_live_054.py --out <fresh-directory>.

This tests the public ISO/catalog/engine workflow, not the GUI or CHD path.
Gameplay limits remain in [RELEASE_0.1.54.md](RELEASE_0.1.54.md).
The immutable release tag and manifest source commit remain
f97ada9eff52f1f1ed4363dcc34c8eef67e8d247; this verification report is a later update.
