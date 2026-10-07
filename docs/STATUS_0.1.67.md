# Status help — local test build 0.1.67

The original help writer wraps the translated Learn Skills hint onto a third
row. This room screen displays only two rows, so both its SELECT icon and label
disappear. The new second row uses **L/R Switch — SELECT Learn Skills**.
Five native space cells reserve 34.875 pixels between SELECT and its label;
the icon itself follows the measured proportional prefix width.

The shortcut string is relocated to appended memory. Three audited native
bindings use the new string; the old string, adjacent descriptions, and Level
Up's separate hint remain intact. The L/R hint is shortened within its own
slot. No writer buffers, row limits, or glyph capacities are enlarged.

The name table already contains **Rexx** and **Aty** for all four protagonist
class ranks. A Japanese name in an older save is a player-name value, not an
untranslated table entry. This build preserves that value and all custom names.
Whether the reported name was kept as the default or entered manually remains
unconfirmed; no name conversion has been applied.

Validation passes 18 cumulative groups: 14 rerun on the completed ISO, three
retained groups supported by unchanged bank/helper checks, and the new native
Status formatter/position checks. The new checks cover 16 formatter combinations
and 18 icon cases at two load bases, with buffer/stack guards and nonmatch
fallbacks. The retained Give Food helper also executes through the new handler
at both bases. The private chapter-script arena remains writable and intact.

PPSSPP 1.20.4 fresh boot, normal Chapter 15 Continue/load, and battle-menu
interaction pass with JIT and IgnoreBadMemAccess disabled. No save state was
used. Exact room-screen visual verification remains pending a matching save.

Test ISO: `work/output/0.1.67/Summon_Night_3_EN_0.1.67.iso`.
This is a local test build; the published release remains 0.1.65.
