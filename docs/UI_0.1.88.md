# 0.1.88 — Shine Saber spell caption (local test build)

Restore the missing Shine Saber spell name as “Crush! L.G.Sword”. The previous
“Crush! L.Gen.Sword” label contained 18 encoded cells, exceeding the existing
16-cell font-cache strip even though its proportional width fit the column.
The new label retains Crush, Light General's initials, and Sword in 16 cells
and advances 120.75 pixels at the existing proportional scale.

Check all 235 nonempty spell names for both the 16-cell cache limit and the
140-pixel column budget. Update the English literal in the static table and
its master cached copy. Synchronize the existing battle-banner name dictionary
to the corrected spelling, and execute all 144 dictionary matches at two load
addresses. Preserve pointers, archive sizes, executable instructions, loaded
memory use and save format. All 0.1.87 fixes are retained.

Fresh-boot tests with a normal in-game save reproduce the blank row on 0.1.87
and show the corrected proportional caption on 0.1.88 in Summon Index. Switching
to Dark Bringer and back preserves the caption. Reading the live font cache
confirms its largest strip holds 16 cells. The exact Create Summons casting
screen was not replayed.

The ZIP contains Retro Trans Tools upgrades from published 0.1.83 and local
0.1.87. Boot normally and load an in-game save. This is a local test build;
0.1.83 remains the published release. Runtime coverage and limits are recorded
in the included gameplay validation. The separate Brave Medal award heading
remains pending.
