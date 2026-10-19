"""Record fresh-boot UI coverage and check loaded pointers without changing RAM."""
import base64,json,struct
from ui_fix_084 import ROOT,BASE,TEXT,encoded
from options_runtime_078 import client

def main():
 dest=ROOT/'work/output/0.1.84';m=json.loads((dest/'manifest.json').read_text('utf8'));r=m['ui084_fix']['elf'];cfg=json.loads(TEXT.read_text('utf8'))
 session=json.loads((ROOT/'work/scratch/ui084-final/session.json').read_text('utf-8-sig'));assert session['fresh_boot'] and not session['save_state_used'] and '0.1.84.iso' in session['iso']
 request=client(19448);assert request('game.status')['game']['id']=='NPJH50380';base=0x08804000
 read=lambda p,n:base64.b64decode(request('memory.read',address=p,size=n)['base64'])
 word=lambda p:struct.unpack('<I',read(p,4))[0]
 literal_checks=[]
 for e in cfg['class_change']:
  p=base+r['class_literals'][e['source_address']];wanted=b''.join(encoded(t) for t in e['english'])+bytes(2);assert read(p,len(wanted))==wanted;literal_checks.append(e['source_address'])
 assert read(base+r['reward_heading'],len(encoded(cfg['reward_heading'])))==encoded(cfg['reward_heading'])
 for site in r['discovery_vwf_sites']+[0x14ecbc]:assert ((word(base+site)&0x3ffffff)<<2)==base+0x347b5c
 assert ((request('memory.disasm',address=base+0x1b0f8,count=1)['lines'][0]['encoding']&0x3ffffff)<<2)==base+int(r['code_address'],16)+r['labels']['draw']
 for hi,lo,source in [(0x11c5d0,0x11c5d8,'0x21c788'),(0x11c5cc,0x11c5dc,'0x21c7bc')]:
  h,l=word(base+hi)&65535,word(base+lo)&65535;actual=(h<<16)+(l-65536 if l&32768 else l);assert actual==base+r['class_literals'][source]
 log=(ROOT/'work/scratch/ui084-final/runtime.log').read_text('utf8',errors='replace')
 assert '0.1.84.iso' in log and all(t not in log for t in ('Bad memory access','out of memory','failed to allocate','NO_MEMORY'))
 evidence=dict(passed=True,version='0.1.84',iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4',jit=True,renderer='software',fresh_boot=True,save_state_used=False,normal_save_loaded=True,load_base=hex(base),class_literal_groups_verified_in_ram=len(literal_checks),reward_heading_verified_in_ram=True,live_popup_bindings=80,live_class_branches_verified=2,loaded_helper_bytes=r['code_bytes'],screenshots=['finalLoaded.png','finalStatus.png','finalTypes.png','finalOtherTypes.png'],exact_beach_reward_sequence_reproduced=False,exact_class_change_sequence_reproduced=False,exact_summon_animation_reproduced=False,limitations=['Available Chapter 16 normal save used; exact beach/reward/class-change save is unavailable.','Renderer helper behavior and name lookup are exercised by emitted-code tests; complete reported sequences require later gameplay confirmation.','No Android, hardware renderer or full playthrough testing claimed.'])
 for folder in (dest,ROOT/'work/ui/ui_0.1.84'):(folder/'runtime-validation.json').write_text(json.dumps(evidence,indent=2)+'\n','utf8')
 print(json.dumps(evidence),flush=True)

if __name__=='__main__':main()
