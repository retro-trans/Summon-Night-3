# Repeated boat dialogue — 0.1.39

Corrects `stages_1119_1120_1121` in resource `00:00065` to:

> Come on, while we can,
> let's hurry to the boat.

The source contains one request to hurry to the boat while the opportunity
remains. English fragments in batches starting at rows 1041 and 1121 repeated
the same clause. The adjacent protagonist variant already had correct wording.
This is a translation assembly mistake, not repeated execution of the scene.

## Implementation and verification

Read the three original fragments together and checked the adjacent protagonist
variant. The new source-bound group review is in
`work/translation/en/repetition_0.1.39/review.json`. Historical release inputs
were not edited. This group-level correction supersedes the old assembled text.

The patch reuses the two correct English strings and preserves the affected
branch's own speaker arguments, display helper and return jump. Only its existing
36-byte trampoline allocation changes; eight unused bytes become NOPs. Script
length, pool contents and original branches stay unchanged. Dialogue and newly
recorded backlog pages receive the same corrected page.

Validation checks original source hashes, current script hash, all pool references,
complete target reconstruction, line/page limits, instruction destinations and
compression round trips. Symbolic execution confirms the corrected page and
identical behavior for all 619 other layout groups in this script. A scan for
repeated four-word sequences within the opening script's translated groups
flagged only this group. This heuristic is not a complete semantic review.

The scene has not been replayed in-game. Existing backlog entries or a loaded
save state's old script may retain the earlier text; test by loading an in-game
save from before the line in the new ISO.

This local test build includes 0.1.38 and 0.1.37 changes and is not a public
GitHub release. Their previously documented runtime limitations remain.

## Files

- `work/output/0.1.39/Summon_Night_3_EN_0.1.39.iso`
- `work/output/0.1.39/manifest.json`
- `tools/repetition_039.py`: source-bound correction and script verification.
- `tools/build_repetition_039.py`: incremental archive build on immutable 0.1.38.

Rebuild into a new directory with
`tools/build_repetition_039.py --write --destination work/scratch/repetition_rebuild039`.
