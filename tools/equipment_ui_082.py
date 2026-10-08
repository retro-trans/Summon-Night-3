"""Keep composed equipment captions out of native ten-cell row buffers."""
import hashlib,json,struct
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va as off

BASE=ROOT/'work/output/0.1.81'
TARGET=ROOT/'work/translation/en/ui_0.1.82/equipment.json'
SITES={0x193fa0:'equipment_list',0x196110:'equipment_status'}

def encoded(text):return (encode_dialogue(text,'')[0] if text else b'')+bytes(2)

def captions():
 t=json.loads(TARGET.read_text('utf8'));rows=[]
 for mode in range(len(t['attack_modes'])):
  for weapon,name in enumerate(t['weapons']):
   attack=t['attack_modes'][8 if mode==1 and weapon==8 else 9 if mode==2 and weapon==8 else mode]
   text='' if mode==7 else attack+'×'+name
   assert len(text)<=16
   rows.append(text)
 return rows

def emit(a):
 for name,register in [('equipment_list','s0'),('equipment_status','s1')]:
  a.label(name);a.i(9,'sp','sp',-16);a.i(43,'ra','sp',12)
  a.jump('caption');a.move(register,'v0');a.i(35,'ra','sp',12);a.i(9,'sp','sp',16);a.ret()
 a.label('caption');a.table_address('v0')
 a.i(11,'t0','a1',10);a.branch(4,'t0','zero','empty')
 a.i(11,'t0','a2',15);a.branch(4,'t0','zero','empty')
 # Index = attack * 15 + weapon. Table contains relative string offsets.
 a.emit(REG['a1']<<16|REG['t0']<<11|4<<6)
 a.emit(REG['t0']<<21|REG['a1']<<16|REG['t0']<<11|0x23)
 a.emit(REG['t0']<<21|REG['a2']<<16|REG['t0']<<11|0x21)
 a.emit(REG['t0']<<16|REG['t0']<<11|2<<6)
 a.emit(REG['v0']<<21|REG['t0']<<16|REG['t0']<<11|0x21)
 a.i(35,'t0','t0',0);a.emit(REG['v0']<<21|REG['t0']<<16|REG['v0']<<11|0x21);a.ret()
 a.label('empty');a.i(9,'v0','v0',600);a.ret()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();rows=captions();payload=bytearray(bytes(602));offsets=[]
 for text in rows:
  offsets.append(len(payload));payload.extend(encoded(text))
 for i,o in enumerate(offsets):struct.pack_into('<I',payload,i*4,o)
 payload.extend(bytes(-len(payload)%4))
 hooks={p:(n,3<<26|0x67a4c>>2) for p,n in SITES.items()}
 elf,r=append(old,emit,hooks,bytes(payload))
 for p in SITES:assert elf[off(elf,p+4):off(elf,p+8)]==old[off(old,p+4):off(old,p+8)]
 r.update(version='0.1.82',baseline_sha256=hashlib.sha256(old).hexdigest(),output_sha256=hashlib.sha256(elf).hexdigest(),caption_count=len(rows),max_caption_cells=max(map(len,rows)),scope='Separate immutable captions for both equipment-type consumers; preserve native weapon IDs, attack modes, icons, armor labels and saved names.')
 return elf,r
