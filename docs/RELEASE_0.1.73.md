# Summon Night 3 English — v0.1.73

English translation test release for the Japanese PSP edition **NPJH50380**.
Includes the translations and fixes from local builds 0.1.66–0.1.70 and the
final 0.1.73 summon-record repair. Translation and full-route testing remain
incomplete.

## Apply

Use [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools):
refresh the catalog, choose Automatic and select your source ISO. Manual
Apply xdelta and DeltaPatcher also accept these patches. Keep checksum
verification enabled.

| Source image | Patch |
|---|---|
| Clean Japanese NPJH50380 | `SN3-English-v0.1.73.xdelta` |
| Published English v0.1.65 | `SN3-English-v0.1.65-to-v0.1.73.xdelta` |

Only these two xdelta patches are supplied. Local intermediate builds are
not sources for the upgrade patch; use the clean Japanese image instead.
No game image or private save is distributed.

**Start the updated ISO fresh and load an in-game save.** Emulator save
states retain the old executable and damaged memory. The fix handles the
invalid cached bindings reproduced in the supplied normal save.

## Changes since v0.1.65

- Fix Yard's All-Purpose Pot crash with the white Neutral Summonite Stone.
  Bound the native cached-name copies, retain full display names separately
  and clear invalid saved accessory bindings while preserving valid IDs.
- Translate R's name and the shared Summon Friend class; align SELECT / Give
  Food and restore the SELECT / Learn Skills hint on the Status screen.
- Translate 601 remaining summon-profile, skill, support and mastery fields,
  plus 24 map labels, including Rocky Shore and the Endless Halls labels.
- Translate 191 remaining summon spell name fields and 333 item, stone,
  fishing and gallery-reward fields. Include Tamahipo's breath names and
  numbered art rewards. Use measured short forms where space requires them.
- Translate crafting help, dismissal and completion confirmations, favorite
  actions and eligibility messages; preserve button tokens and placeholders.
- Translate the remaining equipment/transformation help fragments and the
  framed startup notice. Preserve original artwork and publisher logos.
- Preserve custom player names, costs, effects, statistics, undiscovered
  question marks and the previous Chapter 15 script-memory fix.

## Validation and limits

The exact release ISO passes 15 cumulative regression groups and 1,220
native cached-name, initialization and saved-record cases at two load bases.
Both patches are decoded and checked against the full target ISO hash using
Retro Trans Tools. Public catalog discovery and the upgrade route are checked
after publication.

The final crash test fresh-boots PPSSPP 1.20.4 on Windows with JIT and audio
enabled, bad-memory suppression disabled, and no runtime memory edits or
old save state. From the supplied normal Chapter 2 save, Yard creates, names
and equips the white-stone summon, casts Random Hit and returns to another
unit's menu. Screenshots and a summary are recorded under
`work/ui/release_0.1.73` and `work/ui/pot_0.1.73/pot073-final`.

The earlier local translation passes also checked a normal Chapter 15 save,
Picolit's and Takeshi's profiles, Tamahipo's spell names, the combination list
and the English startup notice. These earlier checks are not a full final-ISO
playthrough. The reported Linux host is not directly tested. Full routes,
Night Talk, puppet shop, Cooking, room skills and save/reload are not
exhaustively tested. Some text and names remain provisional; player-entered
Japanese names are retained. A long Extra Brave Goal list label still clips.

This is an **AI-assisted machine translation**, drafted and edited with large
language models under the maintainer's direction. It has not received complete
human Japanese-to-English proofreading.

GitHub's Source code downloads contain tools, English targets and review
records, not playable game images. Incremental builders require locally
supplied original media and historical intermediate outputs.

[Report issues](https://github.com/retro-trans/Summon-Night-3/issues) with the
patch version, emulator version, chapter, reproduction steps and screenshot.
State whether you used an in-game save or emulator save state.

Apply this free patch to your own copy. Do not sell the patch or prepatched images.
