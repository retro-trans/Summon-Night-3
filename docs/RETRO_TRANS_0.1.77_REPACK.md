# Optimized 0.1.77 public patch verification

The [0.1.77 release](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.77)
now contains the optimized original-to-current patch, **14,383,778 bytes
(13.7 MiB)**, and the unchanged 0.1.73 upgrade, **4,485,851 bytes**.

Both public routes passed with Retro Trans Tools 0.5.1 on 2026-10-08:

- A fresh public catalog recognizes the clean Japanese original and published
  0.1.73, each with a direct Latest route to 0.1.77.
- Both patches were actually downloaded and applied through Automatic mode.
- Both complete 1,691,269,120-byte results are recognized as 0.1.77 and match
  SHA-256 `d35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427`.
- All ten public asset sizes and SHA-256 digests match the optimized local package;
  every checksum entry was checked locally.
- [Public catalog validation](https://github.com/retro-trans/retro-trans-tools/actions/runs/37730084301) passed.
- The previous cached catalog passes its immutability check against the new one.
  The retired 407,197,655-byte full patch remains recorded with its old URL/hash,
  while the replacement uses `SN3-English-v0.1.77-optimized.xdelta`.

The correction changes only patch encoding and release metadata. The game ISO,
game build inputs, 0.1.73 upgrade and release tag are unchanged. The manifest's
game source commit remains `e08b3899667dcafb5412e173b48a43afdde65797`.
People already using 0.1.77 do not need to patch again.

Evidence:
`work/ui/release_0.1.77/OPTIMIZATION-VALIDATION.json`,
`work/ui/release_0.1.77/REPACK-PUBLIC-ASSET-VALIDATION.json` and
`work/ui/release_0.1.77/REPACK-AUTOMATIC-VALIDATION.json`.
Reproduce the public test with
`tools/verify_retro_trans_repack_077.py --execute --out <fresh-directory>`.

This verifies the public ISO/catalog/engine workflow. No emulator was needed
because both outputs match the previously tested game image exactly. GUI and CHD
paths are outside this check. Gameplay limits remain in the
[release report](RELEASE_0.1.77_REPACK.md).

Use a 256 MiB source matching window for future full patches, as described in
[PATCH_PACKAGING.md](PATCH_PACKAGING.md), and fully decode each patch before
publication.
