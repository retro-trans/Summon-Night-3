# Reported UI fixes — local 0.1.61

The existing translation of ジップトースト is **Zip Toast**. The screenshot
lost its last character in a glyph-widget path. This build switches exact
recognized English spell names in single-row glyph widgets to the existing
centered variable-width strip renderer. It uses one existing font object,
retains the 32-cell strip limit, forces a fresh binding after switching modes,
and restores the owner's row-index pointer and character limit after drawing.
The generic native renderer and unknown names retain their original behavior.

The imported Yard lettering changes only the pixels in the ordinary and battle
name layers. Both map packages receive the same Island Map heading. Original
palettes, texture descriptors and sprite dimensions are preserved. Built-in
image generation supplied the lettering; prompts are recorded in
`work/ui/report_0.1.61/imagegen.json` and palette previews in that folder.

The short location label **First Shore** represents はじまりの浜辺
(Shore of Beginnings). Its relocation-backed pointer now addresses appended
English text; the source pool is preserved. The exact map consumer and its
visual fit have not yet been verified in PPSSPP.

The five **Indirect Atk** variants use one complete help line, such as
`Range: Adj Up2 Dn2 Yokai`. Adj means an adjacent tile, Up2/Dn2 preserve the
two-level height range, and the element follows the project's terminology.
All original table fields outside the ten selected pointers remain unchanged.

## Verification

- The finished ISO passes all 14 regression groups, including inherited crash
  guards, all equipment and spell help formatters, skills, Cooking, summon
  hints and Level Up.
- Actual emitted MIPS runs in 420 wrapper and 84 binder cases at two relocation
  bases. Cases include known names, prefixes, extended names, empty/Japanese
  text and rejected widget shapes, with stack and callee-saved-register guards.
- The actual native whole-row binding loop takes the full-string path for
  Zip Toast and uses exactly one existing font object.
- 210 centered font-pixel tests verify bounds, cache handling and transparent
  tails. The new renderer's graphics body is tested at its ABI boundary;
  this is not a full emulator rendering simulation.
- All five new help blocks pass actual guarded native staging.
- Fresh-boot PPSSPP 1.20.4 loads the copied normal battle save. The Flame Knight
  Summon Index page shows the full Zip Toast label. No save state is used.
- Retro Trans Tools decodes the 0.1.55 upgrade to the exact candidate ISO hash.

The reported casting animation, map-label bubble and Yard scene still require
matching saves for visual verification. These checks do not constitute a full
playthrough or a claim that every game path is crash-free.

## Local test files

- ISO: `work/output/0.1.61/Summon_Night_3_EN_0.1.61.iso`
- Upgrade: `work/output/report-test-v0.1.61/SN3-English-v0.1.55-to-v0.1.61.xdelta`
- ISO SHA-256: `8ff88bd2008308f22ad95a005f4ce75531cc77a72d31569502585ae4c127c5a2`

This local test includes all changes from 0.1.56 through 0.1.60. The patch source
is the last published release, 0.1.55. No GitHub release is created in this pass.
