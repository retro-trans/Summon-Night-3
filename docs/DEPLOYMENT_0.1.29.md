# Deployment VWF and shortcut alignment — 0.1.29

Base: immutable 0.1.28. The name, class, attack and stance calls in the status
card now use the previously tested, bounded 16-cell VWF binder. Longer labels
retain its native fallback. Call sites: 0x16e9d4, 0x16ea58, 0x16f8e8, 0x16fa1c.

Support descriptions are built in chunks of up to eight cells. The bind at
0x16eb94 now uses the existing proportional packer; 0x16ec0c positions each
chunk by the measured prefix advance at native 7/8 scale. Unknown cells retain
the original 14-pixel advance.

The icon callback at 0x64490 replaces the fixed index*13 position with the
same measured prefix used for the text. It only applies to text matching the Deployment
shortcut source at module 0x338a2c, including temporary runtime copies. Icon placeholders and unknown cells retain
13-pixel advances. Native Y/Z, style and icon artwork remain unchanged.

Fifty-four emitted-MIPS cases at two load bases verify prefix positions,
nonmatching-source fallback, unknown cells, stack guards and preserved
registers. The build checks all ISO files and all archive resources.

Runtime verification passed in PPSSPP 1.20.4 with software rendering, a fresh
launch and an in-game save. Aty and Soldier both display proportional name,
class, attack and stance fields. Aty's support description reads naturally
across its three packed chunks. Circle/Deploy, Triangle/Status/Gear and
Cross/Map icons align with their labels without overlap.

The Status/Gear view opens, preserves numeric stat spacing, and returns to the
map normally. Screenshots and framebuffer metadata are in
`work/ui/ui_fixes_0.1.29/runtime/final_*.png` and matching JSON files.
Only Aty/Soldier and the pictured support description were tested live.

Tested ISO SHA-256:
`0c467f525735c6f52b4cb8d6dd802c52dc218845bc7904fee72654aff7562cda`.
All 23 bank indexes and 5,729 unchanged bank resources were verified.

