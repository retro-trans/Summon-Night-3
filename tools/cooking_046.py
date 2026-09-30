"""Cooking catalog, native book labels, and scoped proportional text on 0.1.45."""
import json,struct,hashlib
from PIL import Image
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from font_metrics import collect
from font_patch import REG
from menu_code_020 import append
from stages_pupil_names import parse_elf
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import descend,replace_tree
import battle_elf_patch as patcher
BASE=ROOT/'work/output/0.1.45'
FOLDER=ROOT/'work/translation/en/cooking_0.1.46'
ART=ROOT/'work/ui/cooking_0.1.46'
sha=lambda b:hashlib.sha256(b).hexdigest()
ELF_TEXT={0x218c6c:'Not enough ingredients.',0x218c88:'Cannot make any more.',0x21c8e8:'OK',0x21c8f0:'Cook',0x21c8f8:'Materials',0x21c904:'Task',0x21c910:'How many?',0x21c924:'Servings'}
VWF_SITES=[0x11ef74,0x11ef9c,0x11eff8,0x11f044,0x1227a0,0x122c24,0x1231a8,0x123254,0x1232f4]

def emit_position(a):
 def r(fn,rd,rs,rt='zero'):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
 def sh(rd,rt,n):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6)
 a.label('recipe_position');a.i(9,'sp','sp',-80)
 saves=[('ra',76),('a0',64),('a2',68),('s0',32),('s1',36),('s2',40),('s3',44),('s4',48),('s5',52)]
 for reg,off in saves:a.i(43,reg,'sp',off)
 # Native s0 owner, s4 row*13, s3 column, s2 row. Preserve 4 icon-padding cells.
 a.i(9,'s5','zero',0);a.i(11,'t0','s2',3);a.branch(4,'t0','zero','no_pad');a.i(9,'s5','zero',4)
 a.label('no_pad');sh('t0','s4',1);r(0x21,'s0','s0','t0');a.i(9,'s0','s0',0x4770)
 a.move('s1','s3');a.move('s2','zero');a.move('s4','zero')
 a.label('loop');a.branch(4,'s1','zero','current')
 a.i(37,'a0','s0',0);a.i(9,'t3','zero',0x4081);a.branch(5,'a0','t3','metric')
 a.branch(4,'s5','zero','metric');a.i(9,'s5','s5',-1);a.i(9,'t3','zero',112);a.branch(4,'zero','zero','sum')
 a.label('metric');a.move('s5','zero');a.jump(0x32e380)
 a.i(9,'t3','zero',16);a.branch(4,'a0','t3','fallback');sh('t3','v0',3);r(0x23,'t3','t3','v0');a.branch(4,'zero','zero','sum')
 a.label('fallback');a.i(9,'t3','zero',112)
 a.label('sum');r(0x21,'s2','s2','t3');a.i(9,'s0','s0',2);a.i(9,'s1','s1',-1);a.branch(4,'zero','zero','loop')
 a.label('current');a.i(37,'a0','s0',0);a.jump(0x32e380);a.i(9,'t3','zero',16);a.branch(4,'a0','t3','adjust')
 a.i(9,'t3','zero',3);r(0x23,'t3','t3','v1');sh('t4','t3',3);r(0x23,'t3','t4','t3');r(0x21,'s2','s2','t3')
 a.label('adjust');sh('t3','s3',7);sh('t4','s3',4);r(0x23,'t3','t3','t4');r(0x23,'s2','s2','t3')
 a.int_to_float('s2',4);a.i(15,'t3','zero',0x3e00);a.emit(17<<26|4<<21|REG['t3']<<16|2<<11);a.emit(17<<26|16<<21|2<<16|4<<11|4<<6|2);a.add_float(12,12,4)
 a.i(35,'a0','sp',64);a.i(35,'t9','sp',68);a.emit(REG['t9']<<21|REG['ra']<<11|9);a.emit(0)
 for reg,off in saves:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',80);a.ret()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows();previous=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf';data,report=patcher.prepare(old,[dict(idx[f'elf:ui:{o:08x}'],target_full=t) for o,t in ELF_TEXT.items()],idx)
 finally:patcher.BASELINE=previous
 assert not report['skipped'],report['skipped']
 out=bytearray(data)
 for off,text in [(0x218c34,'Party Skills'),(0x218c4e,'provide this'),(0x21c92c,'Make these?'),(0x21c944,'Yes'),(0x21c94c,'No')]:
  row=idx[f'elf:ui:{off:08x}'];n=row['source_byte_length'];assert sha(old[off:off+n])==row['source_sha256'];raw,_=encode_dialogue(text,'');assert len(raw)<=n
  out[off:off+n]=raw+bytes(n-len(raw));report['entries'].append(dict(id=row['id'],target_text=text,mode='in_place'))
 rel=parse_elf(old)['phdrs'][2];rels=list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]))
 for site in VWF_SITES:
  assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbdec>>2 and (site,4) in rels
  struct.pack_into('<I',out,site+192,3<<26|0x347b5c>>2)
 # Position hook preserves the existing delay-slot row Y calculation.
 out,helper=append(bytes(out),emit_position,{0x121f20:('recipe_position',REG['a2']<<21|REG['ra']<<11|9)})
 report.update(vwf_calls=[hex(p) for p in VWF_SITES],recipe_position=helper,native_recipe_pool=78,native_rows=6,native_columns=13)
 return out,report

