# Summon screen — 0.1.57

The reported page used the Japanese Create Summons background even though its
spell list had been translated. Its top hints still used fixed-width text, so
Cast Magic overlapped the second icon and Dismiss extended past the screen edge.

The fix imports **Create Summons** and **Affinity:** only in their text regions
of `02.DAT` resource 2953, child 0. The original frame, seal and other pixels remain
unchanged. The Affinity label is also imported in the related resources 2954 and
2955; their other headings are outside this fix.

Confirm, Set Name, Cast and Dismiss reuse the shipped, length-checked proportional
Type wrapper. Their exact per-mode icon/text anchors move left. Cast Magic becomes
Cast; other hint wording and button meanings remain unchanged. No code, relocation
records, allocation sizes or loaded segment ranges are added.

## Validation

- Validate the loader structure, existing jump relocations and exact changed-byte
  scope. Execute the wrapper in ten cases at two game load addresses with guarded
  stacks and caller register checks.
- Measure text against the native 480-pixel screen: Cast ends by 373 before the
  second icon at 388; Dismiss ends by 472. Confirm, Set Name and Type fit too.
- Pass all 13 regression groups on the finished ISO. Three old audits require a
  byte-exact historical executable; verify that the only changes are this hint
  patch before supplying those audits with the unchanged historical code view.
  The shared-guard audit also uses this validated historical view only for its
  inherited-segment equality comparison, because that segment contains the
  unrelated Cast literal. Its guard execution, all 131,072 glyph cases and
  relocated staging tests still run the actual candidate executable. All other
  groups and the new hint group use the actual candidate executable.
  The final entry point is `tools/verify_stability_057_final.py`.
- Create the local 0.1.55-to-0.1.57 xdelta with Retro Trans Tools and verify the
  complete decoded ISO hash. This test patch includes the 0.1.56 Magna fix.

ISO SHA-256: `939e53bd1e6a3202012f985f918d7f855fc294fed8fc44f8ddae9d6c9c1f959e`.

The text import resolves the stable module address through the current loaded
segment header. Later builds retained unused copies at older file offsets;
changing those copies does not affect the live screen. A runtime check caught
that distinction, and the final audit explicitly checks the loaded Cast string.

The built-in image generator localized the flat background. Its complete prompt
and source asset are recorded in `work/ui/summon_0.1.57/imagegen.json` and
`create_summons_generated.png`; mechanical importing preserves all pixels outside
the two text regions. Native preview: `2953_native.png`.

Fresh-boot runtime evidence uses isolated PPSSPP 1.20.4 with a copied normal
Chapter 15 battle save, JIT and software rendering, with bad-memory ignoring off.
Screenshots and navigation evidence are kept under `work/ui/summon_0.1.57/runtime`.
The corrected candidate was reached through normal load, Unit List, Special and
Pact: All. `runtime/craft_corrected.png` shows Gravis on the same Create Summons
page as the reported Injecks screenshot: both English background labels and the
complete Cast/Dismiss hints fit. The exact Injecks row was not exercised. No bad
memory access was logged during this navigation. These checks cover this page,
not a full playthrough.
