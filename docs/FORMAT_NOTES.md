# Verified extraction findings

Updated 2026-09-26. These findings extend the initial repository scan. The goal
remains translation of all Japanese game text. Extraction and bounded playable
candidates exist; the translation and production insertion pipeline are incomplete.

## Source and executable

- `work/source/original.iso` is a working copy verified against the original
  ZIP and ISO SHA-256 values in `source_scan.json`. The original ZIP is unchanged.
- `work/source/EBOOT.enc` is the original encrypted executable. `pspdecrypt 1.0`
  successfully decrypted tag `D91613F0` (type 2) to `work/source/EBOOT.elf`.
- The plaintext executable is 2,885,105 bytes. SHA-256:
  `82cc184377986d90d298ee4918fb11bd0e3524659e5c6f8b7b3c859f4d232684`.
- ELF segment 0 starts at file offset `0xC0`, virtual address zero. Addresses
  below are module-relative; runtime addresses additionally require the load base.
- A file descriptor table at ELF file offset `0x2262F0` has 16-byte records:
  bank ID, filename pointer, resource count, and flags. Bank counts agree with
  the decoded resource indexes.
- Initialization around module address `0x137C8` loads bank 00 resource 44 and
  obtains the indexes for the other banks from its children. This was the key
  to finding the external indexes. The initial audio-only interpretation of
  `00.DAT` was incomplete: it also contains shared data and indexes.

## Indexed packs and external bank indexes

Header, little-endian:

```text
u16 entry_count
u16 tag = 1
u16 unit_shift
u16 bias_units
entry_count * { u32 offset_units; u32 length_units; }
```

For a payload entry:

```text
unit = 1 << unit_shift
byte_offset = (offset_units - bias_units) * unit
byte_size = length_units * unit
```

The earlier scan treated the last two header fields as one 32-bit shift; that
only works for packs whose bias is zero. External indexes use a nonzero bias
because their original index sectors are omitted from the corresponding DAT.

Bank 00 contains its own index at offset zero. Its resource 44 is an eight-child
pack with 16-byte units:

| Child | Content |
| --- | --- |
| 0 | Bank 01 index: 1,314 entries, bias 6 sectors |
| 1 | Bank 02 index: 3,929 entries, bias 16 sectors |
| 2 | Bank 03 index: 5,001 entries, bias 20 sectors |
| 3 | Pack containing the 19 voice-bank indexes |
| 4 | Shared resource pack, duplicated by bank 02 resource 4 |
| 5 | Sound-resource pack |
| 6 | Character data pack, duplicated by bank 01 resource 1 |
| 7 | Shared data pack, duplicated by bank 02 resource 3 |

All 23 bank indexes were checked: entries are contiguous, stay in bounds,
and account for each complete DAT size. Empty entries are significant and must
retain their IDs. The movie `04.DAT` is separate from these 23 indexed banks.

`resource_inventory.json` records all bank entries, their index locations, and
recursive nodes from banks 00/01/02. Audio-bank internals and movie text still
need scope-appropriate checks; the index validation is not text-coverage proof.

## V4 containers

A second format starts with little-endian `0x00040000`. Its 40-byte header has:

```text
u32 version; u32 reserved;
u32 name_count; u32 names_offset;
u32 entry_count; u32 index_offset;
u32 reserved[4];
```

Each optional name record is 20 bytes: a 16-byte zero-terminated ASCII name
and a 32-bit key whose high 16 bits identify the entry. Examples include `BI`,
`SCRIPT`, `AI`, `SUPPORT`, and `MAP`. The low key bits need further semantic study.

Each eight-byte index entry contains a **big-endian 24-bit offset**, a
**big-endian 24-bit length**, and two flag bytes. Offset and length use 16-byte
units. The flag bytes are zero in the examined examples; preserve them rather
than assuming their semantics. Fully zero entries are missing resources and do
not advance the payload cursor. Nonempty entries are contiguous.

The inventory recognizes 719 V4 containers, with no remaining unclassified
nodes beginning with this header. It includes 80 sections explicitly named
`SCRIPT`. This does not establish that all scripts are named or uncompressed.
The inventory snapshot marks 11,718 leaves unclassified. A later script index
recognizes 801 of those exact nodes; their locations and hashes match in the
current repository rescan. Reconcile these classifications before counting
remaining unknown resources. Other text/graphics/compression semantics still
require investigation.

## Character and class labels

The first child of bank 01 resource 1 has a 32-bit record count followed by
32-byte records: one entity number and seven relative string pointers. The
first string-pool position is `4 + record_count * 32`. Strings use CP932,
terminate with zero, and may be shared by several records.

- 784 records; 753 distinct string offsets; 2,312 pointer references.
- 746 of these strings contain Japanese characters; seven do not.
- Every nonzero pointer was bounds-checked and every target strictly decoded.
- The table is byte-identical to bank 00 resource 44 / child 6 / child 0.
  Both copies must be changed when building a translation.
- `work/translation/en/character_labels.index.json` stores source hashes,
  offsets, and pointer fields, without storing a full Japanese transcript.
