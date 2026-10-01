# Battle-event translation checkpoint — 0.1.55

Completed 2026-10-01. These are reviewed translation inputs, not a published build.

Subsequent delivery: [v0.1.55 was built and released](RELEASE_0.1.55.md), with
[public Retro Trans verification](RETRO_TRANS_0.1.55.md). The checkpoint and
its original limitations below are retained as translation-stage provenance.

## Scope and review

All 642 remaining indexed battle-event fragments in 27 resources are translated.
Resources: 136–149, 157–161, 165–172, nested in `01.DAT`.
This completes the missing battle-event scope identified by the v0.1.54 Sheet audit;
it is not a claim that every kind of text in the game is translated.

Nine slices contain 80 consecutive fragments each, except the final two-fragment
slice. Authors read neighboring dialogue and actual display groups. Independent
reviewers compared the drafts with Japanese source and recorded examined ranges,
uncertainties, preserved omissions and exact draft hashes. No source transcripts
are stored with these targets.

Five reviewed corrections clarify strength (211, 213), simultaneous destruction
(374), and the impersonal lovestruck/battered joke (560–561). Name normalization
then applies the current reference, Teacher terminology and Beardy nickname.
Provisional battle terms and supporting references remain in the battle glossary.

The user selected GPT-6.1 Sol for subsequent translation-agent work. This batch's
reviews completed using the inherited current model while that selection was
pending; Terra was unavailable and was not used.

## Acceptance and technical validation

`work/translation/en/battle_0.1.55/accepted.json` contains final English targets,
compiled display records and input hashes. Draft snapshots remain unchanged so
their independent reviews remain verifiable. Use the acceptance loader or this
checkpoint, rather than raw author drafts, for future integration.

All 27 resources compile in memory: 284 original dialogue groups produce 329
pages, with at most three lines per page and 208 pixels per line. Every display
span is simulated with the original speaker, balanced stack and return location.
Original event code outside the replaced display spans is unchanged. Text is
relocated, so translation length is not limited to original storage slots.

Three source-verified mode-2 speaker operands are preserved. Resource 148's
display span at 1704–1736 contains an additional blank text append at 1720–1724;
it is handled only for that exact source sequence. Reflow copies the actual
speaker at 1728 without reintroducing an extra line into each generated page.

Eight negative checks reject missing review hashes, author self-acceptance,
missing examined context, fabricated counts, stale hashes, incorrect correction
resource identity, duplicate corrections and an invalid blank pool entry.
Review acceptance also verifies full boundary dialogue groups and bound adjacent
drafts. The historical compiler and released snapshots are untouched.

Revalidate without writes:

```powershell
python tools/validate_battle_055.py
```

After inspecting the preview, `--write` refreshes the accepted checkpoint.

## Outstanding delivery steps

- Integrate into a new ISO and test representative events in PPSSPP.
- Build and publish a release only on request, retaining the clean-source patch
  and the upgrade from the immediately preceding published release.

## Translator Sheet refresh — 2026-10-01

Updated all 642 previously blank Current English cells in `21 Other battle events`
(column D, within rows 2–649). The six already translated records are unchanged.
Readback verified every edited cell and all other cell values, notes, formats and
validation in the tab. Proposed English, reviewer fields, speakers, row order and
hidden archives are preserved. Read me now identifies the new battle text as the
reviewed, unreleased v0.1.55 checkpoint.

Receipt: `work/scratch/sheets_export_055/battle055_refresh_receipt.json`.
The accepted checkpoint's Sheet-pending limitation reflects its creation time;
the later refresh receipt records delivery. Native browser inspection was
unavailable (browser kernel exited); API checks confirmed existing WRAP formatting,
300-pixel English columns and sufficient existing row heights without resizing.
No local Japanese transcript or credentials were saved.

The separate 363 older Sheet export-mapping omissions are unchanged by this pass.
