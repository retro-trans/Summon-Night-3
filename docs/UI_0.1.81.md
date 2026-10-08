# Summon Night 3 English 0.1.81 — local test upgrade

Includes all changes through 0.1.80. Apply the included 0.1.77 → 0.1.81
xdelta to the published 0.1.77 ISO using Retro Trans Tools. Start the game
fresh and load an in-game save.

- Align the triangle icon in Assist-only help with the proportional text
  prefix, preserving its row, button behavior and other help-icon handlers.
- Use variable-width lettering for required-member names and category labels
  in Assist INFO windows, including Protagonist and Magna / Toris.
- Preserve entered names, save buffers, combat requirements and all other
  ISO files.

Fresh-boot checks with an in-game save confirmed Sky Torrent and Heaven's Net
member lists and the shared Assist help renderer in the Summon Index. A live
trace confirmed the new icon helper executed on the second help row.
The exact battle sequence in the supplied screenshots was not replayed.
Relocated helper and field-binding checks passed at two PSP load bases.

This is a local test build, not a published release. Validation reports are
included. No direct Android validation or full-game playthrough was performed.
