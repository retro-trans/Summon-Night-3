# Equipment help crash - v0.1.47

## Diagnosis

The newly received state is in the protagonist's room, browsing Inventory /
Weapon. Its thumbnail still highlights Ray Edge, but the active description
matches weapon record 26, Black Rose Knife: four native stat fields, Blind
on hit at 30%, Beast attack affinity, and a female equipment restriction.
The formatted text has 56 U16 cells across three rows. Its renderer owns
54 glyph objects. The saved state is already partway through an overrun;
resuming reaches module PC 0x1cbea8 with an invalid attachment pointer.

The same formatter remains in v0.1.46. This is a separate input path from
the previously fixed Brave Goals overflow. It does not indicate bad save data.

## Change

A scoped helper runs after the equipment formatter. It counts the text and
leaves descriptions at or below 54 cells byte-for-byte unchanged. Over-budget
help uses compact equivalents (Hit, Atk, Female/Male, No Poss., Imm, Key,
Eva+) and removes repeated alignment spaces. Native stat tokens, values,
line breaks, effects, and equipment restrictions remain intact. No pool size,
gameplay data, archive text, or old hashed build input is changed.

Black Rose Knife changes from 56 cells to 45 (49 with the key-item marker).
Sleep Rose Knife and a multi-immunity accessory are also covered. The test
matrix includes every equipment record with both possible key-marker values,
including combinations which may not occur in normal play.

## Validation

- 717 nonzero weapon, armor, and accessory records; 1,434 formatter cases.
- Native writers execute with temporary/output buffer guards and 27-cell
  row bounds. All formatted descriptions contain at most 54 total cells.
- All 1,434 outputs execute through the native help parsing/staging code.
  Graphics binding calls are boundary stubs which assert every object index
  is inside the 54-object pool. No substituted text-wrap implementation.
- The unchanged v0.1.46 formatter/staging reproduces the reported weapon's
  failure at object index 54, establishing the regression test.
- All 1,419 already-fitting variants retain identical text.
- Build verification checks inherited input hashes, ISO extents, cached
  resources, all bank indexes, and unchanged files/resources.

The supplied state was reproduced in isolated PPSSPP. It contains older
executable memory and is already inside the failed rendering operation.
An attempted recovery on a private copy did not give a reliable playable
state. The fixed menu has therefore **not been visually verified through a
fresh in-game visit**. The native formatter/staging checks pass; they do not
replace the user's emulator retest. The incoming archive is untouched.

## Testing and outputs

Restart the updated ISO and use Continue / a normal in-game save. Loading
an old PPSSPP state restores old executable code and can restore the crash.

- `work/output/0.1.47/Summon_Night_3_EN_0.1.47.iso`
- `work/output/0.1.47/SN3-English-v0.1.42-to-v0.1.47.xdelta`
  requires the exact v0.1.42 translated ISO; reconstruction verified.
- `work/output/0.1.47/SN3-English-v0.1.46-to-v0.1.47.xdelta`
  requires the exact v0.1.46 translated ISO.
- `work/output/0.1.47/SN3-English-v0.1.47.xdelta`
  requires the original Japanese ISO.
- `work/output/0.1.47/XDELTA-VALIDATION.json` records round-trip checks.

This is a local test build, not a new GitHub release. User states, memory
captures, and private diagnostic files remain under ignored work folders.
