# Version 0.1.15 — reported menu gaps

The user confirmed that the screenshots were taken from 0.1.14. These gaps
were separate executable literals and menu textures that the earlier battle
translation did not replace.

## Included changes

- Backlog top-right voice action: Replay (compact form of Replay Voice).
- Attack styles: V. Slash, H. Slash, Thrust, Strike, Fire, Throw, Special,
  V. Throw and H. Throw. The Japanese label beneath Aty was an attack style,
  rather than the equipped weapon's name.
- Battle preparation menu: Battle Prep, Deployment, Battle Info, Inventory,
  Summon Index, Options, Save, Load and Start Battle. Related Party Abilities
  buttons are also included. All ten designs have selected/unselected artwork.
- All descriptions belonging to those commands, including deployment/status/
  equipment, victory/defeat conditions and summon combination information.

The chapter dialogue is inherited unchanged from 0.1.14. This update does not
claim completion of every interface screen or every equipment name in the game.

## Implementation and checks

Twenty-one English strings occupy nineteen relocated bundles; two strings are
continuations of their preceding descriptions. Only relocation-backed source
references are changed. The backlog index originally began three bytes before
the actual text; this update targets the proven literal start and preserves
the preceding binary bytes.

The native description getter at module address 0x67da8 reaches the setter
0x632a0 and copier 0x649dc..0x64a34. It walks up to three NUL-terminated U16
lines into a 174-byte buffer. The build simulates that exact line traversal,
compares every resulting line with its English target, and checks buffer size.
Explicit wrapping limits help lines to 30 characters without omitting text.
This is a conservative layout bound, not a substitute for an in-game capture.

Independent meaning review was completed by the ui015_meaning_review agent.
Attack-style abbreviations preserve the vertical/horizontal distinction.
No character names or player-entered names change.

Twenty native sprites replace 75 identical occurrences in ten 02.DAT packs.
Every original native sprite round-trips through the encoder before replacement;
the original dimensions, alpha shape and palettes are retained. The build checks
all archive indexes and compares unrelated files/resources with 0.1.14.
Historical input hashes are verified before packaging.

Final packaging passed: 4,405 unrelated resources in the rebuilt banks remain
identical, all 23 archive indexes validate, and unchanged ISO files match
0.1.14. Final ISO SHA-256:
`bc064be79e7e9f874927e9708b3d24b43088085843ff7dedc6bf9ebd878efe6b`.

## Artwork provenance

Generated with the built-in ImageGen tool, then mechanically cropped, resized
and converted into native game textures. No text rectangles were painted over
the original Japanese labels.

- Final generated atlas: [buttons_atlas.png](../work/ui/menu_0.1.15/buttons_atlas.png)
- Final prompt set: [prompt.json](../work/ui/menu_0.1.15/prompt.json)
- Converted sprites and import report: `work/ui/menu_0.1.15/native/`
- Original sprite exports: `work/ui/menu_0.1.15/source/`
- Final text/layout inputs: `work/translation/en/menu_0.1.15/text.layout.targets.json`
- Final layout report: `work/translation/en/menu_0.1.15/text.layout.report.json`

The earlier text.targets.json/text.report.json in that folder record the initial
unwrapped draft; the layout versions and current builder supersede them.

## Runtime verification limits

An earlier 0.1.15 candidate booted in an isolated PPSSPP instance, and all
nineteen new text bundles matched live memory. Captures showed the opening
movie/background, not the actual battle menu. An unchanged 0.1.14 comparison
had the same capture/navigation problem. Those captures are diagnostic evidence
only; they are not proof of battle-menu appearance. The final description
wrapping revision has static checks but no live-menu verification.

The user's emulator, original saves and earlier ISOs were not modified.
Open the new ISO from a fresh boot and load an in-game save. An older PPSSPP
save state may retain old executable data and scripts.
