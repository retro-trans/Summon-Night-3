# Retro Trans public verification: 0.1.65

The [published release](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.65)
was verified on 2026-10-02 through Retro Trans 0.3.1 with a fresh catalog and
download cache.

- [Catalog validation and refresh](https://github.com/retro-trans/retro-trans-tools/actions/runs/37008314218) passed.
- The clean Japanese image has a direct Latest route to v0.1.65.
- Published v0.1.55 is recognized with a direct upgrade route to v0.1.65.
- The public upgrade patch was downloaded and applied through Automatic mode.
- The complete 1,680,816,128-byte result is recognized as v0.1.65 and matches
  SHA-256 `521824961e5441dd245b80a12940dbd4db3146fcf2d46a1df7c36909fc28ab7d`.
- All nine downloaded public assets match the locally verified package exactly.
- Exactly two xdelta assets are published: clean-source-to-current and
  preceding-published-release v0.1.55-to-current. Both passed complete round-trip
  decoding before publication.

Evidence: `work/ui/release_0.1.65/automatic-validation.json` and
`work/ui/release_0.1.65/publication-validation.json`.
Reproduce Automatic verification with
`tools/verify_retro_trans_live_065.py --execute --out <fresh-directory>`.
The asset-comparison procedure is in `tools/verify_public_assets_065.py`;
it refuses to overwrite the saved report.

This covers the public ISO/catalog/engine workflow, not the GUI or CHD path.
Gameplay limits remain in [RELEASE_0.1.65.md](RELEASE_0.1.65.md).
The immutable release tag and manifest source commit remain
`687935184c9f98f592e61bd59529d8c142780719`; this report is a later verification update.
