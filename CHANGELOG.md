# Changelog

## 0.1.81 - Published release (2026-10-08)

- Publish all UI fixes from local builds 0.1.78–0.1.81, including Options masks,
  Night Talks, related translations, skill popups, Replay help and Assist VWF.
- Publish only original → 0.1.81 and published 0.1.77 → 0.1.81 patches.
- Encode the full patch with a 256 MiB source window and verify both complete
  decoded ISOs, manifests and checksums for Retro Trans Tools compatibility.


## 0.1.81 - Assist button alignment and member-list VWF (local test build, 2026-10-08)

- Place the triangle icon using the same proportional Assist-only prefix as
  the help text; preserve all other icon handlers and button behavior.
- Use the existing VWF binding for required-member INFO names and category
  labels, fixing Protagonist and Magna / Toris crossing column boundaries.
- Preserve custom names, combat requirements, existing code/data and every
  other ISO file. Carry forward all 0.1.80 fixes.
- Verify both relocated paths and fresh-save Sky Torrent / Heaven's Net
  INFO windows with one emulator; package a Retro Trans Tools test upgrade
  from the previous published release, 0.1.77.

## 0.1.80 - Skill popups, summon names and Replay help (local test build, 2026-10-08)

- Translate the branch-specific Learn Skills prefix and Skill Point warning;
  render the failure-message widget with variable-width lettering.
- Render hidden skill-name markers as "Unknown"; compact and wrap proficiency
  bonuses within the help box, removing identical repeated mastery rows.
- Restore missing English skill-card names by coalescing free adjacent strips
  when large strips are exhausted; preserve texture dimensions and memory size.
- Translate all default summon-name text widgets used by summon popups and
  battle banners; preserve custom names and saved name buffers.
- Translate Replay selection help and all chapter labels and titles, keeping
  chapter titles consistent with the translated cards and Teacher preference.
- Translate Replay's image-based chapter prefix, extra-story marker and Halls
  marker; retain the original digits, palettes and sprite dimensions.
- Rebuild 132 battle-specific Brave Order fields with explicit end markers,
  bounded help and compact labels; correct the truncated Azlier/Preempt order.
- Apply current character-name spellings to these new inputs, preserve
  combat data and published snapshots, and carry all 0.1.79 category fixes.
- Check actual help staging and relocated helpers at two load bases; test
  with one emulator and package a Retro Trans Tools upgrade from published 0.1.77.

## 0.1.79 - Related UI categories and Night Talks (local test build, 2026-10-08)

- Restore the blank Chapter 7 Night Talks titles; compact both captions over
  the native strip limit, keep title scaling proportional, and separate footer labels.
- Translate remaining attack-skill names, help and mastery effects, fortune
  messages, Fariel labels, equipment types and weapon-range descriptions.
- Translate location entry plaques and remaining story/selection speaker-name
  graphics, including Guardian Shrine and Misumi and their related categories.
- Include the 0.1.78 Options selected-mask fix; preserve native asset geometry,
  palettes, combat data, player-entered names and published build inputs.
- Verify native text staging, relocated layout helpers, built assets and a
  fresh boot with a normal save using one emulator; package a Retro Trans Tools
  test upgrade from published 0.1.77.

## 0.1.78 - Options selection masks (local test build, 2026-10-08)

- Remove the retained Japanese text masks behind selected Cursor Direction
  and L/R Function labels; clear the black shapes outside the English glyphs.
- Check all five selected Options labels and both menu modes.
- Preserve native palettes, dimensions, other textures, executable and ISO layout.
- Package a local Retro Trans Tools test upgrade from published 0.1.77.

## 0.1.77 - Full-patch packaging correction (2026-10-08)

- Reduce the original-to-current xdelta from 407,197,655 to 14,383,778 bytes
  with a 256 MiB source matching window; verify the identical released ISO.
- Publish the optimized full patch under a new filename and withdraw the old
  patch identity while preserving it in the Retro Trans Tools catalog.
- Synchronize manifests and checksums; preserve the unchanged 0.1.73 upgrade.

## 0.1.77 - Optional battle headings and skill alignment (release, 2026-10-08)

- Translate VS Phantom Warriors and all remaining headings in its encounter-card
  category: 29 optional-battle sprites with 15 distinct labels.
- Keep battle victory/defeat conditions and unrelated sprite children unchanged.
- Align Blade Awakening and related labels with the other skills; restrict the
  centered binder to the original animation-banner context.
- Verify the already translated summon-equipment question, Yes/No choices and
  related crafting notices through their live executable references.
- Check Aty's skill list and Yard's All-Purpose Pot + white Neutral stone through
  naming and equipment from a fresh boot and supplied normal save.
- Preserve native palettes, dimensions, codecs, prior renderer guards and saves.
- Publish Retro Trans Tools patches from the original Japanese image and published 0.1.73.

## 0.1.76 - Gallery translations and menu fitting (local test build, 2026-10-08)

- Translate all 38 Sound titles, the related main Gallery title fields,
  229 Night Talk captions and 21 Ending captions.
- Translate matching Gallery headings, buttons, chapter tabs and nameplates.
- Align all five Options labels at a consistent size and repair both footer states.
- Shorten Options help to the existing safe limit, fixing the Event Voices and
  Forecast "Text error" messages without weakening the shared text guard.
- Use proportional text for purchase item names, questions, quantities and prices.
- Translate the separate Try On help line shown while choosing a character.
- Fit Gallery control labels in their existing slots and translate default
  protagonist names for display while preserving custom names and stored save data.
- Preserve the empty-row terminator required by gallery caption loaders;
  check every translated caption independently to prevent adjacent titles joining.
- Draw exact translated Gallery captions as bounded strips, preventing English
  titles from overrunning the original per-character font allocation.
- Include the separate Night Talks caption bank, fit visible titles to their
  column, and translate copied default-name rows without changing saved names.
- Carry forward the earlier Shop, Meimei, minigame, Cooking, Party Ability,
  summon-index and white-stone pot repairs.
- Keep native palettes, geometry, compression and numeric gameplay fields.
- Package a local Retro Trans Tools upgrade from published 0.1.73.

## 0.1.75 - Related UI category sweep (local test build, 2026-10-08)

- Extend the latest and earlier screenshot requests to matching UI categories.
- Translate 365 remaining unit/class labels and 176 native notices.
- Display translated default names from existing saves while preserving custom names.
- Translate location labels, Meimei's menus, conversation nameplates and matching copies.
- Translate all seven minigame instruction pages and related controls/results,
  including quit confirmations and native prize/rank labels.
- Use proportional text in native item-reward messages.
- Preserve the previous Cooking, Party Abilities, summon-index and white-stone pot fixes.
- Keep native palettes, sprite sizes, compression codecs and numeric gameplay fields.
- Run QA with at most one emulator instance.
- Pass all 14 inherited regression groups and the new name/reward CPU checks.
  Review the final image through a fresh boot and normal in-game save.
- Package a Retro Trans Tools test upgrade from published 0.1.73, including 0.1.74.

## 0.1.74 - Cooking text recovery and related menus (local test build, 2026-10-08)

- Translate and fit the title-screen Extra Story / Main Story prompts.
- Translate Marurur, Flower Fairy and related fairy class names.
- Translate all 29 Party Ability names and descriptions and 29 food effects.
- Fit party names beside their controls; translate all five native Hero Tales
  volume names and all six EXP-help variants.
- Fix Cooking descriptions overwritten by the native event-script arena;
  protect resident table children 37–48 in a 77,824-byte private buffer.
- Translate both Unit Form help copies and restore symbolic stat spacing
  on Summon Index / Combine pages, preserving every numeric output.
- Retain the 0.1.73 white-stone pot crash repair and save layout.
- Enforce a single PPSSPP instance for new QA launches.
- Supply a local 0.1.73-to-0.1.74 Retro Trans Tools upgrade.
- Verify the six reported screens from a normal save, 36 Hero Tales selector
  cases, 1,220 retained name-cache cases and all 14 inherited audit groups.

## 0.1.73 - UI translations and Yard / white-stone pot crash fix (release, 2026-10-07)

- Publish the cumulative translations and alignment fixes from local builds
  0.1.66 through 0.1.70 together with the final 0.1.73 crash repair.
- Supply only original-to-0.1.73 and published-0.1.65-to-0.1.73 patches, with
  Retro Trans Tools manifests, checksums and decoded-image verification.

- Terminate loaded cached names within the native 20-byte field.
- Reset saved accessory bindings outside the valid 121-entry range, including
  the CP932 text bytes left by older name overflows. Preserve every valid ID.
- Retain full default names, custom names and the existing save record layout.
- Pass 1,220 native name, initialization and saved-record cases at two load
  bases, plus all 14 inherited validation groups (15 groups in total).
- Fresh-boot the supplied normal Chapter 2 save in PPSSPP 1.20.4 with JIT,
  audio enabled and bad-memory suppression disabled. Verify Yard's white
  Neutral stone crafting, naming, equipping, Random Hit use and a subsequent
  unit menu, without runtime memory edits or the old state.

## 0.1.72 - Default summon-name cache bounds (diagnostic build, 2026-10-07)

- Protect the default-name initializer as well as the native rename path.
- Keep full English display names in separate storage while preserving the
  game's 20-byte internal name field and neighboring binding records.
- Pass 520 rename/getter cases and 192 actual default-initializer cases at
  two load bases. Identify that the supplied save restores damaged bindings,
  requiring the subsequent load-time repair.

## 0.1.71 - Summon-name cache diagnostic (not for distribution, 2026-10-07)

- Bound the native rename copy and preserve full names through a display getter.
- Pass 520 native name cases and all 14 inherited validation groups.
- Reproduce the white-stone crash despite those checks; identify the separate
  default-name initialization copy for the subsequent fix.

## 0.1.70 - Skill formatter help and startup notice (local test build, 2026-10-06)

- Translate twelve remaining equipment and transformation help fragments,
  including counterattack/ailment chances, critical-hit defeat, piercing,
  elevation range, Snipe, distance penalties and remaining uses.
- Translate the startup notice image while retaining its ornate-frame design,
  native size, palette and sprite layout. Keep publisher logos unchanged.
- Retain and verify all twelve existing common stat/resistance helps, including
  `Max MP +10/level.` from 0.1.69.
- Preserve numeric records, source pools, prior hooks and published snapshots.
- Validate native dynamic formatting, row limits and guarded output buffers.
- Pass all 15 validation groups. Visually verify the English startup notice
  under strict JIT settings and load a normal battle save without a memory error.

## 0.1.69 - Summon spells, stones and gallery rewards (local test build, 2026-10-06)

- Translate all 191 remaining summon spell name fields, including Tamahipo's
  Spice, Acid, Fatal and Petron Breath. Retain full names beside measured display forms.
- Translate 333 remaining fields for Summonite Stones, consumables, fishing bait
  and the related gallery rewards and descriptions. Include all animation art
  numbers, summon art, promotional art, event art and ending titles.
- Translate crafting help, dismissal and completion confirmations, favorite
  actions and eligibility messages through 18 source-bound native text blocks.
- Preserve runtime names, numeric favorite limits, the triangle control token,
  spell costs and effects, source text pools and undiscovered question marks.
- Retain the existing Takeshi profile and Rewards obtained heading fixes.
- Keep plant romanizations, Ixellion and Reaver provisional in the glossary.
- Pass 16 validation groups. Fresh-boot a normal Chapter 15 battle save with
  strict JIT settings; visually verify Takeshi's profile, Tamahipo's four breath
  names and the summon combination list. Exact early reward/dismissal states
  remain pending a matching save.

## 0.1.68 - Related UI category translations (local test build, 2026-10-06)

- Translate 601 remaining fields across summon profiles, active/passive skills,
  support descriptions and common-skill mastery effects, including level variants.
- Translate 24 related map location labels, including Rocky Shore and the
  sixteen Endless Halls labels; use measured short display forms where needed.
- Reformat 12 existing English descriptions so help and mastery fit together.
  Preserve native stat icons, numbers, costs and undiscovered-entry masks.
- Append translated text, preserve original pools and numeric records, and
  synchronize resident-table copies. Retain the SELECT/Learn Skills correction
  and private chapter-script arena without changing their native code.
