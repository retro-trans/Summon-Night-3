# Learn Skills — 0.1.41

Local test build based on 0.1.40; not a GitHub release.

## Report and changes

The report shows Japanese header/tabs/footer and skill names, wide Latin
spacing, an empty selected Pact card, and a closing bracket on its own line.
The screenshot came from another user; no matching unlocked save is available.

- Translate the five native header/tab sprites in 02.DAT resource 1343 child 2:
  Learn Skills, selected/unselected Common Skills, selected/unselected Unique Skills.
- Translate Confirm, Back and Switch Skills and route their three exact callers
  through the existing bounded VWF renderer. Also enable it for the protagonist
  label and skill-card names. Costs, levels, portraits and unrelated renderers stay intact.
- Shorten 15 generated Pact Ritual names and five static variants to `Pact: ...`.
  Every variant fits the 16-cell renderer limit; the reported Beast title becomes
  `Pact: Beast`. Actual resolution of the empty card remains visually unverified.
- Shorten the crafting prefix and wrap before whole affinity names while reserving
  room for the closing bracket. The reported text becomes `Craft [Beast/Neutral]`.
- Translate 31 table name entries: all 27 remaining common weapon/stat/resistance
  names, Unit Summon, Double Attack, Double Move and Double Item. Use compact
  `Sword Prof.` / `Mech. Resist` labels within the card width; full translations
  remain in the target metadata. This does not claim every unique skill or all
  skill descriptions have been translated.
- Preserve numeric stats, skill costs and all non-name fields. Repack both the
  shared static data and its resident cache consistently.

## Checks

- Execute all 15 nonempty native Pact-name combinations and 31 description
  combinations. At most two lines, 27 cells per line, no lone closing bracket,
  and guarded output memory remains intact.
- Execute 108 actual VWF-wrapper cases at two PSP load bases, with clobbering
  native-call stubs. Names and controls use VWF and stay within stack guards.
- Parse all 23 bank indexes and compare 5,727 unrelated resources byte for byte.
  Verify original input hashes and all rebuilt ISO files/cache copies.
- Inspect all five palette-converted labels. Fresh isolated PPSSPP boot succeeds.
- Exact unlocked Learn Skills layout is still pending a suitable in-game save.

## Files

- ISO: `work/output/0.1.41/Summon_Night_3_EN_0.1.41.iso`
- SHA-256: `56dd6bac4296cb25467dde3d1536928fed42f977f5cce4ed8d6ea79cb5b8e4fa`
- Builder: `tools/build_skills_041.py`
- Changes: `tools/skills_041.py`
- Native checks: `tools/verify_skills_041.py`
- Text targets: `work/translation/en/skills_0.1.41/targets.json`
- Generated atlas: `work/ui/skills_0.1.41/labels_generated.png`
- Imported labels: `work/ui/skills_0.1.41/label_0_native.png` through `label_4_native.png`
- QA: `work/ui/skills_0.1.41/verification.json`

Start the ISO fresh and load an in-game save; old emulator save states can restore
old executable and text data.

## Graphics provenance

The built-in image-generation tool generated the atlas; no CLI fallback was used.
Native sprites were inspected first. Direct reference-file access failed in the
sandbox, so the final call generated a new atlas from the following specification.
Only cropping, resampling, matte compositing, source-alpha application and native
palette quantization were applied afterward.

Final prompt:

> Generate a production sprite atlas for a PSP fantasy JRPG menu. Transparent canvas 640x720, five separate horizontal buttons aligned x40, row y10,154,298,442,586. First button520x120 with ornate orange wood frame, tiny curled spiral ornament on left, gold parchment center gradient and dark brown condensed bold serif text 'Learn Skills', thin cream outline. Remaining buttons360x80: restrained amber-orange wood/parchment rectangle with fine cream border, slight angled rounded right edge. Row2 text 'Common Skills' bright pale gold selected; Row3 same text 'Common Skills' muted brown-gold unselected; Row4 'Unique Skills' bright pale gold selected; Row5 'Unique Skills' muted brown-gold unselected. Exact text, keep generous transparent separation. Text crisp and condensed, must remain legible when firstbutton reduced104x24 and tabs72x16. No additional text, no Japanese, no large ornaments, no shadows outside sprites. Consistent warm 2000s tactical JRPG orange menu style.
