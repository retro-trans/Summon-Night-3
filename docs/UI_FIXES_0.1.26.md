# UI fixes 0.1.26

This build uses 0.1.25 as its immutable base and addresses the four supplied
inventory, summon-index and battle-dialogue screenshots.

- The locked summon description retains its question marks and now says
  “Favorites Only.” Its two-line record starts at executable file offset
  0x216428; the reference is to that root, not the restriction's text address.
- Shine Saber's ability becomes “Crush! Light Gen. Sword.” The name is
  relocated in summon-ability table 13, record 233, slot 8, with the resident
  master-table copy updated identically. The label uses proportional spacing.
  The native cache only has entries of 1, 8 and 16 cells. A new helper handles
  17–32 Latin cells by copying two native glyph chunks to guarded stack storage,
  then packing their ink into one existing 16-cell strip. Labels qualify only
  when their measured advance fits 256 native pixels; shorter labels and
  unsupported glyphs retain the existing path.
- Kyle's name lettering and matching shadow layer are replaced in both
  02.DAT portrait pack 914, children 3 and 4, and battle pack 1098, children 1
  and 2. Other portrait layers are unchanged.
  The spelling follows the selected SN6 Vita gallery glossary. The transparent
  lettering was generated with the built-in image tool, scaled proportionally
  and mapped to the original native palettes.

The text was independently reviewed for meaning. The full translation is
“Shatter! Light General's Sword!” The compact display retains the imperative
and sword title, abbreviating General and using a title compound so the label
clears the MP cost. The hidden
ability remains hidden; no question-mark placeholders are revealed.

Inventory stat rows use symbolic font mode 6: a source space may draw a plus
sign instead of an ordinary space. Their placement now uses the native callback;
ordinary descriptions retain VWF. Live tracing and a temporary native-call probe
identified the overlap before the mode-specific correction was built.

The emitted long-label MIPS passed 12 cases at two relocation bases using the
actual glyph pixels. Checks cover two bounded native population calls, the
16-cell drawing extent, adjacent texture memory, stack bounds, cache-code
invalidation and preserved registers. Archive building compares all untouched
resources, validates all 23 bank indexes, and checks the resident table mirror.

The final ISO was tested in PPSSPP 1.20.4 with software rendering, a fresh
launch and a copied in-game save (no save state). The first pirate battle's
preparation menus confirmed readable AT+17, Favorites Only with locked question
marks preserved, and the full compact spell name clear of the MP value. Starting
the battle confirmed Kyle's English label and translated opening speech.

Final screenshots and capture metadata are in
`work/ui/ui_fixes_0.1.26/runtime/final_*.png` and matching JSON files. Their
hashes are bound to the release ISO in the manifest. This is a targeted test of
the available saved-game menus and first battle, not a full playthrough. The
larger portrait-name variant was checked as a native decoded asset; the battle
variant was additionally checked in-game.
