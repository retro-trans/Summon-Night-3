# Menu help and generic enemy names — 0.1.35

Base: immutable 0.1.34.

The separate in-battle Summon Index description now reads “View summon details
and combination results.” The category audit also found and translated 23 other
menu-help records, including shopping, Gallery, summon training, favorites,
level changes, minigames, loading and retreat. All 58 references in this help
group resolve to English and fit two rows of at most 27 cells each.

The shared unit-name catalog now translates 39 generic enemy labels, including
Pirate, Bandit, Assassin, Outlaw, Ghost Captain and Beastfolk. This updates 164
references, including shared class-label references. Native unit names retain
the established ten-cell limit; compact forms and full translations are recorded
in work/translation/en/menu_enemy_0.1.35/targets.reviewed.json. Existing VWF
rendering is retained. Named story characters and named creature species are
separate categories and are not claimed complete by this change.

The meaning reviewer checked 24 help groups (28 original source literals) and
all 39 enemy labels. The established glossary term “Endless Halls” is retained.
Longer labels use compact identifiers, including “Red Glove” for the Crimson
Glove Assassin; that abbreviation is not a separate organization-name claim.

All translations are appended and references redirected. Original text pools,
unselected name pointers and unrelated archive resources remain unchanged.
Both the resident and bank copies of the unit-name catalog match. The build
verifies all 23 archive indexes, 5,728 unchanged resources and historical input
hashes. No save files are modified by the patch.

## Runtime checks

Verified in an isolated PPSSPP 1.20.4 instance with software rendering, after a
fresh launch and loading the in-game Suspend save created with 0.1.34 (no
emulator save state). The in-battle Summon Index description displays on two
complete lines. Pirate appears in English with VWF in both the compact unit
card and the full status screen. Opening and closing status returns normally.
This also confirms that this older suspend save picks up the new Pirate label.

Evidence: final_help, final_enemy, final_status and final_return PNG/JSON pairs
in work/ui/ui_fixes_0.1.35/runtime. Runtime coverage is the first battle's
Summon Index help and Pirate display; the other new help groups and enemy names
were checked against their source strings, pointers and length limits, not
visited individually in-game. Unrelated status headings/classes and equipment
text visible on that screen are outside this category pass.

ISO SHA-256: 01ae84776c9ad3d5e57bdb6f35291f79b0377f9c1322636703cd6b8544c062db
