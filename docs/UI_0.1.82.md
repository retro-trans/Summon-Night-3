# 0.1.82 equipment-type captions — local test build

Fixes the first two blank Equip Type rows reported on published 0.1.81.
The native composer writes into ten-cell buffers. Translated captions exceeded
those buffers, merging consecutive rows into unrenderable strings.

Both consumers now reference separate immutable captions instead of writing
into those buffers. All 150 attack/weapon combinations are covered, including
the native throwing-mode substitution and empty special-mode caption.
Greatsword is abbreviated as Greatswd only in combined Equip Type captions;
standalone Greatsword labels remain unchanged. Captions fit the existing
sixteen-cell text cache. Weapon IDs, attack modes, icons, armor labels,
player-entered names, saves and combat data are unchanged.

Validation: 616 executed consumer cases at two load addresses, invalid-ID and
adjacent-buffer guards, inherited code/data checks, and hashes of every ISO
file. Only EBOOT.BIN changed. Reproduced the blank rows on 0.1.81, then
fresh-booted 0.1.82 with the supplied normal Chapter 16 save. Reviewed Rexx's
five rows, Kyuuma's equipment types, and a return to Rexx. One emulator was
used at a time and closed after QA. No RAM writes or save states were used.

Apply SN3-English-v0.1.81-to-v0.1.82.xdelta to the published 0.1.81 ISO with
Retro Trans Tools. This is a local test upgrade, not a published release.
Android and a full-game playthrough have not been tested.
