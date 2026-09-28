# Script memory and display investigation

Latest follow-up: candidate `0.1.4` supplies a separately allocated 192-object
font pool. The 69-glyph crash regression, later 72/68-glyph pages and one choice
branch pass, with all six hooks, object vtables and the complete script verified
in RAM. The separate live pool is at `0x08b32010`, 43,008 bytes. Direct allocation/
free-event tracing and broader acceptance remain; see [0.1.4 QA](RUNTIME_QA_0.1.4.md).

Earlier follow-up: candidate `0.1.3` loads the complete 188,010-byte opening script
and its added executable hooks, but fails on a 69-glyph page. The text context's
font pool pointer at `+0x30` and capacity at `+0x34` identify only 64 initialized
objects of stride `0xe0`; these are separate from the context's glyph records.
Source setup passes 64 at module `0x6b510`. Preserve the captured fault and trace
storage ownership/lifecycle before expanding it. See [0.1.3 QA](RUNTIME_QA_0.1.3.md).

Earlier follow-up: candidate `0.1.2` loads the complete 187,702-byte opening script,
including appended code for word wrapping and continuation pages. Selected
portrait pages and a choice result are verified. See
[0.1.2 runtime QA](RUNTIME_QA_0.1.2.md) and [dialogue layout](DIALOGUE_LAYOUT.md).
Larger chapter allocations, other loaders, tokens, and save/load remain open.

Follow-up: candidate `0.1.1` now loads a 66-byte-larger opening script and renders
three relocated English lines. Its complete live contents and third processed
line are verified. See [current runtime QA](RUNTIME_QA_0.1.1.md). The investigation
below records the original `0.1.0` state and still-unresolved broader constraints.

Observed 2026-09-26 using candidate `0.1.0`, PPSSPP 1.20.4, and its live debugger.
The process was revalidated and remains CPU-stepping on the first opening-story
screen. No memory was changed, input sent, or new build launched for these checks.
ELF addresses below are module-relative; observed runtime addresses are session
specific. The main module load base was `0x08804000`.

## Workspace allocation and script regions

The executable calls allocator wrapper `0x13e2c` at `0x12dc0`, requesting
`0x1380000` bytes. The wrapper records the returned base at object offset 8 and
the requested size at offset 12; `0x13ee4` returns that base.

Live manager `0x08a3cd80` contained flags `1`, block ID `0x117`, base
`0x08b42000`, and size `0x1380000` (20,447,232 bytes). Its end is `0x09ec2000`.
Runtime code immediates confirm the manager address. Do not infer it directly
from unrelocated ELF immediates; PSP relocation adjusts them and JIT markers can
replace individual instructions in raw memory reads.

| Script role | Offset from workspace | Observed/derived address | Evidence |
| --- | --- | --- | --- |
| Common | `0x240000` | `0x08d82000` observed | Loader calls at `0x209c8`, `0x20b50`; full original script matches RAM |
| Main | `0x248000` | `0x08d8a000` observed | Loader call at `0x2116c`; full original script matches RAM |
| Secondary | `0x2c0000` | `0x08e02000` derived | Loader call at `0x21324`; buffer contents not verified |
| Encoded input scratch | `0xf88000` | `0x09aca000` derived | Shared input address at all four story decompression call sites |

The spacing is 32,768 bytes from common to main, and 491,520 bytes from main
to secondary. These are observed fixed start differences, **not proven safe
capacities**: all uses and adjacent regions must be mapped. The largest indexed
compressed script decodes to 420,108 bytes (`00:00295`), so retaining its original
pool and appending all translations can exceed the apparent main-region spacing.
Production support must relocate/expand allocation as needed, rather than impose
original string byte limits. The full 20 MiB workspace is not free script space.

## Live VM state and first text consumer

| VM | Runtime object | Script base | Script PC (words) | Active native call |
| --- | --- | --- | --- | --- |
| Common | `0x08a3a9a4` | `0x08d82000` | `0x2d1f` | `0x1003`, state 1 |
| Main | `0x08a3a9e4` | `0x08d8a000` | `0x88f` | `0x3052`, state 2 |

The main VM's stack pointer is `0x08a3a25c`; stack index and frame base are both
35, and capacity is 128 words. Native arguments precede the saved argument count
and prior frame base. Accessor `0x1e8020` computes argument `i` at
`stack[frame_base - 2 - argument_count + i]`.

Native dispatcher `0x21690` chooses a group using ID bits 12–15 and a member using
the low 12 bits. The group pointer table is at `0x2267c8`, with eight-byte member
descriptors. Group 3's table is `0x227088`:

| ID | Handler | Current interpretation |
| --- | --- | --- |
| `0x3050` | `0x29b74` | Queues a text pointer, boolean field, and integer field through `0x68d00` |
| `0x3051` | `0x29c3c` | Passes two arguments to `0x6b5c4`; exact role not yet proven |
| `0x3052` | `0x2c1b0` | Uses eight arguments and a state machine; active while the opening text is visible |

The first centered text corresponds to `00:00065:text:0002646e` (source offset
156,782), pushed at instruction byte offset 76,240. Its call at 76,244 invokes
script helper word 2,003. That helper passes the string, zero, and minus one to
native `0x3050`. Following strings have intervening calls and conditional branches;
pool order must not be treated as an unconditional dialogue transcript.

## Rendering structures requiring bounds checks

`0x68d00` stores one 12-byte text descriptor and increments a count without an
observed capacity check. Reset routine `0x68d40` initializes six descriptors.
`0x68d70` initializes six processed-line records, each with 32 four-byte entries.
`0x68bfc` fills the entries from 16-bit input, expanding three special token
classes through runtime pointers; no output bound is visible in that routine.

These structures need tracing before longer Latin lines are rendered. The 32
entries are not yet a validated user-facing character limit: conversion, tokens,
line splitting, and glyph widths must be established. Do not truncate translations
to fit an inferred limit. The live text context was `0x08e30910`; its pending queue
was empty after processing the first visible line.

Current next step: trace real-heap lifecycle and remaining alternate/stress
pages for the corrected font pool. Mapping all workspace regions and validating
branches, transitions, substitutions, and save/load remain open.
