# Bounded runtime checks for 0.1.12

Tested ISO: `work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso`.

SHA-256: `ed929381d11623ec30d144cc4846dc3db2a0e764cdbc15135b26ce7a537bd075`.

An isolated PPSSPP session fresh-booted the final ISO, reached the title and
translated name-entry screens, and continued into the opening and harbor.
The loaded resource 65 matched the final compiled script exactly:
`edce3ae14584541fc412d62d33d2c544ac657639ebe093dc8b28c48855ea3ab2`.

The final screenshot shows Rexx at the harbor with the two fully rendered lines
“The letter said it was a” / “boy, as I recall.” The observed character records
matched the expected English text. This is opening group 445–447, not the new
cabin checkpoint.

Evidence:

- `work/ui/stages_0.1.12/runtime/final_boot.png`
- `work/ui/stages_0.1.12/runtime/final_setup_select.png`
- `work/ui/stages_0.1.12/runtime/final_post_setup01.trace.json`
- `work/ui/stages_0.1.12/runtime/final_resume_state01.trace.json`
- `work/ui/stages_0.1.12/runtime/final_opening_to_native01.trace.json`
- `work/ui/stages_0.1.12/runtime/final_opening_translation.png`
- `work/ui/stages_0.1.12/runtime/final_evidence03.trace.json`

The cabin/Belfrau checkpoint, Chapter 2, Chapter 3, night conversations, all
alternate routes, and save/load were not played through in this bounded test.
Their translated targets and script changes passed the documented static
checks. This is a test build, not full-game or full-three-chapter runtime
acceptance. See `BUILD_0.1.12.md` and `chapters_coverage_audit_0.1.12.json`.

The test used an isolated configuration and muted sound. Audio resources were
verified unchanged during the build; sound was not auditioned in this run.
Only the owned test process (PID 133304, verified by its isolated executable
path) was stopped afterward. The user's existing PPSSPP process was untouched.
