# System menu localization - v0.1.44

The reported System menu now uses **Status**, **Cooking** and **Gallery**
button graphics. Selected and normal states are replaced across 44 matching
resource copies (28 Status, eight Cooking, eight Gallery).

The four conditional Status help strings are:

- View status; change gear.
- Status/gear; learn skills.
- View summoned unit status.
- Train summoned units.

The first line depends on skill-learning availability; the optional second
line depends on summoned-unit access and training availability. These short
strings keep every combination within the existing two-line text allocation.

## Validation

- All six unlock combinations executed through the native formatter with
  exact output, 27-cell line and 54-glyph limits, and buffer guards checked.
- The Brave Goals native regression checks still pass.
- All six palette-encoded 112x24 sprites were visually inspected; original
  alpha masks and resource lengths are preserved.
- ISO directory extents, all 23 bank indexes, 5,714 unchanged bank resources,
  and cumulative historical input hashes pass validation.
- Both xdelta files decode back to the exact v0.1.44 ISO.
- Fresh boot and Continue of the supplied Chapter 15 save passed in PPSSPP
  1.20.4 with strict memory checking. This save is inside a story battle and
  does not permit Retreat, so the exact System hub screen has **not** been
  visually verified in-game. Native formatter and sprite checks are separate
  from that runtime limitation.

ISO SHA-256: `a8f9093ab0ee8783e72cd61630ecb746d40acb9b13f34713d476adaa40497ef3`

## Files and use

- Test ISO: `work/output/0.1.44/Summon_Night_3_EN_0.1.44.iso`
- Upgrade from exactly 0.1.43: `work/output/0.1.44/SN3-English-v0.1.43-to-v0.1.44.xdelta`
- Full original-source patch: `work/output/0.1.44/SN3-English-v0.1.44.xdelta`
- Patch hashes and round-trip reports: `work/output/0.1.44/XDELTA-VALIDATION.json`

Restart the patched ISO and load a normal in-game save. Older emulator save
states retain older executable and resource data. This build is local testing;
no new GitHub release was published.

## Artwork provenance

The **built-in image_gen tool** generated the menu sprite atlas using the
reported screenshot as a style reference. The complete final prompt is saved
in `work/ui/system_0.1.44/prompt.json`; the workspace source asset is
`work/ui/system_0.1.44/buttons_generated.png`. `atlas.json` records source crops
and game resource paths. Final native sprites are in
`work/ui/system_0.1.44/native/`. Processing crops and scales the atlas, restores
original transparency and encodes the existing game palette.
