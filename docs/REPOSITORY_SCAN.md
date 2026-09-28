# Repository scan — 2026-09-26

## Current rescan: both translation slices accounted for

The [new audit](workspace_audit_2026-09-26_rescan.json) passes **60 checks**.
It rehashes the working source ISO, latest candidate, executable and recorded
build/review inputs; reconciles all 801 scripts against the inventory; and checks
both canonical opening assignments against their independent reviews and source
row identities. Derived build selections are excluded from draft totals.

There are **160 assigned rows, 159 nonempty drafts and 159 meaning-reviewed
drafts** across `opening_000` and `opening_001`. The second file already existed
but was missing from the previous status count. Its 80 rows have a matching
independent review; no new translation or meaning review was performed in this
scan. One first-slice row remains null. Groups 43 and 75 require coordinated
integration, followed by glossary normalization. The latest image still includes
78 opening rows and three labels.

Script totals remain 151,840 Japanese occurrences and 49,545 distinct hashes.
There are 746 Japanese label strings, four glossary entries and 10,917 remaining
unclassified resource nodes. These figures do not establish complete game scope.
Build versions remain `0.1.0`–`0.1.4`; the next unused version is `0.1.5`.
The required folder structure is present; version control is not initialized.

Additional saved files document the Recent events choice and an unfinished
font-pool trace. The trace records 17 page-clear/glyph events, an input timeout,
and cleanup of all 17 installed trace points. Direct allocation/free acceptance
is still unproven. Supplemental choice screenshots and geometry need merging
into the coverage manifest. Existing documented coverage totals stay at their
previous baseline; no emulator was controlled during this rescan.

The [plan](TRANSLATION_PLAN.md) now explicitly orders tracer calibration, memory
and rendering acceptance, reviewed-slice integration, and complete playable
opening work. Asset discovery, UI measurement and sourced terminology can
proceed alongside the technical work. English and PPSSPP remain working
assumptions; real PSP support is undecided. No reliable full-game date or
completion percentage can be derived yet.

## Earlier same-day audit and planning refresh

The workspace contains five test builds (`0.1.0` through `0.1.4`), the required
folder structure, extraction/rebuild tools, English targets, independent reviews,
a four-entry glossary, and actual game screenshots. There is no Git repository.
English and PPSSPP remain working assumptions; target-language confirmation and
real PSP support remain open decisions.

The new [audit report](workspace_audit_2026-09-26.json) passes **42 checks**:
23 file-hash comparisons and 19 identity, inventory, count, and status checks.
Hashes cover the working source ISO, latest candidate ISO and executable, all
18 recorded build inputs, and both review inputs. The original ZIP and older
build images were not rehashed. These checks do not constitute new runtime or
translation review evidence.

Fresh recounts confirm 801 scripts, including 247 compressed resources and 327
with text; 153,524 nonempty string occurrences, 151,840 Japanese occurrences,
49,545 distinct Japanese hashes, and zero strings without indexed references.
The opening assignment contains 79 nonempty drafts out of 80 rows, with 78
selected for insertion. There are three target labels out of 746 indexed
Japanese labels. Saved runtime and visual coverage remain as documented below.

All 801 script resources match inventory IDs, bank/path, offset, size and hash.
They were included in the older inventory's 11,718 unclassified nodes. A derived
classification therefore leaves **10,917 unclassified resource nodes**:

| Bank | Remaining unclassified nodes |
| --- | ---: |
| `00.DAT` | 143 |
| `01.DAT` | 5,906 |
| `02.DAT` | 4,868 |

The original inventory remains intact for tools that discover scripts through
its unclassified-node list. The reconciliation is saved separately. Unknown
nodes may contain graphics, other nontext data or further containers; this is
not a remaining-text count or a complete game denominator.

The [updated plan](TRANSLATION_PLAN.md) keeps runtime acceptance first, permits
asset discovery and terminology work alongside it, and defines opening-section,
full-draft, review and release milestones. This refresh changes documentation
and adds a reproducible audit; it creates no game build or new translation.

## Implementation follow-up: 0.1.4 regression passed

Candidate `0.1.4` now expands the dialogue pool to 192 separately allocated
native objects and adds bound capacity checks. The exact 69-glyph fault, later
72/68-glyph pages and the About myself branch pass. All 78 targets and the
decoded script remain unchanged. Current runtime traces cover 38 complete
logical rows; cumulative complete visual coverage is 17. See
[0.1.4 QA](RUNTIME_QA_0.1.4.md), [font implementation](FONT_RENDERING.md), and
[current status](translation_status.json). Real heap cleanup tracing, alternate
paths, maximum pages, tokens and save/load remain. The next unused version is
0.1.5. The rescan comparisons below are historical input hashes from before
the 0.1.4 tool changes; they are not claims that those tools remain unchanged.

