# Release 0.1.54: remaining story translation

Public test release for NPJH50380; full-route and hardware stability are not established.

## Scope

- 43,668 new story fragments, 134 accepted script resources.
- 71,356 translated occurrences including shared dialogue.
- 34,031 dialogue groups / 38,683 pages.
- Largest decoded script: 489,972 bytes, below the compiler's 0x78000 ceiling.
  This static bound does not establish runtime allocation safety for every route.
- Teacher terminology update from the local v0.1.53 build is included.
- Original-to-current and published v0.1.52-to-current patches only.

## Candidate identity and verification

- Output size: 1,676,941,312 bytes.
- SHA-256: `cdf3899bb3aeec87e03cc979b203c56edcbcd1b270036397dfdd37b00488b8c5`.
- Built on immutable v0.1.53; only selected 00.DAT story entries changed.
  All other ISO file contents and untouched entries of that bank match the baseline.
- 13 story/compiler/storage/display/conditional-layout regression tests pass.
- All 134 script compiles, exact source/control bindings, and simulated dialogue
  calls pass. The source-review audit covers all 43,668 new rows.
- No empty complete new dialogue boxes or misplaced music markers in the final scan.
- All 12 cumulative stability audit groups pass on the actual ISO.
- Fresh boot: PPSSPP 1.20.4, JIT, software rendering, IgnoreBadMemAccess=False.
  Chapter 15 normal-save Continue, Brave Goals, Inventory with Black Rose Knife,
  and Summon Index with Dritol pass without a memory fault.
- Screenshots pause intentionally at the display import. Those debugger stops
  are not game crashes.
- Both release patches round-trip through the Retro Trans engine to the exact
  complete target image.

## Limits

This completes the scoped remaining-story translation pass, not every Japanese
string or graphic in the game. Some names/lore spellings remain provisional.
The Extra Brave Goal mystery row still overflows; Japanese Summon Index
descriptions remain visible. Full routes, individual new-script heap allocation,
early-chapter/Night Talk gameplay, puppet shop, room skills, Cooking and
save/reload are not verified in this exact candidate. No mobile or original-PSP
compatibility claim is made.

The test release passes the four required smoke tests. The stable-release
coverage requirement is not met.

## Evidence and provenance

- `work/translation/en/story_0.1.54/translation_audit_final_story_20261001.json`
- `work/translation/en/story_0.1.54/current_compiler_revalidation_20261001.json`
- `work/ui/story_0.1.54/runtime-validation.json`
- `work/ui/story_0.1.54/stability-report.json`
- `work/ui/story_0.1.54/runtime/`

The versioned source includes English translations, source identities and brief
review notes; no full Japanese dialogue dump, private credential or user save.
Published manifests and earlier release assets are preserved. The only superseded
tool input is recorded with both historical/current hashes in the new build
summary, while the prior manifest and ISO remain unchanged.
