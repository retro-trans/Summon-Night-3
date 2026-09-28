# Translation plan

## Current interface request

The user requested translation of the five setup/options screenshots and
discovery of **all game interface text**, including battle, inventory, status,
tutorials and save/load. See [reviewed translations](SETUP_UI_TRANSLATIONS.md)
and [interface discovery](INTERFACE_TRANSLATION.md). The setup/options catalog
has 64 reviewed records representing 51 distinct English texts; seven tiny
thumbnail records remain unresolved. No UI translation has been inserted.

The broader queue contains 3,633 shared-table strings in 56 bounded batches,
960 classified executable candidates, and known graphical text families.
Finish the reviewed setup/options insertion and verify it in a new version
before using it as the UI pipeline for the wider queue. Unlike the existing
dialogue pilot, this needs native bitmap text repacking and executable constant
relocation, with independent encoding/layout verification. Coverage of all
compressed graphics and runtime consumers remains open. Existing opening and
font-lifecycle work below remains a separate outstanding work package.

## Objective and decisions

Create a reproducible translation of this exact PSP source, beginning with a
small playable proof and expanding only after longer text can be inserted safely.
English is the working target pending confirmation, with target files under
`work/translation/en/`. Real PSP hardware support remains an open requirement.

Use PPSSPP as the initial debugging and visual test environment. Whether the
final patch must also support real PSP hardware remains an open requirement;
avoid making emulator texture replacement the only delivery path until that
choice is settled. Do not estimate a full translation schedule until text
extraction provides reliable counts and the insertion proof passes.

The [format notes](FORMAT_NOTES.md), [script specification](SCRIPT_FORMAT.md),
and [latest runtime checks](RUNTIME_QA_0.1.4.md) record current evidence.
Candidate `0.1.4` contains three labels and 78 reviewed opening rows with compact
Latin spacing and a separately allocated 192-object font pool. The exact
69-glyph page that crashed `0.1.3` now passes, as do later 72- and 68-glyph pages
and the About myself choice. All code hooks and the complete script match RAM.
The failed `0.1.3` and earlier full-width `0.1.2` remain preserved for comparison.
The broader font/layout/branch/save-load acceptance gate has not passed. The script index
has 151,840 Japanese occurrences and 49,545 distinct source strings; UI, other
tables, and image/video text still prevent a complete coverage count.

The repository rescan verified 2,314,749 instructions and 567,372 control-flow
references across all 801 indexed scripts. All 153,524 nonempty strings have a
valid instruction reference; the earlier 1,669 missing references use the VM's
20-bit offset form. Schema 2 now stores those verified references and preserves
all existing text IDs. This removes a decoding uncertainty; it does not prove expanded script
allocation or rendering. Evidence is in [script_vm_validation.json](script_vm_validation.json).

Current readiness:

| Area | Confirmed | Remaining work |
| --- | --- | --- |
| Source and containers | Source identity, decrypted executable, 23 bank indexes, existing repack checks | Inspect remaining opaque/compressed resources |
| Script text | 801 resources, 151,840 Japanese occurrences, verified references in schema 2 | Map commands, scene order, speakers, and branches |
| Translation | Two 80-row assignments: 159 nonempty drafts independently meaning-reviewed; 78 inserted | Integrate both boundary groups, normalize glossary terms, compile the new selection, then verify it in game |
| Documented runtime coverage | `0.1.4` coverage manifest records 38 logical rows processed; cumulative complete visual coverage is 17 | Consolidate supplemental Recent events evidence by distinct source ID; keep loaded, processed and visually checked counts separate |
| Reinsertion | Label and opening-script builds work; expanded script matches RAM | Other loader regions and complete-chapter allocation |
| Layout and QA | `0.1.4` fixes the pool overflow on tested 69/72/68-glyph pages and preserves the About myself branch | Direct heap lifecycle tracing, alternate routes, maximum stress, styles/tokens, battle/status, save/load |
| Terminology | Four core sourced entries plus nine reviewed setup/UI entries | Opening cast, places, organizations, and recurring game terms |

Do not treat the 49,545 distinct Japanese hashes as a translation row count:
identical source text can need different English in different scenes. Keep all
occurrences until their contexts are established. Full-game completion percentages
and delivery dates remain unsupported while categories are still undiscovered.

The [current workspace audit](workspace_audit_2026-09-26_rescan.json) passes 60
checks, including both canonical opening slices, their independent-review hashes
and source identities. All 801 indexed scripts are matched to resource
inventory nodes by identity and location/hash. The derived inventory leaves
10,917 unclassified nodes (143 in `00.DAT`, 5,906 in `01.DAT`, 4,868 in `02.DAT`).
These are discovery work items, not counts of Japanese text. Keep the original
inventory unchanged because the extraction tools use its original classifications.

