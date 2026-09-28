# Interface source formats

These observations apply to the verified NPJH50380 source. The new tools decode
and index source material; they do not yet insert translated UI into the game.

## Native static sprites

Resources beginning `01 00 00 00 01 11 21 00` have a texture-directory offset
at `0x14` and palette-directory offset at `0x18`, both absolute within the resource.
The texture directory begins with a little-endian 32-bit count and 32-byte
descriptors. Descriptor layout is `<4H4I2H2BH`:

| Field | Interpretation |
| --- | --- |
| Four 16-bit values | Visible width/height, texture width/height |
| Four 32-bit values | Pixel offset relative to texture-directory base, pixel byte size, format, palette index |
| Two 16-bit values | Width/height powers |
| Two bytes | Swizzle flag, flags |
| Final 16-bit value | Pixel pitch |

The verified decoder handles format 4 (4-bit indices, low nibble first) and
format 5 (8-bit indices). Swizzle 1 uses 16-byte by 8-row tiles; swizzle 0 is
linear. Pixel allocation may contain exactly the visible rows or one additional
8-row guard block. The exported image is cropped to visible dimensions only
after decoding all stored rows. Other allocations are rejected explicitly.

The verified palette path has one palette and index zero. At palette-base+4,
four 32-bit values describe relative byte offset, size, palette format and color
count. Format 3 is RGBA8888; 16 or 256 colors are supported. Multiple-palette
resources remain a decoding gap. Resources with different headers, including
`01 00 00 00 01 21 21 00`, are not assumed to be static images.

Some top-level setup packs use obfuscated LZ with key `0x9831`; the decoder
requires bounded decompression and a zero padding tail before parsing the inline
pack. Source hashes and decoded-pack hashes are separate. Offsets within a
compressed pack refer to its decoded bytes, not locations in the ISO.

## Shared static strings

Pack `02:00003` is byte-identical to resident pack `00:00044/00007`. Twenty
children contain recognized CP932 string pools. Each begins with a 32-bit count,
a fixed-stride record array and a pool of NUL-terminated strings. Some arrays
contain a final dummy record; the inferred layout records both header and actual
record counts. Pointer columns are inferred only when every value is zero or an
exact pool-string start, and the bounded layout must be unique.

The index records direct pointer fields and every valid pool string. A string
without a direct pointer is retained as consumer-unverified; it may be a later
line of a multi-string field, but this is not assumed. Repacking requires proving
those compound-field consumers before relocating strings independently. Both
mirrored copies must be updated consistently in a future build.

## Executable literals and name entry

The initial executable scan covers file offsets `0x214780` through `0x221e78`.
Valid Japanese-bearing CP932 spans are candidates, not automatically UI strings.
Semantic classification identified binary false positives, boundary errors,
fallback text, service dialogue and runtime-composed messages. Standalone quotes,
English-only strings and text outside this range require additional discovery.

The shown options help is at `0x21ca58` through `0x21caf0`. Naming constants
include Rexx/Aty at `0x21c978`/`0x21c984`, confirmation quote/suffix at
`0x21c990`/`0x21c994`, Yes/No at `0x21c9ac`/`0x21c9b4`, and empty-name help at
`0x21c9bc`. The confirmation surrounds a runtime name; it must not hardcode Rexx.

The shared Auto-Name handler is module address `0x12a4c4`. Mode zero copies
the stored protagonist default back to the editable buffer. Nonzero mode cycles
through up to three preset pointers, skipping missing/current entries; the lookup
is deterministic. The independent behavior review retains eleven code/data-range
hashes. In these ranges, original ELF file offset equals module address + `0xc0`.

## Current limits

The screenshots measure inspection regions, not maximum characters. Sprite
dimensions are not proof of runtime clipping, scaling or how components combine.
The current dialogue font hook does not prove UI renderer behavior. Preserve
controller symbols, dynamic names, styles, palette states and keyboard character
data. Relocate strings instead of imposing the Japanese source byte budget;
measure the resulting UI and test every relevant state in a new version.

Full graphics/text coverage is still open. See [interface inventory](INTERFACE_TRANSLATION.md)
for counts, explicit gaps and links to the classification metadata.
