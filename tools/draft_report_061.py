"""Preview the small reported UI translation scope before writing it."""
import argparse,json
from sn3_archive import ROOT,GameSource,parse_index,child
from spell_name_059 import label
from report_ui_061 import BASE,TEXT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.60.iso') as s:
  raw=s.resource('02.DAT',3);b=child(raw,parse_index(raw,len(raw)),13)
  names=sorted({label(b,4+n*40+32) for n in range(237) if label(b,4+n*40+32).isascii() and 0<len(label(b,4+n*40+32))<=32})
 assert 'Zip Toast' in names
 spec=dict(version='0.1.61',source_build='0.1.60',banner_names=names,
  zip_toast=dict(source='ジップトースト',english='Zip Toast',reference='https://w.atwiki.jp/sn3psp/pages/99.html',reason='Last character clipped by display limit; existing translation is correct.'),
  yard=dict(source='ヤード',english='Yard',reference='work/glossary/character_reference_sn6_vita.json',ordinary_pack=917,battle_pack=1101),
  map_heading=dict(source='島全景',english='Island Map'),shore=dict(source='はじまりの浜辺',full_translation='Shore of Beginnings',english='First Shore',note='Compact map location label; source literal remains intact.'),
  attacks=[dict(record=422+i,source='間接攻撃',english='Indirect Atk',help=['Range: Adj Up2 Dn2 '+element],element=element) for i,element in enumerate(['Machine','Yokai','Spirit','Beast','Neutral'])])
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(TEXT),spec=spec),ensure_ascii=False,indent=2),flush=True)
 if a.write:TEXT.parent.mkdir(parents=True,exist_ok=True);TEXT.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
