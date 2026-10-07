# Public release verification: 0.1.73

Published release: https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.73

- Release tag and build manifest identify source commit
  `0c5fe056cb8afd041c73ceaeac4fcf67d1ea19f0`.
- All ten uploaded assets match their local SHA256 hashes and byte lengths.
  The only xdelta assets are original-to-0.1.73 and 0.1.65-to-0.1.73.
- Both release patches passed complete decoded-ISO hash verification locally.
- Catalog workflow 37602895774 completed successfully and registered the release.
- Retro Trans 0.5.1, commit `e487cf698e3a40e7dfa5db20822ffaeaba6e5d8c`,
  discovers the public catalog entry and a direct original-to-Latest route.
- With a fresh cache and the real public download client, Automatic upgrades
  the published 0.1.65 ISO to 0.1.73 and recognizes the result.
- The final 1,686,472,704-byte image has SHA256
  `79e60216dbd74b6bc1b5abe14806557b17d4544f3c6518a5f6ada6a73f3be685`.

The older local Retro Trans 0.3.1 copy cannot read the current catalog's newer
manifest schemas. The public check uses the current 0.5.1 client. This is an
ISO/API check; GUI and CHD workflows are not tested here. The separate gameplay
report covers the actual Yard/white-stone crash regression.

Machine-readable receipt: `work/ui/release_0.1.73/PUBLIC-VALIDATION.json`.
Re-run using `tools/verify_retro_trans_live_073.py --patcher
work/scratch/retro-trans-tools-release073 --out <fresh-directory> --execute`.
