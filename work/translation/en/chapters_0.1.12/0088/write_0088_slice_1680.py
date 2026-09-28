import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
OUT=Path(__file__).with_name('slice_1680.targets.json')
TEXT={1680:"it'll be better there.",1681:"What?",1682:"A ship!?",1683:"You have a ship!?",1684:"A ship!?",1685:"You",1686:"have a ship!?",1687:"Sure.",1688:"It's broken now,",1689:"but not beyond repair.",1690:"We have food and water",1691:"enough for a while,",1692:"stored up.",1693:"If you help with repairs,",1694:"as thanks, we'll take you",1695:"to the nearest port.",1696:"......",1697:"Considering who we are,",1698:"it's only natural you",1699:"wouldn't trust us.",1700:"But even so,",1701:"could you perhaps",1702:"trust us?",1703:"...All right.",1704:"For now, I'll trust you.",1705:"All right.",1706:"For now, I'll believe you.",1707:"Wait a moment!",1708:"Before the complicated talk,",1709:"we should thank our guests first.",1710:"Yes, you're right!"}
def build():
 r,rows,data=chapter_source(88);assert set(TEXT)==set(range(1680,1711));ts={}
 for n in TEXT:
  x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');encode_dialogue(TEXT[n],s);ts[x['id']]={'id':x['id'],'source_sha256':x['source_sha256'],'source_offset':x['source_offset'],'source_byte_length':x['source_byte_length'],'reference_instructions':x['reference_instructions'],'resource_row':n,'text':TEXT[n],'status':'draft','notes':'No source control tokens.'}
 return {'resource_id':r['id'],'assigned_range':[1680,1710],'rows_examined':{'ranges_inclusive':[[1660,1710]],'count':51},'translations':ts,'uncertainties':[],'new_glossary_requests':[]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','count':len(d['translations'])}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
