# Summon Night 3 English 0.1.80 — local test upgrade

Includes all changes through 0.1.79. Apply the included 0.1.77 → 0.1.80
xdelta to the published 0.1.77 ISO using Retro Trans Tools. Start the game
fresh and load an in-game save.

- Translate the remaining Learn Skills failure-message prefix and Skill
  Point warning; use variable-width lettering in those message boxes.
- Render hidden skill-name markers as "Unknown" while preserving the game's
  lock conditions. Compact and wrap weapon-proficiency help within the native
  help limit, removing identical repeated mastery rows.
- Restore missing English skill-card labels by combining unused adjacent
  texture strips when longer labels exhaust the available large strips.
- Translate default summon names on text widgets used by summon popups and
  battle banners, including Dritol and Nagare. Preserve custom names.
- Translate all chapter labels and chapter titles used by Replay and saves,
  and the Replay selection help.
- Replace Replay's image-based chapter markers with "Ch", "Extra" and "Halls".
- Give all battle-specific Brave Order help entries explicit end markers.
  Fit list names to their strips and help to the 54-character staging pool,
  including the condition requiring Azlier's defeat before Preempt activates.
- Carry forward the prior translations of Wind Blade, Magic Attack and
  related attack skills, plus the earlier Options and Night Talks fixes.

This is a local test build, not a published release. The included validation
reports distinguish live in-game checks from static and renderer checks.
No direct Android validation or full-game playthrough was performed.
