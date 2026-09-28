# Summon Night 3 — translation project

Tools and an English fan translation for **Summon Night 3** on PSP, Japanese
release **NPJH50380**.

## Contribute

This is an early, incomplete translation. Bug reports, Japanese-to-English
proofreading and route playtesting are welcome. Please [open an issue](https://github.com/retro-trans/Summon-Night-3/issues)
with the patch version, emulator version, chapter, steps to reproduce and a
screenshot. State whether you loaded an in-game save or an emulator save state.

## Play it

The latest test release is **[v0.1.41](https://github.com/retro-trans/Summon-Night-3/releases/tag/v0.1.41)**.
It includes identified story and battle-dialogue resources through Chapter 8,
along with ongoing menu, item, summon, enemy-name and variable-width font work.
**It is not a complete translation or a fully playtested eight-chapter build.**

### Apply

Use your own clean Japanese ISO with the source hash listed below.

| Your source image | Patch |
|---|---|
| Japanese PSP release, NPJH50380 | `SN3-English-v0.1.41.xdelta` |
| English v0.1.36 | `SN3-English-v0.1.36-to-v0.1.41.xdelta` |

**Desktop patcher:** [Retro Trans](https://github.com/retro-trans/retro-trans-tools)
**0.3.1** has been tested with this patch. In manual **Apply xdelta** mode,
select your original ISO, the downloaded patch and a new output filename.
For **Automatic** mode, refresh the patch catalog, select your clean Japanese
ISO (or verified English v0.1.36) and choose **Latest** or **0.1.41**.
Both release patches are built and round-trip verified with Retro Trans.
See the [release report](docs/RELEASE_0.1.41.md) and
[public Automatic verification](docs/RETRO_TRANS_0.1.41.md).

**Alternative:** [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher)
accepts the same `.xdelta` file. Keep checksum verification enabled.

**Command line:** use [xdelta3](https://github.com/jmacd/xdelta):

```sh
xdelta3 -d -s "Summon Night 3 (Japan).iso" "SN3-English-v0.1.41.xdelta" "Summon Night 3 English v0.1.41.iso"
```

| Image | SHA-256 |
|---|---|
| Clean Japanese source — 1,658,159,104 bytes | `00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda` |
| English v0.1.41 output | `56dd6bac4296cb25467dde3d1536928fed42f977f5cce4ed8d6ea79cb5b8e4fa` |

Use an unpacked ISO; this patch does not apply directly to ZIP, CSO or CHD files.
A checksum mismatch means the source is different. Check its hash instead of
disabling verification. Choose the full patch for Japanese or the separate
upgrade patch for the exact v0.1.36 English image.

Start the new ISO fresh and load an **in-game save**. Emulator save states keep
the old executable and resources. Fresh boot passed on v0.1.41; v0.1.40 also loaded a copied early-battle save.
Exact unlocked Learn Skills and normal Night Talk playthrough checks remain pending.
Broad save compatibility is not yet established.

## Check the translation

English targets and source identities are in [work/translation/en](work/translation/en).
Records use resource IDs, offsets and source hashes so the Japanese can be read
from your own game image without publishing a full Japanese script dump.

The latest [coverage and test report](docs/RELEASE_0.1.41.md) distinguishes
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

**v0.1.41 is a test release.** It includes the changes since v0.1.36:
Night Talk text reflow and 19 nameplates, Sonolar's ordinary/battle nameplates,
a repeated Chapter 1 line fix, 25 accessory names and shared effect text,
and Learn Skills headings, 31 skill names, controls and proportional spacing.
Pact titles and crafting-description wrapping are also corrected.

Automated checks and a fresh emulator boot passed. The reported unlocked
Learn Skills screen and normal Night Talk scenes still need in-game verification.
Some unique skill names/descriptions and long accessory-effect layouts remain
unfinished or unverified. See the release report for the precise scope.

Other routes, later chapters, some classes, equipment text, named creatures
and graphical labels still need translation or playtesting. Original PSP
hardware has not been tested. Structural checks do not establish complete
gameplay coverage or translation accuracy.

### Human proofreading

No audited count of human-reviewed lines is available. The recorded agent
reviews are AI reviews and should not be read as human proofreading totals.
See [CHANGELOG.md](CHANGELOG.md) for the version history and documented limits.
