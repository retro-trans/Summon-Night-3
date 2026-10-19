# 0.1.85 — Level Up controller hint spacing (local test build)

Fix the overlapping Circle/OK, Cross/End and Select/Skills hints in Level Up.
The native icon artwork is wider than the renderer's nominal character advance.
Add space after each icon and use “Skills” for the Select label. Apply the same
spacing to bonus-point confirmation.

The full hint stays on one line within the native 27-cell staging limit. Native
formatter tests cover all eight combinations of unit availability, bonus-point
allocation and optional skill access. Tests guard both sides of the buffer and
check the icon/text bounds using the actual proportional font metrics.

Reuse existing English storage. No executable, ISO or loaded-memory growth;
preserve code, relocations, save data, progression rules and all other ISO files.
Retain all fixes from local 0.1.84 and published 0.1.83.

The test package supports 0.1.83 and 0.1.84 input ISOs through Retro Trans Tools.
Use the patch matching your input version, or let the tool identify the image.
Start normally and load an in-game save rather than an older emulator state.
This is a local test build; 0.1.83 remains the published release.
