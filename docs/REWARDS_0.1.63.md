# Rewards and joining messages — local 0.1.63

The reported reward screen now says **Rewards obtained!**, **F Aid**, and
**Concept Art 02**. All 34 Concept Art labels (the generic label and 01–33)
are translated together. Statistics, quantities, money and experience values
are unchanged.

The shared recruitment popup displays the existing character-name field on
the first row, followed by **joined the party!** on the second row. The source
quotation and grammatical suffix become English quotation marks. Kyle is an
example, not a hard-coded replacement. The same native selector also handles
materialization, joining battle/support, leaving battle and rejoining battle;
its associated labels are translated as a coherent group.

English strings are appended to the executable and item table; original pools
are preserved. Only proven relocation-backed references and seven font-bind
calls change. Both resident copies of the item table are synchronized.

The reward heading is rendered as one complete proportional text strip in
the first native font object. A blank second object preserves the original
structure without creating a gap inside the English sentence. Reward item
names use the existing length-checked short VWF wrapper. Recruitment labels
use a new length check that delegates to the existing VWF strip renderer for
up to 32 cells and retains the native binder for longer input. The name's
existing cell rectangle uses centered proportional lettering. No extra
font-object pool is allocated, and saved/custom names are not rewritten.

## Verification

- All 14 inherited ISO regression groups pass, including renderer guards,
  equipment/spell formatters, Cooking, Level Up and summon controls.
- The unchanged native notification selector chooses the expected translated
  label in 32 cases covering four supported modes, puppet state, unit ID and
  the character condition flag.
- Twenty wrapper cases exercise the actual appended code at two load bases,
  including English/Japanese/custom names, empty input and the 32/33-cell
  boundary, with guarded stack memory.
- Actual existing VWF code passes 480 banner cases, 96 bind cases and 210
  font-pixel cases against this candidate. The prior awakening/Mujina help
  and Set coordinate checks also pass.
- Measured party-message ink spans 104.25 pixels at the popup's 0.75 scale,
  below the 116-pixel region before the sprite. Item labels fit the measured
  reward-row budget.
- Fresh-boot PPSSPP 1.20.4 resolves all 13 selected live text-pointer pairs to
  the expected English strings and all seven font-bind calls to their intended
  helpers. No memory fault is recorded during this boot check.
- Archive verification preserves 5,728 unchanged bank resources and all
  23 indexes. The local 0.1.55-to-0.1.63 patch is checked with Retro Trans Tools.

Exact reward and recruitment popup screenshots remain pending a save before
those events. Instruction-level checks stub native graphics calls; the fresh
boot proves loaded pointers and helper targets, not those popups' appearance.
Evidence is in `work/output/0.1.63/ui-regression.json`, `stability-report.json`
and `runtime-validation.json`.

ISO SHA256: `7cf656433dd825c08c2811417ac66f7c1383d24d7706c1d57e8fcd478bee95a0`.
