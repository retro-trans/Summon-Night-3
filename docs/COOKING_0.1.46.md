# Cooking localization - v0.1.46

The reported Cooking book now has English recipe names, concise recipe
summaries, ingredient names and descriptions, controls, quantity prompts,
and Cooking/Ingredients artwork.

## Scope

- 29 populated recipes in table 40, including the ten late summon dishes
  in the report. The table has 49 records; unused records are untouched.
- Matching names in the inventory consumables table (19).
- 25 populated ingredient names and descriptions in table 20.
- 137 table-text entries in total, plus executable controls/messages.
- Recipe descriptions use six rows with at most 13 native text cells per
  row. The first three rows keep four padding cells around the food icon.
  Full English meanings are saved alongside the concise UI wording in
  `work/translation/en/cooking_0.1.46/targets.json`.
- Proportional spacing is scoped to the Cooking description-position call,
  recipe headings, ingredient names and controls. It does not enlarge or
  relocate the native 78-object recipe text pool.

The reported final recipe is **Cosmic Choco**: a chocolate snack for Beast
World summons with a deep flavor evoking all of nature. Humans cannot eat it.
The UI condenses this to fit the book, while the catalog retains the meaning.
Ingredient labels use compact forms where necessary, including **Nature Ess.**
and **Greens**, to avoid the quantity column.

## Validation and limits

- All 29 recipe descriptions execute through the native per-glyph loading
  loop. Exact glyph placement slots and buffer guards pass.
- The emitted MIPS position helper passes 3,044 character-position cases
  at two relocated load addresses, including preserved registers, Y/Z,
  stack guards, icon padding and a Japanese fallback case.
- Names are checked against the existing 16-cell VWF wrapper and measured
  pixel budgets: 138 for recipe names and 102 for ingredient names.
- Ingredient help retains the two-line, 27-cell / 54-total-glyph limits.
- Recipe costs, quantities, item effects and all non-text table fields
  remain byte-identical. The existing System help and Brave Goals checks pass.
- Cooking title, Ingredients book strip and list heading were inspected
  after native palette encoding. Transparency remains exact; the book's
  pixels outside the small heading rectangle remain exact.
- Cumulative source hashes, ISO extents, bank indexes and unchanged resources
  are verified by the build. Patch reconstruction hashes are recorded in
  `work/output/0.1.46/XDELTA-VALIDATION.json`.

The user does not currently have a normal save at this screen. Therefore,
**the Cooking menu has not been visually tested in a live emulator**. Native
text-loop tests and decoded-asset inspection do not substitute for that check.

## Outputs

- `work/output/0.1.46/Summon_Night_3_EN_0.1.46.iso`
- `work/output/0.1.46/SN3-English-v0.1.45-to-v0.1.46.xdelta`
- `work/output/0.1.46/SN3-English-v0.1.46.xdelta` (original Japanese source)

Restart the patched ISO and load a normal in-game save. Old emulator states
retain earlier code and resources. This is a local test build; no GitHub
release was created.

## Artwork provenance

The **built-in image_gen tool** supplied the English Ingredients strip.
The exact successful prompt and crop coordinates are saved in
`work/ui/cooking_0.1.46/prompt.json`; the workspace image is
`work/ui/cooking_0.1.46/ingredients_generated.png`. Only its heading strip is
used, preserving the rest of the original book. The list header reuses that
strip; Cooking reuses the translated v0.1.44 sprite. Palette-encoded results
are saved in `work/ui/cooking_0.1.46/native/`.
