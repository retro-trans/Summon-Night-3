# Build 0.1.5 — opening and harbor test ISO

File: [Summon_Night_3_EN_0.1.5.iso](../work/output/0.1.5/Summon_Night_3_EN_0.1.5.iso)

- Size: 1,658,781,696 bytes.
- SHA-256: `41a01d53794c14b88c041520d30fd1586e98bc54ad53ea2c0c91fa206beb7ea0`.
- 609 translated dialogue/choice source entries, including both protagonists and all four student branches, plus three existing character labels. This adds 531 entries over 0.1.4.
- 188 reflowed groups, 41 added continuation pages; longest generated page 76 glyphs against the 192-object pool.
- The three dialogue passages in the supplied screenshots are included. The graphical Adnias Harbor banner and setup UI graphics are not.

## Verification

The builder verified source identity, ISO file/extents, unchanged files/resources,
all label references, script compression round-trip, relocated text and generated
page contents. Every generated group was simulated to check display arguments,
balanced stack and return to the original continuation. Branch and menu code,
including excluded Japanese references, is unchanged.

The decoded opening script is 234,726 bytes, below the existing mapped 0x78000
next-start bound. This is a static bound, not proof of runtime allocation or
save/load behavior. The font patch is unchanged from 0.1.4. No emulator state was
changed for this build; **in-game testing remains pending**.

## Japanese retained within the opening/harbor scope

- 12 rows in four long-choice menus exceed the current conservative single-line limit.
- 12 rows in six special-display groups use an unvalidated display helper.
- Two rows containing a musical note need a verified glyph metric.
- Three rows around the player name need measured runtime expansion.
- Three quiz rows remain unresolved in meaning review.

Complete groups/menus are retained without shortening the English drafts.
The rest of the game and untranslated interface assets remain Japanese.

Use this ISO for testing. Start from the title screen or a normal game save;
an emulator save state may retain script memory from the previous ISO.

Evidence: [layout and exclusions](harbor_build_layout_0.1.5.json),
[build manifest](../work/output/0.1.5/manifest.json),
[workspace integrity audit](workspace_audit_0.1.5.json).
