# Build 0.1.9 — backlog spacing

[ISO](../work/output/0.1.9/Summon_Night_3_EN_0.1.9.iso) · [Backlog screenshot](../work/ui/backlog_0.1.9/runtime/backlog.png)

The dialogue history used fixed 16-pixel Japanese cells for English, separately
from the proportional dialogue-window renderer. Long lines ran beyond the panel.
Both speaker names and history text now use the same measured Latin ink widths
as dialogue. Original glyph pixels, sentence content, font size and line breaks
are preserved. Unmapped characters keep their original 16-pixel cells.

The patch packs the ink inside each existing native 1/8/16-cell texture strip and
advances the next strip by its measured width. It changes only four backlog call
sites. It does not expand the object pool or alter other font users. Cache keys
are invalidated after packing so later owners repaint their original glyphs.

## Verification

- Executed the emitted MIPS instructions in 202 guarded cases at two load bases:
  all 93 supported Latin characters, spaces, punctuation, 16-cell strips and
  mixed Japanese fallback. Checked pixels, strip boundaries, stack/register
  preservation, cache invalidation and measured advance.
- Booted the final ISO in isolated PPSSPP 1.20.4. Inspected naming, beach backlog,
  earlier entries after scrolling, normal dialogue after closing, and new history
  entries after reopening. [Evidence](../work/output/0.1.9/backlog_runtime_validation.json).
- All 35 other ISO files are byte-identical to 0.1.8, including every resource
  bank and audio file. Validated all 23 bank indexes and the changed executable.
- The 512 lines in the current reflowed dialogue groups have a maximum measured
  width of 243 pixels, within the 356-pixel history panel.

The exact harbor scene from the report and full-game routes were not replayed.
The voice-playback label remains Japanese; this build fixes spacing and does not
add translations. Prior chapter cards and translations are retained. This is
still a partial English translation. Audio playback was not retested.

Boot the new ISO from a fresh start, then load an ordinary in-game save if needed.
Old PPSSPP save states retain the old executable in memory and can restore the bug.

SHA-256: `0823fe7450c916be6689d852df1ec89e7a83a798e2ac83201a7d836ea53a09bc`. Size: 1,659,451,392 bytes.
Next unused version: **0.1.10**.
