# Release 0.1.55: remaining battle-event translation

Public test release for Summon Night 3 PSP, Japanese NPJH50380.

## Changes

- Translate and independently review all 642 remaining indexed battle-event
  fragments in 27 scripts, forming 284 dialogue groups and 329 generated pages.
- Correct tactical timing, ambiguous references and character terminology after
  source review; keep documented uncertainty and intentionally unfinished speech.
- Preserve native speaker operands and a verified blank-line display sequence
  while relocating and wrapping the new English.
- Include all v0.1.54 story translations and earlier interface/crash-guard fixes.
- Refresh the translator Sheet with the 642 accepted English fragments, preserving
  Proposed English and review fields.

## Candidate identity

- Size: 1,676,998,656 bytes.
- SHA-256: `d75654f7d9381293b8b78e8e7ddd8766bd2c518e9da05a8a7983205abd04bfe9`.
- Built on published v0.1.54. Only 27 nested battle scripts and the corresponding
  archive index changed; all 31,742 untouched archive entries and other ISO file
  contents match the previous build. The executable is unchanged.
- Largest new decoded battle script: 6,796 bytes.

## Validation

- All 27 scripts pass source/review hash binding, control-token and encoding
  checks, simulated speaker/stack/event flow and 208-pixel/three-line page limits.
- Eight negative review/input checks and 13 existing story regression tests pass.
- The actual ISO passes all 12 cumulative stability audit groups using
  `verify_stability_052.py`. An initial invocation of the obsolete base audit
  rejected already-released Cooking/guard changes; the current audit handles
  those changes and passed without altering the candidate.

- Fresh-boot PPSSPP 1.20.4, JIT, software rendering and strict memory handling
  pass Chapter 15 Continue, Brave Goals, Inventory/Black Rose Knife and Summon
  Index/Dritol. No memory fault appears in the log. Display-import debugger pauses
  are intentional screenshots, not crashes.
- Both published patches pass full round-trip verification. All nine public assets
  match the local package, and the public Retro Trans Automatic-mode v0.1.54
  upgrade produces the exact target image. See [public verification](RETRO_TRANS_0.1.55.md).

## Limits

This completes the indexed remaining battle-event translation scope, not every
Japanese string or graphic in the game. It is an AI-assisted translation awaiting
complete human proofreading. Some names and lore terms remain provisional.

Full-route playthroughs, individual new battle-event runtime allocations, mobile
and original-PSP compatibility are not established. The known Extra Brave Goal
mystery row overflows; some Summon Index descriptions remain Japanese.

Use a fresh boot and a normal in-game save. Emulator save states retain old code
and resources. Only clean-source-to-current and published-v0.1.54-to-current
xdelta patches belong to this release; complete game images and private saves
are excluded.

## Evidence

- `work/translation/en/battle_0.1.55/accepted.json`
- `work/ui/battle_0.1.55/runtime-validation.json`
- `work/ui/battle_0.1.55/stability-report.json`
- `work/ui/battle_0.1.55/runtime/`
- [Translation and Sheet checkpoint](BATTLE_TRANSLATION_0.1.55.md)
