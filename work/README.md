# Working files

- `output/`: versioned test builds `0.1.0` through `0.1.4`, with manifests and evidence.
- `glossary/`: JSON terminology and character/location/organization records.
- `ui/`: actual game screenshots and associated layout metadata.
- `translation/<language>/`: target records, source-reference indexes, and reviews.

English remains the working assumption. `translation/en/` contains metadata
indexes, three reviewed label targets, 159 reviewed opening drafts, and 78-row
build selections. The setup/options catalog adds 64 reviewed UI records
(51 distinct English texts), with a wider interface discovery queue and explicit
unresolved entries. `glossary/` contains four core entries and nine accepted UI
terms; proposed files are retained as provenance, not counted twice. A verified working
ISO and decrypted executable are under `source/`; actual screenshots and layout
metadata are under `ui/`. Temporary investigation files belong in `scratch/`.

Latest candidate `0.1.4` passes the font-pool crash regression and selected later
pages/choice branch. Broader runtime acceptance is incomplete. Preserve all
builds and the original 0.1.3 fault; the next unused version is `0.1.5`. See
`docs/RUNTIME_QA_0.1.4.md` and `docs/TRANSLATION_PLAN.md` at the workspace root.
Do not store extensive Japanese script exports. Consult the plan in `docs/` for
record fields and validation requirements.
