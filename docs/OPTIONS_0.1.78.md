# Options selected labels — 0.1.78 local test

This build removes the black shapes behind selected **Cursor Direction** and
**L/R Function** labels. The text importer had restored the original Japanese
glyph transparency on two English text textures because their dimensions matched
a button texture. The corrected importer uses the English glyph transparency.
The pointer, label positions, dimensions and palettes are preserved.

The complete Options category was reviewed: Music Volume, Event Voices,
Forecast, Cursor Direction and L/R Function, in both browsing and editing modes.
All other textures in this resource remain identical to 0.1.77. Exactly 2,349
bytes of the ISO changed; every byte outside the fixed Options resource matches
0.1.77, including the executable and image layout.

Apply `SN3-English-v0.1.77-to-v0.1.78.xdelta` to the **published 0.1.77 ISO**
with Retro Trans Tools. The test ZIP includes its compatible manifest and
checksums. Boot the patched ISO afresh; an old save state can retain old textures.
Normal in-game saves can be used.

- Source ISO SHA-256: `d35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427`
- Target ISO SHA-256: `612b68c3ea4bb20341c2ee8f7bfe170e59f47fb1853ca08e03d2a9dcc025237f`

Validation used one isolated Windows PPSSPP 1.20.4 instance, a fresh boot and
the title-screen Options menu. Each of the ten row/mode combinations was visually
reviewed from the native framebuffer; leaving Options returned to the title
screen successfully. No save state, loaded in-game save or game-memory edits
were used. Temporary capture breakpoints were removed after each screenshot.
The emulator was closed after testing.

Audio was enabled, but the host logged an audio-device initialization error;
audio playback was not validated. This is a scoped Options check, not an Android
device test or a full gameplay regression test. Static texture checks and a full
patch decode verify the exact target ISO independently of the screenshots.

Review evidence: `work/ui/options_0.1.78/reviewed/`, native mask comparison in
`work/ui/options_0.1.78/mask_comparison.png`, and the asset/runtime validation
reports included in the test package. This local test is not a published release.
