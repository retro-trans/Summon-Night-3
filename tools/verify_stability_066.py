"""Prove actual 066 changes before executing inherited scoped regression groups."""
import verify_stability_065 as previous
import sys,json
import verify_stability_061
from status_fix_066 import prepare_elf,BASE

def checked_view(elf):
    assert elf==prepare_elf()[0],'Unexpected 066 executable'
    return previous.checked_view((BASE/'EBOOT.elf').read_bytes())

previous.rewards_063.prepare_elf=prepare_elf
previous.rewards_063.prior_audit_view=checked_view
verify_stability_061.prepare_elf=prepare_elf
if __name__=='__main__':
    if '--execute' not in sys.argv:
        print(json.dumps(dict(mode='preview',arguments=sys.argv[1:],scope='Read the completed ISO, prove the scoped 066 executable changes, execute inherited regression groups, and save the requested report.'),indent=2))
    else:
        sys.argv.remove('--execute')
        raise SystemExit(previous.previous.previous.previous.previous.previous.main())
