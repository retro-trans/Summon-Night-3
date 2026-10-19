"""Extend the existing exact-banner VWF path to the attack-skill category."""
import hashlib,json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from spell_name_059 import label
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
from stat_spacing_026 import _file_offset_for_va as off
from font_patch import Assembler,REG
from skill_pool_080 import emit as pool_emit

BASE=ROOT/'work/output/0.1.85'
TEXT=ROOT/'work/translation/en/ui_0.1.86/banner.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def add(a,rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x21)

def names_from_source():
 with GameSource(BASE/'Summon_Night_3_EN_0.1.85.iso') as s:
  st=s.resource('02.DAT',3);b=child(st,parse_index(st,len(st)),25)
  names=sorted({label(b,4+n*48+32) for n in range(struct.unpack_from('<I',b)[0])}-{''})
 assert max(map(len,names))<=16 and 'Deadly Strike' in names
 prior=json.loads((ROOT/'work/translation/en/report_0.1.61/strings.json').read_text('utf8'))['banner_names']
 return names,sorted(set(names)|set(prior))

def emit(a,book_count,match_delta):
 a.label('match');a.move('v0','zero');a.branch(4,'a0','zero','match_return');a.table_address('t0');a.i(37,'t1','t0',0);a.i(9,'t8','t0',4);a.i(9,'t2','t0',4+book_count*2)
 a.label('candidate');a.branch(4,'t1','zero','match_return');a.i(36,'t3','t2',0);a.i(9,'t5','t2',1);a.move('t4','a0');a.move('t7','t3')
 a.label('compare');a.i(36,'t6','t5',0);a.emit(REG['t6']<<16|REG['t6']<<11|1<<6);add(a,'t6','t8','t6');a.i(37,'t6','t6',0);a.i(37,'t9','t4',0);a.branch(5,'t6','t9','miss');a.i(9,'t5','t5',1);a.i(9,'t4','t4',2);a.i(9,'t7','t7',-1);a.branch(5,'t7','zero','compare');a.i(37,'t9','t4',0);a.branch(5,'t9','zero','miss');a.move('v0','t3');a.ret()
 a.label('miss');add(a,'t2','t2','t3');a.i(9,'t2','t2',1);a.i(9,'t1','t1',-1);a.branch(4,'zero','zero','candidate')
 a.label('match_return');a.ret()
 a.label('center_bind');pool_emit(a)
 # Reuse the audited free-strip coalescer with the centered banner packer.
 a.fixups=[(i,k,0x348a7c if k=='jump' and v==0x347b5c else v) for i,k,v in a.fixups]
 # The old exact-name matcher entry now jumps here. Its original relative
 # branch had no absolute relocation, so register this one explicitly.
 a.relocs.append((match_delta,0x304))

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TEXT.read_text('utf8'));attack,names=names_from_source();assert cfg['attack_names']==attack and cfg['banner_names']==names
 raw=[encode_dialogue(t,'')[0] for t in names];book=sorted({x[0] for b in raw for x in struct.iter_unpack('<H',b)});lookup={v:i for i,v in enumerate(book)};assert len(book)<256
 payload=bytearray(struct.pack('<HH',len(names),len(book))+struct.pack('<'+'H'*len(book),*book))
 for b in raw:
  cells=[x[0] for x in struct.iter_unpack('<H',b)];payload.append(len(cells));payload.extend(lookup[c] for c in cells)
 payload.extend(bytes(-len(payload)%4));manifest=json.loads((BASE/'manifest.json').read_text('utf8'));prior=manifest['report061_ui']['elf'];match=int(prior['code_address'],16)+prior['labels']['match'];seg=parse_elf(old)['phdrs'][3];base=seg[2]+seg[4]
 probe=Assembler();emit(probe,len(book),match-base);assert len(probe.words)*4+len(payload)<0x1000
 patched=bytearray(old);assert struct.unpack_from('<I',old,off(old,match))[0]==0x10800020
 struct.pack_into('<II',patched,off(old,match),2<<26|base>>2,0)
 start=int(prior['code_address'],16)+prior['labels']['bind'];end=int(prior['code_address'],16)+prior['labels']['original_bind'];sites=[p for p in range(start,end,4) if struct.unpack_from('<I',old,off(old,p))[0]==2<<26|0x348a7c>>2];assert len(sites)==1
 center_site=sites[0];struct.pack_into('<I',patched,off(old,center_site),2<<26|(base+probe.labels['center_bind'])>>2)
 result,r=append(bytes(patched),lambda a:emit(a,len(book),match-base),{0x14ebd8:('center_bind',3<<26|0x1cbdec>>2)},bytes(payload))
 assert validate_loader_structure(result)
 r.update(version='0.1.86',source_sha256=sha(old),output_sha256=sha(result),prior_match=match,prior_draw=int(prior['code_address'],16)+prior['labels']['draw'],prior_center_branch=center_site,attack_name_count=len(attack),banner_names=names,attack_names=attack,codebook_cells=len(book),compact_dictionary_bytes=len(payload),original_ui_tables_unchanged=True,save_bytes_unchanged=True,loaded_page_growth=((base+r['code_bytes']+4095)//4096-(base+4095)//4096)*4096)
 return result,r