## Historical repository rescan: 0.1.3 runtime failure

The workspace has four versioned candidates, extraction/rebuild tools, metadata
indexes, English targets and independent reviews, four glossary entries, and
actual game screenshots. The required folder layout is present. There is no
Git repository. English and PPSSPP remain working assumptions; real PSP support
and target-language confirmation are still open.

Fresh read-only checks passed **41 integrity comparisons**: source ISO, both
0.1.2/0.1.3 ISOs and the patched executable (four), all 17 current build inputs,
11 font/layout validation inputs, two selection review inputs, four screenshot
hashes, and three runtime-report manifest links. The original ZIP was not
rehashed. The source hash remains
`00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda`.

Fresh recounts confirm 801 scripts, 327 containing text, 153,524 nonempty strings,
151,840 Japanese occurrences, 49,545 distinct Japanese hashes, zero unreferenced
strings, 79 opening drafts, 78 selected targets, and four glossary entries.
These script counts still exclude unclassified text categories and cannot
support a full-game completion percentage. The older inventory still includes
recognized scripts among its 11,718 unclassified nodes; reconcile that overlap.

The current executable and Latin layout dry runs reproduce the saved 0.1.3
hashes and pass 940 modeled hook cases, 22 group executions, preserved choice
control flow, compression round-trip, and 14 unsafe-case rejections. The legacy
layout still reproduces the 0.1.2 script hash, 15 groups, 13 extra pages, and
ten unsafe-case rejections. Saved validation reports were not overwritten.

**Runtime acceptance fails despite those static passes.** The native font pool
has 64 entries, while seven generated pages require 67–72. A live read-only
inspection confirms group 33 stopped constructing its 65th object on a 69-glyph
page, with invalid PC `0x1fb`. The complete live script still matches 0.1.3.
The original setup routine passes capacity 64 at module `0x6b510`, independently
supporting the allocation diagnosis. See [0.1.3 QA](RUNTIME_QA_0.1.3.md) and
`work/output/0.1.3/font_pool_fault.json` for precise evidence.

Four saved screenshots were inspected: title, protagonist selection, centered
dialogue, and portrait dialogue. The two translated pages are readable and the
portrait sentence fits one page, but those successes do not make this build
playable. The speaker-name graphic and other setup UI remain Japanese.
This refresh does not increase cumulative distinct-row visual coverage.

The [translation plan](TRANSLATION_PLAN.md) now prioritizes proper font storage
and lifecycle expansion in **0.1.4**, whole-page capacity checks, and reproducing
the failing page before continuing token/branch/save-load and larger-script
allocation checks. Terminology, UI measurements, and asset classification can
proceed while the technical gate remains open; bulk production waits for it.

This rescan preserved fault evidence through a guarded diagnostic and updated
documentation/UI metadata. It did not create another game build, change target
translations, resume the game, or alter RAM. Historical scans below retain the
claims and hash comparisons valid at their earlier baselines.

## Historical repository rescan: 0.1.2 baseline

The workspace contains extraction/rebuild tools, metadata-only source indexes,
English targets and independent reviews, four glossary entries, actual game
screenshots, and three partial test builds (`0.1.0` through `0.1.2`). The requested
`docs`, `tools`, and `work` categories are present. There is no Git repository;
`.gitignore` already excludes original media, working binaries, vendor tools,
scratch data, and generated build directories.

| Area | Confirmed baseline | Limit |
| --- | --- | --- |
| Source | PSP `NPJH50380`; verified working ISO and decrypted executable | Exact source identity matters for every patch |
| Resource inventory | 23 bank indexes, 13,889 recursive nodes | Resource classification and text coverage are incomplete |
| Script index | 801 scripts, 247 compressed, 327 containing strings; 151,840 Japanese occurrences, 49,545 distinct Japanese hashes | These are script-pool counts, not the full game or a count of context-independent translations |
| Labels | 746 Japanese strings; three reviewed and inserted | Visual fit in label consumers remains unverified |
| Opening translation | 80 assigned rows, 79 drafts independently reviewed, 78 selected for `0.1.2` | A sentence spans the next assignment and is excluded from the build |
| Build and saved runtime evidence | `0.1.2` has 15 reflow groups and 13 added pages; the complete 187,702-byte script matched RAM | 35 logical rows have processed-cell evidence; cumulative complete visual evidence covers eight rows across `0.1.1`/`0.1.2` |
| Glossary and UI | Four sourced entries, selected screenshots and bounded geometry measurements | Wider terminology, all text classes, and complete font metrics remain open |

