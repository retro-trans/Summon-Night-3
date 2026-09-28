# Retro Trans compatibility — v0.1.35

Tested on Windows on 2026-09-28 with Retro Trans 0.3.1, source commit
`945bb58210c9e84ba8a4c7b5fb503b2b19418c0d`. The existing published delta was
used unchanged. The game source tag remains
`0f73aa060d9d052a86452db1145f593b932756b5`.

## Results

- The actual `manual_patch` implementation and bundled xdelta engine applied
  the delta to the clean Japanese ISO successfully.
- The official release validator accepted the canonical manifest, validation
  report, checksum file and patch.
- The actual catalog importer accepted the release asset set.
- Recognition identified the original ISO; Latest, Next version only and
  explicit 0.1.35 each selected the expected single patch.
- The actual `apply_plan` implementation applied that plan successfully.
- Both complete 1,670,623,232-byte outputs matched SHA-256
  `01ae84776c9ad3d5e57bdb6f35291f79b0377f9c1322636703cd6b8544c062db`.
- Recognition identified the output as 0.1.35 with no further Latest upgrade.
- An existing output was rejected; the original ISO and delta were unchanged.

The catalog test supplied locally staged assets through a transport adapter.
It tests the real importer, planner, engine and verification code, but does
not establish public catalog discovery or download access. No visible GUI,
CHD conversion or additional gameplay testing was performed in this check.

## Release contract

The release supplies exactly one `BUILD-MANIFEST.json`, `VALIDATION.json`,
`SHA256SUMS.txt` and its listed `.xdelta`. The former versioned manifest is
preserved as `BUILD-DETAILS-v0.1.35.json` so it cannot be mistaken for a second
protocol manifest. Original build inputs and the published patch are unchanged.

The [Retro Trans release standard](https://github.com/retro-trans/retro-trans-tools/blob/main/docs/RELEASE_STANDARD.md)
requires a public game repository and a non-prerelease for discovery. At test
time this repository was private and v0.1.35 was a prerelease. Automatic
catalog availability has not been claimed. Manual Apply xdelta is verified.

## Reproducing the local test

`tools/retro_trans_compat_035.py` previews by default. With `--write` it creates
fresh output and scratch directories, runs both full patch applications and
writes machine-readable evidence. It requires the local original ISO, the
historical release assets and a Retro Trans checkout; `--patcher` selects the
checkout. Keep the checkout at the tested commit to reproduce these results.
The script refuses to replace existing test outputs.
