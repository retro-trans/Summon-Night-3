# Candidate 0.1.1: first translated dialogue

Tested 2026-09-26 with PPSSPP 1.20.4 and software rendering. This candidate
retains the three labels from `0.1.0` and adds three independently meaning-reviewed
opening lines. It is a partial technical candidate, not a complete translation.

ISO: `work/output/0.1.1/Summon_Night_3_EN_0.1.1.iso`

SHA-256: `3f41c344db3352decee68c6cec17695c20a0079e7bcf0079819f2f465ab5174f`

## Passed

- Static reconstruction checks pass for all 23 bank indexes, 2,312 character
  references, 34 untouched ISO files, and 1,452 untouched bank resources.
- Main story resource `00:00065` was relocated and re-encoded. Its decoded size
  increases from 182,526 to 182,592 bytes; all original string-pool bytes and
  instruction boundaries remain. The ISO is 4,096 bytes larger than the source.
- Clean launch reaches title, new game, protagonist/name selection, and the
  opening dream. The three English lines display in sequence with working
  advance prompts. Actual captures were inspected for complete text and clipping.
- All 182,592 decoded script bytes match live memory at `0x08d8a000`, including
  the new references and two-byte terminators. The processed display structure
  contains all 14 glyphs of the third line, with no control-token entries.

| Target | Original bytes | New display bytes | Actual capture |
| --- | ---: | ---: | --- |
| `...waken.` | 12 | 18 | `work/ui/0.1.1_dialogue_01.png` |
| `Huh...?` | 10 | 14 | `work/ui/0.1.1_dialogue_02.png` |
| `Now, awaken...` | 24 | 28 | `work/ui/0.1.1_dialogue_03.png` |

All three exceed their original string allocation. They are stored at newly
appended offsets 182,526, 182,546, and 182,562. This proves a bounded expansion
within the existing main-script region; it does not prove enough memory for
every complete translated chapter.

## Encoding and layout findings

The original dialogue processor advances in two-byte CP932 units. It cannot
consume ordinary ASCII target bytes directly. `dialogue_encoding.py` preserves
readable ordinary English in target JSON and converts build output to existing
full-width Latin glyphs. It preserves the game's special token characters and
rejects punctuation that would accidentally turn into a control token.

The game displays the expected letters with wide spacing. This is an initial
working rendering path. Proportional Latin layout, wrapping, nearly full boxes,
and complete glyph coverage remain to be addressed. No English line was shortened
to fit its original byte length. The longest verified pilot line has 14 display
units; this is not a maximum capacity claim.

The renderer reads a 16-bit terminator. Relocation now adds aligned zero padding
after the last appended string as well as between strings, preventing a read
past a one-byte terminator into stale memory.

## Evidence and reproduction

- Build-time record: `work/output/0.1.1/manifest.json`.
- Fresh complete-script comparison: `work/output/0.1.1/script_runtime_validation.json`.
- Screens and observed glyph bounds: `work/ui/screens_0.1.1.json`.
- Draft slice: `work/translation/en/opening_000.targets.json`.
- Independent review: `work/translation/en/opening_000.meaning_review.json`.
- Exact build selection: `work/translation/en/opening_pilot.targets.json`.

Launch the candidate with the workspace launcher and `-Software`. Skip the
movie, wait for the title, press Start, select New Game and Normal, then wait
for protagonist selection to finish loading. Select Rexx, accept Machine affinity,
press Start in name entry, choose Yes with Up, and confirm. Circle advances each
opening line. Do not send the entire setup sequence before transitions finish;
inputs during loading can be ignored.

The current hidden test process is recorded in `work/scratch/ppsspp_session.json`.
It was left CPU-stepping on the third translated line, with no capture breakpoint
remaining. Revalidate liveness/state and resume explicitly before sending input.

## Remaining acceptance work

This test covers three centered single-line displays on one opening route.
Ordinary multi-line dialogue boxes, runtime substitutions, choices/branch results,
save/load, scene transitions, battle/status UI, all label consumers, and real PSP
hardware remain unverified. The default player name and most UI remain Japanese.
The builder's current script profile is limited to the mapped opening main-script
resource; additional loader regions and larger allocations still need support.

The translator and independent reviewer each examined 132 rows for an 80-row
slice. There are 79 English drafts with no required meaning corrections, plus one
unresolved boundary row. The reviewer supplied a coordinated two-row completion
proposal; it remains unapplied until both sides are integrated together. Voice
cut-ins, an unusual inheritance reference, and optional-choice tone are explicitly
flagged for later context/voice review. This is not final translation acceptance.
