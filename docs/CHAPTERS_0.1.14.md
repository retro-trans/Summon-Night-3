# Chapters 4–8 translation work

This build extends the 0.1.13 translation through Chapter 8. All identified
dialogue resources in the scope below have English targets. The packaged ISO is
`work/output/0.1.14/Summon_Night_3_EN_0.1.14.iso`.

## Scope

| Section | Distinct source fragments |
| --- | ---: |
| Chapter 4 main branches | 2,584 |
| Chapter 5 main branches | 2,705 |
| Chapter 6 main branches | 1,872 |
| Chapter 7 main branches | 2,236 |
| Chapter 8 main branches | 3,003 |
| Optional/night conversations across these chapters | 2,593 |
| Shared school, minigame and other conversations | 3,957 |
| Total new translation contexts | 18,950 |

The common block is duplicated in the game. Chapters 4–5 contain an earlier
1,808-fragment subset. The compiler maps this subset by exact source hashes:
0–463 are unchanged; old464–1807 correspond to common2613–3956. Chapters 6–8
share the complete3,957-fragment block. Optional scripts also share the first
11 unlock messages. With duplicates,71 script resources cover31,206 source
occurrences. A fragment is not necessarily a complete sentence or dialogue box.

## Meaning and terminology

Translation proceeds in consecutive80-row slices with neighboring context.
Branch alternatives remain separate. Source Japanese is read transiently from
the original game; saved slices contain English and source identity metadata.
Review files state whether coverage is independent review or author self-check.
Earlier literal machine drafts in Chapter 4 received independent corrections
before inclusion. Independent meaning review covers 4,193 distinct fragments;
the remaining 14,757 have translator self-checks. The accepted review files bind
these records and corrections to the exact draft hashes. Structural tests do
not certify translation accuracy.

The user-selected SN6 PS Vita gallery supplies character spellings. New glossary
entries record evidence and mark unresolved English names as provisional.
Player-name tokens remain dynamic. Review corrections precede spelling
normalization; published0.1.13 inputs remain untouched.

## Compilation changes

The versioned compiler preserves dialogue flow while wrapping full translations
into pages. It also supports direct eight-argument native dialogue calls.
Each replaced instruction span stores as much of its new instruction sequence
as fits; any overflow uses an appended continuation. Splits occur only on
verified instruction boundaries. Incoming branches into a replaced span are
rejected. Each rewritten span is simulated against the original to compare
display calls, arguments, stack balance and complete page content.

After layout, string storage is rebuilt from live VM string references. Equal
byte strings share storage; unused intermediate copies are omitted. Every live
string is compared byte-for-byte before and after compaction, and every other
instruction remains identical during that pass. Logical draft records that are
no longer referenced are retained as audit metadata, not live string entries.
The compiler retains the 491,520-byte allocation guard. Passing this guard is not
a complete proof of runtime allocation safety.

Complete main-script compilation produces 297,078 bytes for Chapter 4,
301,006 for Chapter 5, 385,308 for Chapter 6, 408,612 for Chapter 7, and
455,062 for Chapter 8. All are below the guard. Native dialogue symbols remain
supported by the original font; controls and player-name tokens are preserved.

Four compiler regression tests passed, covering compacted string ownership,
inline/overflow dialogue continuations, entry-point protection and rejection
of scripts that could fall through into appended code.

## Completed validation

- Complete 71-resource coverage, source bindings, review bindings, preserved
  control tokens, layout limits and rewritten display-span simulations passed.
- ISO archive round-trip checks passed, with 34 unchanged files, 4,341 unchanged
  bank resources and all 23 archive indexes verified against build 0.1.13.
- All 817 manifest input hashes were checked again after packaging.
- An isolated PPSSPP instance booted this exact ISO. All 161 inherited English
  executable bundles matched live memory. Captures and machine-readable reports
  are in `work/ui/chapters_0.1.14/runtime`. The user's emulator was untouched.
- ISO size: 1,659,803,648 bytes. SHA-256:
  `ef1637b6ed064fc069c95f7bca3cfe50bf7404ee978e3b49b517fdaf40df224a`.

## Remaining limits and loading

The new chapter scripts have not received a full route playthrough or live
layout verification. Fresh boot and structural simulation do not prove every
gameplay branch. Not every translation has independent second-pass review.
Provisional terms and ambiguous readings are recorded in the versioned glossary
and accepted review files. Scope derives from the identified dialogue scripts;
it is not a claim that every possible loader route has been traced at runtime.

Open the new ISO with a fresh emulator boot and load an in-game save. Older
PPSSPP save states can retain previously loaded scripts and Japanese text.
The historical Chapter 6 draft self-check predates the final memory improvements;
the completed build manifest and checks supersede its allocation failure.
