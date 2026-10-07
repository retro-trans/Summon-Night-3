# Related UI translations: local 0.1.69

Base: immutable local 0.1.68. This is a test build, not a published release.

The reported screens expose untranslated names from shared summon and item
tables and untranslated native crafting/confirmation text. The Takeshi profile
and reward heading are already translated in the base; their consumer pointers
are explicitly checked for retention.

## Coverage

- Table 13: all 191 remaining referenced Japanese spell names, including all four
  Tamahipo breaths. Previously translated names and generated spell descriptions
  retain their existing values. Unit Form labels and every undiscovered mask stay distinct.
- Table 19: 333 remaining fields in records 1–28 and 165–322: five stone types,
  consumables and bait, gallery unlock items, art descriptions and ending titles.
  Internal R/debug items and unrelated equipment are outside this category pass.
- EBOOT: 18 translated blocks for crafting help, dismissal, ending creation,
  favorite settings, color changes, favorite limits and character eligibility.
  The shared quote prefix is bound separately for eligibility and named confirmations.
  Both directly referenced No choices receive their own relocated pointer.

## Display and preservation

Names fit 16 encoded cells and 108 pixels at the existing 0.875 display scale;
the widest new name measures 107.625 pixels. Dried Sardines displays as Dried
Sardine. Animation Art 28/29 displays as Anim. Art 28/29. Full English forms are
retained in translation metadata. Item help fits two rows, at most 27 cells each.
Greek Omega retains its native glyph and 16-pixel fallback advance.

Native restrictions retain the runtime character name and question-mark fallback:
Only CUSTOMXX can favorite. / Unit Form: CUSTOMXX only.
Actual native concatenation tests cover default, custom and undiscovered names.
Player-entered names and the numeric favorite limit are preserved.

All translated strings are appended to new storage. Only source-bound pointers
change in table records; spell and item numbers, costs, effects and flags stay
byte-identical. Both resident static-table copies are synchronized. Existing
native renderer, status, SELECT and private script-arena hooks are preserved.

## Review notes

Two translation agents reviewed the spell and item categories. Character spelling
uses the current SN6 Vita overlay. Teacher is used in gallery titles.

Plant item names use provisional romanizations; Ixellion, Hermit Blow and Gere
spell names remain provisional. GT Magnyum preserves the source's cat pun.
Reaver is a provisional rendering of the class opposed to Saver. Its identity is
supported by the [PSP Isola class notes](https://w.atwiki.jp/sn3psp/pages/88.html),
which associate it with Isola and the protagonists' Karma route; this does not
establish an official English localization. Spell context was checked against
the [PSP status reference](https://w.atwiki.jp/sn3psp/pages/112.html).

Gallery title Upon Waking... preserves its unspecified subject. I'm Happy infers
the speaker in an extra-story ending title. These are labels, not dialogue records.

Validation reports and runtime images are under work/ui/categories_0.1.69.
All 16 groups pass, including 235 native spell-description variants, 184 new
item-help staging cases, six native eligibility concatenation cases, all 340
new display names, and the retained SELECT/Give Food paths. Strict PPSSPP 1.20.4
JIT fresh-boots and loads the normal Chapter 15 battle save without a save state.
Takeshi's two profile rows and Tamahipo's four breath names are visually verified;
their names fit beside the unchanged MP costs. The combination list also renders.
Exact early-story reward/gallery states require a matching normal save; source
pointer and native staging checks cover those translations separately.
