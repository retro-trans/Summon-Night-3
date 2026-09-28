# Script decoding and verified references

Candidate `0.1.2` adds explicit display-group wrapping through appended script
code. Its selected replaced spans have new instruction boundaries; the original
unchanged-boundary relocation profile remains available. See
[dialogue layout](DIALOGUE_LAYOUT.md) for the transformation, checks, and limits.

Updated 2026-09-26. No complete source transcript is stored here. All addresses
are module-relative ELF addresses unless explicitly called runtime addresses.

## Compression

The decoder at `0x1e56d0` takes output in `a1`, encoded input in `a2`, and a
16-bit key in `a3`. Key zero selects `0x9831`. The story loader at `0x209c8`
and asynchronous loaders at `0x20b50`, `0x2116c`, and `0x21324` use `0xa695`.
The implementation is in `tools/sn3_codec.py`.

The first five encoded bytes specify output length. With `high = key >> 8`,
`low = key & 255`, and `seed = byte[0] XOR high XOR low`, the output length's
little-endian bytes are:

```text
byte[2] XOR seed XOR low
byte[4] XOR seed XOR low
byte[1] XOR seed XOR high
byte[3] XOR seed XOR high
```

The token stream starts at byte 5. Each flag byte is XORed with `high XOR low`
and consumed least-significant bit first. Zero denotes one literal, decoded as
`encoded XOR high XOR (~output_position & 255)`. One denotes a back-reference:
length is a nibble plus 2 (range 2–17); low and high nibbles alternate across
back-references, even across flag groups. The packed length byte is XORed with
`low`. Distance is `(encoded XOR high XOR low XOR (output_position & 255)) + 1`
(range 1–256). Copies may overlap. The decoder rejects truncated data, invalid
distances, output overruns, and output lengths above its bound.

Two complete outputs were compared with live emulator memory in the opening
story scene. Both were byte-identical:

| Source | Encoded bytes consumed | Decoded bytes | Runtime address | Decoded SHA-256 |
| --- | ---: | ---: | --- | --- |
| `00:00064` | 12,116 | 24,826 | `0x08d82000` | `d3aa3d884ef2288ada7dd43438c5bde32c158a39156cd0c160b4b086f97c4c3a` |
| `00:00065` | 86,535 | 182,526 | `0x08d8a000` | `420430e031d5cd45771871f516ad850de53b65c789e009f5a49caae70643ffa7` |

Default-key decoding also validated indexed containers from `00:00049`,
`00:00050`, and `02:00027`. Other call-site keys observed are `0x1a17`, `0x1a15`,
`0x1a0b`, `0x1731`, and `0x1507`; their asset categories still need investigation.
The matching encoder now uses a deterministic greedy 256-byte window, including
overlapping matches and length-nibble pairing across flag groups. Re-encoding all
247 compressed scripts restores the exact decoded bytes: 9,038,034 decoded bytes,
4,107,784 original encoded bytes, and 4,102,426 re-encoded bytes. Encoded streams
need not be byte-identical. A general recursive compressed-resource inventory
still needs implementation. Candidate `0.1.1` now proves runtime decoding of the
expanded opening main script; all 182,592 bytes match its rebuilt output.

## Script pools

Recognized scripts start with the 12 bytes `010000000102000000100102`.
The following little-endian words include variant `0x1020` or `0x1010` at
offset 12, an entry value at offset 16, and the string-pool word offset at
offset 20. Multiply the latter by two to obtain the byte offset. Offsets 24
and 28 are zero in accepted scripts. The pool begins with an empty string;
nonempty strings start at even offsets and are NUL-terminated CP932.

`tools/script_strings.py` validates the full pool and stores only IDs, hashes,
locations, encoding metadata, and verified instruction references. For compressed resources,
string offsets refer to the decoded resource; the outer source bank offset and
encoded-resource hash remain separately recorded. A matching source hash does
not make two occurrences interchangeable translation contexts.

Current measured scope:

- 801 script resources: 554 stored directly and 247 compressed.
- 327 resources have strings; 474 have no nonempty strings.
- 153,524 nonempty string occurrences; 151,840 contain Japanese.
- 49,607 distinct source strings by hash; 49,545 contain Japanese.
- The initial `0x0105` scan missed 1,669 occurrences. The saved schema-2 index
  resolves all of them as extended 20-bit references and preserves all original
  153,524 stable string identities, hashes, and source locations.