- Pass the inherited regression audit, 254 native help/master combinations,
  373 staging cases and the retained Status/SELECT/Give Food checks.
- Fresh-boot a normal Chapter 15 save in strict PPSSPP 1.20.4 JIT; verify menu
  browsing and Picolit's translated two-line Summon Index profile in game.
- Exact early-story map/deployment/skill screens remain pending a matching save.

## 0.1.67 - Restore Status Learn Skills hint (local test build, 2026-10-03)

- Keep SELECT / Learn Skills on the visible second help row; shorten the
  L/R hint to Switch and reserve space for the SELECT icon.
- Place the matching SELECT icon using proportional prefix width, retaining
  the previous Give Food handler and all nonmatching shortcut behavior.
- Relocate the longer shortcut string; preserve adjacent descriptions,
  buffer limits, custom player names and the private chapter-script arena.
- Default protagonist table labels are already Rexx/Aty. Japanese names
  stored in existing saves remain unchanged pending default/custom clarification.
- Pass 18 cumulative regression groups and a strict PPSSPP 1.20.4 fresh-boot
  normal-save load and battle-menu check. Exact room-screen visuals remain pending.

## 0.1.66 - Summon Status labels and feeding hint (local test build, 2026-10-03)

- Translate R's unit name using the current character reference.
- Translate the shared class label as Summon Friend for R, Teco, Onibi and
  the fourth companion, including all four class-rank slots per companion.
- Place the SELECT icon before Give Food using the proportional width of
  preceding text. Scope the correction to the matching second-row hint.
- Preserve all other shortcut handlers, gameplay values and the 0.1.65
  private chapter-script arena. Synchronize bank and resident label copies.
- Native relocation, stack-guard and fallback checks pass at two load bases.
- Pass 17 cumulative regression groups and a fresh-boot Chapter 15 normal-save
  load and battle-menu check in PPSSPP 1.20.4 with strict memory checking.
- Exact reported room-screen visual verification is pending a matching save.

## 0.1.65 - Resident-table overlap fix (release, 2026-10-02)

- Give the chapter-common script its own loader-owned 32 KiB buffer, preventing
  it from overwriting expanded resident tables when a chapter loads.
- Preserve all translations, native decoding/binding and other memory regions.
- Verify all 20 chapter-common scripts fit, and test the relocated helper at
  two load bases. The largest current script is 27,404 bytes.
- Include the accumulated UI fixes from local builds 0.1.56–0.1.64.
- Pass 16 cumulative regression groups and fresh-boot Chapter 15 Continue,
  Extra Brave Goal, equipment and Summon Index smoke tests. Verify all 620
  live Extra Brave table text pointers against the source data.
- Publish only original-to-current and published 0.1.55-to-0.1.65 patches,
  with full decoded-ISO verification through Retro Trans Tools.

## 0.1.64 - UI report fixes and Learn Skills (local test build, 2026-10-02)

- Translate Dash!, Fighting Spirit, Guts and Item Throw with their help and
  mastery effects; retain the existing proportional skill-card renderer.
- Preserve gentle-terrain/straight movement and mastery height limits, all
  four conditions disabling ZOC, near-death penalty reduction and item range.
- Relocate twelve selected text fields in tables 28/31 and synchronize the
  cached static tables. Preserve all costs, levels, stats and original pools.
- Keep the executable byte-identical to 0.1.63. Check all four help blocks
  through native staging within the 54-object limit and measure card names.
- Pass all 14 inherited regression groups and a fresh PPSSPP 1.20.4 boot.
- Exact Learn Skills visual checks remain pending a matching save.
- Verify the local 0.1.55-to-0.1.64 test upgrade with Retro Trans Tools and
  a full decoded-ISO hash comparison.
- Withhold publication after a broader Chapter 15 smoke test found that the
  chapter-common script overwrote the expanded Extra Brave Goal table.

## 0.1.63 - Rewards and joining messages (local test build, 2026-10-02)

- Translate the Rewards obtained! banner, F Aid and all 34 Concept Art labels.
- Translate the shared party-joining popup and its related battle/support,
  materialization, departure and return variants. Preserve the character-name
  field and saved/custom names rather than hard-coding Kyle.
- Apply bounded proportional text to the banner, reward item names and popup
  labels, and center the name within its existing rectangle. Preserve native
  fallback for oversized popup text and all original font-object allocations.
- Append strings and synchronize cached tables; preserve reward values,
  statistics, quantities and original text pools.
- Pass 14 regression groups, 32 native notification-selector cases, 20 new
  wrapper cases and the inherited VWF pixel/bounds checks. Verify all 13 live
  text-pointer pairs and seven helper targets in a fresh PPSSPP 1.20.4 boot.
- Exact reward/recruitment visual checks remain pending matching saves.
- Verify the local 0.1.55-to-0.1.63 upgrade with Retro Trans Tools validation
  and a full decoded-ISO hash comparison.
  This pass does not publish a release.

## 0.1.62 - Blade Awakening, Mujina and Set alignment (local test build, 2026-10-02)

- Translate four Blade Awakening skill variants and their help. Retain
  ailment/possession immunity and the availability of Berserk Summoning.
- Translate Mujina's alternate names, three spells and two-row lore; preserve
  discovery placeholders, player names, statistics, costs and unlock conditions.
- Use a compact proportional Set hint with its icon and text inside the right
  screen edge. Extend the existing scoped banner VWF to the new English names.
- Append English strings and synchronize the resident table copy. Retain all
  prior local UI fixes and the existing bounded renderer and crash guards.
- Pass 14 regression groups, 480 wrapper cases, 96 binder cases, 210 centered
  pixel cases, five native description-staging cases and six native hint modes.
- Fresh-boot PPSSPP 1.20.4 shows Mujina's name, lore and three spells without
  clipping after loading a copied normal battle save. Exact awakening and
  Create Summons Set visual checks still require matching saves.
- Verify the local 0.1.55-to-0.1.62 patch with Retro Trans Tools and a complete
  decoded ISO hash comparison. No release is published by this pass.

## 0.1.61 - Spell banner VWF and reported UI (local test build, 2026-10-02)

- Display the complete Zip Toast name with centered proportional lettering.
  Convert only recognized translated spell names in single-row glyph widgets
  to the existing bounded strip renderer; reuse one existing font object and
  preserve native behavior for unrelated, Japanese and player-entered text.
- Translate Yard's ordinary and battle nameplates, keeping native sprite
  dimensions and palettes. Confirm the three backlog copies already say Yard.
- Translate the Island Map heading in both map packages and relocate the
  First Shore location label. Retain the original location string in its pool.
- Translate the five related indirect-attack commands and their range/element
  descriptions. Append their strings and synchronize the resident table copy.
- Pass 14 inherited regression groups, 420 renderer-wrapper cases, 84 binder
  cases, 210 centered pixel cases and five native help-staging cases.
- Fresh-boot PPSSPP 1.20.4 loads the copied normal Chapter 15 battle save;
  the Summon Index shows the complete Zip Toast name. Exact casting-banner,
  map-label and Yard scene visual verification remains pending matching saves.
- Verify the local 0.1.55-to-0.1.61 upgrade through Retro Trans Tools, including
  a complete decoded ISO hash comparison. No release is published by this pass.

## 0.1.60 - Level Up localization and alignment (local test build, 2026-10-02)

- Translate the selected and unselected Level Up headings while preserving the
  original frame, palette and sprite dimensions.
- Translate unit selection, unavailable-unit and bonus-point allocation text,
  plus OK, End and Confirm button hints. Reserve space after SELECT so Learn
  Skills clears its wider icon; preserve the player-entered protagonist name.
- Change only this screen's six text bindings and two heading textures. Keep
  shared Learn Skills labels and previous local fixes intact.
- Pass 14 regression groups, including all eight native Level Up formatter
  states, guarded glyph staging and 54 positioning cases at two load bases.
- Fresh-boot PPSSPP 1.20.4 loads the copied normal battle save. Exact Level Up
  visual verification remains pending a matching save.
- Package the local 0.1.55-to-0.1.60 upgrade with Retro Trans Tools and verify
  its complete decoded ISO hash.

## 0.1.59 - Shine Saber spell-name overlap (local test build, 2026-10-02)

- Shorten Crush! Light Gen. Sword to Crush! L.Gen.Sword, preserving the imperative,
  Light General title and sword reference while leaving space for the MP cost.
- Check every already translated name in the spell table against a conservative
  140-pixel display width. The reported skill is the only one exceeding it.
- Change only the spell-name pointer and append its compact label. Synchronize
  the resident table copy and retain all previous fixes without changing code.
- Pass all 13 regression groups. Exact spell-list visual verification remains
  pending a matching save; fit is measured against the reported layout.
- Verify the local 0.1.55-to-0.1.59 upgrade with Retro Trans Tools and a complete
  decoded ISO hash comparison.

## 0.1.58 - Charge action label (local test build, 2026-10-02)

- Translate the separate special-command entry チャージ as Charge. The status
  label was already translated; the action banner used another table entry.
- Relocate the command label with the existing two-byte font encoding and update
  its resident table copy. Preserve the executable and all other table entries.
- Retain the Magna and summon-header fixes from local builds 0.1.56–0.1.57.
- Pass 13 regression groups and a complete Retro Trans Tools patch round trip.
  Fresh-boot save loading and the Special menu work; the exact Charge banner
  still needs a save with the command available.

## 0.1.57 - Summon screen heading and hints (local test build, 2026-10-02)

- Translate the Create Summons heading and Affinity label inside their original
  background regions. Preserve the frame, seal and all other pixels.
- Use the shipped proportional text wrapper for Confirm, Set Name, Cast and
  Dismiss. Shorten Cast Magic to Cast and move each mode's hints inside the screen.
- Retain the 0.1.56 Magna fix and earlier crash fixes. Add relocation, register,
  stack and screen-bound checks for the changed hint calls.
- Pass 13 regression groups and the Retro Trans upgrade-patch round trip from
  the last published release, 0.1.55. Keep this build and patch local for testing.
- Confirm the translated heading and complete Cast/Dismiss hints in a fresh-boot
  PPSSPP 1.20.4 Create Summons screen using a copied normal game save.

## 0.1.56 - Magna nameplate (local test build, 2026-10-02)

- Translate Magna's ordinary dialogue and battle nameplates using the current
  character-name reference. Preserve the original frames, palettes and sprite sizes.
- Translate the matching exact-name entries in all three backlog name tables.
- Build on 0.1.55 without changing its executable, story scripts or previous fixes.
- Pass archive integrity, texture bounds and all 12 current regression groups; the reported
  beach conversation still needs an in-game visual check with a matching save.

## English PS2 guide 0.1.1 - Original layout (2026-10-01)

- Replace the redesigned reading edition with English text in the original
  scanned layout, following the user's correction.
- Preserve all 35 original scans, including illustrations, screenshots, diagrams,
  table borders, icons, page numbers, packaging, and the disc photograph.
- Map instructional prose, captions, headings and table text to their original
  positions. Keep text inside illustrative screenshots and official branding as
  printed; remove explanatory notes added only for the redesigned edition.
- Reuse the independently reviewed English translations and current glossary.
- Check text fit, glyphs, scan coverage and embedded JPEG hashes; render and
  inspect all spreads before delivery.

## English PS2 guide 0.1.0 - 2026-10-01

- Translate all 35 supplied packaging, manual and disc scans into a clean English
  reading edition, preserving PS2 controls, original page references and statistics.
- Independently review all scan groups against their sources; correct meaning,
  recipe, numerical and caption errors before the final terminology pass.
- Produce a searchable PDF with 66 source-topic bookmarks, clear tables and
  archival publisher notices. Record source hashes and review evidence locally.
- Disclose the unreadable fishing screenshot note, provisional minor names and
  original data quirks. Omit decorative art and incidental screenshot statistics.
- Render the PDF and verify translated-text coverage and page layout.

## 0.1.55 - Remaining battle-event translation (test release, 2026-10-01)

- Publish both verified patches; check all nine public asset hashes. Register in
  Retro Trans and pass a public Automatic-mode upgrade from v0.1.54 with complete
  output-hash and target-recognition checks.
- Translate all 642 remaining indexed battle-event fragments across 27 resources,
  using nine consecutive slices and independent Japanese-source meaning reviews.
