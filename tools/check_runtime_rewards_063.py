"""Read loaded PPSSPP pointers; preview evidence before saving it."""
import argparse,json,base64,struct,hashlib
from sn3_archive import ROOT
from rewards_runtime_063 import request
from rewards_063 import prepare_elf,PAIRS,TEXT
from dialogue_encoding import encode_dialogue
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 session=json.loads((ROOT/'work/scratch/rewards063-runtime/session.json').read_text(encoding='utf-8-sig'));assert session['fresh_boot'] and not session['save_state_used']
 game=request('game.status');assert game['game']['id']=='NPJH50380';_,r=prepare_elf();base=0x08804000;spec=json.loads(TEXT.read_text(encoding='utf8'));targets={x['va']:x['english'] for x in spec['literals']}
 read=lambda ptr,n:base64.b64decode(request('memory.read',address=ptr,size=n)['base64'])
 word=lambda ptr:struct.unpack('<I',read(ptr,4))[0]
 pairs=[]
 for hi,lo,va in PAIRS:
  h,l=word(base+hi),word(base+lo);actual=((h&65535)<<16)+((l&65535)-65536 if l&32768 else l&65535);expected=base+int(r['literal_addresses'][hex(va)],16);assert actual==expected
  encoded=encode_dialogue(targets[hex(va)],'')[0]+b'\0\0';assert read(actual,len(encoded))==encoded
  pairs.append(dict(high=hex(hi),low=hex(lo),address=hex(actual),english=targets[hex(va)]))
 for site,target in r['bindings'].items():assert (word(base+int(site,16))&0x3ffffff)<<2==base+int(target,16)
 log=(ROOT/'work/scratch/rewards063-runtime/runtime.log').read_text(encoding='utf8',errors='replace');assert '0.1.63.iso' in log and 'Bad memory access' not in log
 evidence=dict(version='0.1.63',fresh_boot=True,ppsspp='1.20.4',load_base=hex(base),save_state_used=False,live_text_pairs=pairs,live_vwf_bindings=7,exact_reward_screen_verified=False,exact_party_join_screen_verified=False,screenshot='work/ui/rewards_0.1.63/runtime/boot.png')
 target=ROOT/'work/output/0.1.63/runtime-validation.json';print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(target),evidence=evidence),indent=2),flush=True)
 if a.write:target.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
