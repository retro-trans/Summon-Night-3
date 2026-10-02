"""Scoped fixes for spell banners, Yard, map labels and indirect attacks.

Pure preparation by default; historical builds are never modified.
"""
import argparse,json,struct,hashlib,unicodedata
import numpy as np
from PIL import Image
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_codec import decompress,compress
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from font_patch import REG
from stages_pupil_names import parse_elf,validate_loader_structure
from spell_name_059 import label
BASE=ROOT/'work/output/0.1.60'
ART=ROOT/'work/ui/report_0.1.61'
TEXT=ROOT/'work/translation/en/report_0.1.61/strings.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def add(a,rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x21)

def emit_banner(a,count):
 # Exact bounded content matching; other widgets and custom names are unchanged.
 a.label('match');a.branch(4,'a0','zero','not_match');a.table_address('t0')
 a.i(35,'t1','t0',0);a.i(9,'t2','t0',4)
 a.label('candidate');a.branch(4,'t1','zero','not_match')
 a.i(35,'t3','t2',0);add(a,'t3','t0','t3');a.i(35,'v1','t2',4)
 a.move('t4','a0');a.move('t5','v1')
 a.label('compare');a.i(37,'t6','t3',0);a.i(37,'t7','t4',0)
 a.branch(5,'t6','t7','next');a.branch(4,'t6','zero','matched')
 a.branch(4,'t5','zero','next');a.i(9,'t5','t5',-1)
 a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.branch(4,'zero','zero','compare')
 a.label('next');a.i(9,'t2','t2',8);a.i(9,'t1','t1',-1);a.branch(4,'zero','zero','candidate')
 a.label('matched');a.move('v0','v1');a.ret()
 a.label('not_match');a.move('v0','zero');a.ret()

 a.label('draw');a.i(9,'sp','sp',-80)
 for r,o in [('ra',76),('s0',64),('s1',68),('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(43,r,'sp',o)
 a.move('s0','a0');a.move('s1','zero')
 a.branch(4,'s0','zero','native_draw')
 a.i(35,'t0','s0',0x34);a.branch(4,'t0','zero','native_draw')
 a.i(43,'t0','sp',48);a.i(36,'t0','s0',0x64);a.i(43,'t0','sp',52)
 a.i(35,'t0','s0',0x3c);a.i(9,'t1','zero',1);a.branch(5,'t0','t1','native_draw')
 a.i(35,'t0','s0',0x20);a.branch(5,'t0','zero','native_draw')
 a.i(35,'t0','s0',0x50);a.branch(4,'t0','zero','native_draw')
 a.i(35,'t0','s0',0x4c);a.branch(4,'t0','zero','native_draw')
 a.i(35,'t0','s0',0x30);a.branch(4,'t0','zero','native_draw')
 a.i(35,'a0','t0',0);a.jump('match');a.branch(4,'v0','zero','native_draw')
 # One existing 224-byte font object now binds the complete <=32-cell strip.
 # No extra glyph object, row array or source-buffer allocation is needed.
 a.i(43,'zero','s0',0x34);a.i(9,'t0','zero',-1);a.i(40,'t0','s0',0x64);a.i(9,'s1','zero',1)
 # Rebind after switching modes, even if the owner had a clean old glyph cache.
 a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x400);a.i(43,'t0','s0',0)
 a.label('native_draw')
 for r,o in [('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(35,r,'sp',o)
 a.jump('native_prologue')
 a.branch(4,'s1','zero','draw_return');a.i(35,'t0','sp',48);a.i(43,'t0','s0',0x34)
 a.i(35,'t0','sp',52);a.i(40,'t0','s0',0x64)
 a.label('draw_return')
 for r,o in [('s0',64),('s1',68),('ra',76)]:a.i(35,r,'sp',o)
 a.i(9,'sp','sp',80);a.ret()
 a.label('native_prologue');a.i(9,'sp','sp',-272);a.i(43,'s6','sp',252);a.jump(0x1b100,link=False)

 a.label('bind');a.i(9,'sp','sp',-48)
 for r,o in [('ra',44),('a0',16),('a1',20),('a2',24)]:a.i(43,r,'sp',o)
 a.move('a0','a1');a.jump('match');a.i(43,'v0','sp',28)
 for r,o in [('a0',16),('a1',20),('a2',24),('ra',44)]:a.i(35,r,'sp',o)
 a.i(35,'t0','sp',28);a.i(9,'sp','sp',48);a.branch(4,'t0','zero','original_bind')
 a.jump(0x348a7c,link=False)
 a.label('original_bind');a.jump(0x34a0c8,link=False)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();spec=json.loads(TEXT.read_text(encoding='utf8'))
 names=spec['banner_names'];payload=bytearray(4+8*len(names));struct.pack_into('<I',payload,0,len(names))
 for i,name in enumerate(names):
  encoded,_=encode_dialogue(name,'');assert 0<len(encoded)//2<=32
  struct.pack_into('<II',payload,4+8*i,len(payload),len(encoded)//2);payload.extend(encoded+b'\0\0')
 payload.extend(bytes(-len(payload)%4));shore_offset=len(payload)
 payload.extend(encode_dialogue(spec['shore']['english'],spec['shore']['source'])[0]+b'\0\0');payload.extend(bytes(-len(payload)%4))
 expected={0x1b0f8:0x27bdfef0,0x1b0fc:0xafb600fc,0x1b390:3<<26|0x34a0c8>>2}
 for va,w in expected.items():assert struct.unpack_from('<I',old,va+192)[0]==w,(hex(va),hex(w))
 patched,r=append(old,lambda a:emit_banner(a,len(names)),{0x1b0f8:('draw',expected[0x1b0f8]),0x1b390:('bind',expected[0x1b390])},bytes(payload))
 out=bytearray(patched);entry=int(r['code_address'],16)+r['labels']['draw']
 struct.pack_into('<I',out,0x1b0f8+192,2<<26|entry>>2);struct.pack_into('<I',out,0x1b0fc+192,0)
 table=int(r['code_address'],16)+r['labels']['table'];new=table+shore_offset
 assert old[0x21cf88+192:0x21cf88+192+14]=='はじまりの浜辺'.encode('cp932')
 assert struct.unpack_from('<I',old,0x22952c+192)[0]==0x21cf88
 rel=parse_elf(old)['phdrs'][2];records=list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]));assert (0x22952c,2) in records
 struct.pack_into('<I',out,0x22952c+192,new)
 allowed={i for va in (0x1b0f8,0x1b0fc,0x22952c) for i in range(va+192,va+196)}
 assert all(i in allowed for i,(x,y) in enumerate(zip(patched,out)) if x!=y)
 r.update(profile='exact_spell_banner_vwf',source_sha256=sha(old),output_sha256=sha(out),max_cells=32,
  names=names,shore=dict(**spec['shore'],pointer_field='0x22952c',new_address=hex(new)),structure=validate_loader_structure(out))
 return bytes(out),r

def prior_audit_view(elf):
 expected,_=prepare_elf();assert elf==expected,'Unexpected 0.1.61 executable changes'
 return (BASE/'EBOOT.elf').read_bytes()

def imported_word(filename,w,h,iw,ih,y):
 im=Image.open(ART/filename).convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
 box=im.getchannel('A').point(lambda v:255 if v>=12 else 0).getbbox();assert box
 cut=im.crop(box);scale=min(iw/cut.width,ih/cut.height);size=(round(cut.width*scale),round(cut.height*scale))
 out=Image.new('RGBA',(w,h));out.alpha_composite(cut.resize(size,Image.Resampling.LANCZOS),((w-size[0])//2,y));return out

def prepare_names(source,write_assets=False):
 replacements={};reports=[]
 for n,key,cs,dim in [(917,0x1731,[3,4],(144,32,112,20,6)),(1101,0x9831,[1,2],(88,24,76,16,3))]:
  raw=source.resource('02.DAT',n);d,u=decompress(raw,key);assert not any(raw[u:]);ix=parse_index(d,len(d));changes={};layers=[]
  art=imported_word('yard_generated.png',*dim)
  for li,c in enumerate(cs):
   b=child(d,ix,c);rows=texture_records(b);assert len(rows)==1;row=rows[0];assert (row['width'],row['height'])==art.size;wanted=art
   if li:
    px=np.asarray(decode_texture(b,row));colors,counts=np.unique(px[px[:,:,3]>200,:3],axis=0,return_counts=True)
    color=tuple(int(v) for v in colors[counts.argmax()]);wanted=Image.new('RGBA',art.size,color+(0,));wanted.putalpha(art.getchannel('A'))
   out,native,changed=encode_texture(b,row,wanted)
   assert out[:row['data_offset']]==b[:row['data_offset']] and out[row['data_offset']+row['data_size']:]==b[row['data_offset']+row['data_size']:]
   changes[c]=out;layers.append(dict(child=c,changed_pixels=changed,ink_bounds=native.getbbox(),source_sha256=sha(b),output_sha256=sha(out)))
   if write_assets:native.save(ART/f'yard_{n}_{c}_native.png')
  result=repack(d,changes);ni=parse_index(result,len(result));assert all(child(result,ni,e['id'])==changes.get(e['id'],child(d,ix,e['id'])) for e in ix['entries'])
  packed=compress(result,key);assert decompress(packed,key)[0]==result;replacements[n]=packed
  reports.append(dict(resource=n,target='Yard',layers=layers,source_sha256=sha(raw),output_sha256=sha(packed)))
 # Backlog copies use the same current short-name reference.
 for n in (85,86,87):
  raw=source.resource('02.DAT',n);d,u=decompress(raw,0x9831);assert not any(raw[u:]);ix=parse_index(d,len(d));b=child(d,ix,22);out=bytearray(b);changes=[]
  count=struct.unpack_from('<I',b)[0];assert count==255;already=0
  for field in range(4,4+count*8,4):
   ptr=struct.unpack_from('<I',b,field)[0]
   if not ptr:continue
   end=ptr
   while b[end:end+2]!=b'\0\0':end+=2;assert end<len(b)
   text=b[ptr:end].decode('cp932')
   if unicodedata.normalize('NFKC',text)=='Yard':already+=1
   if text!='ヤード':continue
   at=len(out);out.extend(encode_dialogue('Yard','ヤード')[0]+b'\0\0');struct.pack_into('<I',out,field,at);changes.append(field)
  assert changes or already
  if changes:
   result=repack(d,{22:bytes(out)});ni=parse_index(result,len(result));assert all(child(result,ni,e['id'])==child(d,ix,e['id']) for e in ix['entries'] if e['id']!=22)
   packed=compress(result,0x9831);assert decompress(packed,0x9831)[0]==result;replacements[n]=packed
  reports.append(dict(resource=n,target='Yard',backlog_fields=changes,already_translated=already))
 # Both map packages share this exact six-sprite child. Only sprite 1 changes.
 for n in (35,36):
  raw=source.resource('02.DAT',n);ix=parse_index(raw,len(raw));b=child(raw,ix,33);assert sha(b)=='7964a6ebe18df085d544fa8a2153f0f3c04dde23bfe4b00681380c04a03c7bef'
  rows=texture_records(b);assert len(rows)==6;row=rows[1];assert row['number']==1
  art=imported_word('map_generated.png',144,24,132,20,2);out,native,changed=encode_texture(b,row,art)
  assert out[:row['data_offset']]==b[:row['data_offset']] and out[row['data_offset']+row['data_size']:]==b[row['data_offset']+row['data_size']:]
  for t in rows:
   if t['number']!=1:assert np.array_equal(np.asarray(decode_texture(b,t)),np.asarray(decode_texture(out,t)))
  replacements[n]=repack(raw,{33:out});reports.append(dict(resource=n,child=33,sprite=1,target='Island Map',changed_pixels=changed))
  if write_assets:native.save(ART/f'map_{n}_native.png')
 # Append, never overwrite, all five related indirect-attack names/help blocks.
 st=source.resource('02.DAT',3);ix=parse_index(st,len(st));b=child(st,ix,25);assert struct.unpack_from('<I',b)[0]==430;out=bytearray(b);changes=[]
 spec=json.loads(TEXT.read_text(encoding='utf8'))
 for entry in spec['attacks']:
  rec=entry['record'];assert label(b,4+rec*48+32)=='間接攻撃'
  for slot,lines in [(8,[entry['english']]),(9,entry['help'])]:
   field=4+rec*48+slot*4;at=len(out);encoded=b''.join(encode_dialogue(t,'')[0]+b'\0\0' for t in lines)+(b'\0\0' if slot==9 else b'')
   assert max(map(len,lines))<=27 and sum(map(len,lines))<=54
   out.extend(encoded);struct.pack_into('<I',out,field,at);changes.append(dict(record=rec,slot=slot,field=field,offset=at,lines=lines))
 allowed={p for e in changes for p in range(e['field'],e['field']+4)}
 assert all(i in allowed for i,(x,y) in enumerate(zip(b,out)) if x!=y)
 after=repack(st,{25:bytes(out)});ni=parse_index(after,len(after));assert all(child(after,ni,e['id'])==child(st,ix,e['id']) for e in ix['entries'] if e['id']!=25)
 replacements[3]=after;reports.append(dict(resource=3,child=25,changes=changes,original_pool_preserved=True))
 return replacements,reports

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write-previews',action='store_true');a=p.parse_args();elf,r=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.60.iso') as s:packs,art=prepare_names(s,a.write_previews)
 print(json.dumps(dict(mode='write previews' if a.write_previews else 'preview',elf={k:v for k,v in r.items() if k not in ('extra_relocation_records','new_relocations')},resources=sorted(packs),art=art),indent=2),flush=True)
 if a.write_previews:(ART/'import-validation.json').write_text(json.dumps(dict(elf=r,art=art),indent=2)+'\n')
