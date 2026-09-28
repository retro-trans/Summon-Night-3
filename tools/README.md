# Translation tools

## Current test build: 0.1.8

`build_chapter_titles.py` validates the 30 independently reviewed imagegen assets,
imports 31 native title-card instances (including the duplicate Chapter 2), and
preserves their audio, texture descriptors, original palettes and decoded sizes.
Run without flags first and inspect its sample output. Then use `--write-assets`,
inspect all four native contact sheets, and use `--write-iso` to produce 0.1.8.
Existing assets/build outputs are protected against overwriting.

`chapter_qa.py` only advances the isolated port-19381 test emulator and retains
intermediate frames. Preview each named batch before `--execute`.
`record_chapter_build.py` records inspected Chapter 1 runtime evidence and updates
version/status/changelog documents; preview before `--write`.
Run `audit_workspace.py --report docs/workspace_audit_0.1.8.json` before its
`--write` form. See `docs/BUILD_0.1.8.md` for scope and remaining limits.

## Opening/harbor baseline: 0.1.5

`prepare_harbor_build.py` selects 609 reviewed rows supported by the existing
renderer, checks complete groups, simulates every generated page, and leaves
32 rows in Japanese. Preview it before `--write`; its versioned selection and
layout evidence are protected against overwriting. `build_candidate.py` built
the selection `work/translation/en/opening_harbor_0.1.5.targets.json` with
`--font-patch`. The existing font executable is byte-identical to 0.1.4.

`record_harbor_build.py` previews and records the 0.1.5 status and release notes
once. The workspace auditor now reads the selected script file from the latest
build manifest. `docs/workspace_audit_0.1.5.json` records 132 passing checks.
The next unused version is **0.1.6**; older reproduction examples below describe
historical builds and must not overwrite their directories. Runtime testing
of 0.1.5 remains pending; see `docs/BUILD_0.1.5.md`.

## Opening and harbor review consolidation

`prepare_harbor_context.py` verifies source and screenshot identities and previews
the nine-entry research glossary plus four screenshot anchors. `--write` creates
new files only. The supplied crops establish inspection dimensions, not the
maximum text width of every dialogue style.

`prepare_harbor_translations.py` checks eight disjoint 80-row assignments, every
independent review's target hash and coverage, then applies accepted meaning and
complete-group boundary proposals. It scans the target corpus for glossary
aliases and normalizes the successor only after meaning edits. It checks source
identities, group completeness, choice indentation, runtime controls and encoding.
After inspecting its samples, `--write` creates the reviewed catalog, readable
English document and static validation report; existing evidence is never replaced.
This is full-meaning text, not a measured layout or ISO selection.

`update_harbor_status.py` previews changes to status and overview counts. Inspect
the preview before `--write`. Then run `audit_workspace.py` and save its passing
preview under a new report name. The harbor audit reconciles eight slices while
preserving the previous two-slice audit as historical evidence.

## Current workspace audit

`python -B tools/audit_workspace.py` previews an audit of the saved indexes,
current build inputs, source/latest ISO hashes, target counts and glossary.
It matches recognized scripts to the original inventory by ID, bank/path,
offset, size and hash, then reports remaining unclassified nodes separately.
It exports no Japanese transcript and performs no runtime test.

After inspecting the preview, `--write --report docs/<new-report-name>.json`
saves evidence inside the workspace and refuses an existing destination or
failed checks. The saved 2026-09-26 report passes 42 checks and reconciles all
801 scripts, leaving 10,917 unclassified nodes. The original inventory remains
unchanged because extraction tools depend on its original classifications.
This auditor currently uses the English opening pool-192 selection. It now
discovers canonical `opening_NNN.targets.json` slices separately from derived
build selections, checks their source rows and independent-review target hashes,
and reconciles unique assigned, drafted and reviewed IDs. The follow-up
`docs/workspace_audit_2026-09-26_rescan.json` passes 60 checks and counts both
80-row slices: 159 nonempty reviewed drafts, with 78 currently selected.