- `character_labels.targets.json` has three drafts, independently meaning-reviewed
  and inserted in candidate `0.1.0`. All are verified in the loaded table; none
  has yet passed visual label-fit checks.

Relocate target strings into a newly appended pool and rewrite every associated
pointer. Rebuild containing indexes, and account for the resident cached copy.
Do not overwrite adjacent source strings or impose their original byte lengths
as a target budget. Dialogue may use a different reference format and still
requires separate investigation.

## Runtime evidence and current limits

Latest candidate `0.1.4` adds a separately allocated 192-object font pool and
matching whole-page guards. The exact 69-glyph crash, later 72/68-glyph pages,
and About myself branch pass. All six hooks, 192 object vtables and the complete
script match live evidence. Direct heap lifecycle tracing, alternate routes,
maximum pages, tokens and save/load remain. See [latest QA](RUNTIME_QA_0.1.4.md).

Earlier candidate `0.1.3` integrates compact Latin spacing and pixel wrapping.
The entire expanded script and added executable code match live memory, and
two sampled pages pass visual checks. It then fails on a 69-glyph page because
the native pool has only 64 font objects. Seven generated pages exceed that
capacity. See [failed candidate QA](RUNTIME_QA_0.1.3.md) and
[font findings](FONT_RENDERING.md). The candidate is not accepted.

Candidate `0.1.2` contains three labels and 78 reviewed opening rows. Bounded
word wrapping adds continuation pages, and the About myself choice reaches its
expected backstory. The complete expanded script matches saved live-memory
evidence; selected screenshots verify a two-page sentence and the choice screen.
See [previous runtime QA](RUNTIME_QA_0.1.2.md) and
[dialogue layout](DIALOGUE_LAYOUT.md) for the exact scope. Font-object capacity,
runtime tokens, larger allocations, alternate paths, and save/load remain open.
The observations below for `0.1.0` preserve the original label-loading evidence.

Candidate `0.1.0` boots under portable PPSSPP 1.20.4 and reaches the title,
new-game menus, character/name selection, and opening story. Its websocket API
works at `127.0.0.1:19380`. All 2,312 loaded character pointers and the complete
normalized table match the candidate; see `work/output/0.1.0/runtime_validation.json`.

The built-in GPU capture API still returns `Could not download output`. Earlier
renderer experiments used incorrect options: `-software` paused startup and did
not select the software renderer. The launcher now uses `--graphics=software`
or `--graphics=directx11`, as implemented by PPSSPP 1.20.4. The new
`capture_framebuffer.py` captures actual software-rendered PSP display buffers
through a temporary `sceDisplaySetFrameBuf` breakpoint. It validates stride and
pixel format, removes the breakpoint, and resumes unless `--hold` was requested.
Actual captures and bounded UI measurements are indexed in `work/ui/screens.json`.
See [runtime QA](RUNTIME_QA.md) for exactly what has and has not passed.

`work/scratch/ppsspp_session.json` records the most recently launched process.
Revalidate its process ID and the websocket before treating it as live; a saved
session file by itself is not evidence. The pip dry-run process used during
setup was terminated after switching to verified wheel downloads; there is no
pending package installation to wait for.

## Next technical steps

1. Preserve all candidates through `0.1.4`; `0.1.5` is the next unused version.
   The font-pool crash regression now passes. Trace actual heap cleanup/reuse,
   visit alternate groups 15/35/41, and test maximum pages before completing
   token/branch/save-load checks.
   Existing wrapping is a bounded opening profile, not general support.
2. Story decompression and 801 script pools are indexed. All instruction
   boundaries, control targets, and text references now pass static validation,
   including the 1,669 extended references missed by the earlier scan. The index
   now stores them, and compression/relocation pass static corpus checks. Extend
   the opening-only build path to other mapped loaders, map commands and dialogue
   order, and establish runtime/rendering capacity. See [script format](SCRIPT_FORMAT.md) and
   [runtime investigation](SCRIPT_RUNTIME.md) for the remaining insertion gate.
3. Continue measuring actual UI boxes with the working capture path and verify Latin
   glyphs, expanded labels/dialogue, choices, scene changes, and save/load.
4. Reconcile resource classifications, complete category coverage, and expand
   the sourced glossary. After the technical gate passes, translate remaining UI
   and dialogue using the 80-row context/review workflow from `BASE_RULES.md`. Executable
   UI/default names are separate from character labels: three Rexx occurrences
   are at ELF file offsets `0x2161a8`, `0x219d30`, `0x21c978`; three Aty occurrences
   are at `0x2162f4`, `0x219d3a`, `0x21c984`. Their consumers still need tracing.

## Tool provenance

- [pspdecrypt release](https://github.com/John-K/pspdecrypt/releases/tag/1.0)
- [PPSSPP release](https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4)
- [PPSSPP debugger implementation](https://github.com/hrydgard/ppsspp/tree/v1.20.4/Core/Debugger/WebSocket)

Tool archives/wheels and their hashes are recorded under
`tools/vendor/download_manifest.json`. Tools and working binaries stay local.
