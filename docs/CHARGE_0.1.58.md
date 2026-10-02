# Charge action label — local 0.1.58

The screenshot shows チャージ, translated as **Charge**. The status label in
02.DAT resource 3, child 0, record 10 already points to English. The separate
special-command label in child 28, record 50, slot 8 still points to Japanese.

This build appends the encoded English label to that command table, redirects
only its name pointer and synchronizes the resident copy in 00.DAT resource 44,
child 7. The old pool, other pointer fields, other table children and executable
are unchanged. The six native 16-pixel cells fit within the approximately
204-pixel banner shown in the report. No rendering hook is introduced.

The build is based on local 0.1.57 and retains its changes. This is a local test
build; historical published assets and inputs are preserved.

Validation: the finished ISO's redirected pointer resolves to the full English
label, both resident copies match, all 13 regression groups pass and the local
0.1.55-to-0.1.58 upgrade passes Retro Trans Tools' complete decode/hash check.
The ISO SHA-256 is
`3e020020cae975eb2ec3f831f9ff26b39b9f0e1c16a34dc758f708835b7556a8`.

An isolated fresh boot of PPSSPP 1.20.4 loaded a copied normal Chapter 15 save
and reached the protagonist's Special menu without a bad-memory fault. That
unit does not have Charge available, so the exact action banner has not been
visually verified. Evidence is under `work/ui/charge_0.1.58/runtime`; this is
not a full-playthrough stability claim.
