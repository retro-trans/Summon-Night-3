# Opening dialogue reflow

The full-width profile below was implemented for candidate `0.1.2`, 2026-09-26.
It is a bounded opening profile, not general script-allocation support.

Current `0.1.4` uses `opening_latin_pixels_pool192_v2` with a matching separately
allocated 192-object font pool and whole-page capacity checks. Text and page
breaks are unchanged from 0.1.3. The exact crash and selected later long pages
now pass; see [0.1.4 QA](RUNTIME_QA_0.1.4.md). The old pixel selection is preserved
as failed-build evidence and rejected by the current builder.

Candidate `0.1.3` adds `opening_latin_pixels_v1`, measuring source glyph advances
at 208 portrait / 448 centered pixels, 31 cells per line, and three lines per
page. It produces 22 reflow groups and five extra pages. **Runtime QA fails:**
seven pages exceed the 64-object native font pool; group 33 crashes at object
65. A page capacity check and real storage/lifecycle expansion are required.
See [0.1.3 QA](RUNTIME_QA_0.1.3.md). Per-line cell and pixel checks alone are
insufficient. The legacy profile and historical evidence below remain available
for comparison; wider spacing is not the planned capacity correction.

## Observed geometry

`work/ui/0.1.1_beach_box_02.png` captures the ordinary portrait box with two
original lines. Its text area is approximately x=178..405, y=199..253 on the
480x272 screen. Glyphs advance about 16 pixels and rows about 20 pixels. The
advance icon occupies the lower-right part of the box. These are measurements
of this screen/style, not capacities for every text class.

The pilot therefore uses 13 full-width display units per line and three lines
per portrait page, leaving room for the advance icon. Centered text uses a
provisional 28-unit, three-line policy; its longest alternate-route page still
requires a screenshot. Choice queues retain their original structure and get
only relocated text references.

`0.1.2_wrapped_page_01.png` and `0.1.2_wrapped_page_02.png` show the full sentence
"Why am I lying flat on my back on this beach?" across two pages. The first has
8, 13, and 10 processed cells; the second has 11. Both are readable and leave
the advance prompt clear. Narrower Latin glyphs would reduce the extra paging.

## Transformation

`tools/dialogue_layout.py` consumes explicit complete display groups and reviewed
target records. It validates original string hashes and text references, then:

1. Appends the full encoded targets using the existing relocation tool.
2. Checks that each reflow group consists of consecutive push-string/call pairs
   using normal-text helper word 2003, followed by a mapped display helper.
   Only constant display arguments are accepted. Choice helpers are excluded.
3. Joins a group's target rows with spaces and wraps at word boundaries. Joining
   the result with spaces must reproduce the complete target exactly. Unbreakable
   words, control tokens, unsupported encoding, or unsafe spacing fail explicitly.
4. Appends new script instructions before the original pool, moving that pool
   and updating its header offset. Existing pool-relative references still work.
   A jump at the original group start reaches the appended instructions; the
   rest of that original span becomes no-ops. Any control-flow target entering
   the span's interior causes rejection.
5. Queues at most three lines, calls the original display helper with the same
   arguments, repeats for each continuation page, and jumps back immediately
   after the original span. This adds no persistent VM stack frame.

Unchanged code addresses, original control targets, entry position, and original
pool contents are preserved. Instruction boundaries inside replaced spans do
change; this profile does not claim the older all-boundaries-unchanged invariant.
The complete source pool and complete logical targets are retained for now;
wrapped groups also have separately encoded physical fragments. Logical records
retain their original identities and link to page/line records in the manifest.

The selected source helpers are 2030/2044 for portrait text and 2141/2180/2206 for
centered text. This profile is bound to opening resource `00:00065` and the
verified original source. Other scripts/helpers must be mapped before reuse.
The source span, trampoline, return address, page texts, fragment offsets, and
instruction references are recorded for every changed group.

## Selection and verification

`tools/prepare_opening_layout.py` verifies the independent review's target hash,
then selects rows 0..77 of the opening assignment. Group 43 is deliberately
excluded because it crosses into the next assignment; both halves must be
integrated together. The original draft and independent review stay unchanged.

The final selection contains 78 rows, including three choices. Fifteen groups
are reflowed, adding 13 pages across all included alternatives. Static checks
execute the generated instruction subset with queue/display events, compare
callee IDs and arguments, require balanced stacks and the original continuation,
verify choice control flow, and reject ten unsafe input cases. Compression
round-trip and full script reference checks pass. See
[dialogue_layout_validation.json](dialogue_layout_validation.json).

The complete 187,702-byte candidate script matches live RAM. The recorded first
wrapped page's three physical strings match the processed cells. Build and
runtime records are separate under `work/output/0.1.2/`; the build-time manifest
is immutable. A passed compiler check does not establish voice timing, every
alternative branch, save/load, all box styles, or larger chapter allocations.

## Reproduction

Preview each data-changing operation and inspect representative output before
adding `--write` or `--execute`:

```powershell
python tools/prepare_opening_layout.py
python tools/verify_dialogue_layout.py
python tools/build_candidate.py --version 0.1.5 --script-targets work/translation/en/opening_layout.targets.json
```

The target-selection and validation writers refuse to overwrite their existing
outputs. This previews the legacy comparison profile. Builds `0.1.0` through
`0.1.4` already exist. For the corrected pixel build, use
`opening_latin_pool192.targets.json` and `--font-patch`; see `tools/README.md`.
Use the bundled 64-bit Python for `verify_runtime_scripts.py --version 0.1.2`
and `probe_opening_dialogue.py`. The latter verifies the whole live script,
records processed target IDs without exporting source dialogue, and can advance
to a specified target ID. It stops before automatically selecting a choice.
Actual framebuffer screenshots remain a separate visual check.
