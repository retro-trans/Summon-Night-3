# Battle magic heading translation — 0.1.33

Base: immutable 0.1.32. The battle spell-list heading showed the Japanese saved
summon name even when the summon list and spell names were translated.
The caller at module 0xc0814 used the native text-update method (0x1cbee0),
which bypassed both saved-name lookup and proportional packing.

The new wrapper sends populated heading objects through the existing bounded
list renderer at 0x34a0c8. Null text and unallocated objects retain the native
update path. The existing table contains 121 exact default-name mappings;
unrecognized custom names pass through. The patch changes display behavior
without writing save data or changing the approved name translations.

254 emitted-MIPS cases at two load bases cover heading dispatch, native fallback,
every existing name mapping, custom names and unchanged source strings.
The ISO builder checks all files, 23 archive indexes and 5,729 unchanged resources.
Runtime evidence is in work/ui/ui_fixes_0.1.33/runtime.

Runtime verification passed in PPSSPP 1.20.4 software rendering after a fresh
launch with the existing in-game save (no save state). Dritol now appears in
English with proportional spacing in the battle spell-list heading. Switching
to Shine Saber updates its heading correctly, and backing out returns to unit
commands. Other summon names were checked through the shared mapping tests.
The pre-existing long Shine Saber spell title still crowds its MP cost; this
release changes the summon heading only.

Tested ISO SHA-256:
`27dceb9e458f37872f14779e62312808b9ffb7bc95d2493217c127b3accc391d`.