## 1. Establish the baseline and decode the resource formats

1. Keep the original ZIP unchanged and use its recorded SHA-256 to identify the
   source. Materialize a local working ISO only when needed. Record the exact
   emulator version and settings used for each test.
2. Boot the original game, verify basic navigation and saving/loading, and capture
   the title menu, one dialogue box, one choice, one battle menu, and one status
   screen. Store screenshots and reproduction steps under `work/ui/`.
3. Obtain a decrypted `EBOOT.BIN` from this source. PPSSPP documents a developer
   option to dump the decrypted executable on boot. Inspect resource loading,
   text decoding, font lookup, string references, and allocation behavior.
4. Probe all records of the candidate resource formats, including nested and
   consecutive blocks. Prioritize `01.DAT`/`02.DAT`; use `00.DAT`'s coherent index
   as a structural clue without assuming the same semantics elsewhere.
5. Identify compression, if present, before extracting strings. Compare candidate
   encodings and any glyph tables against text actually displayed in the game.
   A successful generic Shift-JIS decode alone is insufficient evidence.
6. Write a format specification with units, alignment, table layout, empty
   records, compression boundaries, and reference relationships. Build focused
   extract/repack tools only after those details are supported by evidence.

**Exit check:** each relevant record has a stable ID and source location; an
unmodified extract/repack preserves entry contents, ordering, padding, and any
unknown data. Prefer byte-identical resource round trips. If ISO metadata must
change during rebuilding, explain the differences and compare every contained
file. The rebuilt baseline must boot and pass the same smoke test.

## 2. Prove expanded text and fonts before bulk translation

Relocate translated dialogue into newly allocated storage and runtime memory as
required by `BASE_RULES.md`. Update references, loader sizes, offsets, and any
affected script jumps. Do not implement same-byte-length replacement as the
production dialogue strategy. File padding alone does not prove runtime space
is available: measure allocations and validate the new references.

Build a small insertion proof containing:

- A short menu label and a longer label.
- A dialogue line deliberately longer than its original byte allocation.
- A player-name or other runtime substitution, punctuation, and a multiline box.
- A choice with a working branch and a line with timing/control codes.
- Every required character class of the chosen language. For Vietnamese, include
  uppercase/lowercase diacritics and normalization handling. For English, check
  Latin letters, punctuation, and proportional widths where supported.

Determine whether the game uses system fonts, a custom atlas, or both. Map glyphs
and widths; patch rendering or expand the atlas where necessary. Test encoded
byte length, rendered width, line count, and memory requirements independently.
Text relocation removes the original-string byte budget, not finite device memory
or the screen's limits.

**Exit check / remaining `0.1.x` work:** the proof boots from a clean launch, displays the
selected language correctly, renders expanded dialogue, preserves control flow,
and survives save/load and scene transitions. Retain screenshots and a build
manifest. Block bulk translation on this check.

## 3. Build the glossary and measure the UI

Create JSON glossary records under `work/glossary/`. Each entity needs a stable
ID, category, source spelling, target spelling by language, aliases/nicknames,
evidence URLs, verification status, and notes. Character entries additionally
record sourced gender, personality, and role/position; leave unknown fields
unknown. Include places, organizations, items, abilities, and recurring terms.

Research names using game references/wiki sources as required by `BASE_RULES.md`.
When a verified wiki entry and corpus spelling disagree, use the wiki spelling
and record the discrepancy. Escalate ambiguous identity or unsupported claims
for research before adding them as facts. Never infer gender from a name.

For each UI/text class, store an actual screenshot plus a JSON record with:

`ui_id`, screen/state, source asset/record reference, screenshot path, native
resolution, `x`, `y`, width, height, font/glyph metrics, line spacing, maximum
lines, runtime substitutions, and known overflow behavior.

Cover dialogue, speaker names, choices, battle commands, descriptions, inventory,
status/skills, tutorials/help, save/load, and system messages as they are found.
Capture nearly full boxes and long substitutions. Derive pixel-width and line
limits from evidence; do not impose a guessed universal character limit.

**Exit check:** the opening section's entities have verified names, each pilot
text class has a measured layout, and the checker handles runtime expansions.

## 4. Organize the translation data and review workflow

Keep extensive Japanese scripts out of the repository. Resolve source text
locally from stable binary references for translation/review sessions; retain
only short necessary UI labels or glossary spellings. Do not duplicate a complete
Japanese transcript into JSON, documentation, prompts saved on disk, or reports.

