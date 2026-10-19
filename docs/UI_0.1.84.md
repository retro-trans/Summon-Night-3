# 0.1.84 — Battle rewards and class-change UI (local test build)

Changes from published 0.1.83:

- Give both Retreat button states the neighboring Load button's wooden frame,
  highlight, alpha outline and native palette; retain native 112 × 24 geometry.
- Route the missed summon-animation name branch through the existing glossary
  lookup and proportional renderer. This includes Riser and other default summon
  names. Custom names and save data are preserved.
- Use the bounded heading “Rewards earned!” in the reward notification.
- Use VWF throughout the remaining reward/discovery popup bindings. Format
  “Party ability: Stone Search” without a trailing quote crossing the skill name.
  Measure the adjacent found-item name using proportional glyph advances.
- Reuse 0.1.82's immutable equipment captions for proportional class-change rows,
  including HSlash×Katana. No extra caption table is allocated.
- Translate both class-selection help states, confirmation, Yes and No. Display
  the class name on its own row followed by “Use this class?”.

Validation executes the emitted MIPS helpers at two relocated load addresses,
checks saved default-name aliases and custom-name pass-through, and verifies the
button's frame, palette, alpha and footprint. The ISO builder verifies all 23 bank
indexes, unchanged resources and historical input hashes.

An initial candidate exposed a tight PSP memory budget at boot. It was discarded.
The final helper reuses the existing caption arena and adds under 1 KiB of loaded
code/data instead of padding and a duplicate caption index.

Runtime coverage and its limits are recorded in the accompanying validation JSON.
The exact beach/reward/class-change save is unavailable; those complete gameplay
sequences are not claimed as reproduced. Private saves are not distributed.

Apply SN3-English-v0.1.83-to-v0.1.84.xdelta to the published 0.1.83 ISO with
Retro Trans Tools. Start the game normally and load an in-game save so the new
executable is used. This is a local test build; 0.1.83 remains the public release.
