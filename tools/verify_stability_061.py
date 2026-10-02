"""Audit the actual 0.1.61 candidate, with proven historical views for exact older scopes."""
from sn3_archive import ROOT
from report_ui_061 import prior_audit_view,prepare_elf
import levelup_060,verify_levelup_060
import verify_stability_060 as previous
old_view=levelup_060.prior_audit_view
levelup_060.prior_audit_view=lambda elf:old_view(prior_audit_view(elf))
old_prepare=verify_levelup_060.prepare_elf
def candidate_levelup():
 # prior_audit_view first proves every new executable change belongs to 0.1.61.
 elf,_=prepare_elf();prior_audit_view(elf);_,r=old_prepare();return elf,r
verify_levelup_060.prepare_elf=candidate_levelup
if __name__=='__main__':raise SystemExit(previous.main())
