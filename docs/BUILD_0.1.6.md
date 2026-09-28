# Build 0.1.6 — setup screen fix

[Download ISO](../work/output/0.1.6/Summon_Night_3_EN_0.1.6.iso)

- SHA-256: `8f1e67c6d01d8c263a06f4ad45dcb85b9bd4d6031537e0060080f4032b4263ae`
- Size: 1,658,761,216 bytes.
- Adds 68 modified native graphics across five packs: protagonist selection,
  all four affinity headings/descriptions, and normal/highlighted name-entry labels.
- Relocates seven naming literals; Rexx/Aty, confirmation, Yes/No and empty-name
  validation are English. The keyboard opens on ABC/123. Other character tabs remain available.
- Retains the same 609 dialogue/choice entries, three character labels and font
  code from 0.1.5; the decoded dialogue resource is byte-identical.

## Validation

Source and output hashes, all 23 indexes, 32 unchanged ISO files, 3,558 unchanged
bank resources, 2,312 character references, dialogue layout and five native UI
packs passed static verification. Re-encoded textures preserve native palettes,
geometry and all pixels outside the changed regions. ELF literals are relocated;
the original font hook bytes and relocation records are preserved.

PPSSPP 1.20.4 screenshots were inspected for both protagonists and every affinity.
A fresh final-ISO boot verified Rexx selection, English-first keyboard, confirmation
punctuation, blank-name rejection, Delete, Auto-Name and entry into the translated
opening. The Aty/affinity pass used the first candidate's identical graphic packs.
The user's running PPSSPP and saves were not changed.

[Runtime evidence](../work/output/0.1.6/setup_runtime_validation.json) records
each screenshot and the exact ISO used. [Build manifest](../work/output/0.1.6/manifest.json)
records content and source identities.

## Remaining scope

This fixes the reported setup screens. Options, battle/status/inventory/save UI,
the graphical harbor banner and most of the game remain Japanese. Summon-name
variants are statically patched but not yet played through. Full-game, long-name,
audio, save/load and PSP hardware acceptance remain open.

Open this ISO from the title screen or a normal game save. Do not resume an old
emulator save state, which may retain the previous ISO's loaded graphics and code.
