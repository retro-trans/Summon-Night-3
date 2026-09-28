# Candidate 0.1.3 — runtime QA failed

Checked 2026-09-26 with PPSSPP 1.20.4 and software rendering. This candidate
must not be treated as a playable translation milestone. Preserve its image,
manifest, and evidence; the next unused version is **0.1.4**. Candidate 0.1.2
remains the previous partial comparison baseline, not a complete release.

## Build and passing checks

The candidate contains the same three labels and 78 reviewed opening targets.
It adds proportional Latin positioning and matching measurement in the executable,
plus pixel-based wrapping: 22 reflow groups and five additional pages. Glyph
images retain their original 16-by-16 size. The earlier full-width profile used
15 groups and 13 additional pages. No new translation meaning review is claimed.

- ISO: `work/output/0.1.3/Summon_Night_3_EN_0.1.3.iso`, 1,658,761,216 bytes.
  SHA-256: `3ff021946986cbb5b66b8b649e3ec1c2011ddb7fe2466b777e5075b822b7b478`.
- Patched executable: 3,480,232 bytes, SHA-256
  `90775799ac0e18c9fa76eefda9985c8bb151e91040edeee6b66b2b217cc4893e`.
- The complete 188,010-byte decoded script matched live RAM; SHA-256
  `631c69857b12fb1b2df3644a3a09b62af25314bfd0b1715c886588f644ee4ac2`.
- Saved build checks validate 23 bank indexes, 2,312 label references, 33 unchanged
  ISO files, and 1,452 unchanged bank resources. Only EBOOT.BIN, 00.DAT, and 01.DAT
  change. These are structural checks, not proof of runtime safety.
- Clean launch reached the title, protagonist selection, dream, and beach.
  Both relocated hooks and all 672 added code/metric bytes matched live memory.
- Geometry matched measured advances for the first nine-glyph centered line and
  the 44-glyph portrait page in group 24. Actual screenshots show readable text,
  complete words, and a clear advance icon. Group 24 now fits two lines on one
  page. Its measured line widths are 203 and 168 pixels.

Evidence: `font_runtime_validation.json`, `script_runtime_validation.json`,
`font_portrait.json`, and `to_portrait.json` in the build directory; screenshot
metadata is in `work/ui/screens_0.1.3.json`. The saved navigation trace has 14
inputs ending at group 24. Do not extend that trace's coverage to later pages.

## Failure and diagnosis

Advancing toward the choice stopped in group 33 while constructing a page of
69 glyphs (22 + 24 + 23). The debugger remained responsive and held the CPU at
invalid PC `0x1fb`. No completed `to_choice.json` trace exists; this build's
choice and branch checks did not pass.

The subsequent read-only inspection saved `work/output/0.1.3/font_pool_fault.json`:

| Observation | Value |
| --- | --- |
| Text context | `0x08e30910` |
| Font pool pointer / capacity | context `+0x30` = `0x08e35b70`; `+0x34` = **64** |
| Object stride | `0xe0` bytes |
| Initialized objects | Indices 0–63 have vtable `0x08a304f0` |
| Faulting object | Index 64, address `0x08e39370`, vtable zero |
| Construction counter | register `s7` = 64 |
| Return address | `0x0886c328`, following original module call at `0x68320` |

The original glyph initializer calls an invalid virtual-method descriptor after
running beyond the 64-object pool. The original setup call at module `0x6b50c`
passes capacity 64 in its delay slot at `0x6b510`; the preceding release loop
also uses 64 at `0x6b4bc`. This supports a real object-capacity fault, rather
than a debugger timeout being sufficient evidence of an emulator hang.

Seven generated pages exceed this pool: groups 15 (67), 33 (69), 34 (69),
35 (68), 40 (72), 41 (72), and 42 (68), all page zero. Only group 33 has the
captured fault. The others are static capacity violations, not separately
reproduced crashes.

The static font suite still passes all 940 modeled hook cases; the Latin layout
suite still passes its 22 group-execution checks and 14 unsafe-case rejections.
Neither models the actual font-object pool. A line fitting its pixel width and
31-cell limit can still exceed the page's allocation. The 192 glyph records in
the context do not establish 192 initialized font objects.

## Required correction and acceptance

1. Trace ownership, allocation, construction, reset, release, and cache use for
   the font pool. Allocate and initialize sufficient distinct storage; changing
   only the capacity constant would overwrite adjacent state.
2. Bind the layout profile to the executable's verified page capacity. Add a
   whole-page check including expanded runtime tokens and all visible lines.
   Verify boundary cases at 64/65, the failing 69-glyph page, and the supported
   maximum (the current three-line, 31-cell policy permits up to 93 glyphs).
3. Build 0.1.4 from the verified source. Clean-boot through the failing page and
   the choice; check all seven offending pages and relevant alternative routes.
   Check reuse, transitions, and save/load for allocation lifetime problems.
4. Complete the broader token, style, centering, choice, label, and hardware
   requirements in the translation plan. A fixed crash alone does not close
   the full technical gate.

The fault inspection neither resumed nor modified the game. The CPU remains
held at the fault; revalidate the live session before further debugger actions.
