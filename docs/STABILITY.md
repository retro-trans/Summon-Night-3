# Stability checks and test build 0.1.49

## Cause and scope

The three confirmed recent defects violated the original game's text contracts:
Brave Goal text lacked safe length/termination, equipment help exceeded its
54-glyph pool, and two default unit names used single-byte ASCII where the
renderer required two-byte CP932 cells. Variable-width spacing changes visible
width; it does not increase the number of available glyph objects.

The earlier checks were split by feature. Some checked the text buffer but
missed the smaller glyph pool or the real font lookup. These findings establish
patch defects, not general instability in the original game or PPSSPP.

## Changes in 0.1.49

- Bound the shared help reader before native copying: at most three rows,
  27 two-byte cells per row and 54 cells total. Check source alignment and
  user-RAM range before reading each cell. Invalid input uses `Text error`.
- Validate lead/trail bytes before the native font-map lookup. Invalid cells
  use a fullwidth question mark, and the cached cell is updated consistently.
- Record rejection counts and the last rejected value in an in-memory table.
  Ordinary tested gameplay produced no rejections; deliberate negative tests
  incremented each counter once and the game continued.
- Require the combined audit in the new build and patch-packaging scripts.
  Existing historical builders and hashed release inputs remain unchanged.
- Add release preflight checks tied to the ISO hash and runtime evidence.
  Stable labeling is rejected while the required runtime coverage is pending.

These checks protect two shared rendering paths. They do not validate every
allocation, every pointer, every text consumer, or earlier formatting writes.
Correct source data remains necessary. Guards can reject unsupported input
rather than displaying its intended text; a fallback is a reportable defect.

The code change preserves existing translated tables and archive content.
It is a test build, not a claim of complete or crash-free gameplay.

## Automated evidence

`work/output/0.1.49/stability-report.json` passes nine groups against the real
ISO and its executable:

| Coverage | Cases |
| --- | ---: |
| Archive indexes and cached table copies | 23 indexes |
| Referenced unit/class labels | 753 labels, 2,312 references, 784 records |
| Brave Goal title/help staging | 10 |
| Equipment formatting and native staging | 1,434 |
| Populated spell help formatting and staging | 235 |
| Pact names / dynamic help masks | 15 / 31 |
| Cooking text entries / native recipe staging | 137 / 29 |
| Relocated Cooking positions | 3,044 |
| Relocated help guard boundaries | 24 |
| Glyph guard inputs at two load addresses | 131,072 |

Guard tests check register preservation, the displaced delay-slot store,
stack adjustment, continuation addresses, fallback glyph counts and rejection
counters. Boundary cases include exactly 54 glyphs, a 28-cell row, 55 total
cells, null and odd pointers, and the end of user RAM. Native formatter tests
still validate output independently, so a fallback cannot turn an oversized
record into a passing audit result.

Historical negative controls remain in `work/ui/stability_0.1.48`: the audit
rejects the old Brave Goal, equipment and puppet-name failures.

## Runtime evidence

Fresh-boot PPSSPP 1.20.4, JIT, software graphics, strict memory handling:

- Load the supplied normal Chapter 15 battle save through Continue.
- Open the unit list, Battle Info and Brave Goals.
- Browse inventory and select Black Rose Knife, the previous overflow case.
- Open Dritol in Summon Index and inspect spell help/range.
- Verify the running hook instructions match the relocated candidate.
- Inject an overlong help row into the isolated process: rejection count +1,
  no memory fault, and subsequent normal rendering continues.
- Inject ASCII `Re` as a font cell, matching the encoding failure class:
  invalid-glyph count +1, no memory fault, and rendering continues.

Screenshots and an ISO-bound runtime report are in `work/ui/stability_0.1.49`.
The screenshots after injection show recovered rendering; they are not proof
that a fallback remains visible. Counter evidence records the rejected input.
Fault injection changed test-process RAM only, never the ISO or normal saves.

Pending fresh-boot paths: puppet shop, room/skills, Cooking, save then reload,
early chapters, and night talk. The imported older diagnostic state reached
the ship hub but became unavailable on Save; it did not produce a normal hub
save and is not counted as a v0.1.49 runtime pass. The available normal save is
inside a later story battle. No mobile/hardware test or full playthrough is
claimed. Japanese text and some presentation issues remain outside this build.

## Build and release commands

Keep assertions enabled; the combined audit refuses Python `-O`.

```powershell
python tools/build_stability_049.py --write --destination work/output/0.1.49
python tools/verify_stability.py --build work/output/0.1.49 --report work/output/0.1.49/stability-report.json
python tools/package_stability_049.py
python tools/release_preflight.py --build work/output/0.1.49 --channel test
python tools/release_preflight.py --build work/output/0.1.49 --channel stable
```

Build requires a new destination. Packaging requires new patch filenames,
reruns the audit, verifies input hashes, and decodes every patch to confirm the
exact target hash through retro-trans-tools. Use the last two commands before
publishing: test preflight permits explicitly listed gaps; stable preflight
fails until every required runtime path passes. These are local entry points;
legacy GitHub publishing commands are not automatically intercepted.

## Diagnostic layout

Module address `0x351c90` (normally loaded at `0x08b55c90`), four little-endian
32-bit fields: help rejection count, invalid glyph count, last reason, last
value. Reasons: 1 = help length, 2 = source pointer, 3 = glyph encoding.
Counters reset on a fresh boot and are not automatically exported to logs.

## Patches

All three patches passed encode/decode round trips:

- `SN3-English-v0.1.48-to-v0.1.49.xdelta`
- `SN3-English-v0.1.42-to-v0.1.49.xdelta`
- `SN3-English-v0.1.49.xdelta` (original Japanese ISO input)

Target ISO SHA-256:
`18fa469319174bce9635a84e8a5d3e1bd910548e6cd037ff43b7e77e391da935`

Start the patched ISO from a fresh boot and load a normal in-game save.
An older save state can restore the old executable in RAM and bypass the fix.
