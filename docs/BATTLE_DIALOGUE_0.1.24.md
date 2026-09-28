# Battle dialogue translation — 0.1.24

Built on 0.1.23. This release translates the separate battle-event scripts in
01.DAT. Earlier story translation operates on 00.DAT, which is why translated
story scenes could still lead into Japanese battle dialogue.

## Included text

- 528 source fragments in 20 main-battle scripts covering the identified Chapter
  1–8 battles, including protagonist and route variants.
- 8 fragments in two early optional-battle candidates, included conservatively.
- 1,140 fragments in the shared repeatable-battle conversation script, applied
  to all 31 byte-identical source copies. This shared content also contains
  conversations involving characters unlocked later in the game.

The total is 1,676 separately reviewed source-fragment contexts, represented by
35,876 physical occurrences across 53 battle packs. Counts are fragments, not
sentences or unique English lines. Chapter attribution combines script content,
resource structure, and guide correlation; it is not a complete route-loader
trace. See battle_scope_024_draft.json for the evidence and limits.

| Chapter | Battle packs | Fragments |
|---|---|---:|
| 1 | 116–117 | 53 |
| 2 | 118 | 17 |
| 3 | 119–127 | 227 |
| 4 | 128 | 33 |
| 5 | 129–130 | 64 |
| 6 | 131 | 30 |
| 7 | 132 | 23 |
| 8 | 133–135 | 81 |

## Translation and rendering

Meaning reviews precede glossary normalization. The new versioned glossary
extends the user's SN6 Vita Gallery name reference to the shared guest cast.
Source player markers, speaker expressions, and battle event instructions are
preserved. English text is relocated and word-wrapped using the existing VWF;
long dialogue receives extra pages rather than losing its final clauses.

Pages are limited to three lines, 31 expanded cells per line and 208 measured
pixels. The compiler verifies original source hashes and every corrected row,
rejects incoming branches inside rewritten spans, and simulates every original
and new display span. Native queue reset after display was checked in the
executable. EBOOT and the existing UI, crash, and VWF fixes remain unchanged.

## Validation and limits

The build checks all 23 bank indexes, all ISO files, all replacement-pack
siblings, and 31,716 unchanged bank resources. All 53 selected script copies
contain the compiled English dialogue. The shared copies are verified identical
before patching, and all translated scripts pass VM reference and page checks.

Fresh-launch runtime testing uses isolated PPSSPP 1.20.4 software rendering and
a copied in-game save. The first pirate battle is the exercised path. Its
opening speech, extra Aty dialogue pages and transition into the existing battle
tutorial, followed by return to interactive unit commands, are covered by screenshots under work/ui/battle_0.1.24/runtime.

This is not an eight-chapter playthrough. Other branches, optional battles and
the larger shared script have static validation but no full in-game execution
coverage. Character nameplate artwork and tutorial artwork are separate assets;
this dialogue patch does not claim that every such image is translated.
Original PSP hardware and hardware GPU rendering were not tested.
