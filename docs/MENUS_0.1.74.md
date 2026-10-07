# Summon Night 3 English 0.1.74 — local test build

Apply `SN3-English-v0.1.73-to-v0.1.74.xdelta` to the published English
0.1.73 ISO using Retro Trans Tools. Start the patched game normally and
load an in-game save. Keep only one emulator instance running.

This is a local test upgrade; 0.1.73 remains the published release.

## Changes

- Translate the title-screen SELECT prompts as “Extra Story” and “Main Story.”
  Fit both labels inside the existing footer.
- Translate Marurur and the Flower Fairy class, plus related fairy class names.
  Preserve player-entered names and the current character-name reference.
- Translate all 29 Party Ability names and descriptions, and all 29 related
  food effect descriptions. Keep healing, status, costs and other numbers.
  Use compact party labels that clear the ON/OFF controls. Translate all
  five native Hero Tales volume names and their six EXP-help variants.
- Restore the existing English recipe descriptions in Cooking. The repair
  covers the complete table and retains the six-line recipe layout.
- Translate both native copies of the Unit Form help as
  “Deploy using Unit Summon.”
- Restore the native spacing for symbolic stat descriptions on Summon Index
  pages, including Crystal Spirit. Preserve ordinary English proportional text.
- Retain the 0.1.73 Yard / white Neutral stone All-Purpose Pot crash repair.
- Refuse to start another QA emulator while any PPSSPP instance is running.

## Cooking fault and repair

The cooking question marks were reproduced in 0.1.73 after a fresh start and
normal in-game save load. The recipe descriptor pointed into the expanded
resident tables, where the room's event-script data had overwritten its text.
The font guard correctly rejected the script bytes as invalid characters.
The issue was not recipe discovery or a save-state-only problem.

Protect the overlapping tail of the static resource, children 37 through 48,
in a 77,824-byte buffer owned by the executable loader. Copy this region
before the unchanged native initialization. Redirect its twelve child
lookups into the copy; retain the native child-size results, table binding,
pointer relocation, recipe renderer, numeric records and original pools.
The remaining static tables and the event-script arena keep their existing
locations. This avoids allocating a second complete static resource.

## Validation

- Validate every new field: 87 table strings, eight name/class labels and
  15 native text records, including the branch-specific Unit Form copy.
- Execute 198 stat-dispatch cases at two load bases. Retain 1,434 equipment
  formatter outputs exactly, including Crystal Spirit's numbers.
- Execute 36 cases through the actual Hero Tales name and help selectors,
  preserving level clamping, locked names and the caller's registers.
- Execute guarded copy, native initializer-boundary and child-mapping cases
  at both load bases. Prove writes to the former resident location cannot
  change the protected copy.
- Run the inherited 14 validation groups and the separate 1,220 native
  rename, default-name initialization and saved-record repair cases.
- Compare Cooking in 0.1.73 and 0.1.74 using the same private normal save.
  The private room save was created through the game's Save menu from a
  supplied older diagnostic state. The comparison sessions themselves
  both started normally and loaded that saved game, without a state or
  runtime memory edits. Supplied files were not modified.
- Use PPSSPP 1.20.4 with JIT, audio enabled and bad-memory suppression off.
  Fresh-boot screenshots verify both title prompts, Marurur's status,
  two recipes, the upper and lower party lists, Hero Tales 5, Unit Form
  and Crystal Spirit. Cooking still displays correctly after reopening it.
  Final screenshots are under `work/ui/menus_0.1.74/menus074-final8/`.
- Verify the upgrade with Retro Trans Tools, including decoded ISO size and
  SHA-256. The package contains patches and metadata, not game binaries.

These checks cover the reported screens and known rendering paths. They
do not replace a complete playthrough. Historical published inputs remain
unchanged; native saves retain their existing layout.
