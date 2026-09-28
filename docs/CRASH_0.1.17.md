# Battle Prep crash — 0.1.17

The user reports that confirming Battle Prep on the first ship battle crashes
0.1.16, while the Japanese version opens the menu. The user explicitly confirmed
a fresh launch followed by loading an in-game save. This is a patch defect;
an old save state is not the explanation for this report.

## Cause and correction

The native help widget binds a pool of **54** glyph objects at module address
0x63d94: the call at 0x63da0 passes a2=0x36 in its delay slot at 0x63da4.
The loop at 0x64bf0..0x64cc4 selects a glyph object with a 0xe0-byte stride
and increments the count without checking that capacity.

The 0.1.15 Deployment description, inherited by 0.1.16, renders 56 glyphs.
Party Abilities renders 58. Both exceed the allocation. The previous build
checked the 174-byte text staging buffer and line widths, but missed this
separate glyph-object limit. Merely relocating text to more bytes cannot
increase the renderer's object allocation.

The crash screenshot reports PC 0x089da6b8 during the menu matrix-transform
path. Those instructions are identical in the original and translated builds.
Overwriting adjacent rendering objects explains a subsequent failure there;
this causal path is supported by binary inspection, but still awaits a live
before/after trace of this exact battle transition.

The reviewed replacement descriptions are:

- Deployment: “Select units for battle.” / “View status; change gear.”
- Party Abilities: “View Party Abilities;” / “choose abilities for battle.”

Each uses 49 glyphs total and fits on two lines. No menu function is omitted.
Two related status strings and the cursor-direction help are also made to fit
their native line storage. The status hint with a single-line consumer remains
single-line; it is not incorrectly split with an embedded terminator.

## Verification

- Both original overflowing descriptions fail the new capacity check.
- All 19 audited native help groups pass the 54-object limit, 29-cell per-line
  storage limit, at most three lines, and the 174-byte staging limit.
- Every changed group round-trips through its actual two-byte encoding and
  native NUL-delimited line traversal.
- Only five existing, relocated English allocations change: 129 ELF bytes.
  Executable size, instructions, pointers, sections and relocations are unchanged.
- All other ISO files, including all 23 resource banks, are byte-identical
  to 0.1.16. Earlier published inputs remain unchanged.
- Independent meaning review: [review](../work/translation/en/menu_0.1.17/meaning_review.json).
- Build and regression details: [hotfix report](../work/output/0.1.17/hotfix.report.json).

The user offered to navigate to the battle for live testing. The exact
before/after in-game result is pending; do not describe this build as
playthrough-verified. The isolated hidden emulator's title/movie captures are
diagnostic only. User save files were copied for testing, not overwritten.

ISO: `work/output/0.1.17/Summon_Night_3_EN_0.1.17.iso`

SHA-256: `71b6bd5e51199c9fd7663a9b377f4429d0ecb38383b1f5f90fe2efe8578971af`.
