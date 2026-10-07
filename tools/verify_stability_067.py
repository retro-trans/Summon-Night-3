"""Prove 067 edits then execute inherited native regression groups."""
import sys,json
import verify_stability_066 as previous
import verify_stability_061
from status_fix_067 import BASE,prepare_elf
def checked_view(elf):
 assert elf==prepare_elf()[0],'Unexpected 067 executable'
 return previous.checked_view((BASE/'EBOOT.elf').read_bytes())
previous.previous.rewards_063.prepare_elf=prepare_elf
previous.previous.rewards_063.prior_audit_view=checked_view
verify_stability_061.prepare_elf=prepare_elf
if __name__=='__main__':
 if '--execute' not in sys.argv:print(json.dumps(dict(mode='preview',arguments=sys.argv[1:],scope='Verify actual completed candidate with 14 inherited native regression groups and the proven 067 changes.'),indent=2))
 else:
  sys.argv.remove('--execute')
  import verify_stability_060
  raise SystemExit(verify_stability_060.main())
