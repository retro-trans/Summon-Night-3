# Font atlas and proportional spacing

Observed 2026-09-26 with PPSSPP 1.20.4 and software rendering. The original
reversible experiment below used candidate `0.1.2`. Candidate `0.1.3` exposed a
64-object font-pool overflow. Candidate `0.1.4` supplies a separate 192-object
pool and passes the exact 69-glyph fault plus later 72/68-glyph pages. See
[0.1.4 QA](RUNTIME_QA_0.1.4.md). Broader runtime acceptance remains incomplete;
the next unused build version is `0.1.5`.

## Confirmed source assets

The game already has usable Latin shapes inside a custom 16-by-16 font atlas.
The wide dialogue spacing comes from fixed cell advances, not uniformly wide
letter ink. The two identical font resources are:

| Resource | Bank byte offset | Padded size |
| --- | --- | --- |
| `00:00044/00004/00000` | 37,284,080 in `00.DAT` | 473,088 |
| `02:00004/00000` | 456,704 in `02.DAT` | 473,088 |

Both complete resources have SHA-256
`0db773359358341c6d4f235d6db74fd1096e0dd5164ab199adbaf8a4845af9e2`.
The header begins `BIT\0`; the little-endian fields used by the live renderer are:

| Offset | Field | Observed value |
| --- | --- | --- |
| `0x10` | Bits per pixel, u32 | 4 |
| `0x14` | Glyph width, u16 | 16 |
| `0x16` | Glyph height, u16 | 16 |
| `0x18` | Bitmap payload bytes, u32 | `0x73000` (471,040) |
| `0x1c` | First glyph bitmap | 128 bytes per glyph, 3,680 glyphs |

Rows are linear; the low nibble is the left pixel of each byte. Remaining bytes
after the payload are padding for this resource. Uninterpreted header fields
remain unchanged. A one-based glyph index selects bitmap offset
`0x1c + (index - 1) * 128`.

The mapping table is in the verified decrypted executable at module address
`0x226000` (file offset adds `0xc0`). It contains 128 page pointers. For the
existing two-byte CP932 encoding, select page `(lead - 0x80)`, then the u16 entry
at `(trail - 0x40) * 2`. Zero/missing entries trigger native fallback behavior;
the metrics tool rejects them rather than accepting fallback as glyph coverage.
This lookup is supported by disassembly at `0x1d8f54..0x1d8fac`.

`tools/font_metrics.py` verifies the source executable and both font resources,
then measures all 93 printable ASCII characters supported by the current
two-byte encoding profile. Literal square brackets remain rejected because
their converted forms collide with game control tokens. The table is in
`work/ui/latin_font_metrics.json`; it records glyph IDs, bitmap hashes, inclusive
ink bounds, and a proposed spacing policy. It does not claim all 93 characters
have been visually tested in the game.

| Character | Ink width | Proposed advance |
| --- | ---: | ---: |
| `i` | 3 pixels | 4 pixels |
| `E` | 9 pixels | 10 pixels |
| `m` | 13 pixels | 14 pixels |
| `W` | 15 pixels | 16 pixels |
| period | 2 pixels | 3 pixels |
| space | blank | 5 pixels |

The proposal leaves one pixel after each glyph's inclusive ink bounds and uses
a five-pixel ordinary space. Glyph drawing remains 16-by-16: no bitmap scaling,
replacement, or horizontal squeezing is needed for this experiment.

## Runtime path

These module addresses refer to the source ELF whose SHA-256 is
`82cc184377986d90d298ee4918fb11bd0e3524659e5c6f8b7b3c859f4d232684`.
The observed module base is `0x08804000`; globals must be resolved from actual
relocated instructions rather than blindly adding that base to raw immediates.

| Routine | Observed purpose |
| --- | --- |
| `0x68070` | Classify two-byte source characters as ordinary glyphs or control tokens |
| `0x68bfc` | Read u16 source units, advance by two, expand runtime substitutions, emit four-byte processed cells |
| `0x69228` | Supply base glyph dimensions; current style is 16-by-16 |
| `0x69274` | Supply fixed advances; current horizontal advance is 16 |
| `0x6a038` | Construct and position glyph objects from processed lines |
| `0x6a79c` | Separate text measurement used by layout; must be traced/patched consistently |
| `0x682e8` | Initialize a glyph object and its font-cache object from a processed character |
| `0x69d28` | Render a glyph using its size, position, anchor, and animation fields |
| `0x1cbb28` / `0x1cbba4` | Populate a font object's cache when its ready flag is clear |
| `0x1d8e34` | Map two-byte codes and copy glyph bitmaps into the texture cache |
| `0x1e4ac8` | Count two-byte string units; not a variable-byte ASCII decoder |

Changing source bytes to plain ASCII without changing the reader is invalid.
The current two-byte profile can retain existing glyph lookup while a future
patch changes advances and text measurement.

Observed live locations, specific to this session:

- Text context: `0x08e30910`; style field at `+4` is **0** on this page.
- Processed rows: context `+0x84`, stride `0x8c`; cells begin at row `+0x0a`
  and hold `{u16 CP932 bytes, u16 token kind}`. There are 32 cell slots per row.
- Glyph array: context `+0x3e0`, stride `0x60`; count at context `+0x4be0`.
- Glyph fields: font object pointer `+0`; width/height `+4/+8`; x/y `+0x40/+0x44`;
  anchor x/y `+0x50/+0x54`; line index `+0x58`.
- First font object: `0x08e35b70`; its `+0xc8` points to the processed character.
  Vtable entries are eight-byte descriptors, not a packed array of function pointers.
