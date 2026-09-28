English translation test build for **Summon Night 3** on PSP, Japanese release
**NPJH50380**. This cumulative update includes all fixes from 0.1.37–0.1.41.
The translation remains incomplete; story and battle coverage through Chapter 8
is not a fully playtested eight-chapter release.

### Apply

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools) **0.3.1**.
Refresh its catalog, select your clean Japanese ISO or verified English v0.1.36
ISO, and choose **Latest** or **0.1.41** in Automatic mode.

Manual **Apply xdelta** and [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher)
also accept the matching patch. Keep checksum verification enabled.

| Your source image | Patch |
|---|---|
| Clean Japanese PSP ISO, NPJH50380 | `SN3-English-v0.1.41.xdelta` |
| English v0.1.36 ISO | `SN3-English-v0.1.36-to-v0.1.41.xdelta` |

The clean Japanese source is **1,658,159,104 bytes**, SHA-256
`00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda`.
The v0.1.36 source SHA-256 is
`9bfe8d6411492e86f58847bd58a9bd8f1581c30f83759b984c899dd1c1ff6edf`.
Both patches produce **1,672,138,752 bytes**, SHA-256
`56dd6bac4296cb25467dde3d1536928fed42f977f5cce4ed8d6ea79cb5b8e4fa`.

Command line with [xdelta3](https://github.com/jmacd/xdelta):

```sh
xdelta3 -d -s "Summon Night 3 (Japan).iso" "SN3-English-v0.1.41.xdelta" "Summon Night 3 English v0.1.41.iso"
```

Use unpacked ISOs. Upgrade patches require the exact published source image;
local test builds are not interchangeable. Start the new image fresh and load
an **in-game save**; emulator save states retain old code and resources.

### What changed since v0.1.36

- **Night Talk:** reflow 1,348 dialogue groups to two lines per page and translate
  all 19 blue nameplates, including Belfraw.
- **Nameplates and dialogue:** translate Sonolar's ordinary/battle nameplates
  and remove Aty's repeated request to hurry to the boat.
- **Accessories:** translate 25 remaining names and shared effect text; fix
  missed Learn Skills/Key Item references and long ailment-group buffer handling.
- **Learn Skills:** translate headings, tabs, controls and 31 skill names;
  use proportional spacing on skill cards and controls, shorten Pact titles,
  and correct crafting-help wrapping so the closing bracket stays with text.
- Preserve all earlier translation and interface fixes, item statistics,
  recipes and unrelated resources.

### Testing and remaining limits

Both full and upgrade patches passed complete round-trip decoding and output
SHA-256 checks using Retro Trans 0.3.1. Archive and native-renderer checks passed;
the newest image passed a fresh PPSSPP boot. The preceding accessory build also
loaded a copied early-battle save and displayed the Deployment layout.

**The exact unlocked Learn Skills screen and normal Night Talk playthroughs
still need gameplay verification.** The reported Skills screenshot came from
another user without a matching save. The corrected boat scene and Sonolar
nameplates received structural/artwork checks, not a new scene playthrough.
Some unique skill names/descriptions remain untranslated, and long accessory
effect layouts still need visual checks. No complete route or PSP hardware
testing is claimed.

See the [release report](https://github.com/retro-trans/Summon-Night-3/blob/v0.1.41/docs/RELEASE_0.1.41.md)
for detailed scope. AI-assisted drafting and review are not human proofreading.

### What's included

- Full Japanese-to-English patch and upgrade from published v0.1.36.
- Canonical build manifest, round-trip validation report and SHA-256 checksums.
- Versioned SHA-1/SHA-256 lists, application instructions and changelog.

### Source code and contribution

GitHub's source archives contain translation targets, tools, glossary and UI
evidence, not a playable game. Incremental builders need locally supplied game
data and historical intermediate outputs.

[Report issues](https://github.com/retro-trans/Summon-Night-3/issues) with the
patch/emulator versions, screenshot, chapter, reproduction steps and whether
an in-game save or emulator save state was used.

---

No complete game image is included. Apply the patch to your own copy.
This patch is free; do not sell it or prepatched images.
