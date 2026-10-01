# Teacher terminology, v0.1.53

The user requested Teacher instead of Professor. The new glossary preference is
`work/glossary/terminology_preferences.json`; historical translation inputs remain
unchanged. The nine reviewed English corrections are in
`work/translation/en/terminology_0.1.53/targets.json`.

The update starts from the exact released v0.1.52 ISO. It replaces nine distinct
battle-dialogue passages: one in resource 118 and eight in the common script,
including all 31 shared copies. Capitalized address becomes Teacher; the common
noun becomes teacher. The resulting 32 scripts contain 249 changed line slots.

The builder edits only the existing string slots and zero-fills the unused bytes.
No script code, pointer, archive offset, executable, speaker, page count or line
break changes. It simulates all 541 groups in the two canonical scripts, validates
the shared copies, checks that line width never grows, and compares the complete
ISO with the prior build, allowing only the reviewed changes.

Build with `python tools/build_terminology_053.py --write`. The builder also runs
the existing cumulative safety audit against the actual new ISO. Validation
reports are written beside the ISO. This is a local test build; the affected
scenes have not been checked in live gameplay. No release has been published.
