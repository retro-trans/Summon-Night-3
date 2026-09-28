"""Learn Skills text, card VWF and native menu labels on immutable 0.1.40."""
import json,struct,hashlib,unicodedata
from PIL import Image
import battle_elf_patch as patcher
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va
from menu_art_015 import descend
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_code_020 import append
from font_patch import REG
from stages_pupil_names import parse_elf
BASE=ROOT/'work/output/0.1.40'
FOLDER=ROOT/'work/translation/en/skills_0.1.41'
ART=ROOT/'work/ui/skills_0.1.41'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows();prior=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf'
  data,report=patcher.prepare(old,[dict(idx[f'elf:ui:{off:08x}'],target_full=text) for off,text in {0x21dfe8:'Confirm',0x21dff0:'Back',0x21dff8:'Switch Skills'}.items()],idx)
 finally:patcher.BASELINE=prior
 assert not report['skipped'],report['skipped']
 out=bytearray(data);manifest=json.loads((BASE/'manifest.json').read_text());shortened=[]
 for e in manifest['ui_fixes027_text']['entries']:
  if e['target_text'].startswith('Pact Ritual: '):text=e['target_text'].replace('Pact Ritual: ','Pact: ')
  elif e['source_offset']==0x217484:text='Craft ［'
  else:continue
  p=_file_offset_for_va(out,int(e['new_address'],16));span=e['encoded_bytes']
  assert out[p:p+span]==e['display_text'].encode('cp932')+b'\0\0'
  raw,display=encode_dialogue(text,e['target_text']);assert len(raw)+2<=span
  out[p:p+span]=raw+bytes(span-len(raw))
  shortened.append(dict(id=e['id'],target_text=text,new_address=e['new_address'],display_text=display))
 assert len(shortened)==16
 # Scoped callers only: protagonist label, three footer hints, skill card name.
 # Existing safe Type wrapper supports <=16 U16 cells and retains the native
 # fallback for longer names. Numeric cost/level rendering stays native.
 calls=[0x145f74,0x146364,0x146398,0x1463b0,0x146fcc]
 for site in calls:
  assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbdec>>2
  assert struct.unpack_from('<I',old,site+196)[0]==0x34060001
  struct.pack_into('<I',out,site+192,3<<26|0x347b5c>>2)
 # Reserve a closing-bracket cell and wrap before a whole affinity name.
 # These five sites are exclusive to the Pact description builder.
 def emit(a):
  a.label('pact_word');a.i(9,'sp','sp',-48)
  for reg,off in [('ra',44),('a0',16),('a1',20),('a2',24)]:a.i(43,reg,'sp',off)
  a.move('a0','a2');a.jump(0x1e4ac8)
  a.i(35,'t0','sp',16);a.i(35,'t1','t0',0x14)
  a.emit(REG['t1']<<21|REG['v0']<<16|REG['t1']<<11|0x21)
  a.i(11,'t1','t1',27);a.branch(5,'t1','zero','pact_append')
  a.move('a0','t0');a.jump(0x1e51c4)
  a.label('pact_append')
  for reg,off in [('a0',16),('a1',20),('a2',24)]:a.i(35,reg,'sp',off)
  a.jump(0x1e4ee0);a.i(35,'ra','sp',44);a.i(9,'sp','sp',48);a.ret()
 # Build 0.1.40 ends with U16 data. Include its existing zero file padding
 # in the loaded segment so the next MIPS instruction is four-byte aligned.
 parsed=parse_elf(out);seg=parsed['phdrs'][3];pad=-(seg[2]+seg[4])%4
 if pad:
  end=seg[1]+seg[4];assert out[end:end+pad]==bytes(pad)
  assert end+pad<=parsed['phdrs'][2][1]
  struct.pack_into('<II',out,parsed['phoff']+3*32+16,seg[4]+pad,seg[5]+pad)
  for n,section in enumerate(parsed['sections']):
   if section[3]==seg[2] and section[4]==seg[1]:struct.pack_into('<I',out,parsed['shoff']+n*40+20,section[5]+pad)
 report['instruction_alignment_padding']=pad
 out,wr=append(bytes(out),emit,{site:('pact_word',3<<26|0x1e4ee0>>2) for site in [0x669f4,0x66a0c,0x66a24,0x66a3c,0x66a54]})
 report['pact_word_wrap']=wr
 report.update(shortened_pact_strings=shortened,vwf_calls=list(map(hex,calls)),entries=report['entries']+shortened)
 return bytes(out),report

