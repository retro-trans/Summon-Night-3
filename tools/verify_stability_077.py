"""Prove 077 changes before replaying inherited crash and renderer audits."""
import sys,json
import verify_stability_076 as previous
import verify_stability_061,rewards_063
from battle_fix_077 import BASE,prepare_elf
def checked_view(elf):
 assert elf==prepare_elf()[0],'Unexpected 077 executable'
 return previous.checked_view((BASE/'EBOOT.elf').read_bytes())
rewards_063.prepare_elf=prepare_elf
rewards_063.prior_audit_view=checked_view
verify_stability_061.prepare_elf=prepare_elf
if __name__=='__main__':
 if '--execute' not in sys.argv:print(json.dumps(dict(mode='preview',scope='Inherited crash and renderer guards.')))
 else:
  sys.argv.remove('--execute');import verify_stability_060
  raise SystemExit(verify_stability_060.main())
