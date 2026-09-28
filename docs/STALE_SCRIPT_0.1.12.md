# Japanese cabin dialogue diagnosis, 2026-09-27

The supplied corridor screenshot corresponds to Chapter 1 source rows 905–906.
The translation in 0.1.12 is “They're still just a child.” The neutral pronoun
is intentional because this passage is shared by the pupil routes. The female
protagonist's corresponding rows 914–915 are also translated.

Read-only inspection of the user's running PPSSPP session on debugger port
19380 found resource 65 at `0x08d8a000`. Its first 188,010 bytes had SHA-256
`631c69857b12fb1b2df3644a3a09b62af25314bfd0b1715c886588f644ee4ac2`,
an exact match for the 0.1.3/0.1.4 script. It matched neither 0.1.11 nor 0.1.12.
This identifies stale loaded script data; it does not distinguish an older ISO
from an older emulator save state. No input, memory changes, restart, or save
operation was sent to the user's session.

The actual 0.1.12 ISO resource was decompressed and checked against its manifest
hash `edce3ae14584541fc412d62d33d2c544ac657639ebe093dc8b28c48855ea3ab2`.
The patched control flow for rows 904–921 was simulated and produced the English
pages recorded in the manifest, including the reported two-fragment sentence.
No replacement build is needed for this dialogue.

To switch translations, save through the game's own save system when available,
then boot `work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso` and load that in-game
save. Avoid restoring a PPSSPP save state created on the earlier translation:
it restores emulator memory, including already-loaded scripts. A fresh start
also loads the new script. Do not discard existing saves.

The screenshot's top-left indicator means “Auto-advance OFF.” It is a separate
interface element and is not part of the chapter-dialogue coverage claim.

Save-state implementation reference:
https://github.com/hrydgard/ppsspp/blob/master/Core/SaveState.cpp
