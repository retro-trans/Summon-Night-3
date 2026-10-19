# 0.1.83 — Berserk Summon crash fix (local test build)

The stone-break notification was 52 characters long. The native per-character
message renderer has 31 pointer slots, followed by its counter. A longer row
overwrote that counter with a font-object pointer, then wrote outside memory.
The supplied 0.1.81 state reproduces the reported invalid access exactly.

The notification now reads "Berserk Summon broke the stone!" (31 characters).
Eight related oversized battle warnings were shortened as well. All 27 audited
action restrictions and summon notifications fit the 31-character bound.
Only existing English literals change: no code, relocations, combat rules,
save formats, or other ISO files change. Includes the 0.1.82 equipment-row fix.

The native binder tests reproduce the original bad store at 0x2c961c20 and
verify 56 cases at two load addresses, including the 31-character boundary.
Runtime QA uses PPSSPP 1.20.4, JIT, software graphics and strict memory checks.
The recovered message displays fully, confirming it returns to battle, and
Suspend saving completes. A separate fresh boot tests the normal Suspend copy.
No full-game playthrough, Android, or hardware-renderer testing is claimed.

Apply SN3-English-v0.1.81-to-v0.1.83.xdelta to the published 0.1.81 ISO using
Retro Trans Tools. This is a local test build; 0.1.81 remains the published release.

The supplied state was already inside the corrupted text loop. An untouched
old state still contains the old executable and text. A private recovered
normal Suspend save is provided separately: copy its ULJS00303SN3BATTLE folder
into your emulator's PSP/SAVEDATA folder, preserving your existing folder as
a backup, then start 0.1.83 normally and choose Continue. This resumes just after
the stone-break message. The original supplied archive remains unchanged.

Recovery changes only nine notification literals, the interrupted renderer's
four loop registers and PC, its corrupted counter and cached text dimensions.
Combat/turn data and code are preserved. The resulting normal Suspend save
was created through the game's own menu, not by editing its DATA.BIN.