- Apply five reviewed fragment corrections, then normalize current glossary names
  and the Beardy nickname. Preserve uncertainties and intentional unfinished speech.
- Validate 284 dialogue groups / 329 generated pages in memory: preserve speakers,
  control tokens, branch destinations and untouched event code; enforce text-box fit.
- Handle three verified native speaker operands and one source-locked blank append
  without changing the historical battle compiler or published build inputs.
- Pass eight negative acceptance/input checks, 13 story regression tests and all
  12 cumulative stability audit groups on the built ISO.
- Fresh-boot PPSSPP passes Chapter 15 Continue, Brave Goals, Inventory/Black Rose
  Knife and Summon Index/Dritol with strict memory handling. Full routes and
  individual new battle-event allocations remain unverified.
- Build on published v0.1.54; verify 31,742 untouched archive entries. Package
  only the clean-source patch and upgrade from published v0.1.54.
- Update and read back all 642 battle Current English cells in the translator
  Sheet. Preserve Proposed English, review fields, notes, formatting, row order
  and archives; label the Read me checkpoint as unreleased v0.1.55.

## Translator sheet refresh - 2026-10-01

- Audit remaining blank cells: distinguish 8,913 intentional continuations,
  363 older export-mapping omissions and 642 unmapped battle-event fragments.
  Record the scope gap without changing translator entries.
- Refresh 24,778 Current English cells across 12 tabs from reviewed v0.1.54
  release inputs; match all 71,356 released story occurrences by stable key.
- Read back every changed range and preserve Proposed English, reviewer fields,
  notes, source text, speakers, order, formatting and hidden archives.
- Update the Read me checkpoint and explain intentional blank continuation
  fragments. Save the verified local refresh receipt; release files are unchanged.

## 0.1.54 - Remaining story translation (test release, 2026-10-01)

- Publish the two verified patches and confirm all nine public asset hashes.
  Register the release in Retro Trans and verify a real Automatic-mode upgrade
  from v0.1.52, including complete output hash and target recognition.
- Build all 134 accepted story scripts on v0.1.53; publish only the clean-source
  patch and upgrade from published v0.1.52.
- Verify unchanged ISO file contents and untouched archive entries. Pass 13
  compiler regression tests and all 12 cumulative stability audit groups.
- Fresh-boot PPSSPP passes Chapter 15 Continue, Brave Goals, Inventory/Black Rose
  Knife and Summon Index/Dritol. Record existing UI defects and untested routes.
- Verify both patches against the complete target ISO with the Retro Trans engine.

### Translation completion checkpoint (before build)


- Complete translation and independent source review of all 43,668 remaining
  story fragments across 134 resources. All resources now have accepted reviews;
  no undrafted rows or pending reviewed corrections remain.
- Correct shifted dialogue boxes, missing clauses, speaker/request direction,
  family relationships and duplicated continuations. Complete the final branch
  review and apply canonical names afterward, preserving historical inputs.
- Add source-locked support for the final branch's display helpers and shared
  conditional tails. All 134 resources pass in-memory compilation; every current
  recorded compiler input is verified. Nine regression tests and three targeted
  negative checks pass.
- Reopen resource 364 after the final music-marker scan revealed shifted text.
  Recheck all 1,804 new rows, correct its first slice, and remove the extra marker
  in resource 410. The final full-corpus scan finds no empty complete new dialogue
  boxes or music-marker mismatches.
- Save the final audit and progress checkpoint. Provisional lore/place spellings
  remain documented. Runtime allocation and gameplay are unverified; no ISO,
  release, Git push or Google Sheet update was produced.

### Earlier checkpoints

- Finish all remaining story drafts: 43,668 new fragments across 134 resources;
  no undrafted fragments remain. Independent review and release validation continue.
- Consolidate resource 485 meaning reviews through row 4447 and verify remaining
  reported corrections. Restore missing phrases, distinguish Teacher and their
  companions, correct hypothetical events and request direction, and remove
  duplicated music markers. No empty complete new dialogue boxes or music-marker
  mismatches remain in the final resource; terminology and wordplay remain flagged.
- Renew 150 older review rows in resources 279, 281 and 282, preserve superseded
  proof records, and accept their corrected translations. All three compile in
  memory and every recorded compiler-input hash verifies.
- Checkpoint (2026-10-01): 37,857 rows have current independent review proofs;
  active proof bindings pass. Older coverage gaps, one incomplete 80-row review,
  final-resource consolidation, name/title normalization and gameplay tests remain.
  No ISO, release, Git push or Google Sheet update.

- Complete main resource 482: all 1,383 new fragments independently reviewed,
  corrected and accepted. Restore the plea to stay alive, fix known speakers and
  duplicate boundary text, and preserve an unfinished confession.
- Validate its original display helper 2246 by exact source signature and add
  conservative pagination support while retaining conditional name paths. Four
  display-helper tests pass. Resource 482 compiles in memory to 1,519 dialogue
  groups / 1,653 pages (214,986 decoded bytes); runtime allocation and gameplay
  remain unverified.
- Renew 187 older meaning-review rows in resources 274-276 and 278, preserving
  superseded proofs byte-for-byte. Recompile those four scripts plus 482 and
  verify every recorded compiler-input hash.
- Draft 2,400 fragments of final resource 485 with parallel Terra authors.
  Review its first 720 rows and repair an additional missing boundary anchor;
  correct request direction, place/person confusion, shifted dialogue and
  duplicate music markers. Further meaning review and name normalization remain.
- Checkpoint (2026-10-01): 42,050 fragments drafted; 1,618 remain, all in resource
  485. Four older incomplete reviews still cover 190 pending rows. This is a
  translation checkpoint only: no ISO, release, Git push or Google Sheet update.

- Complete the final eleven Chapter 18 companion scripts (465-467, 470,
  473-479): 1,228 new fragments drafted, independently reviewed and accepted.
  All 21 Chapter 18 companions now have accepted meaning reviews.
- Correct Azlier's narration and younger-brother relationship, Kyle's addressee,
  Yard's promise direction, omitted summoning/shipbuilding details and duplicated
  dialogue. Apply canonical names after meaning fixes; record provisional nicknames.
- Validate the final eleven scripts in memory: 646 dialogue groups and 788 pages,
  with original display calls simulated and exact input hashes verified. No ISO
  or gameplay test was performed; runtime allocation remains unverified.
- Checkpoint (2026-10-01): 38,267 fragments drafted; 5,401 remain in main resources
  482 and 485. Active review bindings pass; nine older incomplete reviews still
  cover 377 pending rows. Preserve translator-sheet edits and published inputs.

- Complete and independently review ten Chapter 18 companion scripts: resources
  458-463, 468-469 and 471-472, covering 1,526 new-text fragments. Add 1,069
  previously undrafted fragments and review the three earlier companion drafts.
- Correct exam-result speakers, request direction, missing child references,
  duplicated dialogue at a slice boundary, and known character pronouns.
  Apply frozen terminology rules after meaning corrections; preserve short Bel,
  use teacher for the profession, and record provisional book/city terminology.
- Verify all ten accepted scripts in memory: 841 dialogue groups and 1,081 pages;
  every display call is simulated, live text and unrelated code are preserved,
  and compiler-input hashes pass. No ISO or gameplay test was performed.
- Checkpoint (2026-10-01): 37,039 fragments drafted; 6,629 remain. Active review
  bindings pass. Continue Chapter 18 resource 465, remaining companions, and main
  resources 482/485. Nine older incomplete reviews still cover 377 pending rows.

- Complete Chapter 17 main resource 433: all 2,595 new fragments independently
  reviewed and accepted, adding the remaining 1,475 fragments this checkpoint.
  Restore missing dialogue boxes, remove duplicate and shifted meanings, and fix
  request direction and Rikuto's farewell message about his own wife and child.
- Normalize Chapter 17 Elgo, Clyps, Core Cognizance and Rikuto after meaning review;
  record the spell call "Oni Summon: Wind Blade" as provisional. Preserve historical
  glossary snapshots and all prior review proof chains.
- Verify Chapter 17 in memory at 305,786 of 491,520 decoded bytes, with 2,132
  dialogue groups and 2,377 pages. Verify exact display-wrapper signatures for
  helpers 2154 and 2219 before paging their dialogue; retain original conditional
  paths and display calls. Six regression checks pass; no ISO or gameplay test.
- Checkpoint (2026-10-01): 35,970 new fragments drafted; 7,698 remain. Active review
  bindings pass. Continue Chapter 18 support scenes, then main resources 482/485;
  377 rows in nine older incomplete review records still require renewed review.

- Complete and independently review Chapter 16 main resource 410: all 3,224 new
  fragments. Restore omitted meanings, dialogue boundaries and actor direction;
  normalize Chuur, Bel, Ishlar, sword titles and the descriptive disease demon's curse.
- Verify Chapter 16 in memory at 357,482 of 491,520 decoded bytes. Bind display
  helper 2154 to its exact source signature and preserve its original calls while
  paging eight dialogue boxes. Keep menu choices on their original display path;
  fit three labels and an overlong repeated laugh. Five regression checks pass.
- Continue Chapter 17 resource 433 through row 2927: 1,120 new fragments drafted
  and independently reviewed. Correct character relationships, a yes/no reversal,
  unsupported speaker claims, duplicated questions and shifted dialogue boxes.
- Checkpoint (2026-10-01): 34,495 new fragments drafted; 9,173 remain. Active review
  bindings pass. Next row is Chapter 17 resource 433:2928; its final terminology
  normalization and compilation remain pending. No ISO or gameplay validation.

- Complete and independently review Chapter 15 main resource 387 and 18 companion
  scripts: 7,522 new fragments. Correct missing, duplicated and shifted dialogue,
  negation and actor direction before normalizing names.
- Verify all 19 Chapter 15 scripts in memory. Main 387 uses 431,320 decoded bytes
  within 491,520. Add source-bound branch pagination for resource 393 and verify
  both original paths, display calls and live-text preservation. No ISO/gameplay test.
- Restore 173 historical review records, including 169 by exact hash and four from
  retained clean root records. Replace three unrecoverable proofs with fresh source
  reviews; archive damaged records and affected acceptance snapshots. Re-review the
  older resource 364 supplemental correction and reaccept resources 329, 331 and 364.
  Active review bindings now pass; nine older semantic-completion records remain pending.
- Continue Chapter 16 with 80-row slices and independent full-box review. Repair a
  duplicated boundary sentence and preserve the honorific needed by the following
  dialogue. Keep translator-sheet entries and released snapshots unchanged.
- Checkpoint (2026-10-01): Chapter 16 resource 410 rows 1808–3087 add 1,280 independently
  reviewed fragments. Restore actor-neutral phrasing where the script cannot establish
  a speaker, fix timing and past/future meaning, and retain an English name/overeating
  pun. Source/control audit passes; 31,431 new fragments drafted and 12,237 remain.
  Continue at row 3088; Chapter 16 name normalization and compilation remain pending.

- Complete Chapter 13 main resource 341 and all 19 in-scope companion scripts: add
  2,647 new fragments, retranslate 332 legacy main rows, and accept 3,230 rows after
  independent source review. Preserve the 71 replaced legacy slices and their hashes.
- Correct misplaced/duplicated dialogue, empty boxes, reversed actions, speaker pronouns,
  and a measured choice-label overflow. Normalize names after meaning corrections;
  record provisional Lady of Thorns and Coral Viper title references.
- Verify all 20 Chapter 13 scripts in memory, including two-line Night Talk layouts.
  Main 341 compiles to 269,892 decoded bytes within 491,520; preserve live text and
  original display calls. No ISO or gameplay validation yet.
- Checkpoint: 22,629 new fragments drafted, 21,039 remain; next main resource is 387
  (Chapter 15). Keep human spreadsheet edits and published snapshots unchanged.

- Audit the remaining story scope and separate exact shared-library reuse from new dialogue.
- Apply updated BASE_RULES: 80-row slices, surrounding context, sourced character facts,
  explicit uncertainty and retained-omission notes, and dry-run previews before data writes.
- Keep earlier unpublished drafts pending independent meaning review against the updated rules.
- Add a separate relocation compiler with verified two-line Night Talk pages and the
  existing decoded-script allocation limit. Draft layout checks do not imply gameplay validation.