- Renderer manager: `0x08a3bfc0`; font wrapper at `+0xcac`; source bitmap at
  `0x08c42800`. The complete 471,068-byte header-plus-payload matches the source.

## Reversible in-game test

`tools/probe_font_spacing.py` previews the exact known page and planned x changes.
Execution first saves a backup and baseline screenshot. It verifies the complete
candidate script, font bytes, processed characters, glyph identities, style,
and sizes before modifying only x and anchor x. It captures the changed page,
restores those fields in `finally`, verifies them, and captures the restored page.
It sends no dialogue-advance input. It requires a held CPU and leaves it held;
temporary framebuffer breakpoints are removed by the capture helper.

The tested group 42 page 0 contains 35 glyphs using 15 distinct characters:

| Existing page line | Original cell span | Proposed advance span |
| --- | ---: | ---: |
| Even though | 176 pixels | 102 pixels |
| it was in the | 208 pixels | 102 pixels |
| south, snow | 176 pixels | 99 pixels |

Actual before, after, and restored screenshots are saved under
`work/ui/font_spacing_probe_001/`. Visual inspection confirms readable compact
lettering, unchanged letter height/shape, visible word spaces, and an unobstructed
advance icon. The existing page breaks remain unchanged. This partial page does
not add a complete logical row to the translation's visual-coverage count.

The restored text rectangle `[178, 198, 389, 255)` is pixel-identical to the
baseline. Full-screen hashes differ because the game advances animation while
capturing. All three PNG hashes match their metadata; the same dialogue and
original coordinates were revalidated after restoration. The CPU is held and
the breakpoint list is empty. See `backup.json`, `result.json`, and
`visual_review.json` in that experiment directory for exact evidence.

## Historical 0.1.3 executable candidate

`tools/font_patch.py` adds two relocated hooks: glyph setup at module `0x6a4a0`
and measurement at `0x6aa38`. The 672-byte code/metric segment supports 93
mapped characters at default style, preserving unmapped-character and other-style
fallbacks. Mapped spaces and punctuation can also occur in Japanese; unchanged
Japanese geometry is not a blanket guarantee. The executable verifier exercises
940 modeled cases at two relocation bases. The original caller/callee contracts
are modeled, so this does not test the native object's allocation or lifecycle.

`opening_latin_pixels_v1` wraps at 208 portrait / 448 centered pixels, with
31 cells per line and three lines per page. It produced 22 groups and five extra
pages from the same 78 targets. Two runtime pages passed geometry and screenshot
checks before the object-pool fault. That compiler lacked a whole-page
font-object capacity check; seven generated pages exceed 64 cells.

The font pool is separate from the context's 192 glyph records. Context `+0x30`
points to the font pool and `+0x34` stores its capacity. Original module `0x6b488`
uses a pool at parent-object `+0x52e0`, releases 64 entries at stride `0xe0`,
then calls `0x68a2c` at `0x6b50c` with 64 as the capacity. The array ends at
parent `+0x8ae0`, immediately followed by other fields. Increasing the embedded
array count would corrupt them.

## 0.1.4 allocation correction and remaining work

The current patch keeps the embedded array intact and redirects four additional
call sites. `0x6b50c` allocates 43,008 bytes through native routine `0x1ea6cc`,
constructs 192 objects with `0x1cba50`, then binds the new pointer through original
`0x68a2c`. Parent reset at `0x6b304`, setup reset at `0x6b4fc`, and close at
`0x6b554` release owned storage before their original operations. The ordinary
per-page `0x68b00` already iterates the context capacity and reuses the new pool.

Cleanup calls `0x68b00`, destructs every element with `0x1cba8c` and flag zero,
frees the whole raw allocation with `0x1ea718`, and clears pointer/capacity.
The allocation uses raw storage, not the native array helper's hidden cookie.
Capacity 192 identifies owned storage within these dialogue-only hooks; original
zero/64-capacity contexts are not freed. Both independent model contexts retain
separate allocations. The source hash and six original call/relocation records
are checked before building. There are no runtime RAM patches in the new image test.

The new code/metric segment is 1,056 bytes. The matching
`opening_latin_pixels_pool192_v2` compiler checks whole-page capacity and requires
`latin_ink_spacing_pool192_v2`. Pixel/cell limits and the script are unchanged.
`verify_font_pool.py` checks emitted lifecycle code at two load bases; live code,
192 initialized objects, corresponding glyph pointers, and selected geometry
are independently checked by `verify_runtime_font.py`.

1. Directly trace real heap allocation/free, reset/close, scene changes and reuse;
   the model and passing normal progression do not prove every lifecycle path.
2. Visit alternate groups 15, 35 and 41, and test maximum pages/cache pressure.
   Continue checking pixel, cell, page-object and token-expansion bounds together.
3. Validate the entire supported character set, punctuation, mixed text, centered
   and portrait layouts, choices, style changes, long substitutions, and page
   boundaries. The square-bracket encoding conflict remains a separate issue.
4. Complete choices, transitions and save/load. Improve one-word continuation
   pages without dropping meaning. Preserve all builds and immutable manifests;
   use `0.1.5` for any subsequent image change.

Reproduce with 64-bit Python 3.9+ for the live probe. Preview first, inspect the
characters/coordinates, and use new evidence destinations:

```powershell
python tools/font_metrics.py
python tools/font_metrics.py --write
python tools/probe_font_spacing.py work/ui/font_spacing_probe_002
python tools/probe_font_spacing.py work/ui/font_spacing_probe_002 --execute
```

The metrics writer refuses its existing output. The live probe refuses an
existing directory or a page that does not match its measured portrait profile.
