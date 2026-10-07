# Yard / All-Purpose Pot crash fix, 0.1.73

Reported build: 0.1.65. Combination: Yard, All-Purpose Pot, white Neutral
Summonite Stone. Private copies of the supplied normal save and PPSSPP state
are used for diagnosis; the incoming archives are preserved.

## Reproduction

- Reproduced from the supplied 0.1.65 state.
- Reproduced on a fresh 0.1.70 boot using the supplied normal save, with audio
  enabled. The problem is not limited to stale save states.
- The native resource decoder receives an unrelated, uncompressed resource
  and interprets its first bytes as an approximately 101 MB decoded size.
  This corrupts memory, including sound-thread return addresses.
- Runtime summon-name records have a 32-byte stride and a 20-byte name field.
  Unbounded copies of English names overwrite the following binding fields.
  The default `Summon Mate` name overwrites a binding halfword with CP932 text.

## Corrected paths

The 0.1.71 diagnostic build bounded the native rename call at module offset
0x57578 and supplied a full-name getter at 0x57530. Its 520 emitted-instruction
checks and inherited static audits passed, but the real white-stone test
still crashed. It is not suitable for distribution.

The default initializer has a separate unbounded copy at 0x54900. The 0.1.72
diagnostic routes that call through the same bounded helper. The initializer
processes 96 slots, including unnamed/unused slots. The native record retains
at most nine wide glyphs plus a terminator; a loader-owned display table holds
the full name. Numeric fields and the saved record layout are unchanged.

The getter compares the native prefix before returning the full display name,
so a different player-entered name falls back to the native text. Names are
trimmed only for trailing full-width padding. All shipped English names fit
the display table's 31-wide-glyph capacity.

The supplied normal save restores old damaged fields over the corrected
defaults. The 0.1.73 test build also bounds the name load at 0x629ac and validates
the saved binding fields at 0x629b4. Accessory IDs outside the static table's
valid range of 0 through 120 are cleared with their binding flag; all valid
IDs and flags are preserved. The loaded name is terminated within its field.
These changes repair runtime copies without rewriting the incoming save or
changing the serialized record layout.

## Validation

- 520 native rename/getter cases at two load bases.
- 192 additional cases executing the actual default-initialization loop at
  two load bases. All adjacent binding fields remain zero as initialized.
- A private RAM diagnostic clearing the damaged binding/name suffix allows
  the previously failing white-stone creation to complete in 0.1.71. This
  diagnostic does not modify any output ISO or incoming save.
- 508 saved-record cases executing the actual load fragment at two load
  bases. Check all 121 valid binding IDs and representative invalid values,
  custom names and the default name that triggered the overflow.
- All 14 inherited native/static validation groups pass, plus the new cache
  regression group: 15 groups in total.
- Fresh-boot 0.1.73 using the supplied normal Chapter 2 save in PPSSPP 1.20.4
  Windows x64, with JIT, software rendering, audio enabled and
  IgnoreBadMemAccess disabled. No save state or diagnostic RAM edits.
- All 96 loaded names have an in-field terminator; all loaded accessory
  bindings are valid. The damaged record's binding is now zero.
- Yard creates the white Neutral / All-Purpose Pot summon, completes naming,
  and uses Random Hit on himself in the private QA copy. MP changes 73 → 68
  for crafting, then 68 → 53 for the spell; HP changes 66 → 52. The new summon
  is obtained and equipped, and Kyle's menu works afterward.
- No bad-execution or memory-map fault appears in the runtime log. The
  ordinary ATRAC no-loop warning also appears in earlier working runs.
- Evidence and validation reports are under `work/output/0.1.73` and
  `work/ui/pot_0.1.73/pot073-final`. Linux is not directly tested, and this
  targeted regression check is not a full playthrough.

Old PPSSPP states contain the previous executable and RAM. For testing an ISO
upgrade, boot the new ISO and load a normal in-game save.

## Local upgrade

`work/output/SN3-English-test-v0.1.73.zip` contains the 0.1.65-to-0.1.73
xdelta, Retro Trans build manifest, checksums and round-trip validation.
It is a local test package, not a published release. Applying the patch to the
recorded 0.1.65 source recreates the tested target exactly.

Target ISO SHA256:
`79e60216dbd74b6bc1b5abe14806557b17d4544f3c6518a5f6ada6a73f3be685`

Test ZIP SHA256:
`62337a3e66e27a9f6512f79bd3ccd81335a647af2baf4d58b05427a19453a3fc`

## Published package

The release package uses the same tested 0.1.73 ISO and adds the clean-original
route alongside the published-0.1.65 upgrade. Its manifest records the release
source commit; the historical local test ZIP remains unchanged. See
`docs/RELEASE_0.1.73.md` for the cumulative changes and installation instructions.
