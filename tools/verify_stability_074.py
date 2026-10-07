"""Verify 074 mutations separately, then use the prior audited code view."""
import sys,json
import verify_stability_073 as previous
import verify_stability_061,rewards_063
from menus_fix_074 import BASE,prepare_elf

def checked_view(elf):
 assert elf==prepare_elf()[0],'Unexpected 074 executable'
 return previous.checked_view((BASE/'EBOOT.elf').read_bytes())

rewards_063.prepare_elf=prepare_elf
rewards_063.prior_audit_view=checked_view
verify_stability_061.prepare_elf=prepare_elf
if __name__=='__main__':
 if '--execute' not in sys.argv:print(json.dumps(dict(mode='preview',scope='Prior native audits; new menu and stat dispatch checks run separately.')))
 else:
  sys.argv.remove('--execute');import verify_stability_060
  raise SystemExit(verify_stability_060.main())
