# Shine Saber spell-name overlap — local 0.1.59

The spell label 打ち砕け光将の剣 means “Shatter! Light General's Sword!” Its
existing compact translation, “Crush! Light Gen. Sword,” measures 172.375 pixels
at the inherited 0.875 font scale. The previous 185-pixel allowance included the
MP cost column and therefore accepted a name that visibly overlaps it.

The new display is **Crush! L.Gen.Sword**, measuring 139.125 pixels. L. abbreviates
Light and Gen. abbreviates General; the imperative and sword reference remain.
The revised conservative allowance is 140 pixels. All 41 already translated
names in this table fit it after this correction. Japanese names still awaiting
translation are outside this English-width audit.

Only 02.DAT resource 3, child 13, record 233, slot 8 changes. The compact label is
appended and its pointer redirected; old pool bytes and all other table fields
are preserved. The resident table copy in 00.DAT resource 44, child 7 is updated
identically. The executable remains byte-identical to local 0.1.58.

This is a local test build based on 0.1.58. Historical release assets and inputs
are preserved. Exact Shine Saber spell-list runtime verification needs a save
where the unit has this summon equipped; measured fit is not a visual gameplay
check.

ISO SHA-256:
`b49b53d0010debeb44d6f5a9802161d8f34355119a97b6a66ac0f1efc2c2634c`.

All 13 inherited regression groups pass against this finished ISO. The separate
name audit checks all 41 translated labels and verifies that only the selected
pointer and its appended string change. Patch packaging uses Retro Trans Tools
and compares the complete decoded ISO hash with the build manifest.
