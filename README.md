# Summon Night 3 — translation project

Tools and an English fan translation for **Summon Night 3** on PSP, Japanese
release **NPJH50380**.

## Contribute

This is an early, incomplete translation. Bug reports, Japanese-to-English
proofreading and route playtesting are welcome. Please [open an issue](https://github.com/retro-trans/Summon-Night-3/issues)
with the patch version, emulator version, chapter, steps to reproduce and a
screenshot. State whether you loaded an in-game save or an emulator save state.

## Play it

The latest test release is **[v0.1.55](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.55)**.
It adds 642 independently reviewed battle-event fragments across 27 scripts,
and includes the v0.1.54 story translation and all earlier crash guards and
interface fixes. The indexed remaining story and battle-event passes are complete;
other text, graphics and full-route testing remain incomplete.

### Apply

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools), refresh its
catalog, and select your source ISO. Manual Apply xdelta and DeltaPatcher also work.

| Your source image | Patch |
|---|---|
| Clean Japanese NPJH50380 | `SN3-English-v0.1.55.xdelta` |
| Published English v0.1.54 | `SN3-English-v0.1.54-to-v0.1.55.xdelta` |

Use the exact source version and keep checksum verification enabled.
Both patches are fully round-trip verified with the Retro Trans engine.
[Public Automatic-mode verification](docs/RETRO_TRANS_0.1.55.md) also passed
for the v0.1.54 upgrade.

```sh
xdelta3 -d -s "Summon Night 3 (Japan).iso" "SN3-English-v0.1.55.xdelta" "Summon Night 3 English v0.1.55.iso"
```

| Image | SHA-256 |
|---|---|
| Clean Japanese source - 1,658,159,104 bytes | `00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda` |
| English v0.1.55 - 1,676,998,656 bytes | `d75654f7d9381293b8b78e8e7ddd8766bd2c518e9da05a8a7983205abd04bfe9` |

Start the new ISO fresh and load an **in-game save**. Emulator save states retain
old code and resources. The [release report](docs/RELEASE_0.1.55.md) distinguishes
automated checks from fresh-boot testing. Chapter 15 Continue, Brave Goals,
Inventory and Summon Index passed; full-route and individual new-script runtime
allocation testing remain pending.

## Check the translation

English targets and source identities are in [work/translation/en](work/translation/en).
Records use resource IDs, offsets and source hashes so the Japanese can be read
from your own game image without publishing a full Japanese script dump.

The latest [coverage and test report](docs/RELEASE_0.1.55.md) distinguishes
in-game checks from static checks. Broader scope is documented in
[Chapters 1–3](docs/BUILD_0.1.12.md), [Chapters 4–8](docs/CHAPTERS_0.1.14.md),
and [battle dialogue](docs/BATTLE_DIALOGUE_0.1.24.md).

## Translate it

Start with [TRANSLATING.md](TRANSLATING.md). Preserve source identities,
control codes and player-name markers. Review meaning before fitting text to
the interface, and use the versioned glossary for names and terminology.

Published build inputs are historical snapshots. Make corrections in new
versioned files rather than rewriting the inputs recorded by an older release.

## What is here

| Path | Contents |
|---|---|
| `TRANSLATING.md` | Translation workflow and build limitations |
| `TOOLS.md` | Tool entry points and dependencies |
| `tools/` | Archive readers, compilers, font patches, builders and verifiers |
| `work/translation/en/` | English targets, source identities and review records |
| `work/glossary/` | Names, terminology and supporting references |
| `work/ui/` | UI measurements, translated artwork and runtime screenshots |
| `docs/` | Format research, per-build coverage and validation reports |
| `CHANGELOG.md` | Version history and fixes |

Original ISOs, extracted executable/resource binaries, save data, vendor
programs, scratch files and local test ISOs are excluded from Git. Download
the `.xdelta` release asset to play; GitHub's source-code archive is the
translation workspace, not a playable game or a game patch.

## Using these tools

The tools use Python and expect a locally supplied Japanese image. For a
read-only source check:

```sh
python tools/scan_source.py "Summon Night 3 (Japan).iso"
```

Build scripts are versioned incremental research tools. Many require local
intermediate builds, extracted data and separately installed dependencies;
this repository is not yet a one-command clean-build distribution. See
[TOOLS.md](TOOLS.md) before running them.

## Do not sell this

This fan translation is free. Do not sell the patch, prepatched images,
preloaded devices or access to its downloads. Summon Night 3 and its original
assets belong to their respective rights holders. No complete game image is
distributed here.

## Credits

- Project direction, screenshots and playtesting: the repository maintainer.
- Translation drafts, review assistance, tooling and reverse engineering:
  AI-assisted work using Codex, directed by the maintainer.
- Character spellings follow the maintainer-selected
  [Summon Night 6 PS Vita Gallery](https://summonnight.fandom.com/wiki/Summon_Night_6:_Lost_Borders/PS_Vita_Gallery).
- Runtime checks use [PPSSPP](https://www.ppsspp.org/); release patches use
  [xdelta3](https://github.com/jmacd/xdelta).

## Status

**v0.1.52 is a test release.** It includes crash repairs and shared text safety
checks, weapon and armor translations, two-row equipment descriptions, corrected
stat spacing, System menu translations, and Cooking localization and alignment.

Automated checks cover known rendering paths; they do not establish a crash-free
game or complete translation accuracy. Exact runtime coverage and outstanding
checks are listed in the release report. Other routes, later chapters, some
classes, named creatures and graphical labels still need translation or testing.
Original PSP hardware has not been tested.

### Human proofreading

No audited count of human-reviewed lines is available. The recorded agent
reviews are AI reviews and should not be read as human proofreading totals.
See [CHANGELOG.md](CHANGELOG.md) for the version history and documented limits.
