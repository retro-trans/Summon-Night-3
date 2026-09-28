# Version 0.1.16 — status, battle submenus, inventory and options

This build addresses the six reported screens and carries forward the
Chapter 1–8 dialogue and previous interface changes from 0.1.15.

## Changes

- Deployment/status controls and related help text, including status/equipment,
  unit cycling, feeding and skill commands.
- Fixed the garbled Family Teacher class: the earlier ASCII label was read
  by a two-byte consumer. All six class references now point to the reviewed
  compact label **Tutor**. Player-entered names are unchanged.
- Support skill names and descriptions, including **Search for ingredients.**
- The visible weapons: **Novice Sword** and **Baygnart**.
- The visible summon: **Dritol**, with a complete two-line compact description:
  “Large-drill land developer.” / “Built for long polar work.”
- Battle Info submenu buttons and related menu variants, including selected
  and alternate unselected states. Win/Lose retains both outcomes.
- Options title, labels, selection states, footer controls and descriptions.
- Summon Index background title and Affinity label; compact L/R Affinity hint.
- Defeat conditions shortened to **Protagonist KO** and **All allies KO** to
  avoid overflowing their native box.

Baygnart and Dritol are provisional transliterations, not claimed official
English spellings. The source references and decisions are in
[the glossary](../work/glossary/menu_0.1.16.json). This release translates the
two shown weapons and one shown summon, not every entry in those databases.

## Checks and limits

- Independent meaning review, including the compact labels and descriptions.
- 24 newly relocated executable strings; two corrected existing conditions.
- 17 new shared-table strings including the summon description continuation.
- 46 imported native sprites, 89 resource replacements across 20 art packs.
- All 23 bank indexes validate. Cached static tables match their bank copies;
  all five character-table children match, allowing zero-filled bank padding.
- 843 versioned input hashes verified. All 32 unrelated ISO files and 5,707
  unrelated resources in the rebuilt banks match 0.1.15.
- Native converted artwork inspected for text and cropping. Full battle-menu
  appearance and every menu state still require in-game visual testing.
- Isolated fresh boot passed: 24 new strings, two corrected conditions and all
  19 inherited menu bundles matched live executable memory (45 checks).
  [Fresh-boot evidence](../work/ui/menu_0.1.16/runtime/fresh_boot.json).

The tiny Japanese affinity symbols and text inside illustrative Options
thumbnails remain. Other summon-detail subpanels and unreported database
entries are outside this patch. Do not interpret the translated Summon Index
heading as completion of the entire summon database.

## Fresh launch required

Read-only inspection of the user's running session found none of the nineteen
0.1.15 executable text bundles, nor the 161 inherited 0.1.13/14 bundles, in
their expected loaded locations. Backlog call sites matched the older cache
calls rather than the later layout hook, and attack text still used an
original pointer. This is evidence of old executable state, consistent with
restoring an older PPSSPP save state. It can coexist with newer translated
resource files. The exact cause of that old state is not proven.

Stop emulation, open the 0.1.16 ISO, and load a normal in-game save. Restoring
an older PPSSPP save state can restore the old code and text again. The user's
emulator state and saves were not modified during these checks.

## Artwork and reproducibility

Artwork was generated or edited with **built-in ImageGen**, then cropped,
resized, matted and converted to the native dimensions and palette. Final
project assets:

- [Button atlas](../work/ui/menu_0.1.16/buttons_final.png)
- [Options labels](../work/ui/menu_0.1.16/labels_atlas.png)
- [Options frame](../work/ui/menu_0.1.16/options_frame.png)
- [Summon Index background](../work/ui/menu_0.1.16/summon_index.png)
- [Final prompt set](../work/ui/menu_0.1.16/prompts.final.json)
- [Native import report](../work/ui/menu_0.1.16/native_release/report.json)
- [Final text report](../work/translation/en/menu_0.1.16/insertion.final.report.json)

Earlier native/native_final exports and insertion.report.json are drafts.
The native_release exports and insertion.final.report.json identify the final
imports. The final meaning review's requested Affinity abbreviation was applied
after its code snapshot; both full and compact forms were approved.

ISO SHA-256: `8a3c96b25ca5f99be4ea49ee76e7e4fc464c32a88d31dd073b1c14948fe7364e`.
