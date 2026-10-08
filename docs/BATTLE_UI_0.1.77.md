# Battle headings and skill alignment — 0.1.77 local test

This build translates **VS Phantom Warriors** and the remaining optional-battle
headings in the same encounter-card family. It covers 29 native title sprites
with 15 distinct labels, including Rogue Summon Beasts reused from the already
translated encounter artwork. Victory and defeat conditions were already English
and remain byte-identical.

Blade Awakening, Blade Awakening+ and Berserk Blade use the normal left alignment
in skill lists. The centered text path is restricted to the original animation
banner context, retaining its exact-name matching and allocation limits.

The reported crafting popup and its related notices are included in English:
“Equip the crafted stone?”, “Stone equipped.”, “Choose a Summonite Stone.” and
“Change equipment?”. Their existing translations from 0.1.75 are verified through
the live executable references, including Yes/No rows and empty-row termination.

The new lettering was created with the built-in imagegen tool as a transparent
atlas matching the original beveled fantasy lettering. Its prompt and saved asset
are under `work/ui/battle_0.1.77/`. Import only crops, resizes and quantizes the
generated lettering to each original texture's native size and palette.

Validation includes 16 routing cases at two load addresses, all 29 sprite imports,
four related crafting prompt groups, 14 inherited stability checks, and eight
reviewed screenshots from a fresh boot and normal in-game save. Aty's skill list
is aligned; Yard's All-Purpose Pot with the white Neutral stone completes naming
and equipment without a crash. Audio was enabled and only one emulator ran.

Optional-battle title variants were reviewed as decoded native sprites; those
battles were not played through. Banner routing was checked by bounded execution,
without capturing its animation. This is targeted validation, not a full
playthrough or a test on the user's Linux emulator.

Apply the included **0.1.73 → 0.1.77** patch with Retro Trans Tools to the published
0.1.73 ISO. Local 0.1.74–0.1.76 builds are included in this upgrade. The original
ISO and private saves are not distributed. This package is a local test build,
not a new published release.
