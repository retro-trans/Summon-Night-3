# Full-patch encoding

For future original-to-current releases, explicitly use a 256 MiB xdelta source
matching window (`-B 268435456`). Rebuilding the executable and archives shifts
unchanged files, and a smaller matching window can cause unchanged data to be
stored again in the patch. Always fully decode and hash the resulting ISO before
publication; patch size alone does not establish correctness.

The 0.1.77 correction reduced its full patch from 407,197,655 to 14,383,778 bytes
without changing the game image. `tools/optimize_release_patch_077.py` records the
exact encoding, complete decoding and metadata checks used for that correction.
The 0.1.73 upgrade stayed byte-identical.

Keep the generic `SHA256SUMS.txt` limited to catalog core assets: the two patches,
`BUILD-MANIFEST.json` and `VALIDATION.json`. Versioned checksum files also cover
release documentation. Retro Trans Tools fetches only the core assets while
importing a standard release.

Never replace an already cataloged patch URL with different patch bytes. Publish
an optimized replacement under a new filename, remove the old published asset,
and retain its old URL/hash/size as a withdrawn catalog edge. Verify catalog
immutability against the previous data and refresh the public catalog after all
release assets, manifests and checksums agree. Preserve the released game image,
build inputs and tag when only patch encoding changes.