- Complete the 3,481-row new draft for story resource 249; verify full-script layout
  and relocation at 353,352 decoded bytes within the 491,520-byte allocation limit.
- Independently review all 1,804 new rows in story resource 364, apply verified meaning
  corrections, then normalize Crimson Gloves. Bind acceptance to exact draft and review hashes.
- Verify resource 364 after review at 255,344 decoded bytes and 1,931 pages;
  preserve gameplay validation as a separate outstanding requirement.
- Add review-proof integrity and glossary-normalization checks; reject stale reviews
  and keep unresolved readings explicit. Complete the resource 272 draft in 80-row slices.
- Record sourced location and organization terms with explicitly provisional plant/spell names.

- Add lossless duplicate/suffix string storage; verify referenced bytes and VM instructions
  are preserved. Resource 272 fits at 490,554 decoded bytes; gameplay remains unverified.
- Pause translation at the user's export checkpoint: 10,791 new fragments drafted,
  32,877 remaining; 3,212 rows have current independent review proofs.
- Prepare a chapter-ordered Google Sheets proofreading inventory matching the reference
  columns. Preserve source IDs and untranslated rows; keep Japanese text transient.
  Upload 115,766 proofreading records covering 152,904 source fragments to the user-provided
  Google Sheet. Verify every uploaded block, chapter order, 22 record tabs, reviewer notes,
  validation controls and explicit row heights. Keep uncertain battle chapter assignments
  in separate tabs and retain translation pause. Exclude only 620 internal ASCII setup rows.


- Correct the proofreading export's historical dialogue matching: use original source
  byte offsets, not compiler-dependent row numbers after shared-prefix stripping.
- Add VM-backed speaker roles and explicit unresolved actor slots, script-event IDs,
  and basic-block references. These identify static structure, not a verified route chronology.
- Prepare a corrected scene index with separate shared/prelude and system sections;
  preserve every original record and the original native tabs. Shared scripts contain
  real opening dialogue and must not be mistaken for UI-only material.
- Upload and read back all 115,766 corrected records across 24 record tabs; retain
  the prior 22 record tabs and guide as hidden archives. Preserve all 203 original
  translator/reviewer notes, verify native layout controls, and keep unresolved
  route chronology and fixed-speaker attribution explicit. No translation or build changes.

- Simplify the live translator sheet: remove free bytes, box, px / limit, budget,
  bytes, widest, lines and fits from all 24 current record tabs. Preserve proposed
  translations in column E, reviewer controls, notes, row counts and hidden archives;
  update the guide to the new scene-context column positions.

- Remove section, script event, branch block and source context from the 24
  translator tabs. Preserve all 115,766 row-keyed trace records outside the sheet,
  retain the eight translation/review columns, and update the guide.

- Resume the remaining dialogue translation at the user request, using Terra
  authors in 80-row slices and separate meaning review; retain translator-sheet
  edits and the simplified eight-column review layout.


- Resume checkpoint: add 5,674 new story fragments (16,465 drafted; 27,203 remaining).
  Complete and independently review Chapter 11 main resource 295 and its companion
  scenes; complete the remaining Chapter 9/10 companion drafts and eight Chapter 12 scenes.
- Accept 45 additional resources after meaning corrections and glossary normalization.
  Review complete VM dialogue groups to fix shifted clauses, replaced reactions,
  repeated text, wrong action subjects, and an incorrectly completed interrupted name.
  Keep unresolved author/reviewer readings in the source-bound records.
- Add a read-only whole-dialogue preview for subsequent authors and reviewers.
  Normalize Shartos, Crissles, Maetropa, Sapureth and Azlier after meaning review;
  record sourced pledge/faction terminology and the provisional Elgo Inscription title.
- Support empty internal continuation fragments when their English was consolidated
  within the same dialogue group; still reject empty whole groups and menu labels.
  Prevent overlapping old review proofs from hiding unapplied corrections.
- Verify all newly accepted scenes through the compiler; resource 295 uses 485,348
  decoded bytes and 4,032 pages, within the 491,520-byte allocation. Seven focused
  compiler/storage tests plus the review-overlap regression pass. Gameplay remains
  unverified; no ISO, patch, release or translator-sheet overwrite in this pass.


- Chapter 12 checkpoint: add 2,001 independently reviewed story fragments,
  bringing new-story draft coverage to 18,466 of 43,668 (25,202 remaining).
  Main resource 318 now covers 3957–5556; its remaining 1,516 fragments start 5557.
  Complete and accept all ten remaining Chapter 12 companion scenes 328–337.
- Correct reversed requests and atonement references, duplicated sentences,
  shifted reactions, empty complete dialogue boxes, direct-address pronouns,
  and Misumi's reference to her late husband. Preserve exact source control
  tokens and record unresolved readings without inventing character identities.
- All ten newly accepted companion scripts pass in-memory compilation, allocation,
  original display-call simulation and Night Talk paging checks. Main 318's
  1,600 new rows pass encoding/control checks; 763 complete dialogue groups and
  four direct labels pass nonempty/width checks. Main 318 remains incomplete
  and has not undergone full-resource compilation or gameplay validation.
- Preserve translator-sheet edits and released snapshots; no Google Sheet update,
  ISO, patch or release produced at this checkpoint.


- Complete Chapter 12 main resource 318 with 1,516 additional story fragments
  (rows 5557–7072), bringing draft coverage to 19,982 of 43,668 new fragments;
  23,686 remain. All Chapter 12 main and companion scenes are now accepted.
- Independently review complete VM dialogue groups and correct shifted battle
  lines, reversed actors, duplicate clauses, missing silent reactions, and
  protagonist-dependent pronouns. Preserve Instructor for the military role
  and normalize Crimson Gloves after meaning corrections.
- Verify the complete main script at 479,716 decoded bytes within its
  491,520-byte allocation: 7,073 source rows, 3,438 groups and 3,823 pages.
  Original display calls, live strings, unrelated instructions and special-field
  width checks pass. Record source-bound review and correction receipts.
- Continue next at Chapter 13 main resource 341 row 2053. No gameplay validation,
  Google Sheet update, ISO, patch or release is included in this checkpoint.

## 0.1.53 - Teacher terminology, 2026-09-30

- Investigate the reported v0.1.52 Status crash: released CRC matches; a
  graphics metadata pointer is null. Root cause and runtime fix remain pending.
- Replace Professor with Teacher in nine distinct battle-dialogue passages,
  including all shared copies. Preserve casing, speakers, script flow and layout.
- Record Teacher as the preferred term for future translations.
- Keep published translation inputs and released patches unchanged.

## 0.1.52 - Cooking title alignment, 2026-09-30

- Release packaging: retain only original-to-v0.1.52 and published v0.1.41-to-v0.1.52 patches; withdraw local-test upgrade assets and synchronize the catalog and checksums.
- Add a local v0.1.47 to v0.1.52 upgrade xdelta; verify both input ISO hashes
  and the complete reconstructed v0.1.52 ISO against its released SHA-256.
- Center Pirate Lunch and all 29 recipe titles by their proportional ink width
  inside the existing orange banner. Only the recipe-title renderer call changes.
- Execute the existing centered packer for every title at two relocated load
  addresses; verify exact pixels, banner bounds, cache and stack boundaries.
- Retain the cumulative crash guards, Inventory fixes and translations from
  v0.1.42 through v0.1.51. See `docs/RELEASE_0.1.52.md` for test coverage.

## 0.1.51 - Armor names and stat spacing (test build), 2026-09-30

- Translate all 92 remaining Japanese armor names, including the eight
  untranslated names on the reported Inventory screen.
- Recognize the two omitted native stat symbols when positioning help rows;
  preserve normal text VWF, description bytes and equipment values.
- Check 155 armor-name references, 1,434 unchanged equipment outputs and
  131,072 relocated stat-prefix cases, plus the cumulative safety audit.
- Fresh-boot PPSSPP verification passes for the reported armor selection and
  Black Rose Knife; all three xdelta patches round-trip to the verified ISO.
- See `docs/ARMOR_0.1.51.md` for the cause, verification and test limits.

## 0.1.50 - Inventory names and description layout (test build), 2026-09-30

- Translate all 76 remaining Japanese weapon names, including Glass Edge,
  Chinese Cleaver, Harsneil and Ragres Saber from the reported screen.
- Reflow equipment descriptions that need more than two rows into the
  Inventory help panel. Preserve stats, effects, restrictions and key labels;
  retain existing one- and two-row output unchanged.
- Check all 1,434 equipment/key-item variants against the two-row limit,
  native glyph pool, output buffer and stack boundaries, and content retention.
- Preserve the v0.1.49 shared help and malformed-glyph guards.
- Verify the weapon list and two-row Black Rose Knife description in a fresh
  PPSSPP 1.20.4 session; round-trip check original, 0.1.42 and 0.1.49 patches.
- See `docs/INVENTORY_0.1.50.md` and the build's validation reports for scope.

## 0.1.49 - Shared text safety guards (test build), 2026-09-29

- Guard shared help staging against oversized rows, glyph-pool overflow and
  invalid source addresses before copying text into native buffers.
- Guard the native font-map lookup against malformed two-byte glyph cells.
  Use bounded fallback text/glyphs and record diagnostic rejection counters.
- Require combined candidate audits in the new build and patch packaging
  workflow; extend coverage to skills, Cooking and System menu checks.
- Pass nine audit groups, including 1,434 equipment variants, 235 spells,
  753 unit labels and 131,072 relocated glyph-input cases.
- Fresh-boot PPSSPP 1.20.4: normal Chapter 15 Continue, Brave Goals,
  inventory/Black Rose Knife and Summon Index spell help pass. Live overlong
  text and malformed-glyph injections are contained without a memory fault.
- Add an ISO-bound runtime coverage report and release preflight. Stable
  release checks reject remaining untested hub, save/reload and story paths.
- Provide round-trip verified original, v0.1.42 and v0.1.48 input patches.
  Historical hashed inputs are unchanged. See `docs/STABILITY.md` for scope.

## Unreleased - Stability tooling, 2026-09-29

- Add a read-only combined regression audit for a selected built ISO.
- Validate actual ISO identity, executable and cached-table consistency,
  unit-label encoding, Brave Goal termination, and native equipment/spell
  formatter and staging bounds. Exit unsuccessfully if any check fails.
- Audit v0.1.48: 753 unique labels, 1,434 equipment variants, 235 spell
  descriptions and ten Brave Goal title/help cases pass. Historical broken
  cases from v0.1.41, v0.1.46 and v0.1.47 are rejected.
- Document coverage gaps and the proposed release stability process.
  No ISO or previously hashed build input changes.

## 0.1.48 - Summon Puppet name crash fix (test build), 2026-09-29

- Correct Rexx and Aty default unit names from single-byte ASCII to the
  two-byte encoding required by the puppet/status text renderer.
- Update all eight default-name references in both resident and bank copies.
  Preserve spellings, player-entered names, gameplay data and executable code.
- Audit 753 unique labels and 2,312 references across 784 unit records.
- Verify the reported state resumes after the name-only correction, Rexx
  selection works, and the puppet menu can exit and reopen showing Aty.
- Provide verified upgrades from v0.1.47 and v0.1.42, plus the original-source
  patch. See `docs/PUPPET_CRASH_0.1.48.md` for evidence and test scope.

## 0.1.47 - Equipment description crash fix (test build), 2026-09-29

- Add a direct v0.1.42-to-v0.1.47 upgrade patch; verify exact ISO reconstruction.
- Fix Black Rose Knife help overflowing the native 54-glyph object pool
  when browsing weapons in the protagonist's room.
- Compact only over-budget equipment descriptions, including Sleep Rose
  Knife and an accessory with several immunities. Preserve numeric stats,
  effects, restrictions, native stat symbols, and descriptions already fitting.
- Check all 717 nonzero equipment records with both key-item states through
  the native formatter and help staging loops (1,434 cases). Reproduce the
  previous build's overflow at object index 54 before checking the fix.
- Preserve prior localization and crash fixes. See
  `docs/EQUIPMENT_CRASH_0.1.47.md` for evidence, patch inputs, and test limits.

## 0.1.46 - Cooking localization (test build), 2026-09-29

- Translate 29 recipes, their inventory name copies, 25 ingredient names
  and ingredient descriptions, Cooking controls and quantity prompts.
