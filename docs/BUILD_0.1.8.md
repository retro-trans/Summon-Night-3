# Build 0.1.8 — translated chapter cards

[ISO](../work/output/0.1.8/Summon_Night_3_EN_0.1.8.iso) · [Chapter 1 in-game](../work/ui/chapter_0.1.8/runtime/batch2/08.png)

Translated and redrew all 30 distinct title cards in the discovered native family:
16 numbered chapters, the final chapter, five side stories, one bonus title and
seven ending titles. The additional Chapter 2 copy is replaced too, for 31 native
cards. The supplied screenshot is now **Chapter 1 — A Sudden Beginning**, keeping
the subtitle **Where am I now?**

## Artwork and translations

The built-in image generator redrew the complete cards, retaining each source
palette, star motif and existing English subtitle. Full-canvas downsampling and
native-palette conversion preserve transparency; no cover rectangles or text
overlays are added. All generated assets are saved in
`work/ui/chapter_0.1.8/chapter_93_generated.png` through
`chapter_122_generated.png`.

- [Complete translation list and scope](CHAPTER_TITLES.md)
- [Exact prompts](../work/ui/chapter_0.1.8/prompts.json)
- [Independent meaning review](../work/translation/en/chapter_titles.meaning_review.json)
- [Native conversion records](../work/ui/chapter_0.1.8/index.json)
- [Runtime and visual evidence](../work/output/0.1.8/chapter_runtime_validation.json)

## Validation and limits

All 31 native images were decoded and visually inspected at 480×272. Every pack
round-tripped, retained its decoded size, texture descriptors and palette, and
preserved its RIFF/WAVE audio byte-for-byte. Final ISO verification checked all
23 bank indexes, 32 unchanged ISO files and 3,527 unchanged bank resources.
The executable, prior setup graphics, 609 dialogue entries and three character
labels are preserved from 0.1.7.

The final ISO was booted in a separate PPSSPP 1.20.4 instance with a fresh game.
Chapter 1 was reached naturally, displayed clearly, faded out and returned to the
beach. Other chapter and ending branches were not played through; their artwork
passed native-image and archive checks. Audio playback was not retested. The
user's running emulator and saves were untouched.

Separate executable heading/title metadata remains Japanese until its save/gallery
consumers and layout are verified. Other untranslated UI and dialogue remain;
this is a partial translation, not a full-game release.

SHA-256: `0eeba554066cbc5d56f38744ea8e8f99c1a535e68a981624294b0e8db08e13e0`. Size: 1,658,853,376 bytes.
Restart the game when switching ISO; an old save state may retain loaded textures.
Next unused version: **0.1.9**.
