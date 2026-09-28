# Build 0.1.7 — image-generated menu artwork

[ISO](../work/output/0.1.7/Summon_Night_3_EN_0.1.7.iso) · [In-game preview](../work/ui/imagegen_0.1.7/runtime/title.png)

Replaced the entire character-selection banner and Confirm button using built-in
image generation. The new assets have continuous peach woodgrain, integrated
cream/brown lettering and clean borders. Both protagonist variants use them.
No hand-drawn text or paint-over patches were added to the generated artwork.

## Saved artwork and prompts

- [Generated banner](../work/ui/imagegen_0.1.7/character_banner_generated.png)
- [Generated Confirm button](../work/ui/imagegen_0.1.7/confirm_button_generated.png)
- [Exact prompts and source references](../work/ui/imagegen_0.1.7/prompts.json)
- [Native conversion records](../work/ui/imagegen_0.1.7/index.json)

The built-in image_gen tool edited the original native sprites. Import only crops
transparent padding, downsamples to the original sprite footprint and maps colors
to the original palette. Generated alpha is retained through this conversion.

## Checks and scope

The final ISO was booted in an isolated PPSSPP 1.20.4 instance. Both Rexx and Aty
screens were inspected: text is complete, no rectangular patches or Japanese
letter remnants remain, and the artwork fits the existing menu geometry.
[Runtime evidence](../work/output/0.1.7/artwork_runtime_validation.json).

Static checks verified native pack round trips, untouched sibling sprites and
resources, all 23 indexes, 32 unchanged ISO files and 3,558 untouched bank resources.
The executable, 609 dialogue entries, naming controls and other 0.1.6 translations
are unchanged. Other UI and gameplay were not retested for this artwork update.
The user's running emulator was not changed.

SHA-256: `2fc3a68cfa36c88c06f83fd0449a64c6e20f44a609aa7de61f5aa590af145ca8`. Size: 1,658,763,264 bytes.
Restart from the title screen when switching ISO; an old emulator save state may
retain the prior loaded textures. This remains a partial translation.