- Add concise six-row recipe descriptions; keep full English meanings in
  the translation catalog. Preserve the existing 78-object text allocation.
- Add proportional recipe text with the original food-icon indentation,
  plus proportional headings, ingredient names and controls.
- Translate the Cooking title and Ingredients book/list artwork. Preserve
  every book pixel outside the Ingredients heading replacement.
- Keep recipe costs, quantities, effects and gameplay data unchanged.
- Verify all 29 native recipe-loading cases, 3,044 relocated text-position
  cases and both original-source / 0.1.45-upgrade patch round trips.
  Live Cooking-screen verification awaits a suitable normal save; see
  `docs/COOKING_0.1.46.md` for evidence and limits.

## 0.1.45 - Status stance label width (test build), 2026-09-29

- Shorten Mana Guard to MP Guard and Magic Resist to M. Resist so their
  names fit the shared status field without covering the DF statistics.
- Check all 17 distinct stance labels against the 70-pixel field using the
  game font metrics at the native status scale.
- Preserve stance effects, descriptions, executable code and prior fixes.
- Provide verified original-source and 0.1.44-upgrade xdelta patches.
  See `docs/STANCE_WIDTH_0.1.45.md` for measurements and runtime limits.

## 0.1.44 - System menu localization (test build), 2026-09-29

- Translate Status, Cooking and Gallery graphics in both selection states,
  including matching copies of each resource.
- Translate all four conditional Status help strings for equipment, skills
  and summoned-unit status/training.
- Check all six unlock combinations through the native text writer, with
  two-line bounds and buffer guards; retain the Brave Goals regression checks.
- Preserve all prior build inputs and fixes.
- Provide full and 0.1.43-upgrade patches with exact reconstruction checks.
  Fresh Continue passes; exact System hub runtime verification remains open.
  See `docs/SYSTEM_MENU_0.1.44.md` for evidence and artwork provenance.

## 0.1.43 — Ishlar weapon menu translation (test build), 2026-09-28

- Translate Generasneil, Fell Wildfire, Tyrant's Rampage and Ishlar's two
  shared battle-name references, following the current name glossary.
- Translate all 16 copies of the adjacent-target sword-art help description
  into two bounded lines, with explicit empty-line termination.
- Enable the existing safe VWF wrapper at the weapon heading's separate
  renderer call so Generasneil displays in full.
- Preserve gameplay values and the 0.1.42 Brave Goals fix. Native staging,
  heading fallback/relocation, archive and cumulative input checks pass.
- Supply original-source and 0.1.42-upgrade xdelta patches, each verified
  against the final ISO. See `docs/WEAPON_REPORT_0.1.43.md` for runtime evidence.

## 0.1.42 — Brave Goals crash fix (test build), 2026-09-28

- Package full Japanese-source and 0.1.41-upgrade xdelta patches; verify
  that both reconstruct the exact 0.1.42 ISO.
- Fix all five translated Brave Goal help bundles: add empty-line terminators
  and keep descriptions within two 27-cell lines and the 54-glyph pool.
- Shorten the five associated goal labels to fit their list rows.
- Reproduce the reported `0x29` memory fault on 0.1.41 from both the supplied
  state and a fresh Continue load followed by Battle Info > Brave Goals.
- Verify 0.1.42 Continue, all five goal selections and menu exit with strict
  memory checks in PPSSPP 1.20.4. Native copy guards and ISO checks pass.
- Gameplay conditions and executable code are unchanged. Fresh-boot and load
  the in-game save; a pre-fix emulator state retains old data.
- See `docs/BRAVE_FIX_0.1.42.md` for evidence and test limits.

## 0.1.41 — Learn Skills localization and VWF (test build), 2026-09-28

- Diagnose a reported Continue crash: release CRC matches; the fault maps to
  a native text-renderer object. Copied-save fresh boots also pass with strict
  memory-error handling. Subsequent state analysis confirmed a Brave Goals
  text overflow, repaired in 0.1.42; see `docs/CRASH_CONTINUE_0.1.41.md`.
  No 0.1.41 release bytes changed.

- Publish the cumulative 0.1.37–0.1.41 changes with a full Japanese-source patch
  and an upgrade from public 0.1.36, in the Retro Trans release format.
  See `docs/RELEASE_0.1.41.md` for release scope and remaining test limits.
- Verify public Retro Trans 0.3.1 catalog discovery, Latest routing, real asset
  download and Automatic upgrade output hash. See `docs/RETRO_TRANS_0.1.41.md`.

- Translate Learn Skills, Common/Unique tabs, footer controls and 31 common or
  reported skill-name entries. Enable scoped VWF for skill cards and footer text.
- Shorten Pact titles to fit the card renderer. Wrap crafting descriptions at
  affinity boundaries so the closing bracket stays with its text.
- Pass 15 native name cases, 31 description cases, 108 relocated VWF checks,
  ISO integrity checks and a fresh boot. Exact unlocked-screen verification is
  pending because the screenshot was submitted by another user without a save.
- See `docs/SKILLS_0.1.41.md` for scope, assets and verification limits.

## 0.1.40 — Accessories and Deployment prompts (test build), 2026-09-28

- Translate the 25 remaining accessory names, including all Japanese entries
  shown in Dritol's Combine list, and shared equipment-effect wording.
- Fix missed branch references for Learn Skills and Key Item.
- Prevent long ailment groups from overrunning their native scratch buffer;
  preserve item stats, recipes and native stat-symbol spacing.
- Pass 240 native formatter cases and archive checks. Fresh boot, copied-save
  load and early Deployment layout verified. Exact unlocked UI and long-effect
  visual layout remain pending. See `docs/ACCESSORIES_0.1.40.md`.

## 0.1.39 — Repeated boat dialogue (test build), 2026-09-28

- Removed the unintended repeated request to hurry to the boat in Aty's
  Chapter 1 dialogue. Two adjacent translation batches had translated the
  same phrase; the Japanese contains it only once.
- Reused the correct two-line wording, preserving this branch's speaker and
  continuation. Verified all other 619 dialogue groups in the script unchanged.
- Kept prior nameplate and Night Talk fixes. See `docs/REPETITION_0.1.39.md`.

## 0.1.38 — Sonolar nameplates (test build), 2026-09-28

- Translated Sonolar's ordinary dialogue and battle nameplates, including both
  text and shadow layers. The selected SN6 character reference supplies the spelling.
- Preserved portraits, expressions, native palettes, and the 0.1.37 Night Talk fixes.
- Verified the imported sprites at native size and checked archive repacking,
  compression round trips and untouched resources. See `docs/SONOLAR_0.1.38.md`.

## 0.1.37 — Night Talk layout and names (test build), 2026-09-28

- Identify Night Talk by native display modes 4/5 and reflow 1,348 translated
  dialogue groups in 76 scene resources to two lines per page.
- Use the wider Night Talk text area while retaining the 31 expanded-cell
  limit, control tokens, speaker arguments, and original scene continuation.
- Translate all 19 blue Night Talk nameplates, using the selected character
  reference (including Belfraw). Portraits and unrelated dialogue are preserved.
- Static script, archive, and native-image checks passed. Normal Night Talk
  playthrough verification is pending a suitable save; this is a local test
  build, not a published release. See `docs/NIGHT_TALK_0.1.37.md`.

## 0.1.36 — Gallery tutorial list, 2026-09-28

- Translated all 22 tutorial title records as Review Basics with proportional spacing.
- Shortened Weapons & Range to prevent Comment/Page column overlap.
- Translated Illustrations/Sound headings and the View, Sound Mode, Exit,
  Play and Artwork mode controls in native graphics.
- Preserved locked entries and unrelated assets. See `docs/GALLERY_0.1.36.md`
  for verification and the remaining Gallery translation scope.

## 0.1.35 — Menu descriptions and generic enemy names, 2026-09-28

- Updated release metadata to the Retro Trans v1 contract without changing the
  published patch or game bytes. Tested Retro Trans 0.3.1 manual patching,
  catalog import, recognition, version routing and Automatic patching with
  locally staged assets; both outputs match the complete target SHA-256.
  Made the repository public with maintainer approval and enabled catalog
  discovery. Verified public catalog refresh, real patch download and full
  Automatic output hash. See `docs/RETRO_TRANS_0.1.35.md`.

- Prepared the initial GitHub source snapshot and full Japanese-to-English
  xdelta release, with SRW-Z-style instructions, checksums and build metadata.
  Reworked the README around installation, contribution and coverage limits.

- Translated 24 additional menu-help groups, including the separate battle Summon Index description.
- Translated 39 generic enemy labels across 164 references, including Pirate.
- Checked all 58 menu-help references for English text and safe two-line layout.
- Verified Summon Index help and Pirate in compact/full status after a fresh launch
  with a 0.1.34 in-game Suspend save. See `docs/MENU_ENEMIES_0.1.35.md` for coverage.

## 0.1.34 — Battle menu and saving-message translation, 2026-09-28

- Translated eight battle-menu labels and four Battle Info labels.
- Translated both system-saving message lines with proportional spacing.
- Checked the battle menus and saving popup
  after a fresh launch with an in-game save. See `docs/BATTLE_MENU_0.1.34.md`.

## 0.1.33 — Battle magic heading translation, 2026-09-28

- Applied existing saved-name translations to the battle magic heading.
- Added proportional rendering for the heading; custom names and saves are preserved.
- Checked Dritol, Shine Saber and return to commands
  after a fresh launch with an in-game save. See `docs/MAGIC_HEADING_0.1.33.md`.

## 0.1.32 — Start Battle confirmation VWF, 2026-09-27

- Applied proportional spacing to "Start battle?", "Yes" and "No".
- Centered all three lines and retained the native choice behavior.
- Checked both cursor positions and cancellation
  after a fresh launch with an in-game save. See `docs/CONFIRM_VWF_0.1.32.md`.

## 0.1.31 — Locked-feature popup translation, 2026-09-27

- Translated the locked-feature popup as "Not available yet."
- Centered its English text using proportional spacing.
- Checked the popup, dismissal and map return
  after a fresh launch with an in-game save. See `docs/LOCKED_FEATURE_0.1.31.md`.

## 0.1.30 — Battle Info help wrapping, 2026-09-27

- Fixed the split word and missing spacing in the Win/Lose description.
- Fixed Party Abilities help to fit the actual 27-cell display limit.
- Checked all four Battle Info descriptions, conditions popup and map return
  after a fresh launch with an in-game save. See `docs/BATTLE_HELP_0.1.30.md`.

## 0.1.29 — Deployment VWF and shortcut alignment, 2026-09-27

- Applied proportional spacing to deployment name, class, attack and stance.
- Packed support-skill description chunks with proportional spacing.
- Aligned the Deploy, Status/Gear and Map icons with their labels.
- Verified Aty, Soldier, equipment view and return to map after a fresh launch.
  See `docs/DEPLOYMENT_0.1.29.md`.

## 0.1.28 — Stance crash fix, 2026-09-27

- Fixed oversized stance descriptions and missing end markers that made
  opening the Stance submenu overrun the native text buffers.
- Added bounded two-line descriptions and checked related stance records.
- Verified Guard/Counter selection, reopening and return to play from a fresh
  launch with an in-game save. See `docs/STANCE_FIX_0.1.28.md`.

## 0.1.27 — tutorial notice VWF and Pact Ritual, 2026-09-27

- Centered the Gallery tutorial notice using proportional letter spacing.
- Translated Pact Ritual skill names, including 15 single and combined affinity variants,
  and the dynamically assembled summon-crafting description.
- Verified the notice, Machine/Neutral skill menu and return to play from a
  fresh launch with an in-game save. See `docs/UI_FIXES_0.1.27.md`.

## 0.1.26 — remaining summon labels and Kyle nameplate, 2026-09-27

- Translated the locked-spell Favorites Only restriction while preserving its
  question marks, and added Shine Saber's attack name with proportional text.
- Replaced Kyle's portrait nameplate and shadow layer with English lettering.
- Corrected inventory stat-value spacing; retained the existing text VWF.
- Fresh-launch testing uses a copied in-game save. See
  `docs/UI_FIXES_0.1.26.md` for scope and evidence.

## 0.1.25 — battle commands and tutorial prompts, 2026-09-27

