# Continue crash report — 0.1.41

## Evidence

The reporter's screenshot shows PPSSPP 1.20.4 release on Windows x64, JIT with
flags 0, no cheats/plugins, invalid address 0x00000029, approximate PC
0x08868b8c, and JIT location 0x089cfea8 in function 0x089cfe94.
The screenshot's CRC32 `eb48461b` equals the CRC32 calculated across the entire
verified released 0.1.41 ISO. CRC matching is not a cryptographic identity check,
but it makes a wrong or damaged image a weaker lead. The unrecognized-CRC
message alone does not establish image corruption.

With the game's 0x08804000 load base, the approximate PC is module 0x64b8c,
in the native multi-line help renderer (function 0x64820). The JIT location is
module 0x1cbea8: `sh zero, 6(a1)`, in a rendering-object reset helper. The help
glyph loop calls this helper at module 0x64c14. Its object pointer comes from
the glyph object plus offset 0xc0. If this store generated address 0x29, that
pointer was 0x23, which is invalid. This is an inference without registers.

Both inspected routines are byte-identical to the original executable. This
does not exonerate translated text or earlier memory writes: incorrect text
lengths, missing terminators or damaged object state can fail in native code.
Earlier help/stance capacity bugs involved this same renderer, making its
29-cell line buffers and 54-object glyph pool relevant leads, not a confirmed
cause of this report.

PPSSPP's 1.20.4 fast-memory error handler uses an approximate saved PC and
reports size zero because the access size is not yet decoded there. Do not
treat the displayed `Read Word (sz: 0)` as a precise account of the native
store shown below it. Source:
https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/MemFault.cpp
CRC calculation:
https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/Reporting.cpp

## Reproduction

The submitted archive contains battle suspend, clear and system saves.
Continue was tested with copies of the Chapter 15 battle suspend on the
released ISO, fresh boot, PPSSPP 1.20.4 Windows, software graphics and JIT.
It loads successfully and the unit menu responds.

The initial configuration inherited PPSSPP's `IgnoreBadMemAccess=True` default.
A second, separate instance explicitly used `IgnoreBadMemAccess=False`,
`FastMemoryAccess=True` and JIT. Continue, save confirmation and the transition
into battle also passed. Its log contained no bad-memory-access report during
that sequence. Thus the first success was not sufficient evidence by itself,
but strict testing has not reproduced the reported fault either.

No reporter configuration was supplied. Graphics backend, prior menu actions,
possible emulator-state restoration and exact fault timing remain unknown.
A recording from fresh launch to failure plus `PSP/SYSTEM/ppsspp.ini` and any
`NPJH50380_ppsspp.ini` would help reproduce the remaining environment/state
conditions. Preserve settings and saves; do not use ignored memory accesses
as a claimed fix. No game patch is changed based on this unconfirmed cause.

Submitted archives and extracted data remain private under ignored incoming
and scratch folders. The user's normal PPSSPP instance was not altered.

## Supplied global settings

The subsequently supplied global configuration confirms strict memory checks
(`IgnoreBadMemAccess=False`), JIT, fast memory, zero JIT-disable flags and no
forced CPU frequency. These CPU settings agree with the successful strict test.
It selects Vulkan with software rendering disabled and enables audio. The
successful strict test used software rendering with audio disabled.

Global cheats/plugin switches are enabled, while the crash screenshot reports
no active cheats/plugins. An enabled global switch does not prove that a code
or plugin was loaded at the time. No cheat/plugin definitions or per-game
configuration were supplied. Automatic save-state loading is disabled; this
does not establish whether a state was loaded manually earlier.

`FileLogging=False` means a persistent diagnostic log was not enabled by that
configuration, despite the generic logging switch being enabled. The private
comparison instance enabled file logging and used copies of the submitted
saves. Vulkan boot and native savedata requests ran, but framebuffer download
was unavailable and the desktop capture helper failed to initialize. This
comparison did not establish a successful full Continue-to-battle reproduction
under Vulkan. The earlier software-rendered strict test remains the completed
load test. No new root-cause claim or fix follows from this configuration alone.

Next useful evidence is the per-game `NPJH50380_ppsspp.ini`, if present, and a
fresh-launch crash recording/log. An isolated Direct3D 11 versus Vulkan test
on the affected machine can separate backend-related behavior; keep strict
memory checks enabled. Uploaded configuration and private paths are not
included in the repository.

## Repeated report and expanded test

A subsequent supplied log repeats guest address 0x00000029 and JIT site
0x089cfea8 in function 0x089cfe94. This confirms the same fault signature,
not its upstream cause. The log does not identify which graphics backend was
active, so it alone does not prove that the requested backend switch occurred.

A fresh isolated software-rendered test now retained the reporter's supplied
CPU, system and audio configuration (including strict memory checks and enabled
audio). Continue, battle-suspend confirmation, completion and the return to
Chapter 15 gameplay all passed. No memory fault appeared in its log. The MPEG
UNIMPL message also occurs in this successful run and is not evidence of the
reported rendering-object fault.

An audit of relocated slot-9 descriptions in static tables 31 and 34 found no
changed description exceeding 29 U16 cells per line or 54 total glyphs in the
native three-line traversal. This does not cover every dynamically generated
help string or identify the text active at the reporter's crash.

The most useful next capture is a PPSSPP save state immediately before the
failing Continue action, together with the exact action sequence. It is a
forensic snapshot of live memory, not a substitute for fresh-boot validation
of any future fix. An emulator state may preserve the missing corrupted object,
prior menu state or stale executable data that the in-game save cannot supply.
No new game build or speculative pointer-suppression patch has been made.

## Confirmed reproduction and fix (2026-09-28)

The subsequently supplied PPSSPP state reproduces the fault immediately.
Its renderer at 0x098aeac0 has a glyph count of 55 and capacity 54.
The invalid object is at 0x098b3590, with attachment pointer 0x23; the
`sh zero,6(a1)` instruction attempts address 0x29. The active text is
the recovery-item Brave Goal description, followed by its exclusion note
and then the next goal title. Missing empty-line termination allows this
third, unrelated line to be consumed. Long lines also overrun row bounds
and the 174-byte staging buffer. All five translated common goal
descriptions fail the native layout limits.

A fresh boot of released 0.1.41, Continue, load battle suspend, return to
map, SELECT, Battle Info, Brave Goals reproduces the same fault without
a savestate: displayed PC 0x08868b8c, a1=0x23, object 0x098b3590.
This establishes a translation-data bug, not a corrupt user save or a
Vulkan-specific failure. The earlier Continue-only tests did not enter
the affected menu. It remains unknown whether the reporter also entered
this menu or restored a state there.

Build 0.1.42 repairs all five common goal description bundles and their
labels. A fresh Continue load and all five goal selections plus menu exit
pass under strict memory checking. See BRAVE_FIX_0.1.42.md. Uploaded
savestates, RAM dumps and configuration remain private and ignored.