## Font measurements and reversible spacing probe

`font_metrics.py` verifies the source ELF and both font-resource copies, then
measures ink bounds for 93 supported Latin characters. Preview it before
`--write`; the writer refuses an existing `work/ui/latin_font_metrics.json`.
The proposed advances preserve the native glyph dimensions.

With a fully revealed, CPU-held `0.1.2` portrait page, use 64-bit Python to run
`probe_font_spacing.py work/ui/<new-experiment-directory>`. It previews the exact
glyph x/anchor-x changes; `--execute` saves a backup, captures before/after,
restores coordinates, verifies restoration, and captures the restored page.
It rejects unknown text, choices, tokens, other styles, and existing breakpoints.
No ISO or executable is patched. See `docs/FONT_RENDERING.md` for the source
format, guarded scope, actual screenshots, and remaining production work.

## Opening wrapping and pagination

Candidate `0.1.2` uses `dialogue_layout.py` to wrap complete reviewed display groups
and add continuation pages. It preserves choice IDs and rejects interior branch
targets, unsupported helpers, control tokens, and unbreakable words. That legacy
profile uses full-width glyphs. The pixel profile in 0.1.4 adds a separate
192-object pool and whole-page checks; see the runtime scope below.

Preview `prepare_opening_layout.py` and `verify_dialogue_layout.py` before their
`--write` forms. They refuse to overwrite existing selection/evidence files.
Pass `work/translation/en/opening_layout.targets.json` to the builder for this
78-row legacy selection. The next unused version is `0.1.5`. See
`docs/DIALOGUE_LAYOUT.md` for the exact transformation and limits.

With the matching opening running, use 64-bit Python for
`probe_opening_dialogue.py --version 0.1.2`. Optional `--advance-until <ID-prefix>`
previews a bounded Circle-input sequence; `--execute` runs it. It stops at choices
without selecting one. `--write --report-name <new-name>` saves a trace under the
candidate directory and refuses existing reports. Capture screenshots separately
to verify actual appearance. `verify_runtime_scripts.py` supports both direct
relocations and physical fragments, identifying them by live source pointer.

## Extraction and debugging tools

All data-writing tools preview by default; inspect the preview before adding
`--write` (or `-Execute` for the launcher). Run these from the workspace root:

```powershell
python tools/prepare_source.py
python tools/setup_translation_tools.py
python tools/extract_iso_member.py /PSP_GAME/SYSDIR/EBOOT.BIN work/source/EBOOT.enc
python tools/sn3_archive.py --compact
python tools/character_labels.py
python tools/script_strings.py
python tools/verify_script_tools.py
python tools/verify_repack.py
python tools/build_candidate.py
& tools/launch_ppsspp.ps1
```

`prepare_source.py` verifies both source hashes and refuses to overwrite an
existing working ISO. `sn3_archive.py` writes only metadata, and
`character_labels.py` indexes source references while preserving translations
in a separate target file. Full binary assets remain under ignored working paths.

`pspdecrypt.exe --info work/source/EBOOT.enc` previews the executable type;
`--outfile=work/source/EBOOT.elf work/source/EBOOT.enc` creates its plaintext
working copy. Do not run it over the original ZIP or an existing target.

The archive tools work with the local Python 3.8. The debugger client requires
Python 3.9+; Capstone's downloaded wheel also requires a 64-bit interpreter.
The Codex bundled Python 3.12, located through workspace dependencies, satisfies
both. Invoke that interpreter for `tools/ppsspp_client.py status`,
`screenshot <workspace-path>`, and `press <button>`. Screenshot writes need
`--write`; button actions need `--execute`. The client restores the CPU's prior
stepping state after capture, even if capture fails.

