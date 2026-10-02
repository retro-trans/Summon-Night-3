"""Audit the 0.1.62 ISO and prove scoped executable changes before legacy audits."""
import report_ui_061,report_ui_062
original_prepare=report_ui_061.prepare_elf
report_ui_061.prepare_elf=report_ui_062.prepare_elf
# Prove both new layers before exposing the older immutable Level Up view.
def checked_view(elf):
 prior=report_ui_062.prior_audit_view(elf);expected,_=original_prepare();assert prior==expected
 return (report_ui_061.BASE/'EBOOT.elf').read_bytes()
report_ui_061.prior_audit_view=checked_view
import verify_stability_061 as previous
if __name__=='__main__':raise SystemExit(previous.previous.main())
