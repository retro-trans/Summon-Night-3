"""Prove the actual 065 executable before older scoped rendering checks."""
import cache_065,rewards_063,report_ui_062
original063=rewards_063.prepare_elf
def checked_view(elf):
 expected,_=cache_065.prepare_elf();assert elf==expected,'Unexpected 065 executable'
 prior=(cache_065.BASE/'EBOOT.elf').read_bytes();old,_=original063();assert prior==old
 return (rewards_063.BASE/'EBOOT.elf').read_bytes()
rewards_063.prepare_elf=cache_065.prepare_elf
rewards_063.prior_audit_view=checked_view
import verify_stability_064 as previous
if __name__=='__main__':raise SystemExit(previous.previous.previous.previous.previous.main())