- Translated seven unit-command buttons and the tutorial Next graphic.
- Translated the Gallery tutorial notice and Shine Saber description.
- Kept the description within the native help limits; checked its complete
  display with proportional spacing. The notice keeps native fixed spacing.
- Fresh launch with an in-game save verifies the tutorial transition, commands
  and summon help in the first pirate battle. Earlier chapter work is retained.
- See `docs/BATTLE_UI_0.1.25.md` for asset locations and validation limits.

## 0.1.24 — battle dialogue through Chapter 8, 2026-09-27

- Translated 528 main-battle fragments, 8 early side-battle candidates, and
  1,140 shared repeatable-battle conversation fragments. Updated all 31 copies
  of the shared script: 53 battle packs in total.
- Retained full dialogue with proportional text and additional pages; preserved
  speaker selection, player placeholders, event flow and previous UI fixes.
- Verified every rewritten display span and unchanged archive resource. Fresh
  in-game save testing confirms the first pirate battle speech and added pages.
  Other routes have static validation; no eight-chapter playthrough is claimed.
- See `docs/BATTLE_DIALOGUE_0.1.24.md` for coverage and limits.

## 0.1.23 — compact unit-card VWF, 2026-09-27

- Applied proportional spacing to the unit name, attack, and defense fields on
  the compact battle-map status card. Attack text no longer crowds the shield.
- Replaced the fixed eight-cell bindings with actual-length VWF bindings;
  the reused renderer packs up to 16 cells. Existing wording and numeric fields
  remain unchanged.
- Checked all 328 translated unit/class labels against the name-field width;
  verified Aty, another unit, and selection refresh after a fresh save load.
- All data banks and prior fixes are unchanged. See `docs/CARD_VWF_0.1.23.md`.

## 0.1.22 — battle-map shortcut VWF, 2026-09-27

- Applied proportional spacing to the blue battle-map shortcut panel. Unit List
  and Battle Status now fit without shortening their names or resizing the box.
- Reused the existing bounded VWF renderer through one font-binding call;
  translations, button icons, resource banks, and prior crash fixes are unchanged.
- Verified unit-selected and empty-tile menus after a fresh launch with a copied
  in-game save, plus Battle Prep entry and return. See `docs/MAP_VWF_0.1.22.md`.

## 0.1.21 — spell effect descriptions, 2026-09-27

- Translated the selected-spell descriptions across all 235 populated spell
  records: 18 shared literals, 12 custom groups, and 30 possession effects.
- Retained proportional text, controller glyphs, numerical values, and all five
  previous menu crash fixes. Updated both resident and bank table copies.
- Checked all 235 descriptions with the native formatter and buffer guards;
  verified all 42 table groups in live memory and the shared text references.
- Fresh launch with a copied in-game save verified Battle Prep and Dritol's
  Drill Blow, Drill Rush, and Drill Hurricane descriptions.
- Long platform descriptions use defined abbreviations to preserve exceptions.
  See `docs/DESCRIPTIONS_0.1.21.md` for scope, notation, and verification limits.

## 0.1.20 — proportional menus and saved summon names, 2026-09-27

- Added real variable-width rendering to inventory and Summon Index lists,
  descriptions, menu help, and the Type control; centered the empty-list None label.
- Translated Key Item and remaining empty/equipment-list messages in seven source groups.
- Replaced six native Summon Index control/range sprites in all four matching packs.
- Fixed cached Japanese default summon names from loaded saves at display time:
  121 unique known names/forms, including Dritol on both index and detail pages.
- Verified the final ISO from a fresh launch and copied in-game battle save, with
  screenshots. Preserved all five previous crash fixes. 876 emitted-MIPS cases pass.
- Other battle-map shortcut/status spacing remains outside these tested menu paths.
  See `docs/MENU_0.1.20.md` for validation and limits.

## 0.1.19 — summon names and affinity icons, 2026-09-27

- Added 68 base summon-name translations; all 87 populated base-name entries
  now resolve to English, including the existing Dritol and Shine Saber.
- Used ImageGen to replace the five native affinity tiles with M (Machine),
  O (Oni), S (Spirit), B (Beast), N (Neutral), preserving colors and borders.
  Updated all 20 exact matching occurrences across four interface packs.
- Shortened the clipped top-right Affinity control to Type.
- Corrected source-to-name mapping errors found during independent draft
  review before insertion. Unreviewed aliases and descriptions are not claimed
  as translated; unofficial proper-name romanizations remain provisional.
- Verified cached table copies, all 23 bank indexes, 5,724 unchanged resources,
  and all historical input hashes. Preserved the 0.1.17 crash fixes.
- User clarified the screenshot was from 0.1.17. Exact runtime cause of its
  Japanese Dritol label remains unconfirmed; current table pointers were checked.
  Live visual verification of this release is pending. See `docs/SUMMON_0.1.19.md`.

## 0.1.18 — status, equipment and summon labels, 2026-09-27

- Added 732 translated labels: 328 unit/class names, 307 equipment names,
  96 summon/form/spell names and the empty equipment label (None).
- Includes Soldier, Guard, Rock Mail, Study Manual and Shine Saber; verified
  that the existing Dritol pointer still resolves to English.
- Shortened seven attack/defense labels to fit their narrow status fields:
  VSlash, HSlash, Spec., VThrow, HThrow, Guard and Cntr.
- Independently reviewed meanings and compact labels. Rejected mechanical
  name conversions; uncertain names remain deferred. This is a partial
  category expansion, not a complete class/equipment/summon translation.
- Preserved the five 0.1.17 crash-fix regions byte-for-byte and repeated their
  native glyph-capacity checks. Rebuilt and verified both cached table copies.
- Verified 856 build inputs, 23 bank indexes and 5,727 unchanged resources.
  Runtime visual verification is pending. See `docs/STATUS_0.1.18.md`.

## 0.1.17 — Battle Prep crash hotfix, 2026-09-27

- Fixed a native help-rendering capacity overrun introduced in 0.1.15 and
  inherited by 0.1.16. Deployment used 56 character objects and Party Abilities
  used 58, while their renderer allocated only 54. Both now use 49 objects.
- Preserved the complete meaning through independent review; corrected related
  status-help widths and wrapped the cursor-direction hint at word boundaries.
- Added checks for total glyph-object capacity, per-line storage, terminators
  and staging-buffer size. Both previous overflowing groups fail the regression
  check; all 19 audited help groups pass with the fix.
- Only five existing English text regions change (129 ELF bytes). Every other
  ISO file, including all 23 resource banks, matches 0.1.16 exactly.
- User confirmed the crash occurred after fresh launch and loading an in-game
  save. The earlier save-state explanation does not explain this defect.
- Live Battle Prep confirmation is pending user navigation. See
  `docs/CRASH_0.1.17.md` for evidence and validation limits.

## 0.1.16 — battle submenus, inventory and options, 2026-09-27

- Translated deployment/status hints, support labels, the two reported weapon
  names, the Dritol summon entry, options labels/help and Summon Index heading.
- Fixed the garbled class label with two-byte Tutor text at all six references.
- Shortened overflowing defeat conditions to Protagonist KO and All allies KO.
- Added 46 native sprites across 89 resource occurrences, including alternate
  unselected submenu states and ImageGen options/Summon Index artwork.
- Verified 843 input hashes, 23 indexes, 32 unchanged ISO files and 5,707
  unchanged resources. Chapter 1–8 dialogue is inherited unchanged.
- Diagnosed old executable state in the user's emulator. Fresh boot and a
  normal in-game save are required to test new executable translations.
- Scope, provisional spellings and visual-test limits: `docs/MENU_0.1.16.md`.

## 0.1.15 — battle preparation menu, 2026-09-27

- Translated the backlog voice-playback control as Replay and nine executable
  attack-style labels, including H. Slash and V. Slash.
- Replaced ten menu button designs in both selected and unselected states,
  covering 75 occurrences across ten resource packs. Includes Battle Prep,
  Deployment, Battle Info, Inventory, Summon Index, Options, Save, Load,
  Start Battle and the related Party Abilities button.
- Translated the menu descriptions and wrapped them into native line records,
  with at most three lines and 30 characters per line. Preserved complete wording.
- Preserved 0.1.14's story translations and published inputs. See
  `docs/MENU_0.1.15.md` for validation and runtime limitations.

## 0.1.14 — Chapters 4–8, 2026-09-27

- Translated all identified main dialogue, route alternatives, optional/night
  conversations, and shared school/minigame dialogue used by Chapters 4–8:
  18,950 distinct fragments, covering 31,206 occurrences in 71 scripts.
- Applied 757 meaning corrections. Independent review covers 4,193 distinct
  fragments; the remaining 14,757 have translator self-checks.
- Applied the selected character-name reference to new dialogue and backlog
  labels while preserving player-entered names and released build inputs.
- Added versioned compilation that wraps dialogue across pages, handles inline
  dialogue calls, reuses replaced instruction space, and compacts duplicate or
  unreferenced string storage. Static checks compare every live string and
  simulate each rewritten dialogue span. Four compiler regression tests pass.
- Built `work/output/0.1.14/Summon_Night_3_EN_0.1.14.iso`. Verified 817 input
  hashes, 34 unchanged files, 4,341 unchanged bank resources and 23 indexes.
- Isolated PPSSPP fresh boot passed; all 161 inherited English executable
  bundles matched live memory. New chapter routes and layouts have not received
  a full playthrough. Details and terminology limits: `docs/CHAPTERS_0.1.14.md`.

## Character-name reference update — 2026-09-27

- Adopted the user-selected Summon Night 6 PS Vita Gallery as the primary
  character-name spelling reference and recorded the preference in AGENTS.md.
- Added a 43-character SN3 glossary overlay with gallery aliases, short forms,
  and previous project spellings for lookup. This supersedes older spelling
  locks for future work; released ISO inputs remain historical snapshots.
- This reference update does not produce a new ISO.

## 0.1.13 — battle interface and encounter artwork, 2026-09-27

- Translated 477 battle text strings: deployment/actions, help, confirmations,
  status/attack labels, standby skills and Brave Battle objectives.
- Replaced all 55 distinct text sprites in the discovered encounter-card family,
  covering 611 duplicate uses in 80 packs, including VS Pirates and victory/loss
  conditions. Retained the original backgrounds and native palettes.
- Added 13 English tutorial pages for movement/ZOC, facing/height, weapons,
  standby, ailments, obstacles and skills using native image assets.
- Preserved the 0.1.12 story translation and other existing patches. The build
  verifies unchanged files/resources and all archive indexes.
- Known remaining scope and verification limits: `docs/BATTLE_0.1.13.md`.
- Final checks passed: 377 input hashes, 32 unchanged files, 5,635 unchanged
  resources, 23 indexes, isolated PPSSPP fresh boot, and all 161 English
  executable bundles in live memory. Battle gameplay/layout remains unverified.

## Verification follow-up — stale cabin script, 2026-09-27

- Matched the reported corridor line to Chapter 1 rows 905–906 and verified its
  English translation and surrounding branches in the actual 0.1.12 ISO.
- Read-only inspection found the running emulator still held the 0.1.3/0.1.4
  story script. Documented how to boot the current ISO using an in-game save;
  no game-state changes or redundant ISO rebuild were made. See
  `docs/STALE_SCRIPT_0.1.12.md`.

## 0.1.12 — three chapter story translation candidate, 2026-09-27

- Added 5,533 reviewed story fragments to the previous selection, bringing the
  bounded opening/Chapter 2/Chapter 3 story scope to 6,174 fragments.
- Covered all 1,428 opening rows, the 1,711-row Chapter 2 unique tail, the
  2,319-row Chapter 3 unique tail, and 716 rows across 18 chapter-specific
  night-talk resources. No rows are excluded from this scoped story set.
- Accepted meaning reviews and passed 20 chapter/compiler static validations,
  including branches, direct menus, conditional rows, control tokens,
  relocation, prior translations, and source-pool preservation.
- Retained earlier UI, artwork, and audio. Newly introduced portrait nameplates
  may remain Japanese; this does not claim that all UI is translated.
- Added English runtime pupil names and backlog labels for the new cast, and
  corrected Phlaiz's introduction and final glossary spellings after review.