### Fresh checks in this rescan

All **43 integrity comparisons passed**:

- Complete SHA-256 hashes of the working source ISO, candidate `0.1.2`, and
  decrypted executable (three comparisons).
- Every current input recorded by the build manifest (14), saved script-tool
  validation (six), and saved layout validation (seven).
- Both selection review-input hashes, plus the independent review's target hash
  (three). The original reviewed translation file remains unchanged.
- Runtime report links to the build manifest, candidate image, and decoded script
  (three). These validate saved evidence, not the current emulator state.
- All seven PNG hashes referenced by `work/ui/screens_0.1.2.json`.

The source ISO hash is
`00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda`.
Candidate `0.1.2` is 1,658,165,248 bytes with hash
`924304f8ec1f951d23ec2880ec1428cc23e9d1b8f281d0df61effc75a6ea5bd2`.
The original ZIP was not rehashed during this rescan; its earlier identity is
preserved below and in `source_scan.json`.

Fresh record recounts reproduce the script and Japanese-string totals, zero
unreferenced nonempty strings, 79 nonempty opening drafts, 78 selected rows,
746 Japanese labels, and four glossary entries. All 801 script records match
their recursive inventory IDs, bank/path, offset, size, and source hash.

`python -B tools/verify_dialogue_layout.py` passed in dry-run mode: 15 bounded
group-execution checks, preserved choice control flow, compression round-trip,
and ten rejected unsafe cases. It reproduced 78 targets, 13 additional pages,
187,702 decoded bytes, and hash
`631b8bc638dede0e357305740be337aa4233dce48297bc054169ba3ad867e1b1`.
The corpus-wide static suite was not rerun; its saved report still matches all
six recorded inputs. No validation report was overwritten.

### Findings that change the plan

1. The builder supports bounded wrapping now, but only for mapped opening
   resource `00:00065`. It still rejects unmeasured runtime tokens and applies
   a provisional `0x78000` loader-spacing bound. Neither this bound nor the
   32-cell renderer structure establishes production memory or screen capacity.
2. Full-width Latin rendering works for the selected screenshots but creates
   many short pages. Font decoding, drawing, advance, text measurement, and
   wrapping must be checked together before a narrower profile is accepted.
3. The older resource inventory calls 11,718 nodes unclassified, including all
   801 scripts recognized by the newer script index. Reconcile classifications
   before reporting remaining asset counts. Unknown nodes are not a text count.
4. The old immediate-work plan still proposed building `0.1.2` and described a
   three-line current pilot. This refresh replaces that sequence with `0.1.3`
   and later technical work, followed by a complete opening milestone.
5. Remaining coverage includes other choices/routes, token expansion, voice
   timing, save/load, larger script allocations, executable/default-name UI,
   other tables, and image/video/launcher/credits text where present.

The revised [translation plan](TRANSLATION_PLAN.md) defines priorities and
acceptance checks. English and PPSSPP remain working assumptions; language and
real PSP support are unconfirmed. Full-game scope and delivery time remain unknown.

This rescan read rules, code, metadata, targets/reviews, manifests, and QA
records. It updated documentation only: no new build, translation changes,
emulator operation, or fresh playthrough. Runtime and visual claims come from
[saved 0.1.2 QA](RUNTIME_QA_0.1.2.md) and [translation status](translation_status.json).
The following sections preserve earlier scans; their implementation statements
and input-hash comparisons describe their historical baselines.

## Pre-0.1.2 repository rescan

The workspace now contains extraction/rebuild tools, metadata-only text indexes,
a small glossary, actual game screenshots, and partial `0.1.0` and `0.1.1` test ISOs.
The requested `docs`, `tools`, and `work` folder categories are present. There
is still no Git repository. Original media, local tools, scratch data, and build
outputs are excluded by `.gitignore` for future version control.

