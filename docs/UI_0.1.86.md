# 0.1.86 — Complete proportional action banners (local test build)

“Deadly Strike” was stored in full, but was absent from the exact-name banner
dispatcher. Its banner remained in the original per-character mode with eight
font objects, leaving only “Deadly S” visible.

Extend the existing centered VWF banner path to all 108 translated attack-skill
names, retaining the spell names previously covered. Compare complete native
character sequences through a compact codebook; do not use approximate hashes,
prefix matching, or broad changes to unrelated widgets.

Before binding a longer banner, reuse the audited font-cache coalescer to join
two adjacent unused eight-cell strips when a suitable strip is unavailable.
Preserve occupied strips and row boundaries. The reported label renders all
13 characters with a 112-pixel proportional advance before scaling.

Checks execute the emitted dispatch, existing native widget transition and
centered pixel packer at two relocated load addresses, including long labels,
unrelated text, occupied cache entries and guarded texture/stack boundaries.
The old matcher rejection is reproduced. No new texture atlas or allocated code
page is required; UI data tables, saved names and combat rules are preserved.

Runtime coverage and limitations are recorded in the accompanying validation.
The test ZIP supports published 0.1.83 and local 0.1.85 inputs through Retro Trans
Tools. Start normally and load an in-game save. This is a local test build;
0.1.83 remains the published release.
