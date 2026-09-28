# All game interface: inventory and translation queue

Scope confirmed by the user: **all game interface text**, including battle, inventory, status, tutorials, and save/load.

The [five-screen translation](SETUP_UI_TRANSLATIONS.md) is consolidated with related setup/options variants. The catalog has **64 reviewed translation records (51 distinct English texts)**, six preserved English/numeric records and seven unresolved tiny-thumbnail records. All four summon affinities are included. These targets are not yet in an ISO.

## Shared interface tables

Found **3,633 source strings in 20 structurally bounded tables**, of which 3,619 contain Japanese. The same table pack is mirrored at `02:00003` and `00:00044/00007`; a future build must update both. Counts include repeated strings and fragments.

| Category | Strings | Consumer still unverified |
| --- | ---: | ---: |
| Status labels | 28 | 1 |
| Stat modifiers | 60 | 0 |
| Summon names and forms | 419 | 73 |
| Summon abilities | 254 | 7 |
| Weapon names | 263 | 0 |
| Armor names | 155 | 0 |
| Accessory names | 85 | 0 |
| Items and descriptions | 501 | 15 |
| Ingredients | 56 | 6 |
| Attack commands | 408 | 56 |
| Special commands | 115 | 21 |
| Skills | 517 | 111 |
| Skill short descriptions | 68 | 0 |
| Shared skills | 59 | 0 |
| Support skills | 68 | 10 |
| Help and menu titles | 180 | 0 |
| Music titles | 38 | 0 |
| Food descriptions | 202 | 144 |
| Common brave conditions | 13 | 3 |
| Battle brave conditions | 144 | 12 |

There are 3,174 direct string-pointer references. Another 459 pool strings are retained with unresolved consumers, often adjacent to descriptive text. Adjacency alone does not prove ownership, number of lines or runtime access. The queue contains 56 consecutive source batches, with context on both sides; none of these table batches has been translated in this pass.

## Executable interface text

**960 Japanese-bearing candidates** were individually inspected and classified into 108 adjacent semantic groups. 856 are likely user-facing, 71 are uncertain, and 33 are unlikely. These are semantic confidence ratings; native consumers have not been verified.

Categories include main-menu and equipment help, save/load messages, battle commands and confirmations, inventory restrictions, status effects, shops, class changes, summon management, party abilities, gallery controls, minigame results, and fishing. The queue keeps 25 appraisal-service dialogue lines separate for contextual translation.

Three candidates contain leading binary bytes and require corrected boundaries: voice playback, the save title, and battle selection. Twenty-nine suspected false positives and 11 fallback/legacy labels remain in the audit queue. The current executable scan omits English-only strings and standalone punctuation; they must be recovered when reconstructing complete messages.

## Text inside graphics

| Source family | Discovery result |
| --- | --- |
| Setup/options, packs 28–33 | 410 decoded textures classified; 92 carry text, with 122 mapped translation-record occurrences. Keyboard characters, controls and artwork are tracked separately. |
| Island/location selection, packs 35–36 | 520 decoded textures examined; 12 Japanese label occurrences, representing six unique images. Directory `battle_assets` is provisional and does not mean battle-only use. |
| Night selection, battle preparation/selection, gallery, appraisal | 368 sprites classified; 41 Japanese text sprites and 38 Latin-name portraits queued for glossary consistency. Six gallery sprites still need decoding. |
| Full existing static-texture inventory | 7,263 signatures inspected; 7,262 bounded resources, grouped into 3,729 distinct payloads containing 16,400 sprites. These include art, effects, animations and font data; they are **not** 16,400 texts. |

Selected graphics were decoded to source PNGs with stable IDs, source/image hashes, dimensions and texture-storage offsets. Text regions have inspection rectangles. They are not replacement masks or proven in-game limits.

## Remaining discovery and implementation

Full interface coverage is not yet proven. Remaining work includes compressed graphics outside the selected packs, unsupported palette/texture formats, nested resources and layout consumers, script-driven tutorial/menu text, complete message assembly, and navigation through all game states. Character names and titles also use the existing character-label index.

For the next playable version, begin with the reviewed setup/options targets: relocate executable literals, translate and repack native image text, preserve the keyboard/controller data, then check both protagonists, all affinities, name confirmation, and every options state. The separate dialogue font fix is not evidence that these UI renderers support the same encoding or spacing.

The latest playable build remains **0.1.4**. The next unused version is **0.1.5**. No UI translation is claimed inserted, and the running game was not changed.

## Reproducible artifacts

- `work/translation/en/setup_ui.targets.json`: reviewed targets with immutable draft/review provenance.
- `work/translation/en/interface.index.json`: source hashes, offsets, categories and references; Japanese text resolved locally.
- `work/translation/en/interface.executable_categories.json`: candidate-by-candidate semantic classification.
- `work/translation/en/interface.queue.json`: translation batches, context IDs and audit queues.
- `work/ui/interface_graphics.index.json`: bounded source graphics and duplicate-resource identities.
- `work/ui/user_setup_screenshots/index.json`: original screenshots and measured inspection regions.
- `work/ui/battle_assets/classification.json` and `work/ui/menu_discovery/classification.json`: visual text classification and gaps.

Source Japanese dialogue was not exported. Short UI labels and small UI descriptions are retained where needed for review. Prior drafts, reviews, build inputs and game images are preserved.