These figures exclude executable UI text, character tables, other data tables,
image/video text, and any still-undiscovered resources. They are not a full-game
translation denominator. Raw resource inventory classifications remain unchanged;
this index is a separate, deeper interpretation of those assets.

## Instruction and reference validation

`tools/sn3_vm.py` models the interpreter dispatch at module address `0x1e8050`,
its handler table at `0x22a3f8`, and value reader at `0x1e82a0`. Instructions
start at byte 32 and end at the pool boundary. A 16-bit instruction word contains
six opcode bits, six mode bits, and four high operand bits. The recognized
opcodes range from `0x00` through `0x22`; operand width depends on opcode/mode.

Push-value opcode 5, mode 4, reads one following 16-bit word. Its text address is:

```text
pool_word_offset = (instruction_high_nibble << 16) | following_word
text_address = script_base + pool_byte_offset + pool_word_offset * 2
```

This explains why looking only for instruction word `0x0105` missed larger
offsets. The existing format supports 20-bit word offsets. Appending translated
strings within that range can retain instruction lengths and branch locations;
actual runtime capacity must still be established separately. Schema 2 uses
`reference_instructions` for instruction byte offsets; schema 1's removed
`reference_candidates` identified operand offsets and must not be reused.

Read-only validation against every indexed source resource passed:

- 801 scripts; 2,314,749 instructions decode to the pool boundary.
- Every entrypoint and all 567,372 decoded call/jump targets hit instruction starts.
- All 153,524 nonempty strings have valid references; one reference uses the
  empty pool base. No nonempty string remains unreferenced.
- 1,669 text references use the extended form.

Input hashes, method, and examples are recorded in
[script_vm_validation.json](script_vm_validation.json). These checks establish
structural consistency, not command meanings or the order dialogue is displayed.

## Relocation and static proof

`tools/script_repack.py` appends aligned CP932 target strings, verifies each
source hash, and rewrites all verified references using the existing high nibble
and 16-bit operand. It retains the original pool and all instruction boundaries.
Unknown targets, wrong hashes, raw controls/NULs, encoding loss, and offsets beyond
the format's 20-bit range fail explicitly. Targets remain full-length; no source
byte-length limit is imposed. Runtime substitutions and control-token grammar
still need semantic mapping before production translation.

The dialogue-specific `dialogue_fullwidth_cp932` profile converts ordinary English
targets to existing two-byte wide Latin glyphs, because this consumer reads one
16-bit CP932 unit per character. It preserves the control characters identified
by `0x68070` and rejects accidental punctuation collisions. Strings have aligned
two-byte terminators. Other consumers may use ordinary CP932, so this profile is
explicit per target, never inferred for every script string.

`tools/verify_script_tools.py` dry-runs by default and writes its report only with
`--write`. It checked relocation of the first and last strings of all 327
text-bearing scripts (654 synthetic targets), re-encoded all 247 changed compressed
scripts, exercised shared references and offsets beyond 65,535 words, and checked
1,365 codec edge cases plus 12 invalid inputs. Synthetic text is kept in memory;
no test translation corpus or game asset is written. See
[script_tools_validation.json](script_tools_validation.json).

## Reinsertion gate

The byte-level tools are ready for controlled experiments. Before treating
translated scripts as a playable candidate:

1. Extend the opening-script builder integration to other loader regions while
   preserving source-hash, reference, and unchanged-resource checks.
2. Establish command meanings, jumps, branches, speakers, substitutions, and
   dialogue order. Pool order alone is not confirmed scene order.
3. Measure fixed runtime buffers and adjust allocation/loader behavior as needed;
   reference capacity is not available RAM. Inspect rendering/substitution buffers
   as well as script storage; see [SCRIPT_RUNTIME.md](SCRIPT_RUNTIME.md).
4. The first three longer lines now pass in-game checks. Next validate an ordinary
   multiline box, a substitution, a branching choice, scene transitions, and save/load.
5. The first 80-row pilot slice has 79 reviewed drafts. Expand bulk contextual
   translation after the remaining insertion gate passes. This index retains only
   metadata; target text and review records live in separate files.
