# Setup and options: English translations

The five supplied screenshots and related setup/options screens are translated below. **Build 0.1.6 includes character selection, all four affinities, name-entry graphics and naming messages.** These setup screens were checked in PPSSPP. Options and other interface categories remain pending. See [build notes](BUILD_0.1.6.md) for exact coverage and evidence.

## 1. Options

| Interface text | English |
| --- | --- |
| Title | Options |
| Bgm | Music Volume |
| Voices | Event Voices |
| Forecast | Damage Forecast |
| Cursor | Cursor Movement Direction |
| Lr | L/R Button Function |
| Confirm | Confirm |
| Exit | Exit Options |

Help text:

- Adjust the background music volume.
- Turn event voices on or off.
- Turn the damage forecast display on or off.
- Change the battle cursor's movement direction.
- Change how the L/R buttons work in battle.

Additional L/R settings: **Map Rotation** and **Unit Cycling**. Keep ON/OFF, Min/Max, and controller symbols.

## 2. Protagonist selection

Choose your protagonist.

○ Confirm. L/R changes the selection.

## 3. Spirit affinity

**Spirit Affinity**

Spirit World: Sapureth
Home to spiritual beings such as angels and demons. They are immortal in the Spirit World.
An affinity that excels at recovery and healing, with many status ailment and possession effects. Well suited to beginners.

## 4. Name entry

Choose your protagonist's name.

**Default names:** Rexx / Aty.

**Controls:** Delete, Auto-Name, Confirm; L/R moves within the name.

**Input tabs:** Hiragana, Katakana, Letters & Numbers, Symbols, Kanji.

Auto-Name restores the protagonist’s default name. On the summon naming screen it cycles through preset names. The shared label is intentional; it does not mean random generation.

The Japanese keyboard characters are input data, so they remain available. Choosing an English-first keyboard page is a separate implementation change.

## 5. Name confirmation

Use the name "{name}"?

**Yes / No**

The screenshot example is “Use the name "Rexx"?” The actual prompt must retain the player’s chosen name.

## Other related setup screens

Choose the summon affinity your protagonist will specialize in.

Choose your summon creature's name.

### Machine Affinity

Machine World: Loreilal
A world with an advanced mechanical civilization that creates mechanical soldiers and other machines.
This affinity has the most offensive summons. They are powerful, but their MP costs are also somewhat higher.

### Yokai Affinity

Yokai World: Silturn
A world where humans coexist with supernatural beings such as yokai, dragon gods, and oni gods.
Its summons mainly attack or apply status ailments and possession effects. Many of these effects put enemies at a disadvantage.

### Beast Affinity

Beast World: Maetropa
A land rich in nature, where beastlike humanoids and mythical beasts live in peace.
This affinity is balanced across all summon effects and has some unusual possession effects.

## Review and implementation notes

- The ambiguous tab is **Kanji**, verified from the original graphics.
- Controller icons, arrows, existing English labels, numbers and runtime name insertion are preserved.
- Six tiny regions within options-preview battle screenshots remain unreadable or tentative. One additional enemy label has a verified source reading but needs an English glossary decision.
- Native source IDs, image rectangles, source hashes and original reviews are preserved in `work/translation/en/setup_ui.targets.json`.
- Full descriptions have not been shortened to fit the original Japanese area. Layout and game testing remain required.

Realm spellings follow the project’s [researched glossary](../work/glossary/setup_ui.json). The broader interface inventory and next translation batches are in [INTERFACE_TRANSLATION.md](INTERFACE_TRANSLATION.md).