| Area | Current evidence |
| --- | --- |
| Source | PSP `NPJH50380`; original ZIP, working ISO, and decrypted executable available |
| Resource coverage | 23 bank indexes and 13,889 recursively inventoried nodes; many asset meanings remain unknown |
| Script index | 801 scripts, including 247 compressed; 151,840 Japanese occurrences, 49,545 distinct Japanese hashes |
| Script references | All 801 scripts pass instruction/reference validation; zero unreferenced nonempty strings |
| Character/class labels | 746 Japanese strings; three reviewed English drafts inserted and loaded |
| Build | `0.1.1` contains three labels and three expanded opening lines; saved runtime evidence verifies all three dialogue displays and the complete expanded script in memory |
| Opening translation | 80 assigned rows, 79 drafts independently meaning-reviewed, one cross-slice sentence awaiting joint integration |
| UI evidence | Screenshots and provisional rectangles exist; maximum capacities/font metrics are not established |
| Glossary | Four sourced entries; broader character and terminology research remains |

This rescan inspected rules, implementation, indexes, manifests, QA records,
glossary, translation/review files, and UI metadata. Fresh read-only checks passed:

- Rehashed the complete working source ISO and candidate `0.1.1`; both match their
  recorded SHA-256 values. The candidate hash is
  `3f41c344db3352decee68c6cec17695c20a0079e7bcf0079819f2f465ab5174f`.
- Verified 23 integrity comparisons in total: both ISO hashes, all 12 candidate
  input hashes, six static-validation input hashes, the independently reviewed
  target hash, the runtime report's manifest hash, and matching decoded hashes
  between the build and runtime reports.
- Reran `tools/verify_script_tools.py` in dry-run mode. It checked all 801 source
  resources, round-tripped all 247 compressed scripts, and checked relocation in
  all 327 text-bearing resources using 654 synthetic targets. Its 1,365 codec
  cases, 12 malformed-input checks, shared references, large offsets, and no-op
  byte-identity checks passed. Original instructions, branch targets, and pools
  remained intact. No report or source data was overwritten.
- Recounted the opening targets and glossary: 79 nonempty drafts in an 80-row
  assignment, 79 independently reviewed drafts, and four glossary entries.

The schema-2 index records 2,314,749 instructions, 567,372 control references, and
153,524 nonempty pool occurrences with zero unreferenced strings. This includes
1,669 extended 20-bit references. See [script_vm_validation.json](script_vm_validation.json)
and [script_tools_validation.json](script_tools_validation.json) for saved evidence.

Existing build/runtime results below are supported by saved manifests and QA
records; this rescan did not rebuild the ISO or repeat a playthrough. It changes
documentation only. No new translated build was produced, and the emulator was
not operated for this rescan.

Implementation inspection confirms that the builder currently accepts only the
mapped opening resource `00:00065`, rejects runtime tokens and lines requiring
wrapping, and applies a provisional script-size bound based on loader spacing.
The working glyph profile uses full-width Latin characters. These are real
production constraints, even though the short rendering pilot passes.

The immediate priority is measured wrapping, allocation, and
visual/branch/save-load validation, followed by support for other loader regions.
Executable UI/default names, other tables, and image/video text need separate
discovery. Bulk translation follows the insertion proof. English is the existing working assumption;
target language and real PSP support remain unconfirmed. The full text count is
still unknown, so a completion percentage or release date is not yet justified.

See [TRANSLATION_PLAN.md](TRANSLATION_PLAN.md) for the current sequence,
[FORMAT_NOTES.md](FORMAT_NOTES.md) for formats, and
[translation_status.json](translation_status.json) for measured progress.

## Initial scan record (historical)

The remainder preserves the initial scan before extraction and test builds.
Its candidate interpretations and unknowns describe that earlier state; current
format findings supersede them.

## Summary

This workspace started with `AGENTS.md`, `BASE_RULES.md`, and one game ZIP.
There was no Git repository, extracted asset tree, translation corpus, glossary,
UI evidence, build pipeline, or test build. Python is available locally.

The source is a PSP ISO with disc ID **NPJH50380**. The immediate technical
task is to locate and understand the text and font data inside the resource
containers and executable. Translation volume and reinsertion feasibility are
not established by this scan.

## Source identity

| Field | Observed value |
| --- | --- |
| Archive | `Summon Night 3 (Japan)_2.zip` |
| Archive size | 1,213,501,000 bytes |
| Only archive member | `Summon Night 3 (Japan).iso` |
| ISO size | 1,658,159,104 bytes |
| ISO system identifier | `PSP GAME` |
| Disc ID | `NPJH50380` |
| Application / disc version | `01.00` / `2.00` |
| Required system version field | `6.60` |
| ISO filesystem inventory | 36 files, 5 directories including the root |
| ZIP member integrity | CRC verified by reading the complete ISO |

