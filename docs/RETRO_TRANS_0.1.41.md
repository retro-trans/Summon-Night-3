# Public Retro Trans verification — 0.1.41

Verified after publication on 2026-09-28 using the published Retro Trans 0.3.1
code at `b90feb1df59324dfda96b81ad32eecad4deae867` and a fresh local cache.

- The public catalog includes the release and recognizes the original Japanese
  ISO and published English 0.1.36 image.
- Latest selects the direct original-to-0.1.41 patch or the 0.1.36-to-0.1.41
  upgrade, according to the source identity.
- The actual Automatic implementation downloaded the public upgrade asset,
  applied it, verified the complete output hash and recognized version 0.1.41.
- Output: 1,672,138,752 bytes; SHA-256
  `56dd6bac4296cb25467dde3d1536928fed42f977f5cce4ed8d6ea79cb5b8e4fa`.
- Both full and upgrade patches also passed complete round-trip verification
  before publication. All nine upload digests matched the local files.

The first catalog import rejected supplementary text files listed in the
canonical checksum file: its importer downloads only the protocol files.
`SHA256SUMS.txt` was corrected to list the manifest, validation report and two
patches only. Versioned checksum files retain the supplementary documentation
hashes. No game image, patch, manifest or validation bytes changed.
The [subsequent catalog refresh](https://github.com/retro-trans/retro-trans-tools/actions/runs/36427964172)
succeeded, and the live Automatic check used that public catalog.

Machine-readable evidence: [retro_trans_live_041.json](retro_trans_live_041.json).
`tools/verify_retro_trans_live_041.py` reproduces the ISO check with a fresh
output directory and the versioned patcher checkout. No visible GUI, CHD
conversion or additional gameplay coverage is claimed by this check.

Release source commit remains `b4b976a40c465853849702b51bd786743ceaf13e`.
This follow-up records post-publication testing without changing the release
source tag or immutable build inputs.