def prepare_art(source):
 orig=source.resource('02.DAT',3566);before=descend(orig,[3]);out=before;rr=texture_records(before);im=Image.open(ART/'ingredients_generated.png').convert('RGBA');bar=im.crop((1004,542,1544,603));reports=[]
 for number in [0,1,8]:
  old=decode_texture(before,rr[number]);art=old.copy()
  if number==0:art=Image.open(ROOT/'work/ui/system_0.1.44/native/cooking_0.png').convert('RGBA')
  elif number==1:art.paste(bar.resize((148,16),Image.Resampling.LANCZOS),(276,148))
  else:art=bar.resize(old.size,Image.Resampling.LANCZOS)
  art.putalpha(old.getchannel('A'));out,decoded,_=encode_texture(out,rr[number],art);assert len(out)==len(before)
  assert decoded.getchannel('A').tobytes()==old.getchannel('A').tobytes()
  if number==1:
   a=old.copy();b=decoded.copy();a.paste((0,0,0,0),(276,148,424,164));b.paste((0,0,0,0),(276,148,424,164));assert a.tobytes()==b.tobytes()
  (ART/'native').mkdir(exist_ok=True);decoded.save(ART/'native'/f'texture_{number}.png');reports.append(dict(texture=number,size=old.size))
 catalog=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());group=next(g for g in catalog['resources'] if g['source_sha256']==sha(before));targets={}
 for o in group['occurrences']:
  assert o['bank']=='02.DAT';p=tuple(o['path']);assert descend(source.resource('02.DAT',p[0]),p[1:])==before;targets[p]=out
 packs={n:replace_tree(source.resource('02.DAT',n),{p[1:]:v for p,v in targets.items() if p[0]==n}) for n in {p[0] for p in targets}}
 return packs,dict(textures=reports,copies=len(targets))

def prepare_tables(source):
 targets=json.loads((FOLDER/'targets.json').read_text())['entries'];index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());static=source.resource('02.DAT',3);si=parse_index(static,len(static));patches={};reports=[]
 for n in sorted({e['table'] for e in targets}):
  t=next(t for t in index['tables'] if t['resource_path']==[3,n]);rows={r['id']:r for r in t['strings']};before=child(static,si,n);out=bytearray(before);fields=set();changes=[]
  for e in [e for e in targets if e['table']==n]:
   r=rows[e['id']];p=r['source_offset'];nb=r['source_byte_length'];assert sha(before[p:p+nb])==e['source_sha256']==r['source_sha256']
   payload=b''.join(encode_dialogue(s,'')[0]+b'\0\0' for s in e['lines'])+b'\0\0';out.extend(bytes(-len(out)%2));pos=len(out);out.extend(payload)
   for ref in r['references']:
    f=ref['pointer_field_offset'];struct.pack_into('<I',out,f,pos);fields.update(range(f,f+4))
   changes.append(dict(e,new_offset=pos,references=r['references']))
  assert all(a==b or i in fields for i,(a,b) in enumerate(zip(before,out)));patches[n]=bytes(out);reports.append(dict(child=n,changes=changes))
 patched=repack(static,patches);master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 packs,art=prepare_art(source)
 return {3:patched,**packs},{},repack(master,{7:patched}),dict(units=[],tables=reports,art=art,gameplay_fields_unchanged=True)

def verify(elf,static):
 from verify_cooking_046 import verify
 return verify(elf,static)
if __name__=='__main__':
 elf,r=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as source:tables,_,_,tr=prepare_tables(source)
 print(json.dumps(dict(text=r,tables=tr),indent=2))