The launcher uses a hidden, workspace-local emulator and loopback debugger port
19380. Its `-Software` switch selects `--graphics=software`. Inspect
`work/scratch/ppsspp_session.json`, the actual process, and debugger status before
reusing a session. The built-in GPU capture API fails in this environment, but
`capture_framebuffer.py <workspace.png>` captures real software-rendered frames.
It previews by default; add `--write` to save and optionally `--hold` to leave
the CPU paused for inspection. It supports all four PSP framebuffer formats,
requires no preexisting breakpoints, and removes its own temporary breakpoint.
Resume the CPU before sending input after `--hold`.

Use 64-bit Python 3.9+ for `verify_runtime_labels.py [--version 0.1.0]`, which
compares the complete candidate table with live absolute pointers and previews
its report before `--write`. It leaves an existing debugger pause intact.

`build_candidate.py` starts from the verified original ISO and patches character
labels plus an optional opening-script selection. It previews the changes, refuses
an existing version directory, and verifies the output before finalizing the ISO.
The script selection must be independently meaning-reviewed and use a mapped
loader/display profile. For example, preview the next candidate with:

```powershell
python tools/build_candidate.py --version 0.1.5 --script-targets work/translation/en/opening_latin_pool192.targets.json --font-patch
```

Use the next distinct version for changed builds; never overwrite `0.1.0`,
`0.1.1`, `0.1.2`, `0.1.3`, or `0.1.4`. The layout selection enables bounded wrapping; the earlier
three-line `opening_pilot.targets.json` retains its unwrapped profile. Runtime
tokens whose expansions have not been measured still fail explicitly. Do not
shorten text to work around an implementation gate.

The `--font-patch` option now pairs `latin_ink_spacing_pool192_v2` with
`opening_latin_pool192.targets.json`. This produced candidate 0.1.4, which passes
the original 69-glyph crash regression and selected later pages. The older
`opening_latin.targets.json` belongs to failed 0.1.3 and is rejected by the new
builder's profile checks. Both selections and old evidence remain preserved.

`verify_font_patch.py` dry-runs 940 modeled hook cases. Use
`verify_dialogue_layout.py --profile opening_latin_pixels_pool192_v2` for the
pixel compiler. `verify_font_pool.py` exercises emitted construction/cleanup
hooks against checked native models, including separate contexts and whole-page
boundaries. New default report names include 0.1.4 and refuse existing files.
`verify_runtime_font.py --version 0.1.4` checks six loaded hooks, all 192 object
vtables, glyph pointers and current-page geometry. Preview before `--write` and
choose new `--report-name` values. Direct real-heap cleanup tracing, alternate
paths and save/load still remain; see `docs/RUNTIME_QA_0.1.4.md`.

`inspect_font_pool_fault.py` is specific to the historical held 0.1.3 fault at
PC `0x1fb`. With 64-bit Python, it previews registers, 65 bounded object records,
and the matching processed page. `--write` saves new fault evidence exclusively;
the existing report is protected. It issues no CPU resume, input, breakpoint or
RAM write. It refuses the current 0.1.4 session; preserve the saved 0.1.3 report.

Use 64-bit Python for `verify_runtime_scripts.py --version 0.1.4`. It compares the
entire expanded main script with live memory, checks relocated references and
two-byte terminators, and identifies the current translated processed line. The
default object addresses are specific to this observed opening session; revalidate
them when setup changes. Preview first, then `--write` saves separate immutable
runtime evidence. Existing debugger stepping state is preserved.

`sn3_codec.py` implements bounded story decompression and compression. `script_strings.py`
indexes both direct scripts and decoded `0xa695` streams; it stores no source
transcript. Schema 2 records verified instruction byte offsets for all text
references, including the extended form. See `docs/SCRIPT_FORMAT.md` for the
remaining runtime insertion gate.

`sn3_vm.py` now provides `instructions(data)` and `verify_script(data, pool_rows)`.
It is integrated into `script_strings.py` and checks source-hash, instruction-
boundary, control-target, and string-reference consistency. Verified reference
locations identify instruction starts, while removed schema-1 candidates identify
operands. `script_repack.py` appends translated strings and rewrites these references.

