# 0.1.87 — Crafting accessory name widths (local test build)

The crafting accessory column already uses proportional lettering. Its compact
“One-EyeMagatama” label still advances 142.625 pixels at the current scale,
which reaches the scrollbar. Use “1-Eye Magatama” (121.625 pixels). The related
“Arabesque Charm” label also exceeds the conservative 128-pixel column budget;
use “Arabesque Chm” (117.25 pixels).

Audit all 85 nonempty accessory names, including apostrophes through their
encoded font metrics. Update only these two English literals in both the
static table and the master cached copy. Keep the same allocations, pointers,
archive indexes, executable bytes and ISO size. All 0.1.86 fixes are retained.

The included validation records archive integrity, width checks and runtime
coverage. This ZIP supports published 0.1.83 or local 0.1.86 through Retro Trans
Tools. Boot normally and load an in-game save. This is a local test build;
0.1.83 remains the published release.
