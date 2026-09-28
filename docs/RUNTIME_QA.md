# Candidate 0.1.0 runtime evidence

Tested 2026-09-26 with PPSSPP 1.20.4, software rendering, a hidden workspace-local
process, and the loopback debugger. Original ZIP/ISO remain unchanged.

## Passed checks

- Candidate ISO SHA-256 is
  `c3ebd0a056f344ab5b8a5b18ce9efae793fd62e54fcb68253caed58f82c8746c`.
- Static validation preserved all 34 untouched ISO files and 1,453 untouched bank
  resources; all 23 indexes and all 2,312 character references were checked.
- Clean candidate launch reached the opening movie, title, new-game/difficulty
  menus, protagonist selection, affinity selection, name entry/confirmation,
  and the first story scene. Screenshots are actual framebuffer captures.
- In name entry, the relocated table was found at runtime `0x08ce5830`.
  After converting its absolute pointers back to source-relative values, all
  33,680 bytes match the candidate table. Every one of the 2,312 pointers was
  checked, including all 14 references to the three draft labels.
- Complete decompressed story resources `00:00064` and `00:00065` match live
  memory byte-for-byte. Details and hashes are in [SCRIPT_FORMAT.md](SCRIPT_FORMAT.md).

## Captures and reproduction

`work/ui/screens.json` gives screen IDs, file paths, roles, and provisional UI
rectangles at the native 480×272 resolution. Capture JSON sidecars record the
framebuffer address, stride, format, and PNG hash. Unlisted captures include
opening movie frames and black/transition frames; they are not layout evidence.

Reproduction sequence from a fresh candidate launch:

1. Circle skips the opening movie. Allow the title logo to finish appearing.
2. Start opens the title menu. Circle selects New Game; Circle selects Normal.
3. Circle selects Rexx; Circle accepts the displayed Machine affinity.
4. Start opens default-name confirmation. Up selects Yes; Circle confirms.
5. The first story scene appears. No save was created during this smoke test.

The test session was deliberately left CPU-stepping on the first story scene,
after capture `0.1.0_frame_15.png`. Revalidate the PID/API and state before reuse;
resume explicitly before input. A saved session record is not proof of liveness.

## Open checks and observed gaps

- The name-entry default remains Japanese. It comes from a separate source from
  the patched character/class table. Candidate `0.1.0` does not translate it.
- Rexx, Aty, and Family Teacher are meaning-reviewed and loaded, but their actual
  label rendering, maximum width, clipping, and all consumers remain unverified.
- Dialogue is still Japanese. No translated dialogue or branch was inserted.
- The first story text uses a centered display, not the ordinary dialogue box;
  this capture cannot establish ordinary dialogue limits or maximum characters.
- Save/load, battle menus, status screens, route coverage, real PSP hardware,
  expanded script allocations, and complete font coverage remain untested.
- The build manifest records static verification at build time. Its false runtime/
  visual fields do not claim later acceptance. Subsequent bounded runtime evidence
  is saved separately as `work/output/0.1.0/runtime_validation.json`.

## Capture implementation evidence

The corrected launch parameters come from
[PPSSPP's Windows entry point](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Windows/main.cpp).
The capture uses the documented implementations for
[breakpoints](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/Debugger/WebSocket/BreakpointSubscriber.cpp),
[CPU registers](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/Debugger/WebSocket/CPUCoreSubscriber.cpp),
and [memory reads](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/Debugger/WebSocket/MemorySubscriber.cpp).
The emulator's own GPU capture API failure remains separate from this verified
software framebuffer capture path.
