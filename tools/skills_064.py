"""Scoped Learn Skills table translations on immutable local 0.1.63."""
import hashlib,json,struct,unicodedata
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
BASE=ROOT/'work/output/0.1.63'
TEXT=ROOT/'work/translation/en/skills_0.1.64/strings.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def draft():
 return dict(version='0.1.64',source_build='0.1.63',skills=[
  dict(table=28,record=70,name=['ダッシュ!','Dash!'],
   help_source=['なだらかな地形での直線移動歩数が上昇(上下1段差まで)','移動歩数:5'],
   help=['Move 5 straight; gentle','terrain: up/down 1'],
   master_source=['マスター効果:上下2段差まで'],master=['Master: +/-2']),
  dict(table=31,record=177,name=['闘気','Fighting Spirit'],
   help_source=['ZOC形成:小','石化、マヒ、魅了、眠り状態時は無効'],
   help=['ZOC:S; off if Petrif/Para/','Charm/Sleep'],
   master_source=['マスター効果:最大Α 15'],master=['Master: max Α 15']),
  dict(table=31,record=190,name=['ド根性','Guts'],
   help_source=['瀕死によるペナルティがスキルLv×4%軽減される'],
   help=['Near-death penalty -4%/Lv.'],
   master_source=['マスター効果:最大Α 15'],master=['Master: max Α 15']),
  dict(table=31,record=294,name=['アイテムスロー','Item Throw'],
   help_source=['道具使用距離がスキルLv分伸びる'],help=['Item range +skill level.'],
   master_source=['マスター効果:狙い撃ち効果付加'],master=['Master: adds Sharpshoot.'])],
  meaning_review='skills064_review: preserve gentle terrain, near-death penalty, and effect names; source glyph Α retained without guessing its meaning.',
  costs_levels_effects_unchanged=True)

def prepare_elf():
 b=(BASE/'EBOOT.elf').read_bytes()
 return b,dict(source_sha256=sha(b),output_sha256=sha(b),executable_unchanged=True)

def prepare_names(source,write_assets=False):
 spec=json.loads(TEXT.read_text(encoding='utf8'));static=source.resource('02.DAT',3);ix=parse_index(static,len(static));changed={};reports=[]
 norm=lambda s:' '.join(unicodedata.normalize('NFKC',s).split())
 for n in sorted({r['table'] for r in spec['skills']}):
  old=child(static,ix,n);out=bytearray(old);allowed=set();entries=[]
  for r in [x for x in spec['skills'] if x['table']==n]:
   combined=r['help']+r['master'];assert len(combined)<=3 and max(map(len,combined))<=27 and sum(map(len,combined))<=54
   for slot,wanted,english in [(8,[r['name'][0]],[r['name'][1]]),(9,r['help_source'],r['help']),(10,r['master_source'],r['master'])]:
    field=4+r['record']*48+slot*4;ptr=struct.unpack_from('<I',old,field)[0];actual=[b.decode('cp932') for b in lines_at(old,ptr)[0]]
    if slot==8:actual=actual[:1];assert len(english[0])<=16
    assert list(map(norm,actual))==list(map(norm,wanted)),(n,r['record'],slot,actual,wanted)
    assert sum(s.count('Α') for s in wanted)==sum(s.count('Α') for s in english)
    raw=[encode_dialogue(s,'')[0] for s in english];out.extend(bytes(-len(out)%2));new=len(out)
    out.extend(b''.join(b+b'\0\0' for b in raw)+b'\0\0');struct.pack_into('<I',out,field,new);allowed.update(range(field,field+4))
    assert lines_at(out,new)[0]==raw
    entries.append(dict(record=r['record'],slot=slot,before=list(map(norm,actual)),english=english,pointer_field=field,offset=new))
  out.extend(bytes(-len(out)%ix['unit_bytes']));assert all(i in allowed for i,(a,b) in enumerate(zip(old,out)) if a!=b)
  changed[n]=bytes(out);reports.append(dict(table=n,entries=entries,original_pool_preserved=True,non_text_fields_unchanged=True))
 patched=repack(static,changed);ni=parse_index(patched,len(patched));assert all(child(patched,ni,e['id'])==changed.get(e['id'],child(static,ix,e['id'])) for e in ix['entries'])
 return {3:patched},reports
