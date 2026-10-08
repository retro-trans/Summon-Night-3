# Summon Night 3 English — v0.1.77

English translation test release for the Japanese PSP edition **NPJH50380**.
Includes the translations and fixes from local builds 0.1.74–0.1.77.
Translation and full-route testing remain incomplete.

## Apply

Use [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools):
refresh the catalog, choose Automatic and select your source ISO. Manual
Apply xdelta and DeltaPatcher also accept these patches. Keep checksum
verification enabled.

| Source image | Patch |
|---|---|
| Clean Japanese NPJH50380 | `SN3-English-v0.1.77.xdelta` |
| Published English v0.1.73 | `SN3-English-v0.1.73-to-v0.1.77.xdelta` |

Local intermediate builds are not sources for the upgrade patch; use the clean
Japanese image instead. No game image or private save is distributed.

**Start the updated ISO fresh and load an in-game save.** Emulator save states
retain the old executable and memory. Keep your existing saves backed up.

## Changes since v0.1.73

- Translate VS Phantom Warriors and the remaining optional-battle headings:
  29 native sprites covering 15 distinct labels. Preserve battle conditions.
- Align Blade Awakening and related labels with the other entries in skill lists
  while retaining centering for animation banners.
- Translate related crafting confirmations, including “Equip the crafted stone?”
  and its Yes/No choices. Preserve Yard's white-stone All-Purpose Pot crash repair.
- Fix corrupted question marks in Cooking descriptions and ingredient lists.
  Translate Party Abilities and summon-index help; fix the overlapping bottom
  stat and category labels. Preserve intentional undiscovered placeholders.
- Translate remaining unit/class labels, location labels, equipment notices,
  Meimei's menus, shop confirmations and minigame instructions and results.
- Translate all 38 Sound titles, related Gallery title fields, 229 Night Talk
  captions and 21 Ending captions, plus matching headings, buttons and nameplates.
- Resize and align Options labels and controls; repair Event Voices and Forecast
  help. Fit long purchase names and Gallery captions within their existing areas.
- Translate the title-screen Extra Story control and display default protagonist
  names in English while preserving player-entered names and stored save data.
- Retain earlier renderer safeguards, the Chapter 15 script-memory fix and
  numeric gameplay fields. Apply the current character-name and Teacher glossary.

## Validation and limits

The exact release ISO passes 14 cumulative regression groups and the new audit
of 16 skill/banner routing cases at two load bases, 29 title imports and four
crafting-message groups. All 3,310 build-input hashes are checked. Both patches
are decoded and verified against the complete target ISO hash with Retro Trans
Tools. Public catalog discovery and automatic upgrading are checked after
publication.

The final 0.1.77 runtime test fresh-boots PPSSPP 1.20.4 on Windows with audio
enabled, no save state and no runtime memory edits. From a normal Chapter 2 save,
Aty's skill list is aligned and Yard creates, names and equips a summon using
the All-Purpose Pot and white Neutral stone. The English crafting prompt fits,
and the battle menu remains responsive. Eight screenshots are recorded under
`work/ui/battle_0.1.77/battle077-final`. This run did not cast the new summon;
the earlier published 0.1.73 crash test included casting Random Hit.

Earlier local 0.1.74–0.1.76 tests checked the related Cooking, Party Abilities,
equipment, shop, minigame, Options and Gallery screens from normal saves.
Those checks are not a full final-ISO playthrough. Optional-battle headings are
reviewed as decoded native sprites; the corresponding battles were not played
through. Animation-banner routing is checked by bounded native-code execution;
no animation capture was made in the final run. Full routes and a Linux emulator
host remain untested. Some text and names remain provisional; player-entered and
auto-generated player-editable Japanese names are retained.

This is an **AI-assisted machine translation**, drafted and edited with large
language models under the maintainer's direction. It has not received complete
human Japanese-to-English proofreading.

GitHub's Source code downloads contain tools, English targets and review records,
not playable game images. Builders require locally supplied original media and
historical intermediate outputs.

[Report issues](https://github.com/retro-trans/Summon-Night-3/issues) with the
patch version, emulator version, chapter, reproduction steps and screenshot.
State whether you used an in-game save or emulator save state.

Apply this free patch to your own copy. Do not sell the patch or prepatched images.
