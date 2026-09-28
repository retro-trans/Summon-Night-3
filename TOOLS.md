# Tools

These are incremental translation research tools, generally run from the
repository root with Python 3.12. Supply original media and vendor binaries
locally; they are excluded from Git.

| Tool or group | Purpose |
|---|---|
| `tools/scan_source.py` | Read-only ISO/ZIP inventory and source hashes |
| `tools/prepare_source.py` | Local source preparation; inspect arguments first |
| `tools/sn3_archive.py`, `sn3_repack.py`, `sn3_codec.py` | Archives and compression |
| `tools/index_interface.py`, `character_labels.py` | UI and unit-label indexes |
| `tools/chapter_source*.py`, `battle_source_024.py` | Resolve original dialogue locally |
| `tools/dialogue_encoding.py`, `dialogue_layout.py` | Encoding, controls and layout |
| `tools/build_*.py` | Version-specific builders; prior local outputs required |
| `tools/verify_*.py` | Structural, pointer, layout or emitted-code checks |
| `tools/*runtime*.py`, `capture_framebuffer.py` | Isolated PPSSPP checks and screenshots |
| `tools/package_release_035.py` | Verify the delta round trip and create release metadata |

A read-only source check:

```sh
python tools/scan_source.py "Summon Night 3 (Japan).iso"
```

Depending on the tool, additional dependencies include Pillow, NumPy, Capstone,
pyelftools, websocket-client, PPSSPP, pspdecrypt and xdelta3. They are not bundled.
Inspect the selected tool's imports and documented paths before running it.

`tools/README.md` has older detailed research notes. Its paths and prerequisites
describe specific builds rather than a universal build command. Preserve
published evidence when recreating experiments.