Translation records should contain:

`id`, source archive/entry/offset, source hash, scene/order/branch, speaker and
addressee IDs (or unknown), target text, preserved control tokens, glossary IDs,
UI class, status, reviewer, and uncertainty notes.

Keep a separate coverage manifest counting discovered, exported, drafted,
reviewed, inserted, and in-game-verified records, broken down by text category
and scene. Unknown or unresolved records stay visible in the denominator.

Follow the established translation rules:

- Assign future translation agents slices of **80 consecutive dialogue rows**.
  Give them adjacent context and require `rows_examined` versus `rows_in_slice`.
  If context does not settle a line, leave it unresolved and explain why.
- Draft the full meaning before checking layout. Preserve ambiguity where the
  scene does not establish a subject or referent. Use neutral wording for unknown
  gender. Existing translations can inform an approach but must not be pasted in.
- Preserve control codes, placeholders, links, and token ordering. Measure
  substitutions by their expanded runtime width. Abbreviate only after review;
  never silently truncate a sentence.
- Use meaning review first, then deterministic glossary-name corrections over
  the entire corpus, including speaker fields. Preview representative old/new
  values before any script writes. Maintain the fixed-name do-not-touch list.
- Reviewers report uncertain decisions as well as definite defects. Fix incorrect
  meaning and inconsistent terms without rewriting lines for personal preference.

The three initial label drafts and 159 nonempty English drafts across two 80-row
opening slices have independent meaning review. The first translator and reviewer
each examined 132 rows; the second pair each examined 107. No required meaning
corrections were reported. This is reviewed draft coverage, not production acceptance.
One row remains null in the preserved first-slice file. Complete group 43
(opening rows 78–80) and group 75 (158–160) have coordinated proposals; integrate
each whole group and preserve the original review hashes. Row 160 is contextual
work outside the two assignments and must be registered before insertion.
Then preview and run glossary normalization, including any speaker fields.
Candidate `0.1.4` still contains the same 78 rows; the newer 80 drafts are unbuilt.

## 5. Expand in playable milestones

| Proposed build | Deliverable | Required evidence |
| --- | --- | --- |
| `0.1.0` (built) | Three-label relocation candidate | Static integrity and loaded pointers passed; title/new game/opening captured; visual label fit pending |
| `0.1.1` (built) | Three expanded opening dialogue lines | Complete live-script match and all three lines visually verified; broader gate still open |
| `0.1.2` (built) | 78 opening rows, bounded wrapping and a translated choice | Two-page sentence and choice screenshots; seven complete reflow groups processed; one choice result checked |
| `0.1.3` (built, failed) | Compact Latin spacing for the same opening targets | Preserved evidence of a 69-glyph page overflowing the original 64-object pool |
| `0.1.4` (built, partial) | Separately allocated 192-object pool | Original crash regression and selected later pages pass; heap lifecycle, alternate paths, stress, tokens and save/load remain |
| `0.1.x` (remaining) | Complete technical proof and core UI | Expanded dialogue, control tokens, branch, save/load, fonts, measured UI, no clipping |
| `0.2.0` | Complete opening playable section | Dialogue, choices, tutorials, and encountered UI reviewed together in context |
| `0.3.0` | Full first translation draft | All discovered text categories accounted for; unresolved rows explicitly listed |
| `0.4.0` | Complete editorial and layout pass | Meaning review, final glossary normalization, automated checks, route coverage |
| `0.5.0` | Release candidate | Reproducible patch, clean-source application, regression playtest, documented limits |

Increase the patch component for fixes within a milestone. Versions beyond the
five existing candidates `0.1.0` through `0.1.4` are planned. Define the opening section by actual extracted
scene boundaries rather than an arbitrary row quota. Cover alternative branches,
side content, endings, and image/video text if the inventory finds them.

## 6. Build and verify reproducibly

The planned build sequence is: verify source hash; validate target records and
glossary; encode text/font changes; relocate text; rebuild affected containers;
patch the executable if required; build a test image; run integrity checks;
smoke-test; create a source-dependent patch and manifest.

Use dry-run previews for every data-changing script and inspect representative
changes before applying them. A build must fail visibly for unknown encoding,
missing glyphs, unapproved missing text, damaged control tokens, out-of-bounds
references, or failed layout checks. Diagnose failures rather than truncating
or silently substituting text.

Test meaningful failure cases when implementing parsers and writers: empty
entries, unusual alignment, long relocated strings, shared references, nested
records, invalid bounds, and broken tokens. Validate all file extents after ISO
rebuilding. Compare the original and rebuilt resource inventories.

