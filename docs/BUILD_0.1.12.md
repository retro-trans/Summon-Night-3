# Build 0.1.12 — three chapter story translation candidate

This candidate extends the reviewed English story text through the opening,
Chapter 2, and Chapter 3. It covers **6,174** story fragments: 1,428 in the
opening script, 1,711 in Chapter 2, 2,319 in Chapter 3, and 716 fragments in
18 chapter-specific night-talk resources. This adds 5,533 story fragments to
the 0.1.11 build selection.

ISO: `work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso`

Size: 1,659,627,520 bytes.

SHA-256: `ed929381d11623ec30d144cc4846dc3db2a0e764cdbc15135b26ce7a537bd075`.

## Scope and validation

- No scoped story rows are excluded. The opening script, both chapter-main
  unique tails, and all 18 selected night-talk resources have accepted meaning
  review records.
- Twenty chapter/compiler static validations pass. They preserve source pools,
  earlier translations, branches, direct menus, conditional rows, control
  tokens, relocation data, and simulated dialogue groups.
- The shared UI/library prefix and later chapters are outside this build's story
  scope. This is not a claim that all game dialogue or all interface text is
  translated.
- Earlier UI changes, artwork, audio, and their original resources are retained.
- Build verification checked all 23 archive indexes, preserved 33 unrelated ISO
  files and 4,391 resources in the changed banks, and validated all 276 bound
  build inputs. The final target audit is in
  `docs/chapters_coverage_audit_0.1.12.json`.
- Runtime pupil-name substitution and the new cast's backlog labels use English.
  Meaning corrections precede glossary normalization, including Phlaiz's
  introduction as advisor to the Guardian Lord Falzen.

## QA status and limits

Bounded final-ISO QA passed fresh boot, translated name entry, the exact loaded
Chapter 1 script hash, and fully rendered English harbor dialogue. See
`RUNTIME_QA_0.1.12.md` for traces and the actual screenshot.

The cabin checkpoint, Chapters 2–3, night conversations, alternate branches,
and save/load were not played through in this test. These remain statically
checked; this candidate must not be described as runtime-complete.

Some portrait nameplates for newly introduced characters may still be Japanese.
This release does not translate all UI, graphics, or later-game text.

Next unused version: **0.1.13**.
