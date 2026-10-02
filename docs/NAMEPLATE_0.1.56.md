# Magna nameplate — 0.1.56

The reported Japanese plate reads マグナ. Use **Magna**, the short form of
**Magna Clesment**, following the current character reference. This is a local
test build based on published 0.1.55, not a published release.

## Changes

- Ordinary plate: `02.DAT` resource 953, children 3 and 4, 144 × 32 pixels.
- Battle plate: `02.DAT` resource 1113, children 1 and 2, 88 × 24 pixels.
- Exact Magna backlog labels: resources 85–87, child 22. Relocate the translated
  strings and update their pointers; keep all other names unchanged.

The importer preserves the original texture palettes, descriptors, allocations,
non-pixel bytes and unrelated resource children. The build preserves all other
bank resources except the master index that records changed archive offsets.
The executable and existing dialogue translations remain byte-identical.

## Artwork

Lettering was generated with the built-in image-generation tool using the existing
Sonolar lettering as a style reference. The prompt and method are recorded in
`work/ui/magna_0.1.56/imagegen.json`; the saved source is
`work/ui/magna_0.1.56/magna_generated.png`. Import operations only crop transparent
padding, resize, center and quantize the lettering to the existing game palettes.

## Verification

`tools/magna_056.py` validates source hashes, compressed round trips, unchanged
texture metadata and unrelated children, and exports native sprite previews.
`tools/build_magna_056.py` validates historical inputs, the resulting ISO file
extents, all 23 bank indexes, cached archive indexes and unchanged resources.
The current stability audit is run against the resulting ISO.

All 12 regression groups passed on the finished ISO. The build verifies 5,724
unchanged bank resources and preserves the previous executable. Output SHA-256:
`93c4f9c10eb3902d749071ec388c7283e57b9715e2cb4b086333b1f0f1dd3a62`.

The local upgrade patch is packaged through Retro Trans Tools, including complete
decode-to-ISO hash verification. It is under `work/output/magna-test-v0.1.56` and
applies to the published 0.1.55 ISO. No GitHub release is created by this task.

The reported beach conversation is not available in the current test saves.
Native sprites can be inspected directly, but their placement in that exact
conversation is not yet runtime-verified.