For each build, test a clean boot, new game, representative dialogue/choices,
battle/status/item screens, save/load, and transitions between scenes. Expand
playthrough coverage as content grows. Use actual in-game screenshots for visual
QA; add real PSP testing if hardware support becomes a requirement.

Store each test build under `work/output/0.x.y/` with the image or patch, output
hashes, source hash, tool versions, glossary/translation revision identifiers,
changed asset list, known issues, test results, and a matching changelog entry.
Hash relevant inputs even before Git is initialized. A distributable release
should be a patch that requires the user's matching original source.

## Folder ownership

```text
docs/                         findings, format specs, plan, QA/release notes
tools/                        scanners, extract/repack/build/check utilities
work/
  output/0.x.y/               versioned test images, patches, manifests
  glossary/                  sourced JSON terminology and entity records
  ui/                        actual screenshots and layout metadata
  translation/<language>/    target records, coverage, review notes
  source/                    local working source material, when required
  scratch/                   temporary decoded assets; no persistent transcript
```

All listed categories now exist. `.gitignore` excludes original media, working
binaries, scratch files, vendor tools, and versioned ISO output directories.
Track tools, metadata indexes, target text, glossary records, documentation, and
selected UI evidence when version control is initialized.

## Immediate next work

Following the [repository rescan](REPOSITORY_SCAN.md), `0.1.4` corrects the
64-object pool with separate 192-object storage, constructor/cleanup hooks and
whole-page guards bound to the executable profile. Static checks cover 940
spacing cases, 34 pool lifecycle runs and 22 layout groups. Live tests pass the
original fault, later long pages and one choice branch. Preserve all five builds
and the failed-build evidence. **`0.1.5` is the next unused version**; tests that
do not change the image can continue on `0.1.4` with new evidence filenames.

The [font investigation](FONT_RENDERING.md) identifies 93 Latin glyph metrics.
Four of the seven previously over-capacity pages have processed runtime evidence
(groups 33, 34, 40, 42); groups 15, 35 and 41 remain unvisited. Native allocation
and free events need direct tracing beyond the checked model. Pixel width, line
cells, page object count and script storage remain distinct acceptance checks.

| Priority | Work package | Concrete result and acceptance check |
| --- | --- | --- |
| 1 | Finish font-pool runtime acceptance on `0.1.4` | First calibrate the current tracer through page changes and input acknowledgements. Then trace actual allocation/free, close/reset and repeated scene reuse; check interrupted dialogue. Visit alternate groups 15, 35 and 41. Exercise a 93-glyph stress page at the current three-line maximum and cache pressure. Verify required glyphs/styles and mixed text. Preserve target meaning and record screenshots. Use `0.1.5` only if the image changes. |
| 2 | Complete opening runtime behavior in further `0.1.x` builds | Map substitution and style/timing tokens before enabling them. Test the longest supported player name and other expansions, remaining opening choices and protagonist/dream alternatives, voice timing, transitions, and same-build save/load from a clean launch. Every included page and translated label consumer needs a visual check. |
| 3 | Prove allocation and support other loaders | Measure main, secondary, common-script, and scratch allocations and lifetimes. Relocate or enlarge runtime storage where necessary; update loaders and references. Exercise expanded complete scripts through load/unload and scene transitions without overlap. The current `0x78000` spacing guard is not a proven capacity. |
| Alongside 1–3 | Complete discovery, UI classes, and terminology | Use the reconciled inventory to investigate remaining possible text assets, map speakers/branches, and define a playable opening boundary. Start with consumers known to show Japanese menus, names, tutorials or graphics rather than treating every unknown node as text. Capture and measure the UI classes below; expand sourced glossary entries and fixed-name rules. Discovery and research can proceed before bulk translation. |
| Bounded pilot preparation | Prepare the existing second slice for integration | Preserve both reviewed originals. Apply groups 43 and 75 together using their recorded proposals, register contextual row160, normalize glossary terms after meaning edits, and generate a fresh hash-bound selection. Validate layout and control flow before using a new build version. Research the merchant-family name in contextual rows165/174 before assigning the next slice. This does not open bulk translation. |
| After the technical gate | Complete the opening for `0.2.0` | Translate all dialogue, choices, tutorials, and encountered UI within the defined boundary. Use 80-row assignments with adjacent context, independent meaning review, then scripted name normalization. Integrate the cross-slice sentence together and play every included branch. |
| After the opening milestone | Expand chapter by chapter | Apply the proven pipeline to every discovered category, retain unresolved records, and measure throughput from accepted opening work. Follow `0.3.0` draft, `0.4.0` review/layout, and `0.5.0` release-candidate milestones above. |

