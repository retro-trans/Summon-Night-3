# Status and equipment labels — 0.1.18

Built on 0.1.17. SHA-256:
`702d6adbe8fbbf6a76171b8995a7d3f096341d2f0c766ffcd46b3f5321fca9ea`

ISO size: 1,659,920,384 bytes.

## Changes

| Category | Newly inserted strings |
|---|---:|
| Unit names, classes and titles | 328 |
| Weapon names | 184 |
| Armor names | 63 |
| Accessory names | 60 |
| Summon/form names | 56 |
| Spell names | 40 |
| Empty equipment label | 1 |
| Total | 732 |

Existing Dritol and Novice Sword translations were checked and retained.
Screenshot terms now resolve to Soldier, Guard, None, Rock Mail, Study Manual,
Dritol and Shine Saber. Full name meanings are retained alongside compact UI
forms in the versioned target files.

Seven existing combat labels were shortened. Attack labels use at most six
native glyph cells; defensive actions use at most five. Class labels use up to
ten cells; equipment and summon labels up to fifteen. Limits come from the
provided status screenshots and the native full-width text advance. These are
static layout checks, not a claim of completed live visual testing.

## Verification

- Checked all 856 historical and new input hashes before and after building.
- Verified all 23 bank indexes and 5,727 untouched resources in changed banks.
- Compared unchanged ISO files against 0.1.17.
- Verified the static and character tables match their resident cached copies.
- Re-read Soldier, Guard, Dritol and Shine Saber through candidate pointers.
- Preserved all five 0.1.17 crash-fix regions exactly and repeated their glyph
  count and line-storage checks.
- Only reviewed, hash-bound targets were inserted. Weapon wording overrides
  must match the previous target's source hash and are recorded in the manifest.

## Remaining work

This release expands the categories shown by the user; it does not finish the
entire glossary. There are 415 deferred Japanese unit/class labels, additional
equipment and summon/spell names, and untranslated long summon descriptions.
Some accepted creature names remain provisional romanizations. Mechanical
transliteration drafts were excluded, and their review status must not be
interpreted as insertion coverage.

The story translations through Chapter 8 are inherited unchanged. No runtime
test was completed for this release. Fresh launch and a normal in-game save
are needed to test the new ISO; the earlier fresh-launch crash report was a
real renderer defect, not explained by save states.
