# Battle translation 0.1.13

This build adds battle deployment, action/help text, prompts, status and attack
labels, standby skills, Brave Battle conditions, 13 tutorial pages, and the
encounter-opening title/condition artwork to 0.1.12.

The encounter artwork contains 55 distinct source sprites (including palette
variants and shared heading pieces). All 611 matching uses in 80 resource packs
are replaced. The original backgrounds, palettes, geometry, and unrelated
children remain intact. Imagegen created the English lettering; the importer
only trims transparent margins, splits the heading atlas, resizes, and converts
to the game's original indexed palettes. Prompts and hashes are saved in
`work/ui/battle_0.1.13/encounter_generated/`.

The executable patch relocates 161 directly referenced text records and six
attached Yes/No strings. The shared table patch translates 310 strings across
six tables (275 pointer roots and 35 continuations). Both copies of the shared
table are updated. Unknown adjacent fields and the fixed-stride status block
remain unchanged. Start Battle, End Turn, and Retreat choice bundles have a
traced sequential U16 string consumer; the final two strings remain choices.

Tutorial coverage: movement/ZOC, facing/height, weapons (2), standby (2),
ailments (2), obstacles (2), and skills (3). The English weapon pages use
explicit range tables. Two enemy terms, Jilcooda and Shadow of Primal Sin, remain
provisional source-based translations. Character and world spellings follow
the project glossary and the Summon Night Wiki.

This is not a claim that every game interface is translated. Forty-six selected
executable records still require consumer tracing; 20 later tutorial pages and
the separate battle-menu artwork remain outside this build. Full battle layout
and gameplay acceptance requires testing in the relevant scenes.

The builder validates the complete 0.1.12 input manifest, original file extents,
all 23 archive indexes, relocated text and shared table copies. It compares
every unchanged ISO file and every unchanged resource in modified banks.
Runtime evidence is recorded separately under `work/ui/battle_0.1.13/runtime/`.

Final verification: 377 input hashes, 32 unchanged ISO files, 5,635 unchanged
bank resources, and 23 archive indexes passed. An isolated PPSSPP 1.20.4 fresh
boot rendered the opening movie; all 161 English executable bundles matched
their built bytes in live memory. This was a launch check, not a battle
playthrough. `work/output/0.1.13/verification.json` records the scope. The user's
existing emulator session was not modified.

ISO SHA-256: `2d80129afe4fbfb6157956541aabfb4e4dc628793176368e4ce2e163c3abaa46`.

To test, stop emulation and open the 0.1.13 ISO, then use an in-game save.
An older PPSSPP save state can restore older executable and script bytes.

Sources: [Summon Night Wiki](https://summonnight.wiki.gg/wiki/Summon_Night_3).
