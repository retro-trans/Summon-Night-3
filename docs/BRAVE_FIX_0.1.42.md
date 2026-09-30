# Brave Goals crash fix — 0.1.42

The supplied state exposed overlong, unterminated Brave Goal help text.
The native renderer allocates 54 glyph objects and a 174-byte text staging
buffer. It reads up to three NUL-terminated lines, stopping at an empty
line. The translated table 45 stored adjacent strings without the empty
terminator, so one goal consumed text from following goals.

## Change

Five common goal names now fit in 27 cells. Each of the five descriptions
has two lines of at most 27 cells, no more than 54 glyphs, and an explicit
empty-line terminator. Full rule meanings and compact exceptions are
recorded in work/translation/en/brave_0.1.42/targets.json. The compact
no-KO note uses “KO saves” for incapacitation prevention and “manual” for
voluntary Blade Awakening; automatic awakening still counts as a KO.

Only table-45 text pointers and appended text change, in both the static
bank and its master-cache copy. Goal counters, rewards, flags, conditions,
other records and EBOOT are unchanged. Published input hashes are retained.

## Validation

- Old release fails all five description layout checks.
- Ten new title/help bundles pass the real native staging-copy loop,
  including delay slots and surrounding memory guards.
- ISO filesystem and all 23 bank indexes pass. 5,728 unaffected bank
  resources remain byte-identical. All recorded input hashes pass.
- PPSSPP 1.20.4 Windows x64, JIT, software rendering, strict memory checks:
  old 0.1.41 fresh boot > Continue > battle suspend > SELECT > Battle Info
  > Brave Goals reproduces PC 0x08868b8c with a1=0x23 (address 0x29).
- New 0.1.42 fresh boot > Continue > same menu opens successfully; all five
  translated goal selections display inside the help box; exit succeeds.
  Captures and metadata: work/ui/brave_0.1.42/.

## Test build

work/output/0.1.42/Summon_Night_3_EN_0.1.42.iso

SHA-256: 68b31f4e285e43885a5918583cc8732cba30cb2b3db489d3678bfafead8d34ca

Restart the game and use Continue with the normal in-game save. Loading
an old PPSSPP savestate restores pre-fix text and possibly already
corrupted renderer memory; this build does not repair such states.

Hardware renderers, other PPSSPP versions and a full playthrough have
not been tested for this build. This is a local test build, not a new
GitHub release.