def prepare_tables(source):
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());static=source.resource('02.DAT',3);si=parse_index(static,len(static))
 targets=json.loads((FOLDER/'targets.json').read_text())['entries'];replacements={};reports=[]
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 for n in [28,31,34]:
  table=next(t for t in index['tables'] if t['resource_path']==[3,n]);rows={r['id']:r for r in table['strings']}
  before=child(static,si,n);out=bytearray(before);changes=[];fields=set()
  selected=[x for x in targets if x['table']==n]
  if n==28:
   for rec,aff in {4:'Machine',5:'Oni',6:'Spirit',7:'Beast',8:'All'}.items():
    r=next(r for r in table['strings'] if any(f['record']==rec and f['slot']==8 for f in r['references']))
    selected.append(dict(id=r['id'],text='Pact: '+aff,source_sha256=r['source_sha256'],already_relocated=True))
  for x in selected:
   r=rows[x['id']];p=r['source_offset'];nb=r['source_byte_length'];text=x['text']
   assert sha(before[p:p+nb])==x['source_sha256']==r['source_sha256']
   raw,display=encode_dialogue(text,'');assert len(raw)//2<=16
   width=sum(metrics[c]['proposed_advance_pixels'] for c in text)*.875
   assert width<=108,(text,width)
   out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0')
   for ref in r['references']:
    assert ref['slot']==8
    f=ref['pointer_field_offset'];prev=struct.unpack_from('<I',before,f)[0]
    if x.get('already_relocated'):
     end=before.index(b'\0',prev);existing=unicodedata.normalize('NFKC',before[prev:end].decode('cp932'));assert existing.startswith('Pact Ritual: ')
    else:assert prev==p
    struct.pack_into('<I',out,f,new);fields.update(range(f,f+4))
   changes.append(dict(id=r['id'],text=text,new_offset=new,advance_pixels=width,references=r['references']))
  assert all(a==b for i,(a,b) in enumerate(zip(before,out)) if i not in fields)
  replacements[n]=bytes(out);reports.append(dict(child=n,changes=changes))
 patched=repack(static,replacements);master=source.resource('00.DAT',44);assert descend(master,[7])==static
 # Palette conversion only; generated artwork provides the English lettering.
 pack=source.resource('02.DAT',1343);before=descend(pack,[2]);rows=texture_records(before);out=before
 art=Image.open(ART/'labels_generated.png').convert('RGBA');bands=[(72,357),(417,601),(639,827),(865,1045),(1086,1270)]
 art_report=[]
 for n,((y0,y1),label) in enumerate(zip(bands,['Learn Skills','Common Skills','Common Skills','Unique Skills','Unique Skills'])):
  im=art.crop((0,y0,art.width,y1));im=im.crop(im.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox());native=decode_texture(before,rows[n]);im=im.resize(native.size,Image.Resampling.LANCZOS);matte=Image.new('RGBA',native.size,(154,80,22,255));matte.alpha_composite(im);im=matte;im.putalpha(native.getchannel('A'))
  out,decoded,_=encode_texture(out,rows[n],im);decoded.save(ART/f'label_{n}_native.png')
  art_report.append(dict(sprite=n,label=label,size=list(native.size),rgba_sha256=sha(decoded.tobytes())))
 for row in rows[5:]:assert decode_texture(before,row).tobytes()==decode_texture(out,row).tobytes()
 return {3:patched,1343:repack(pack,{2:out})},{},repack(master,{7:patched}),dict(tables=reports,units=[],graphics=art_report,stats_and_skill_costs_unchanged=True)
