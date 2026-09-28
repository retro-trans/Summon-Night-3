# Changelog

## 0.1.35 — Menu descriptions and generic enemy names, 2026-09-28

- Updated release metadata to the Retro Trans v1 contract without changing the
  published patch or game bytes. Tested Retro Trans 0.3.1 manual patching,
  catalog import, recognition, version routing and Automatic patching with
  locally staged assets; both outputs match the complete target SHA-256.
  Live catalog discovery still requires a public repository and an eligible
  release. See `docs/RETRO_TRANS_0.1.35.md`.

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
