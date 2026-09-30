# Release 0.1.52: Cooking title alignment and cumulative repairs

This is a public test release, not a stable or fully playtested game.
It includes the local fixes from v0.1.42 through v0.1.52. See CHANGELOG.md
for per-version details and the corresponding reports for earlier validation.

## Cooking title fix

The previous recipe-title call packed Latin ink against the left edge of a
fixed-width texture strip. The game centered the whole strip, leaving the
visible title too far left. The title call at module address `0x1227a0` now
uses the existing centered strip renderer at `0x348a7c`. Native title position,
scale, banner artwork, recipe data and other text calls are unchanged.
A complete ISO comparison with v0.1.51 finds exactly two changed bytes.

All 29 recipe titles execute the real centered wrapper and pixel packer at two
load addresses (58 cases). Tests verify exact pixels, cache invalidation,
stack boundaries and preserved registers. Visible title bounds stay inside
x=276..424 on the native 480-pixel screen; their centers are within 0.4375 pixels
of x=350. Pirate Lunch spans x=305.375..394.625, centered at x=350.

## Candidate validation

- SHA-256: `cfb7e7171e87b528ac91ea345c3ac37853eb345b3486fffd2c0a47c99b2f38f7`.
- Size: 1,676,666,880 bytes.
- Twelve cumulative audit groups pass, including equipment, spells, unit labels,
  Cooking, armor/weapon names, layout and memory guards.
- Fresh boot in PPSSPP 1.20.4, JIT/software rendering and strict memory handling.
  Normal Chapter 15 Continue, Brave Goals opening/navigation, Inventory with
  Black Rose Knife, Dritol details and Drill Blow help pass without a memory fault.
- Five live hook words match the candidate. The help-rejection counter remains
  zero. The glyph guard handled 150 malformed cells, last input `0x85`; the exact
  source was not traced. This is evidence of fallback handling, not a claim that
  all displayed text is clean.
- An Extra Brave Goal mystery row still displays an overlong placeholder line.
  Other untranslated text remains visible in the Summon Index catalog.
- The test-release preflight passes. The stable-release coverage requirement is
  not met: puppet shop, room skills, Cooking, save/reload, early chapters and
  Night Talk were not exercised in this candidate's fresh-boot session.
- Cooking has native-code pixel and layout tests, but no live Cooking-screen
  verification. No normal save that opens it is currently available.
- No full-route, mobile or original-PSP test is claimed.

Evidence: `work/ui/cooking_title_0.1.52/`, including the ISO-bound runtime report,
combined audit, preflight and disc comparison. Old-version runtime evidence
remains tied to its original build.

## Release artifacts

The canonical Retro Trans release workflow creates patches from the clean
Japanese source and the preceding published release, v0.1.41.
Local test-build upgrades were withdrawn from the release on 2026-09-30.
Each patch is decoded and the complete target SHA-256 checked. The public
BUILD-MANIFEST.json records source/target hashes, patch hashes and source commit;
VALIDATION.json records the round trips. Versioned README, changelog and
SHA-1/SHA-256 lists follow the project's SRW-Z-style release format.

Use a matching xdelta patch and start the game fresh with a normal in-game save.
Old emulator states can restore an earlier executable. Private submitted saves,
source game data and complete game images are excluded from the repository and
release assets.