- Final ISO passed file integrity and bounded fresh-boot, name-entry, live-script
  hash, and English harbor rendering checks. The cabin checkpoint and Chapters
  2–3 were not played through; full runtime acceptance is not claimed. Next: 0.1.13.

## 0.1.11 — complete opening/harbor text selection, 2026-09-26

- Added all 17 remaining source fragments, including emphatic Salome dialogue,
  both pupil-gender continuations, an exclamation with its music note, and the quiz.
- Kept the original special display style and reflowed eight complete groups
  without shortening their meaning. The 641-fragment opening/harbor selection
  now has no exclusions; compiled source order includes alternate branches.
- Located the separate backlog speaker table and translated seven glossary names
  in all three copies (63 references). Prior graphical nameplates are retained.
- Passed source/coverage, helper-flow, compression and ISO integrity checks;
  preserved 34 unrelated files and 4,411 untouched bank resources.
- Fresh-boot final-ISO PPSSPP verified both reported emphatic groups on the
  Belfrau route, Salome's backlog name, complete loaded name/script data, and
  normal continuation. All 206 workspace integrity checks pass. Other new
  branches have static checks; later scenes remain unfinished. Next: 0.1.12.

## 0.1.10 — harbor gaps and character nameplates, 2026-09-26

- Added 12 harbor choice rows across protagonist/pupil branches and the three-part
  player-name introduction; retained the runtime name and complete meaning.
- Generated five native English nameplates (Belfrau, Salome, Nup, Alieze, Will),
  replacing both name and silhouette layers in all 10 matching portrait packs.
- Checked fresh boot, harbor choices, name substitution, Salome's nameplate and
  normal continuation in isolated PPSSPP. Other routes remain statically checked.
- Preserved 34 unrelated ISO files and 4,404 other resources in changed banks,
  including prior audio, chapter cards and the 0.1.9 backlog fix.
- Opening/harbor coverage: 624/641 source rows. Next version: 0.1.11.

## 0.1.9 — backlog spacing, 2026-09-26

- Fixed widely spaced English speaker names and dialogue in history by packing
  original glyph ink in native texture strips and measuring each strip's advance.
- Preserved complete text, glyph shapes, Japanese fallback and cache reuse.
- Passed 202 emitted-instruction checks and fresh-boot PPSSPP checks for backlog
  display, scrolling, closing, ordinary dialogue and reopening with new entries.
- Kept all 35 other ISO files byte-identical to 0.1.8. No new translations.
- Next version: 0.1.10. Restart the game; old emulator states retain old code.

## 0.1.8 — chapter-title artwork, 2026-09-26

- Translated and independently reviewed 30 distinct titles across all 16 numbered
  chapters, the final chapter, five side stories, a bonus title and seven endings.
- Redrew complete cards with built-in imagegen and inserted all 31 native instances,
  including both Chapter 2 copies. Preserved original English subtitles and audio.
- Inspected every decoded native card; verified transparency, pack round trips,
  unchanged descriptors/palettes, audio identity and final ISO structure.
- Reached Chapter 1 naturally in isolated PPSSPP and checked its display, fade-out
  and return to the beach. Other title branches remain unplayed.
- Preserved prior translations. Separate executable title metadata and other
  untranslated game text remain outside this artwork build. Next version: 0.1.9.

## 0.1.7 — image-generated menu artwork, 2026-09-26

- Rebuilt the complete character-selection banner and Confirm button with the
  built-in image generator to remove visible paint-over patches and improve style matching.
- Inserted both assets in Rexx and Aty packs using the native palette and geometry.
  Saved original generated images, exact prompts and native conversion records.
- Checked both protagonist screens in PPSSPP and verified untouched sibling
  graphics/resources. Preserved the executable and all prior translations.
- Next unused version is 0.1.8. Remaining translation and full-game QA scope is unchanged.

## 0.1.6 — setup screen fix, 2026-09-26

- Inserted native English graphics for both protagonists, all four summon
  affinities and name entry, including normal and highlighted button labels.
- Added English default names, confirmation and empty-name messages; made
  ABC/123 the initial keyboard. Fixed unsupported quote glyphs found in testing.
- Preserved all 609 dialogue/choice entries and the existing font code.
- Verified native texture round trips, unchanged contents and ISO structure.
  Inspected PPSSPP setup screenshots and tested Delete, Auto-Name, confirmation
  and transition to the translated opening. User emulator state was untouched.
- Other interface categories, the harbor banner and most dialogue remain
  Japanese. Full gameplay acceptance remains open; next version is 0.1.7.

## 0.1.5 — opening and harbor test ISO, 2026-09-26

- Built 609 reviewed dialogue/choice entries plus three character labels; 531 more
  dialogue entries than 0.1.4. Includes the three supplied dialogue screenshots.
- Reflowed 188 complete groups and added 41 continuation pages without shortening
  text. Simulated every generated group and verified unchanged branch/menu code.
- Retained 32 source rows in Japanese: 29 awaiting display/choice/name support and
  three unresolved quiz rows. Setup graphics and the location banner remain Japanese.
- Verified the complete ISO structure, unchanged contents, labels, script
  compression, text references, page bounds and review provenance. Reused the
  existing 192-object font patch. Runtime/gameplay testing remains pending.
- Preserved all earlier builds; next unused version is 0.1.6.

## Unreleased — opening and harbor dialogue, 2026-09-26

- Matched the four supplied screenshots to the opening recollection, harbor
  reflection and Adnias Harbor banner. Preserved the original screenshots with
  hashes, dimensions and source-row anchors without exporting Japanese scripts.
- Added a separate nine-entry harbor glossary with sourced character spellings,
  roles and gender evidence. Adnias Harbor and Pastis remain explicitly marked
  project romanizations; unresolved profile details are not guessed.
- Extended translation through the harbor student branches and departure
  reflection in bounded 80-row assignments. Original drafts and independent
  reviews remain preserved; complete sentences crossing assignments are combined
  before scripted name normalization in a separate successor catalog.
- Consolidated 638 reviewed English source rows in the 641-row scope,
  including prior work and two completed boundary rows. Three quiz rows remain
  unresolved. Source order includes alternate routes and sentence fragments.
  Applied 2 meaning/boundary text changes; glossary scan made
  0 spelling changes. Checked every source/review identity, complete group,
  control token and encoded target. Original drafts and earlier builds remain intact.
- This translation pass does not create an ISO or change the running emulator.
  Latest playable build remains 0.1.4; next unused version remains 0.1.5.

## Unreleased — setup translations and all-interface discovery, 2026-09-26

- Confirmed scope as all game interface text. Translated the five supplied
  screenshots and related setup/options variants, including all four summon
  affinities. Consolidated 64 independently reviewed translation records
  (51 distinct English texts), six preserved data records and seven unresolved
  tiny-thumbnail records. Source drafts and independent reviews are immutable.
- Corrected the blurry name-entry tab to Kanji using native graphics. Verified
  Auto-Name in the executable: restore protagonist default; cycle through preset
  summon names. Preserved runtime name composition and controller symbols.
- Added nine reviewed UI glossary terms separately from the existing four core
  entries. Ran glossary normalization after meaning review; no spelling changes
  were needed. Preserved the proposed glossary and its review provenance.
- Indexed 3,633 shared-table strings in 20 tables, including 459 with unresolved
  consumers, and classified 960 executable candidates. Created 56 bounded table
  translation batches plus separate composition, fallback and boundary audits.
- Decoded and classified setup, island/location, night-selection, battle-menu,
  gallery and appraisal graphics. Cataloged all 7,263 known static-texture
  signatures, with 7,262 bounded resources and one rejected resource. These are
  graphics counts, not text counts; full-game coverage remains unverified.
- Preserved all five screenshots with hashes and inspection rectangles. Added
  preview-first discovery/consolidation tools and documentation. Saved 41 passing
  integrity checks covering catalogs, reviews, 1,832 decoded images, five original
  screenshots, 12 executable source fragments and complete table-batch coverage.
- No UI text or images were inserted into a game build. Latest playable image
  remains 0.1.4; next unused version is 0.1.5. Native image editing/repacking,
  executable relocation, text layout and runtime coverage remain required.

## Unreleased — PPSSPP playback volume, 2026-09-26

- Inspected the user's running installed PPSSPP 1.20.4 instance. Enable sound
  was checked, but Game volume was set to Mute (0).
- Changed Game volume to 50%, verified the displayed setting, and returned to
  the same dialogue without advancing or restarting the game. The user later
  confirmed that sound works.
- The separate workspace debugger configuration also disables audio; it was
  not the active window's mute setting. No game image or translation changed.

## Unreleased — two-slice rescan and actionable translation plan, 2026-09-26

- Reconciled the existing second 80-row draft and independent review. Current
  totals are 160 assigned rows, 159 nonempty drafts and 159 meaning-reviewed
  drafts; the image still contains 78 dialogue rows and three labels.
- Extended the auditor to count canonical slice files without double-counting
  build selections, check source-row and review identities, and reject overlaps.
  Previewed and saved a separate audit with 60 passing checks. Preserved the
  earlier audit and original target/review files.
- Updated the scan, plan, status, overview and tool instructions. Prioritized
  tracer calibration and runtime memory/rendering acceptance, complete boundary
  group integration, glossary normalization, and playable opening milestones.
- Flagged existing Recent events evidence for coverage consolidation and the
  partial trace timeout for follow-up. No new runtime acceptance is claimed;
  this rescan creates no translation, game build or emulator interaction.

## Unreleased — repository audit and translation plan refresh, 2026-09-26

- Added a preview-first workspace auditor and saved 42 passing checks, including
  23 file-hash comparisons covering source/latest images, executable, build inputs
  and review inputs. Recounted saved script and target metadata.
- Matched all 801 scripts to the resource inventory with no identity mismatch.
  The derived classification leaves 10,917 unclassified nodes; the original
  inventory remains unchanged for extraction compatibility.
- Updated the repository scan, status and translation plan with these counts,
  corrected the milestone table to include builds 0.1.3 and 0.1.4, and retained
  runtime acceptance before bulk translation. Added audit usage documentation.
- No new game build, translation, runtime test or visual acceptance is claimed.
  Latest candidate remains 0.1.4; next unused build version is 0.1.5.

## 0.1.4 — expanded dialogue font pool and crash regression, 2026-09-26

- Replaced the active dialogue font pool with separately allocated storage for
  192 native objects (43,008 bytes). Added native construction and cleanup hooks
  for parent reset, setup reset and close. Kept the original embedded objects
  and neighboring fields intact; no target text or page was shortened.
- Bound the pixel layout to the matching executable capacity, added whole-page
  checks, and retained unsupported-token rejection. Added a checked MIPS model
  for construction, cache release, destruction/free, repeated reuse, independent
  contexts, allocation failure and 64/65/69/93/192/193-glyph boundary cases.
- Built from the verified source after dry runs. Static checks pass, including
  940 spacing-hook cases, 34 pool lifecycle runs and 22 layout groups. All 78
  reviewed targets, three labels, physical pages and decoded script are unchanged
  from 0.1.3; the independent review file is unchanged.
- Clean-booted the new image and verified all six hooks, 1,056 added code/metric
  bytes, all 192 object vtables and the complete 188,010-byte live script. The
  exact 69-glyph crash page now passes; later 72- and 68-glyph pages pass too.
- Confirmed the About myself choice and backstory continuation. Five saved
  navigation traces cover 37 physical strings and 38 complete logical rows in
  processed cells. Screenshots cover 13 complete logical rows this build, nine
  new distinct rows; cumulative complete visual coverage is 17.
- Saved QA, screenshots and status updates. The CPU remains held at group 42
  page 1. The original failed 0.1.3 image and fault evidence remain preserved.

The crash regression passes; this is still a partial technical candidate. Direct
real-heap cleanup tracing, three alternate over-capacity pages, maximum stress
pages, styles/tokens, other loaders and save/load remain. Most text is untranslated.
Next unused version: 0.1.5. Output SHA-256:
`e02b88d37938c35b45339229e4e62541b08c76cfd492c10412615e4820ef3777`.
See `docs/RUNTIME_QA_0.1.4.md` for the precise scope.

## 0.1.3 — compact Latin rendering candidate; runtime QA failed, 2026-09-26

- Added a source-dependent executable patch for default-style Latin positioning
  and text measurement using 93 source glyph metrics. Added relocation support,
  a modeled 940-case hook verifier, and live code/geometry verification.