These version fields come from the source game's `PARAM.SFO`; they are separate
from this project's future `0.x.y` build numbers. The archive suffix `_2` does
not establish a game revision.

SHA-256 of the original ZIP:

```text
da6cb60a15e3a830927badb8bbaf6a327c32878af53781e495aadabbed742f3c
```

SHA-256 of the uncompressed ISO:

```text
00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda
```

## Asset map

Paths below are inside the ISO. Sizes are exact; interpretations explicitly
marked as candidates still need payload or runtime confirmation.

| File / group | Size in bytes | Evidence and translation relevance |
| --- | ---: | --- |
| `PSP_GAME/SYSDIR/EBOOT.BIN` | 2,885,456 | Starts with `~PSP`, an encrypted PSP executable wrapper. Obtain a decrypted executable to inspect loaders, embedded strings, encoding, and rendering. |
| `PSP_GAME/SYSDIR/BOOT.BIN` | 2,885,105 | The entire file is zero-filled. It is not a usable plaintext executable. |
| `PSP_GAME/USRDIR/00.DAT` | 49,686,528 | Candidate 487-entry table with 2,048-byte units; all entries are contiguous and in bounds, and its end equals the file size. 179 entries have zero length. The first nonempty payload is RIFF/WAVE at offset 4,096. Audio-bank candidate; do not treat entries as dialogue rows. |
| `PSP_GAME/USRDIR/01.DAT` | 247,572,480 | Candidate five-entry table with 16-byte units at the file start. Its indexed region ends at byte 89,328, well before EOF. Prioritize for text/resource investigation; whole-file structure is unproven. |
| `PSP_GAME/USRDIR/02.DAT` | 310,835,200 | Binary data with no recognized sample signature. Prioritize for text, graphics, font, or other resource investigation; role and compression unknown. |
| `PSP_GAME/USRDIR/03.DAT` | 22,296,576 | Candidate two-entry table with 16-byte units; repeated `PPHD`/`PPPG` signatures in the sample. Potential sound-resource container. The initial table only spans 53,200 bytes; do not extrapolate it to the whole file. |
| `PSP_GAME/USRDIR/04.DAT` | 26,193,920 | Begins with `PSMF0015`, a video signature. Inventory any visible text later; no subtitle track was identified. |
| `PSP_GAME/USRDIR/SV00.DAT`–`SV18.DAT` | 19 files | Every file begins with RIFF/WAVE. Likely audio collections, with first RIFF chunk sizes smaller than their containers. Voice/chapter mapping remains unverified. |
| `ICON0.PNG`, `PIC1.PNG`, `PARAM.SFO` | See JSON | Launcher images and title metadata, separate from in-game UI. |
| `psmf.prx`, `libpsmfplayer.prx` | See JSON | Media-support modules; lower priority for translation. |
| `PSP_GAME/SYSDIR/UPDATE/*` | See JSON | Firmware updater assets, outside the translation scope. |

The index hypothesis is a little-endian header of `u16 count`, `u16 tag=1`,
`u32 unit_shift`, followed by `count` pairs of `u32 offset`, `u32 length`.
Candidate byte positions equal the stored values multiplied by `2**unit_shift`.
The bounds checks support this hypothesis, but payload types and rebuilding
behavior remain unverified.

## What was checked

- Listed every ISO9660 file and checked its extent against the ISO size.
- Read the complete ISO for SHA-256 and ZIP CRC validation; separately hashed the ZIP.
- Parsed the main `PARAM.SFO`.
- Probed at most 128 KiB at the start of each resource/executable file, except
  `BOOT.BIN`, whose complete contents were checked for zeroes.
- Checked candidate index bounds, contiguity, empty entries, and indexed end.
- Saved metadata and short binary headers only; no dialogue dump or asset extraction.

The source archive was opened read-only. No emulator session, game boot,
decryption, translation, repacking, or patch application was performed.
Hashing the whole ISO does not mean its whole contents were semantically analyzed.

## Unknowns that determine effort

1. Actual text locations, encoding, script records, and control-code grammar.
2. Container nesting, compression, indexes outside each file, and loader addressing.
3. Font format, character coverage, glyph widths, line breaking, and text-box limits.
4. Relocation strategy, runtime allocation limits, and executable changes needed.
5. Dialogue/UI counts, branch coverage, and any text embedded in images or video.
6. Target language and whether real PSP hardware must be a supported test target.

See [the translation plan](TRANSLATION_PLAN.md) for the order of work.
