# Learn Skills report — 0.1.64

Local test build on immutable 0.1.63. Translate Dash!, Fighting Spirit,
Guts and Item Throw, including their help and mastery effects. The existing
skill-card proportional renderer is retained.

Strings are appended to static tables 28 and 31 and only the twelve selected
text pointers are changed. All original text pools, numerical fields, skill
costs, levels and effects remain intact. The 00.DAT static cache is synchronized
with 02.DAT. The executable remains byte-identical to 0.1.63.

The description panel accepts three rows of at most 27 cells, with 54 glyph
objects in total. Candidate help and mastery text together use 53, 53, 42 and
48 objects. All four blocks pass execution of the actual emitted shared help
staging code. Skill-name widths range from 34.125 to 99.75 pixels within the
108-pixel card allowance. These checks use native code with graphics boundary
stubs; they do not establish exact in-game appearance.

A parallel meaning review approved the final translations, including the
gentle-terrain restriction and near-death penalty. The non-Latin source glyph
in the shared maximum mastery effect is preserved unchanged. Its meaning is
unresolved and no new interpretation or mechanics have been added.

All 14 inherited regression groups pass against the completed ISO. A fresh
PPSSPP 1.20.4 boot reaches the title screen without a memory fault. Evidence is
in the build's ui-regression.json, stability-report.json and
runtime-validation.json. Exact Learn Skills visual verification needs a
matching save. The upgrade from published 0.1.55 passes Retro Trans validation
and full decoded-ISO hash verification. It is a local test patch, not a
published release.
