# Candidate 0.1.2: wrapped dialogue and a translated choice

Tested 2026-09-26 with PPSSPP 1.20.4 and software rendering. This partial
candidate contains the existing three labels and 78 reviewed opening rows,
including three conditional choice labels. Most game text remains untranslated.

ISO: `work/output/0.1.2/Summon_Night_3_EN_0.1.2.iso`

SHA-256: `924304f8ec1f951d23ec2880ec1428cc23e9d1b8f281d0df61effc75a6ea5bd2`

## Passed checks

- Static rebuild verification covers all 23 bank indexes, 2,312 character
  references, 34 untouched ISO files, and 1,452 untouched bank resources.
- Fifteen complete dialogue groups use wrapping and pagination, with 13 added
  pages across the included alternatives. Every target word is preserved.
  Compiler checks verify original helper arguments, balanced stacks, original
  continuations, unchanged choice branches, and ten unsafe-input rejections.
  Compression round-trip passes.
- Clean launch reaches title, character setup, the opening dream, and beach.
  Default executable player-name text remains Japanese.
- All 187,702 bytes of the expanded decoded script match live memory. Logical
  strings, physical fragments, references, and two-byte terminators pass checks.
- "Why am I lying flat on my back on this beach?" displays completely across
  two pages. The first page has 8/13/10 processed cells; the continuation has 11.
  Both screenshots show complete letters and an unobstructed advance icon.
- The first choice displays "Let's see...", "About myself", and "Trivial things".
  "Recent events" is conditional and absent at this first visit, matching the
  original branch logic. The displayed selectable values are 0 and 2.
- After activating selection, record 1 had value 0 (About myself). Confirming it
  reaches group 40, the expected birthplace backstory. Its three pages are
  processed in order, followed by group 42.

Six saved traces contain 55 distinct physical target strings in processed cells.
Seven reflow groups were observed in full: 22, 24, 25, 31, 33, 34, and 40.
Group 42 was observed only on its first page. Counting a reflowed logical row
only after every fragment of its group was seen gives **35 logical rows with
complete processed-cell evidence**. This is not individual screenshot coverage.

## Evidence

| Evidence | Location |
| --- | --- |
| Immutable build manifest | `work/output/0.1.2/manifest.json` |
| Compiler checks and sample pages | `docs/dialogue_layout_validation.json` |
| Complete live-script/first wrapped-page check | `work/output/0.1.2/script_runtime_validation.json` |
| Dream through first wrapped page | `work/output/0.1.2/to_wrapped_dialogue.json` |
| Second page of the beach sentence | `work/output/0.1.2/wrapped_continuation.json` |
| Continuing to the choice | `work/output/0.1.2/to_translated_choice.json`, `choice_arrival.json` |
| Selected branch and continuation | `work/output/0.1.2/choice_result.json`, `choice_branch_continuation.json` |
| Screenshots and exact visual scope | `work/ui/screens_0.1.2.json` |

The first choice-navigation trace reached its configured 20-press limit during
progress. A second bounded trace continued from that state and reached the
choice in two presses. The emulator was not restarted. At the initial choice
display, selection was not active: record 0 was the nonselectable prompt. A guard
prevented premature confirmation; one Circle activated selection, then another
separately checked Circle confirmed value 0.

## Remaining work

- Narrower Latin glyphs and better page composition: full-width lettering is
  readable but causes many short continuation pages.
- Runtime substitutions and control/timing tokens; the builder still rejects
  these until expansion and rendering are measured.
- In-game save/load, voice synchronization, other protagonist/dream branches,
  the other choices and their return paths, and the complete opening section.
- Visual checks for every translated page and label consumer. Group 40's
  screenshot covers its first page; all three pages have processed-cell checks.
- Larger chapter allocations, other loaders, executable/UI and image/video text,
  full glyph coverage, battle/status screens, and real hardware.

The broader insertion gate remains incomplete. The selection excludes the
cross-slice sentence beginning at row 78; integrate its pieces together. The
original 79 drafts and independent review are unchanged.

The emulator was left stepping with no breakpoints at group 42 page 0:
"Even though / it was in the / south, snow". Its process is recorded in
`work/scratch/ppsspp_session.json`; revalidate it before resuming.
