# Retro Trans public verification: 0.1.55

The [published release](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.55)
was verified on 2026-10-01 through Retro Trans 0.3.1 with a fresh catalog and
download cache.

- [Targeted catalog validation](https://github.com/retro-trans/retro-trans-tools/actions/runs/36816372498) passed.
- The clean Japanese image has a direct Latest route to v0.1.55.
- Published v0.1.54 is recognized with a direct upgrade route to v0.1.55.
- The public upgrade patch was downloaded and applied through Automatic mode.
- The complete 1,676,998,656-byte result is recognized as v0.1.55 and matches
  SHA-256 `d75654f7d9381293b8b78e8e7ddd8766bd2c518e9da05a8a7983205abd04bfe9`.
- All nine downloaded public assets match the locally verified package exactly.
- Exactly two xdelta assets are published: clean-source-to-current and
  preceding-published-release v0.1.54-to-current. Both passed complete round-trip
  decoding before publication.

Evidence: `work/ui/battle_0.1.55/automatic-validation.json` and
`work/ui/battle_0.1.55/publication-validation.json`.
Reproduce with `tools/verify_retro_trans_live_055.py --out <fresh-directory>`.

This covers the public ISO/catalog/engine workflow, not the GUI or CHD path.
Gameplay limits remain in [RELEASE_0.1.55.md](RELEASE_0.1.55.md).
The immutable release tag and manifest source commit remain
`2ae53ffdff6af4f8b08bac31faee03427f7b1469`; this report is a later verification update.
