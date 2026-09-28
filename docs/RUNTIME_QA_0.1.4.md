# Candidate 0.1.4 — font-pool crash regression passed

Checked 2026-09-26 with PPSSPP 1.20.4, software rendering, Normal difficulty,
Rexx/Machine, default protagonist name, and the About myself choice. The exact
69-glyph page that crashed 0.1.3 now renders correctly. Later 72- and 68-glyph
pages and the choice branch also pass. This is still a partial technical
candidate; the broader translation gate remains open.

## What changed

The dialogue controller now owns a separate heap pool of **192 font objects**,
43,008 bytes at 224 bytes per object. The original embedded 64-object array and
the neighboring parent-object fields remain in place. Native constructors
initialize the new objects. Reset and close hooks release cached glyphs, clear
references, destruct every owned object without freeing individual elements,
free the allocation once, and run the original context reset/close behavior.

The font profile is `latin_ink_spacing_pool192_v2`; the matching layout profile
is `opening_latin_pixels_pool192_v2`. The builder checks their capacity binding.
The compiler now checks whole-page font-object counts as well as pixel width
and per-line cells. Unmeasured runtime tokens remain rejected.

All 78 target records, three labels, physical pages, and the decoded script
are identical to 0.1.3. The correction expands storage instead of shortening
translation or adding pages to evade the failing case. The original independent
review target hash is unchanged.

## Identity and static checks

- ISO: `work/output/0.1.4/Summon_Night_3_EN_0.1.4.iso`, 1,658,761,216 bytes;
  SHA-256 `e02b88d37938c35b45339229e4e62541b08c76cfd492c10412615e4820ef3777`.
- Manifest SHA-256: `e4788087c1414d1732c5258deb764d390f65f37585c4ce9d5cf9ce5549120c77`.
- Patched ELF: 3,480,696 bytes; SHA-256
  `f0c6586f56db26e1ecad0e79858396b8078552bed47b838b52edd91c5cddceb6`.
- Script: 188,010 decoded bytes; SHA-256
  `631c69857b12fb1b2df3644a3a09b62af25314bfd0b1715c886588f644ee4ac2`.
- Build checks: 23 bank indexes, 2,312 label references, 33 unchanged ISO files,
  1,452 unchanged bank resources. Changes are EBOOT.BIN, 00.DAT and 01.DAT.
- Font hook suite: 940 cases at two relocation bases. Pool suite: 34 emitted
  lifecycle runs, 12 constructed/freed allocations, two simultaneous independent
  contexts, repeated reset/close, saved-register/stack preservation, and a null
  allocation trap. These execute emitted MIPS while modeling native callees.
- Page-bound tests reject 65/69 glyphs with capacity 64, accept up to 192 with
  capacity 192, and reject 193. Layout tests pass 22 group executions, preserved
  helper/branch behavior, compression round-trip, and 14 unsafe-case rejections.

Saved static reports: `docs/font_patch_validation_0.1.4.json`,
`docs/font_pool_validation_0.1.4.json`, and `docs/latin_layout_validation_0.1.4.json`.
Native heap/cache behavior is not proven by the modeled tests alone.

## Runtime evidence

Six hook jumps and the full 1,056-byte added code/metric segment match relocated
live memory. The complete expanded script, references and terminators match
the build. The new pool is at `0x08b32010`, outside the original parent object;
all 192 object vtables match the native font class. Each inspected glyph refers
to its corresponding initialized object.

| Check | Saved evidence in `work/output/0.1.4/` | Result |
| --- | --- | --- |
| First centered page | `font_runtime_validation.json` | 9 glyph positions match metrics |
| Route to original fault | `to_regression.json` | 27 inputs, target group 33 reached |
| Exact fault regression | `font_regression_69.json` | All 69 glyphs constructed and positioned correctly |
| Following page and choice | `to_choice.json`, `font_choice.json` | Group 34's 69-glyph page and continuation processed; 40 choice glyphs match metrics |
| About myself result | `font_backstory_72.json`, `backstory_continuation.json` | Correct group 40; 72-glyph page and one-word continuation |
| Following dialogue | `branch_return.json`, `font_continuation_68.json`, `final_continuation.json` | Group 42, 68-glyph page and complete continuation |
| Final complete script | `script_runtime_validation.json` | All 188,010 bytes match RAM |

The five navigation traces contain 37 distinct physical strings. Mapping every
observed fragment back to complete groups yields **38 logical rows**, including
ten complete reflow groups: 3, 6, 8, 24, 25, 31, 33, 34, 40 and 42. These are
processed-cell counts, not screenshot coverage. Other branches were not visited.

Actual screenshot checks cover the centered line, the choice and selected
highlight, all of group 33, and both pages of groups 40 and 42. All sampled text
is readable and unclipped, and advance icons remain clear. These represent 13
complete logical rows in this build; nine are new relative to prior evidence,
bringing cumulative distinct complete visual rows to 17. See
`work/ui/screens_0.1.4.json` for identities and counting rules. Japanese speaker
graphics and setup instructions remain untranslated. One-word continuation
pages are retained as a known pagination-quality issue.

## Limits and next checks

- The four formerly over-capacity pages in groups 33, 34, 40 and 42 have live
  processed evidence; three also have full geometry and screenshots. Groups
  15, 35 and 41 remain unvisited and require their alternate paths.
- Natural scene/dialogue progression worked, but allocation/free events have
  not yet been directly traced in the real heap. Verify close, reset, repeated
  scene transitions and allocation reuse, including interrupted dialogue.
- A 93-glyph three-line stress page and the complete supported character set,
  styles, tokens, longest substitutions, other choices and label consumers
  still need runtime coverage. Static capacity is 192; this is not a claim that
  every text class can display 192 glyphs or that each was rasterized in-game.
- Save/load, other script loaders, complete-chapter storage and real PSP support
  remain unverified. Most Japanese text is still untranslated.

The CPU is held after capturing group 42 page 1 (`recall.`), with capture
breakpoints removed. Revalidate process/session and resume before input. The
next unused build version is **0.1.5**; further tests can continue on 0.1.4 when
the image itself is unchanged. Never overwrite existing evidence or manifests.