`verify_script_tools.py` verifies original compression round trips, synthetic
relocation across every text-bearing script, unchanged branches/pools, shared
references, large offsets, and malformed inputs. Inspect its dry run, then add
`--write` to save `docs/script_tools_validation.json`. It writes no test assets or
Japanese transcript. Passing static checks does not establish runtime memory or
font/layout safety. Current opening runtime results are in `docs/RUNTIME_QA_0.1.2.md`.

## Interface discovery and reviewed setup targets

Use `index_interface.py` to preview shared static text tables and executable
string candidates; add `--write` only after reading the samples. It checks the
mirrored table pack and records offsets, source hashes and references without
exporting a source transcript. `source_text(id)` resolves an individual entry
locally. A valid table layout is not proof that every string's consumer is known.
The current index includes 459 such unverified pool strings explicitly.

`sn3_ui_textures.py` decodes native indexed source textures. Use the bundled
64-bit Python with Pillow. Example discovery preview:

```powershell
python -B tools/sn3_ui_textures.py --packs 28,29,30,31,32,33 --destination work/ui/new_setup_inspection
```

Inspect the resource/texture counts and skipped records, then repeat with
`--write`. Existing output directories are protected. Generated PNGs are source
evidence, not translated replacements. Unsupported layouts remain in `skipped`.
`catalog_interface_graphics.py` indexes every recognized static-texture signature
in the recursive inventory. Its shape hints prioritize inspection; they neither
detect Japanese text nor exclude art with embedded text.

`register_setup_screenshots.py` preserves the five user-provided screenshots
and bounded inspection rectangles. It requires their original temporary paths
and refuses to overwrite the saved evidence. The saved registry remains usable
after the temporary originals disappear.

`prepare_setup_ui.py` validates immutable draft/review hashes, applies the Kanji
source correction and Auto-Name behavior evidence, then normalizes glossary
spellings. It creates the reviewed target catalog, accepted UI glossary and
readable translation document. `prepare_interface_queue.py` creates metadata-only
table batches and source-family queues. Both preview by default and protect
existing outputs. Later changes require a new reviewed revision, not overwriting
an old review's inputs.

`audit_interface.py` checks source regeneration, reviewed target provenance,
glossary normalization, runtime-name placeholder metadata, all 1,832 exported
image hashes/dimensions, the five screenshot hashes and complete table queue
coverage. Run with 64-bit Python/Pillow. The saved 41-check report is
`docs/interface_audit_2026-09-26.json`; dry runs remain read-only. These checks do
not establish executable relocation, graphic reinsertion or in-game layout.

See `docs/UI_FORMAT.md`, `docs/SETUP_UI_TRANSLATIONS.md` and
`docs/INTERFACE_TRANSLATION.md`. No interface build was created by these tools.

## Original source scan

`scan_source.py` uses the Python standard library (Python 3.8 or later). It reads
the ISO directly from a ZIP, without creating a second large game image. It
supports this source's standard ISO9660 layout; it is not a general-purpose
game extractor or text decoder.

Run from the workspace root. First preview the report with no filesystem writes:

```powershell
python tools/scan_source.py 'Summon Night 3 (Japan)_2.zip'
```

Read the sample findings and intended output path. Then save metadata:

```powershell
python tools/scan_source.py 'Summon Night 3 (Japan)_2.zip' --write
```

The default report is `docs/source_scan.json`. Use `--report` to choose another
path. `--write` replaces that report; it never modifies the source. The scanner
checks ISO file bounds, hashes the entire source and ISO, verifies ZIP member
CRC during the full read, parses the main PARAM.SFO, and records bounded binary
header probes. It retains no dialogue text or extracted assets.

Full reads can take some time. Header signatures and candidate indexes are
evidence for further investigation, not verified extraction formats. A zero
filled `BOOT.BIN` is checked in full. Other probes are limited to 128 KiB/file.