The remaining font tests can use existing reviewed targets plus clearly marked
synthetic stress pages; they need not wait for bulk translation. The repair
preserves every target word and the compact layout. Also check narrow/wide
letters, spaces, punctuation, mixed untranslated
text, centered/portrait/choice measurement, nondefault styles, and the advance icon.
Keep the technical gate open until rendering, runtime
tokens, allocation, branches, transitions, and save/load have explicit passing
evidence for the supported scope. Carry unfinished checks into another `0.1.x`
build with a changelog and known limits instead of treating a pilot as complete.

### Coverage worklist

| Category | Current baseline | Next deliverable |
| --- | --- | --- |
| Script text | 151,840 Japanese occurrences in 801 scripts; 159 reviewed drafts, 78 inserted | Scene/branch/speaker map and occurrence-level assignment ledger; distinguish dialogue, choices, help, and other uses as commands are mapped |
| Character/class labels | 746 Japanese strings; three reviewed, inserted, and loaded | Review remaining labels, normalize all shared references, and check each distinct UI consumer visually |
| Executable and other tables | Default protagonist names and some offsets identified; no complete inventory | Trace consumers and relocation requirements; account for menu/system, item, ability, battle, status, tutorial, and save/load text wherever stored |
| Image, video, launcher, and credits text | Coverage unknown | Catalog visible Japanese, source asset IDs, reproduction steps, and an edit/insertion path for each applicable asset |
| Unclassified resources | Reconciled count: 10,917 after matching all 801 recognized scripts; original inventory preserved | Trace known text/UI consumers into these resources, classify by evidence, and retain unknowns; the count is not a text denominator |

Do not add these categories into a full-game denominator until overlap is
resolved. Count discovered, drafted, meaning-reviewed, normalized, inserted,
runtime-processed, and visually verified records separately. The current
38 processed logical rows are not 38 screenshot-verified rows; the cumulative
complete visual count is 17 across `0.1.1`, `0.1.2` and `0.1.4`.

For UI measurements, start with ordinary/centered dialogue, speaker names, and
choices, then battle commands, status/skills, inventory/descriptions, tutorials,
and save/load/system messages. Store actual screenshots, rectangles, glyph
metrics, line spacing, token expansions, and overflow behavior in `work/ui/`.
The 13-by-3 portrait policy is specific to the current full-width profile; the
32-cell renderer structure is not a universal visible-line limit.

The 160 assigned opening rows include alternative paths and a later compiled
function, so their 159 drafts do not represent 159 consecutive displays on one
route. Preserve source IDs and branch context. Integrate both cross-slice groups
with explicit ownership and renewed review provenance, without overwriting the
original independently reviewed files.

Supplemental evidence exists for the Recent events choice in
`work/output/0.1.4/font_recent_events.json` and `work/ui/0.1.4_recent_events.png`.
Consolidate it into the screenshot manifest and deduplicate row IDs before
updating runtime/visual totals. The saved `font_pool_flushed_calibration.jsonl`
contains 17 page-clear/glyph events, then an input-acknowledgement timeout and
successful breakpoint cleanup. It is partial instrumentation evidence, not
allocation/free acceptance. Earlier zero-event traces do not demonstrate that
native calls were absent. Revalidate the live session before any further input.

Target language and real PSP support remain open decisions. English and PPSSPP
are the working assumptions. Confirm language before bulk translation and the
hardware target before choosing a font or delivery method that excludes it.
No full-game percentage or delivery date is supportable yet. Use the accepted
opening milestone to estimate throughput, including review and playtesting.

This planning refresh retains the saved `0.1.4` regression evidence and broader
unfinished requirements, verifies current build integrity, and reconciles the
resource inventory. It recognizes 80 existing reviewed drafts that the previous
status omitted and flags supplemental evidence for consolidation. It creates no
new translations, game build, or runtime test. If implementation
disproves a format assumption, update the specification and plan before expanding
production.

## Technical references

- [PPSSPP developer tools](https://www.ppsspp.org/docs/development/developer-tools/):
  decrypted executable dumping, debugging, and texture capture.
- [PPSSPP debugger expressions](https://www.ppsspp.org/docs/development/debugger/expressions/):
  memory and breakpoint inspection.
- [PPSSPP texture replacement](https://www.ppsspp.org/docs/reference/texture-replacement/):
  useful for UI/font experiments; emulator replacement packs have a different
  delivery path from an ISO patch.

References checked on 2026-09-26. They describe emulator capabilities, not proof
that this game's text format, relocation, or font changes already work.
