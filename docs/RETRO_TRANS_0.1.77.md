# Retro Trans Tools public verification: 0.1.77

The [published release](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.77)
was verified on 2026-10-08 through Retro Trans Tools 0.5.1 with a fresh public
catalog and download cache.

- [Targeted catalog validation](https://github.com/retro-trans/retro-trans-tools/actions/runs/37720674456) passed.
- The clean Japanese image is recognized with a direct Latest route to 0.1.77.
- Published 0.1.73 is recognized with a direct upgrade route to 0.1.77.
- The public upgrade patch was downloaded and applied through Automatic mode.
- The complete 1,691,269,120-byte result is recognized as 0.1.77 and matches
  SHA-256 `d35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427`.
- All ten public asset sizes and GitHub SHA-256 digests match the final local
  package. Every entry in the three checksum lists was verified locally.
- Exactly two xdelta assets are published: original-to-current and preceding
  published release 0.1.73-to-current. Both passed complete decoded-image hash
  verification before publication. No older patches were removed or changed.

The initial catalog import rejected the generic checksum list because it included
documentation that the importer does not fetch. The generic list now covers the
four core files (two patches, manifest and validation); versioned SHA1/SHA256
lists cover all eight payloads, including documentation and the generic list.
Only the three checksum files were replaced. Patch bytes and the manifest stayed
unchanged. The retried catalog import and final public upgrade both passed.

Evidence:
`work/ui/release_0.1.77/PUBLIC-ASSET-VALIDATION.json` and
`work/ui/release_0.1.77/AUTOMATIC-VALIDATION.json`.
Reproduce with `tools/verify_retro_trans_live_077.py --execute --out <fresh-directory>`.

This covers the public ISO/catalog/engine workflow, not the GUI or CHD path.
The public original-image route was planned; its patch was decoded locally and
its uploaded digest verified. The public upgrade route was actually applied.
Gameplay limits remain in [RELEASE_0.1.77.md](RELEASE_0.1.77.md).
The immutable release tag and manifest source commit remain
`e08b3899667dcafb5412e173b48a43afdde65797`; this report and the main README update
are later publication verification records.
