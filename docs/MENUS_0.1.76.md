# Summon Night 3 English test build 0.1.76

This local test build translates the reported screens and the remaining text
in their matching categories, carrying forward earlier screenshot fixes.

- Translate the Sound category's 38 tracks and the main Gallery title fields.
- Translate 229 Night Talk captions and 21 Ending captions, including the
  separate renderer tables used by those screens.
- Translate Gallery buttons, headings, chapter tabs and partner nameplates.
- Resize and align all five Options labels and repair the normal/editing footers.
- Fix the Event Voices and Forecast help messages within the existing safe limit.
- Fit purchase names, questions, quantities and prices with proportional text.
- Keep the earlier Shop, Meimei, minigame, Cooking, Party Ability, summon-index
  and All-Purpose Pot repairs.

The inputs cover 218 main title fields, 532 gallery caption pointers, 18 native
messages and 82 sprites. Captions retain the empty-row terminator required by
their loader. Original string pools and numeric fields remain intact; only
string pointers and the scoped rendering calls change. Graphic imports preserve
native dimensions, palettes and compression codecs.

Translated Gallery strips use the existing bounded renderer, with one font
object per line. This prevents longer English captions from overrunning the
original per-character allocation. Exact title matching scopes the change to
translated Gallery labels and retains the earlier spell-banner wrapper.
Night Talks also fits the widest visible title into its 140-pixel column.
Both separate Night Talks caption banks are included.

Default-name matching affects display only. Custom protagonist names pass
through unchanged, and stored save bytes are not rewritten.

Apply `SN3-English-test-v0.1.76.zip` with Retro Trans Tools to the published
0.1.73 ISO. The upgrade includes 0.1.74 and 0.1.75. The package manifest and
checksums identify the required source and resulting image.

Validation records and reviewed screenshots accompany this test build.
Live testing uses a fresh boot, a normal in-game save, audio enabled and only
one PPSSPP instance. It does not constitute a complete playthrough.
Screenshots record the image actually tested. Unchanged gallery, Options and
purchase evidence carries forward from the preceding candidate after checking
identical rendering code, graphics and title inputs. The final candidate adds
only the Try On character-selection help message and is checked live separately.
