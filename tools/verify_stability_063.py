"""Audit actual 0.1.63, proving every newer layer before legacy checks."""
import report_ui_062,rewards_063
original_prepare=report_ui_062.prepare_elf
report_ui_062.prepare_elf=rewards_063.prepare_elf
def checked_view(elf):
 prior=rewards_063.prior_audit_view(elf);expected,_=original_prepare();assert prior==expected
 return (report_ui_062.BASE/'EBOOT.elf').read_bytes()
report_ui_062.prior_audit_view=checked_view
import verify_stability_062 as previous
if __name__=='__main__':raise SystemExit(previous.previous.previous.main())
