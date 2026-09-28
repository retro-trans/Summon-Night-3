# Night Talk — 0.1.37 test build

The pictured Belfraw scene is resource `00:00091`, group `chapter_91_18_19`.
Its English text was already translated, but the previous compiler used a
208-pixel, three-line dialogue profile for a box that displays two lines.
The separate Night Talk name graphic was still Japanese.

## Changes

- Identify Night Talk from the actual VM display-helper bodies: helpers 2100
  and 2114 pass native display modes 4 and 5 to function `0x3052`.
  Every selected helper is checked against this signature and hashed.
- Reflow 1,348 translated groups across 76 resource files from the existing
  Chapter 2–8 inputs into 1,594 pages, at most two lines each. Use a 368-pixel
  width while retaining the native 31 expanded-cell limit per line. The current
  proportional Latin renderer is unchanged. Encoding remains the required
  two-byte game format; that does not mean fixed-width visual spacing.
- Preserve the entire text, name/control tokens, speaker arguments and original
  continuation. Apply the current name glossary to these new build inputs.
- Translate the 19 blue Night Talk name sprites in resources 02:01028–01046,
  child 3: Nup, Belfraw, Alieze, Will, Ardylia, Kyuuma, Falzen, Fariel, Yafha,
  Kyle, Sonolar, Scarrel, Yard, Kunon, Misumi, Subaru, Phlaiz, Marurur and Azlier.
  Preserve each portrait/expression child and the native 120×24 geometry/palette.

The screenshot's line becomes:

> Honestly, volunteering to join
> pirates is utterly outrageous!

## Verification

The incremental compiler checks the current decoded script hashes against the
0.1.36 manifest before changing anything. It simulates every changed group's
pages and compares untouched groups before/after. All control destinations,
line widths, expanded-cell limits, exact text reconstruction, original pool,
unrelated code, compression round trips and the 0x78000 allocation limit pass.
The largest changed decoded resource is 20,914 bytes.

The rebuilt ISO verifies all file extents, all 23 archive indexes, both resident
cache copies, every changed resource and 5,634 untouched bank resources.
All 19 imported names were inspected after native palette quantization.
The executable is byte-identical to 0.1.36. Historical manifest-bound inputs
remain unchanged.

A fresh boot of the actual test ISO reached the title screen successfully.
Final ISO re-read verified all 1,348 changed dialogue groups against the audit.
Runtime Night Talk verification remains pending a save at the scene. The copied
in-game save is still at the first battle and its Night Talk Gallery is locked.
A separate disposable harness that substituted the scene at New Game lacked
normal scene initialization and did not provide usable rendering evidence.
That substitution is absent from the test build. Do not treat the static checks
or name sprite preview as a completed Night Talk playthrough test.

This change reflows translated Night Talk in the existing coverage; it does not
claim a complete translation of later chapters, ending name variants, or all
Gallery menus. No new public release has been published yet.

## Files and reproduction

- `work/output/0.1.37/Summon_Night_3_EN_0.1.37.iso`
- `work/output/0.1.37/manifest.json`
- `work/translation/en/night_talk_0.1.37/layout.json`: English groups, classification,
  source hashes, page boundaries, sizes and verification records.
- `work/translation/en/night_talk_0.1.37/name_art.json`: exact built-in imagegen
  prompts, glossary reference, generated asset and native import method.
- `work/ui/night_talk_0.1.37/names_contact.jpg`: imported sprite preview.
- `tools/night_talk_037.py`: rebuild the English layout audit.
- `tools/build_night_037.py --write --destination work/scratch/night_rebuild037`:
  rebuild from immutable 0.1.36 into a new directory.

ISO SHA-256: `cc93bf9099a50a7fed9ad0773167fac38cfecebf0128790c96d96826555f102e`.