- Added pixel wrapping and integrated the executable into candidate builds.
  The same 78 reviewed rows now produce 22 reflow groups and five extra pages;
  the three label translations are unchanged. Static build checks pass.
- Clean launch, complete script/code memory comparisons, a nine-glyph centered
  page, and a 44-glyph portrait page pass. Actual screenshots show compact,
  readable text at unchanged glyph size.
- Runtime testing failed before the choice: group 33 requires 69 font objects
  but the native pool contains only 64. The original initializer calls an invalid
  descriptor on object 65. Seven generated pages exceed the measured capacity.
  Existing static suites miss this allocation constraint despite passing.
- Added a guarded read-only fault diagnostic and preserved registers, pool,
  processed-page identities, and source/build linkage after a dry-run preview.
  Updated QA, UI metadata, status, font notes, repository scan, and translation
  plan with failed acceptance and the required allocation/lifecycle correction.
- The rescan passed 41 hash comparisons and reproduced both layout profiles
  and the hook checks. No new drafts, review claims, or cumulative distinct-row
  visual coverage were added. Existing manifests and images remain unchanged.

This candidate is **not accepted**. `0.1.2` remains the prior partial comparison
baseline; `0.1.4` is the next unused version. Correct font-object storage and
whole-page guards before further bulk translation. Candidate SHA-256:
`3ff021946986cbb5b66b8b649e3ec1c2011ddb7fe2466b777e5075b822b7b478`.
See `docs/RUNTIME_QA_0.1.3.md` for exact passing and failing scope.

## Unreleased — source font metrics and spacing experiment, 2026-09-26

- Identified two identical source font resources, their 3,680 16-by-16 glyphs,
  and the executable's CP932-to-glyph mapping. Added a hash-verified metrics tool
  and source ink measurements for 93 supported printable Latin characters.
- Traced dialogue decoding, glyph setup, cache filling, and rendering. Confirmed
  that ordinary ASCII insertion would conflict with the two-byte reader.
- Added and dry-ran a guarded, reversible current-page geometry probe. Tested
  proportional advances on 35 glyphs without scaling their shapes; saved actual
  before/after/restored screenshots. One line's advance span changed from 208
  to 102 pixels with readable words and a clear advance icon.
- Verified coordinate restoration, the same dialogue/script, empty breakpoints,
  screenshot hashes, and a pixel-identical restored text rectangle. Documented
  source format, measured scope, and remaining executable/layout integration.

This is a temporary RAM experiment, not a new game build. Candidate `0.1.2`,
its manifest, target texts, and translation coverage counts are unchanged.
`0.1.3` remains the next unused build version.

## Unreleased — repository scan and translation plan refresh, 2026-09-26

- Verified 43 integrity comparisons for source/candidate/executable hashes,
  current build and validation inputs, independent review provenance, runtime
  report links, and seven screenshots. Recounted translation and corpus records.
- Reran the opening layout checks in dry-run mode: all 15 groups, preserved
  choice flow, compression round-trip, and ten unsafe-case rejections passed.
- Found that the older resource inventory still classifies all 801 recognized
  scripts as unclassified; added inventory reconciliation to the coverage plan.
- Replaced the stale next-build sequence with a `0.1.2` baseline, proposed
  `0.1.3` font work, explicit runtime/allocation checks, a category worklist, and
  the subsequent opening and full-game milestones. Refreshed format-note status.

Documentation-only change. No new game build, translated targets, source assets,
tools, saved validation records, or emulator state were changed. `0.1.3` remains
the next unused build version.

## 0.1.2 — opening wrapping and translated choice, 2026-09-26

- Inserted 78 independently reviewed opening rows, including three conditional
  choices, excluding the incomplete cross-slice sentence group.
- Added word wrapping and continuation pages through appended script code.
  Fifteen groups add 13 pages; all target words, original helper arguments,
  choice branches, and original continuation addresses are preserved.
- Measured the portrait box and reserved space for its advance icon. Verified
  both pages of one longer sentence in screenshots, selected About myself,
  and reached the correct translated backstory.
- Verified the complete 187,702-byte script in live memory. Six bounded traces
  cover 55 physical strings and 35 complete logical rows in processed cells,
  including seven complete reflow groups. Static build/compiler checks pass.
- Added build/runtime evidence, screenshots, layout documentation, and a guarded
  inspection/advance tool. Original drafts and reviews are unchanged.

This is a partial candidate. Wide Latin spacing, runtime tokens, save/load,
voice timing, alternate paths, larger allocations, and remaining text categories
still need work. Output SHA-256:
`924304f8ec1f951d23ec2880ec1428cc23e9d1b8f281d0df61effc75a6ea5bd2`.
See `docs/RUNTIME_QA_0.1.2.md` for the precise verification scope.

## Unreleased — current-state scan and next translation plan, 2026-09-26

- Rehashed the source ISO and candidate `0.1.1`; verified build inputs, review
  provenance, and runtime-report linkage. All 23 integrity comparisons passed.
- Reran static script checks in dry-run mode: 801 source resources, 247 compressed
  round trips, and relocation across all 327 text-bearing resources passed.
- Refreshed the repository scan to reflect `0.1.1`, 79 reviewed opening drafts,
  and four glossary entries, preserving the clearly marked initial scan history.
- Prioritized measured dialogue wrapping and choice/substitution/save-load tests
  for `0.1.2`, then larger allocation and loader support before bulk translation.
  Added concrete acceptance checks and cross-slice integration requirements.

Documentation-only planning update. No game assets, targets, tools, build
manifests, or emulator state changed; no new build was created.

## 0.1.1 — first translated dialogue candidate, 2026-09-26

- Built a new ISO with three relocated, re-encoded opening lines plus the existing
  three character/class labels. All three dialogue lines exceed their source byte
  lengths; the decoded main script grows by 66 bytes.
- Added a two-byte CP932 display profile using existing full-width Latin glyphs,
  control-token preservation, reserved-punctuation rejection, and complete
  two-byte string terminators. Ordinary English remains in target files.
- Verified 23 bank indexes, 2,312 character references, 34 unchanged ISO files,
  1,452 unchanged bank resources, and all rewritten script references.
- Clean-booted the candidate, visually checked all three translated lines, and
  compared the complete 182,592-byte decoded script with live RAM. Recorded actual
  screenshots, observed glyph bounds, and the third line's 14 processed glyphs.
- Drafted an 80-row opening slice with 132 rows of context examined, then obtained
  independent meaning review with the same coverage. There are 79 drafts and one
  unresolved cross-slice row with a coordinated completion proposal. Preserved
  uncertainty notes rather than inventing omitted identities or gender.
- Added the sourced Empire glossary entry. Most Japanese remains untranslated;
  wrapping, runtime substitutions, branches, save/load, full font coverage, other
  script loaders, and complete-chapter allocation remain open.

Output SHA-256:
`3f41c344db3352decee68c6cec17695c20a0079e7bcf0079819f2f465ab5174f`.
See `docs/RUNTIME_QA_0.1.1.md` for the exact scope of the passed checks.

## Unreleased — script encoding and relocation, 2026-09-26

- Migrated the script index to schema 2 with verified instruction references,
  including extended offsets. All 153,524 existing text IDs, source hashes, and
  source locations are preserved; no indexed string is unreferenced.
- Added a deterministic compression encoder and appended-pool script relocation
  with source-hash checks, exact encoding, 20-bit references, and unchanged
  instruction boundaries/control targets. Original string byte lengths do not
  constrain targets.
- Verified all 247 compressed originals round-trip exactly when decoded and
  synthetic relocation succeeds across all 327 text-bearing scripts (654 targets).
  Checked shared references, large offsets, 1,365 codec edge cases, and 12 invalid
  inputs. Saved reports after dry-run review without writing source transcripts.
- Revalidated the live emulator and inspected its script objects, allocation
  manager, native text command, and fixed rendering structures. Documented the
  20 MiB workspace and remaining allocation/wrapping investigation.

These are static insertion tools and read-only runtime findings. The ISO builder
still patches labels only; no new build or dialogue drafts were produced. Expanded
dialogue, command-token handling, layout, and playthrough validation remain open.

## Unreleased — repository rescan and revised plan, 2026-09-26

- Reviewed the current tools, metadata indexes, glossary, screenshots, build
  manifest, and saved runtime results against the project rules.
- Validated all 801 indexed scripts against their source hashes: 2,314,749
  instructions and 567,372 control references pass. Every nonempty pool string
  has a reference. The 1,669 previously missed references use extended offsets.
- Saved validation metadata without a source transcript and documented the
  distinction between verified VM references and the older saved index.
- Updated the scan, status, format notes, and plan. Prioritized index integration,
  expanded dialogue/compression/allocation proof in `0.1.1`, then contextual
  translation of the opening section for `0.2.0`.

No game assets or translation drafts changed; no new build was produced.
English and PPSSPP remain working assumptions. Full-game coverage is unknown.

## 0.1.0 — partial technical candidate, 2026-09-26

- Built `work/output/0.1.0/Summon_Night_3_EN_0.1.0.iso` with Rexx, Aty, and
  Family Teacher appended to a new label pool in both character-table copies.
- Rebuilt nested packs, the two affected bank indexes, and ISO file extents.
  Verified all 23 indexes, 2,312 label references, 34 untouched ISO files, and
  1,453 untouched bank resources. The image grows by 4,096 bytes.
- Verified byte-identical reconstruction of 843 indexed and 719 V4 containers,
  shared references, long 32-bit label offsets, and rejection of invalid inputs.
- Corrected PPSSPP launch options and added software-VRAM capture. Captured the
  original opening and candidate title, new-game menus, character/name selection,
  and opening story. Verified all loaded label pointers against the candidate.
- Meaning-reviewed all three drafts using sourced wiki terminology. Text remains
  draft until visual/layout and broader runtime checks pass.
- Reverse-engineered story decompression and matched two complete decoded scripts
  against live memory. Indexed 801 script resources, including 247 compressed:
  151,840 Japanese occurrences / 49,545 distinct source strings, without transcripts.
- Recorded 1,669 unresolved script-reference occurrences and separate executable
  UI/default-name text for further investigation.

This candidate is not a complete translation or a passed dialogue/font milestone.
The three labels are loaded correctly but have not yet been visually verified.
Full-game coverage, expanded dialogue, branches, save/load, and hardware tests
remain open. Output SHA-256:
`c3ebd0a056f344ab5b8a5b18ce9efae793fd62e54fcb68253caed58f82c8746c`.

## Earlier groundwork — before candidate 0.1.0, 2026-09-26

- Continued the active objective to translate all Japanese game text, using
  English as the working target pending confirmation.
- Created a hash-verified working ISO and decrypted the game's executable.
- Located the external bank indexes inside bank 00 resource 44; validated all
  23 banks against their complete file sizes.
- Implemented indexed-pack and V4-container readers, including empty V4 slots,
  and recorded 13,889 resource nodes without exporting source dialogue.
- Indexed 746 Japanese character/class strings (753 total string offsets,
  2,312 references) and verified the two resident/bank copies are identical.
- Added sourced glossary entries and three English label drafts: Rexx, Aty,
  and Family Teacher. All remain uninserted and visually unverified.
- Set up portable, versioned analysis and emulator tools with archive hashes.
  Verified debugger boot status; framebuffer capture remains unresolved.
- Added reproducible dry-run tools, format notes, and a current progress record.

No translated build exists yet. The full-game text count and coverage remain
unknown. `0.1.0` is still the first planned candidate build.

## Initial scan — before extraction, 2026-09-26

- Scanned the original source archive and identified PSP release `NPJH50380`.
- Recorded the 36-file ISO inventory, original ZIP/ISO SHA-256 values, verified
  ZIP member CRC, executable status, and bounded resource-header findings.
- Added a reproducible read-only scanner with dry-run preview and explicit
  metadata report writing. Verified the scanner against the supplied source.
- Documented a phased translation plan covering extraction, relocation, font
  support, glossary research, UI measurement, review, and reproducible builds.
- Created the requested work-folder categories and project documentation index.

No game assets were changed and no translated build was produced. Version
`0.1.0` is reserved for the first playable text-insertion proof. Target language
and hardware support remain unconfirmed.
