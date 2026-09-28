"""Write Chapter 2 rows 1200-1279 after a dry-run validation."""
import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / 'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
OUT=Path(__file__).with_name('slice_1200.targets.json')
TEXT={
1200:"wouldn't they?",1201:"!?",1202:"Huh...",1203:"You look so cute,",1204:"but you've got a sharp tongue.",1205:"Haha♪ Hey, Sonolar.",1206:"I think",1207:"I like this person.",1208:"What!?",1209:"Hey, Teach.",1210:"Why don't you come",1211:"aboard our ship?",1212:"What?",1213:"A ship!?",1214:"You have a ship!?",1215:"A ship!?",1216:"You",1217:"have a ship!?",1218:"If we fix the damaged parts,",1219:"we can sail just fine.",1220:"Food and water,",1221:"we'll even provide",1222:"beds.",1223:"If you help with repairs,",1224:"we'll give you a ride",1225:"to the nearest port.",1226:"Well?",1227:"What should I do...?",1228:"　Accept the offer",1229:"　Can't trust them",1230:"All right.",1231:"We'll take you up on that.",1232:"All right.",1233:"We'll take",1234:"you up on that.",1235:"!?",1236:"!?",1237:"!?",1238:"!?",1239:"H-Hey, Scarrel!?",1240:"You can't just...",1241:"It's fine, it's fine.",1242:"I'm sure Kyle will like",1243:"this one, too. And...",1244:"With love,",1245:"anything is forgiven.",1246:"N-No...",1247:"This is...",1248:"...",1249:"...",1250:"...",1251:"...",1252:"Well then,",1253:"I have to introduce you",1254:"to everyone.",1255:"Follow me.",1256:"I can't trust them",1257:"that easily.",1258:"But...",1259:"Trusting them too easily",1260:"could be dangerous.",1261:"But...",1262:"...",1263:"...",1264:"...",1265:"...",1266:"Thinking of this child,",1267:"we can't keep",1268:"sleeping outdoors forever.",1269:"Thinking of this child,",1270:"we can't keep",1271:"sleeping outdoors forever.",1272:"If you can't trust us,",1273:"that's fine, but...",1274:"The pirate Kyle family",1275:"doesn't pull",1276:"cheap tricks like ambushes!",1277:"!",1278:"...",1279:"...All right."
}
def build():
 resource,rows,data=chapter_source(88);assert set(TEXT)==set(range(1200,1280));translations={}
 for n in range(1200,1280):
  row=rows[n];source=data[row['source_offset']:row['source_offset']+row['source_byte_length']].decode('cp932');text=TEXT[n];assert text,n;encode_dialogue(text,source)
  translations[row['id']]={'id':row['id'],'source_sha256':row['source_sha256'],'source_offset':row['source_offset'],'source_byte_length':row['source_byte_length'],'reference_instructions':row['reference_instructions'],'resource_row':n,'text':text,'status':'draft','notes':'Preserves runtime token(s).' if any(t in source for t in '▲♪') else 'No source control tokens.'}
 return {'resource_id':resource['id'],'assigned_range':[1200,1279],'rows_examined':{'ranges_inclusive':[[1180,1299]],'count':120},'translations':translations,'uncertainties':[],'new_glossary_requests':[]}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','translation_count':len(d['translations']),'sample':[(n,next(v['text'] for v in d['translations'].values() if v['resource_row']==n)) for n in (1200,1205,1228,1239,1276)]},ensure_ascii=False,indent=2));
 if a.write:OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
