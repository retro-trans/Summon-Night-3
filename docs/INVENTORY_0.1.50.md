# Inventory text and two-line help: 0.1.50

The reported Black Rose Knife description had three rows. It met the native
54-glyph allocation limit but overflowed the Inventory help panel, which shows
two rows. This build adds a second, visual contract: equipment descriptions
must fit two rows of at most 27 native cells each.

The formatter-tail helper preserves existing one- and two-row descriptions.
For longer descriptions it joins rows, compacts effect labels, collapses
alignment padding, and chooses a word boundary that fits both rows. It prefers
the existing first-row boundary when possible, keeping Black Rose Knife's
`Blind Hit30%` effect together on the second row. It retains
stat control cells, numbers, percentages, effects, gender restrictions and
key-item labels. It does not expand the native buffers or change gameplay data.
It leaves the v0.1.49 help and glyph safety guards unchanged.

The build also translates all 76 remaining Japanese weapon names. Ordinary
loanwords use English names; coined proper names use individually selected
ASCII transliterations, not a claim of official English spellings. The four
reported names become Glass Edge, Chinese Cleaver, Harsneil and Ragres Saber.
Existing English weapon names and armor/accessory translations are preserved.

New inputs are in `work/translation/en/inventory_0.1.50`. Historical build
inputs and their recorded hashes are unchanged.

Validation is recorded in the output manifest and `stability-report.json`:
all 1,434 weapon/armor/accessory and key-item combinations execute the native
formatter and staging loops. Checks enforce the two-row contract, stack and
output-buffer boundaries, preservation of content after documented shorthand,
and English coverage for weapon-name references. The cumulative audit also
retains the Brave Goal, unit encoding, skill, Cooking and renderer-guard checks.
Runtime evidence is recorded separately; static checks do not establish that
every room, menu, chapter or platform has been played through.

Build and patch workflow:

```powershell
python tools/build_inventory_050.py --write --destination work/output/0.1.50
python tools/verify_stability_050.py --build work/output/0.1.50 --report work/output/0.1.50/stability-report.json
python tools/package_inventory_050.py
```

Use the patch matching the exact source ISO version. Start the patched ISO
fresh and load a normal in-game save, because a prior save state can restore
older code into memory.

Final candidate verification (2026-09-30):

- ISO SHA-256: `9040522514c77f8701e41e064ad1ca9402b3ec8b640db41167bcb10a47bbe507`.
- Ten cumulative audit groups passed. All 1,434 equipment/key-item variants
  fit two rows; all 263 populated weapon-name references are English.
- Fresh boot in PPSSPP 1.20.4, JIT with software rendering and strict memory
  handling: normal Chapter 15 Continue, Inventory navigation, translated names,
  quantity alignment and Black Rose Knife's two-row description passed.
- Live help/glyph guard counters stayed zero; all three checked hooks matched
  the final executable, and the emulator log contained no bad-memory-access fault.
- Screenshots and ISO-bound runtime results are in
  `work/ui/inventory_0.1.50/runtime-validation.json`. This runtime check used
  battle Inventory; the room context and mobile platforms remain untested.
- Original-to-0.1.50, 0.1.42-to-0.1.50 and 0.1.49-to-0.1.50 xdelta patches
  were decoded with the retro-trans-tools engine and matched the target ISO
  byte for byte. Patch hashes are in `work/output/0.1.50/XDELTA-VALIDATION.json`.
