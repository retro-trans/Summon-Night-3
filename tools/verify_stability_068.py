"""Prove category ELF changes before running inherited native audit groups."""
import sys,json
import verify_stability_067 as previous
import verify_stability_061
from categories_fix_068 import BASE,prepare_elf
def checked_view(elf):
 assert elf==prepare_elf()[0],'Unexpected 068 executable'
 return previous.checked_view((BASE/'EBOOT.elf').read_bytes())
previous.previous.previous.rewards_063.prepare_elf=prepare_elf
previous.previous.previous.rewards_063.prior_audit_view=checked_view
verify_stability_061.prepare_elf=prepare_elf
if __name__=='__main__':
 if '--execute' not in sys.argv:print(json.dumps(dict(mode='preview',scope='Run 14 inherited native audit groups on the completed 068 ISO.'),indent=2))
 else:
  sys.argv.remove('--execute');import verify_stability_060
  raise SystemExit(verify_stability_060.main())
