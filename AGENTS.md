** Organize folder like this **
work - work folder
    output - contains the file for testing (iso, zip, etc...)
    glossary - contains the one or many json files for glossary
    ui - contains screenshot of actual UI element ingame with label on screenshot if possible, contains files (json,py,...) describe the coordinate, width and height, id and other attributes
    translation/<language code> - contains the target translation of ui element or dialogues or anything that need translation
docs - documents
tools - any tools help with translation
incoming - outside files that need agent to look into

** SOME RULES **
- Avoid contains extensive Japanese scripts (UI elements is fine)
- Identified each build with version 0.x.y (start at 0.1.0)
- Always write change log
- If user told you to remember anything write it down here, make sure to ask user if the new one conflict with old one
- When you commit to git, make sure no sensitive files included, for translation files must not commit original scripts for dialogues or anything that have large number of text (like encyclopedia, battle voice line), UI elements are fine, an opening naration is also fine

** REMEMBER **
- Emulator performance (user requested, 2026-10-08): keep at most one emulator instance running. Run comparisons sequentially; close only an owned QA instance before starting another.
- Every new release must work with [Retro Trans Tools](https://github.com/retro-trans/retro-trans-tools).
- Character-name reference (user selected, 2026-09-27): https://summonnight.fandom.com/wiki/Summon_Night_6:_Lost_Borders/PS_Vita_Gallery . Use its main displayed names as the primary spelling reference; retain parenthetical names as lookup aliases. The current SN3 name overlay is `work/glossary/character_reference_sn6_vita.json`; it takes precedence over older glossary spelling locks. Preserve short names when the source uses a short name, and preserve player-entered protagonist names. Other sources may supply character background or names absent from this gallery.
- Published build inputs are historical snapshots: apply the current name reference to new translation/build inputs, without rewriting files whose hashes are recorded in released manifests.
- Release assets (user requested, 2026-09-30): publish only the original-to-current xdelta and the upgrade from the immediately preceding published release. Local test builds do not count as releases. Keep other requested upgrade patches local; synchronize release manifests, checksums and Retro Trans withdrawal records when removing published patches.
- Terminology (user requested, 2026-09-30): use Teacher instead of Professor in English translations (teacher in common-noun context). Apply work/glossary/terminology_preferences.json to new translation/build inputs; preserve published snapshots.
