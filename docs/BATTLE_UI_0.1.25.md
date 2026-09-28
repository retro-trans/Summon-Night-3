# Battle UI translation 0.1.25

Based on the immutable 0.1.24 release. This update covers the user's four
battle/tutorial screenshots.

## Text and artwork

- Seven unit commands: Move, Attack, Summon, Special, Items, Swap Weapon, Stance.
  These are native 64×16 word textures in 01.DAT, resource 105, children 3–9.
  Their button backgrounds and all other children remain unchanged.
- Tutorial “Next”: the 40×20 word capsule at (247,177) in 02.DAT resource
  3889, child 1. Every pixel outside that rectangle is unchanged, including
  the separately drawn controller icon.
- Tutorial notice: “Tutorials: see Gallery.” The relocated executable string
  retains the empty-line terminator required by this message reader.
- Shine Saber help: “Chaos-rending light blade / Ancient hero dead; aglow.”
  The full meaning draft is retained in the translation review. The two lines
  fit the native 54-object help pool and the narrower visible line area.

The description is stored in 02.DAT resource 3, child 12, record 84, slot 12;
its resident copy in 00.DAT resource 44, child 7 is updated identically.
No published translation input is rewritten.

## Artwork provenance

English word artwork was generated with the built-in image tool and saved as
`work/ui/battle_ui_0.1.25/buttons_generated.png`. The importer extracts the
lettering, scales it to the existing sprite dimensions and maps it to the
original native palette. `native_preview.png` contains the imported pixels.
`next_generated.png` is the generated edit of the source atlas; only the
specified capsule rectangle is imported from it.
The command lettering is proportional artwork; existing dynamic menu VWF is
inherited from earlier releases.

## Validation status

Scratch runtime tests use PPSSPP 1.20.4 with software rendering, a fresh launch
and a copied in-game save. No save state is used. The command menu and Gallery
notice have been checked in the first pirate battle. An earlier long notice
failed during testing; the shorter notice passed through to player control.
Its original failure cause has not been established.

The Gallery notice retains its original fixed character spacing. Its reader
uses a different object layout from the existing menu VWF hooks; no unverified
font hook is added. The summon help continues to use the inherited menu VWF.

Final release evidence is recorded in the published manifest's
`battle_ui025_runtime` section. Runtime coverage is the first pirate battle,
not a complete playthrough.
