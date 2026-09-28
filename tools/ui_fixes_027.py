"""Pact Ritual labels and generated affinity help on immutable 0.1.26."""
import argparse,json,hashlib,struct
import battle_elf_patch as patcher
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from notice_vwf_027 import prepare as prepare_notice
from help_dispatch_027 import prepare as prepare_help
from stages_pupil_names import parse_elf

BASE=ROOT/'work/output/0.1.26';FOLDER=ROOT/'work/translation/en/ui_fixes_0.1.27'
sha=lambda b:hashlib.sha256(b).hexdigest()
PIECES={0x217484:'Craft summons［',0x217498:'/',0x21749c:'Machine',0x2174a0:'Oni',0x2174a4:'Spirit',0x2174a8:'Beast',0x2174ac:'Neutral',0x2174b0:'］'}
AFFINITIES={4:'Machine',5:'Oni',6:'Spirit',7:'Beast',8:'All'}
NAMES={0x2194b8:'All',0x2194c8:'O/S/B',0x2194dc:'M/S/B',0x2194f0:'M/O/B',0x219504:'M/O/S',0x219518:'M/O',0x21952c:'M/S',0x219540:'M/B',0x219554:'O/S',0x219568:'O/B',0x21957c:'S/B',0x219590:'Machine',0x2195a0:'Oni',0x2195b0:'Spirit',0x2195c0:'Beast'}

def ritual_references(data):
 # The generic scanner stops at earlier return-delay writes. These three
 # branch targets instead inherit the LUI in their own branch delay slot.
 refs,users,pairs=original_references(data)
 for address,high,low in [(0x2194d0,0x697d4,0x6981c),(0x2194e0,0x697e0,0x69814),(0x2194f0,0x697ec,0x6980c)]:
  assert pairs[high]==low
  hw,lw=patcher.word(data,high),patcher.word(data,low)
  assert hw>>26==15 and lw>>26==9 and patcher.resolved_address(hw,lw)==address
  assert patcher.word(data,low-4)==0x03e00008
  refs[address]=[dict(kind='hilo',high=high,low=low,register=2)]
  users[high]=[dict(low=low,target=address,opcode=9)]
 return refs,users,pairs

original_references=patcher.references

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows();targets={**PIECES,**{p:'Pact Ritual: '+t for p,t in NAMES.items()}};rows=[dict(idx[f'elf:ui:{p:08x}'],target_full=t) for p,t in targets.items()]
 prior=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf';patcher.references=ritual_references;data,r=patcher.prepare(old,rows,idx)
 finally:patcher.BASELINE=prior;patcher.references=original_references
 assert not r['skipped']
 data,nr=prepare_notice(data);r['notice_vwf']=nr
 data,hr=prepare_help(data);r['help_dispatch']=hr;r['patched_elf_sha256']=sha(data)
 for e in r['entries']:
  va=int(e['new_address'],16);ph=next(h for h in parse_elf(data)['phdrs'] if h[0]==1 and h[2]<=va<h[2]+h[4])
  e['new_file_offset']=ph[1]+va-ph[2]
 return data,r

def prepare_tables(source):
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());t=next(t for t in index['tables'] if t['resource_path']==[3,28])
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,28);out=bytearray(before);changes=[]
 for record,affinity in AFFINITIES.items():
  for slot,text in [(8,'Pact Ritual: '+affinity),(9,'Enables summon crafting.')]:
   row=next(r for r in t['strings'] if any(f['record']==record and f['slot']==slot for f in r['references']))
   p,n=row['source_offset'],row['source_byte_length'];assert sha(before[p:p+n])==row['source_sha256']
   fields=[f['pointer_field_offset'] for f in row['references']];assert all(struct.unpack_from('<I',before,f)[0]==p for f in fields)
   raw,display=encode_dialogue(text,'');out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0')
   if slot==9:out.extend(b'\0\0')
   for f in fields:struct.pack_into('<I',out,f,new)
   changes.append(dict(id=row['id'],record=record,slot=slot,text=text,full_translation=('Ritual of the Pact: '+affinity if slot==8 else 'Enables the creation of summons.'),source_sha256=row['source_sha256'],new_offset=new,pointer_fields=fields))
 patched=repack(static,{28:bytes(out)});master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched})
 return {3:patched},{},master,dict(units=[],tables=[dict(child=28,changes=changes)])

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();_,er=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.26.iso') as s:_,_,_,tr=prepare_tables(s)
 r=dict(version='0.1.27',elf=er,tables=tr,review='Independent reviewer accepted Pact Ritual: Machine and Craft Machine/Neutral summons. Dynamic help retains the same crafting meaning and original affinity selection.')
 print(json.dumps(r,indent=2))
 if a.write:FOLDER.mkdir(parents=True,exist_ok=True);(FOLDER/'review.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
