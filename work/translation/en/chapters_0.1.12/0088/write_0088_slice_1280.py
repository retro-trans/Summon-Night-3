"""Write Chapter 2 rows 1280-1359 after a dry-run validation."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
OUT=Path(__file__).with_name('slice_1280.targets.json')
TEXT={1280:"For now, I'll trust you.",1281:"...All right.",1282:"I'll believe you.",1283:"Hey, come",1284:"over here.",1285:"Hm?",1286:"What is it?",1287:"...Hey, are you really",1288:"going to trust",1289:"those guys?",1290:"Is that wrong?",1291:"They're pirates,",1292:"bad people!",1293:"Yeah, but",1294:"they seem like people",1295:"you can talk to.",1296:"So I'd like",1297:"to trust them.",1298:"Yeah, but",1299:"they seem like people",1300:"you can reason with, right?",1301:"I think",1302:"we can trust them.",1303:"Tch. Don't blame me",1304:"whatever happens...",1305:"Um, over here,",1306:"please...",1307:"Hm?",1308:"What is it?",1309:"Are you really going",1310:"to trust them?",1311:"Is that wrong?",1312:"I'm against it.",1313:"They're pirates, you know?",1314:"Yeah, but",1315:"they seem like people",1316:"you can talk to.",1317:"So I'd like",1318:"to trust them.",1319:"Yeah, but",1320:"they seem like people",1321:"you can reason with, right?",1322:"I think",1323:"we can trust them.",1324:"...I hope so.",1325:"Hey,",1326:"come over here.",1327:"Hm?",1328:"What is it?",1329:"You...",1330:"Are you really sure?",1331:"Is that wrong?",1332:"Of course it is!?",1333:"They're pirates!",1334:"Yeah, but",1335:"they seem like people",1336:"you can talk to.",1337:"So I'd like",1338:"to trust them.",1339:"Yeah, but",1340:"they seem like people",1341:"you can reason with, right?",1342:"I think",1343:"we can trust them.",1344:"Honestly...",1345:"I don't care, then.",1346:"Teacher...",1347:"May I ask something?",1348:"Hm?",1349:"What is it?",1350:"Um...",1351:"Will it really be okay?",1352:"Is that wrong?",1353:"That's not it!?",1354:"But...",1355:"Yeah, but",1356:"they seem like people",1357:"you can talk to.",1358:"So I'd like",1359:"to trust them."}
def build():
 r,rows,data=chapter_source(88);assert set(TEXT)==set(range(1280,1360));ts={}
 for n in range(1280,1360):
  x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');encode_dialogue(TEXT[n],s);ts[x['id']]={'id':x['id'],'source_sha256':x['source_sha256'],'source_offset':x['source_offset'],'source_byte_length':x['source_byte_length'],'reference_instructions':x['reference_instructions'],'resource_row':n,'text':TEXT[n],'status':'draft','notes':'No source control tokens.'}
 return {'resource_id':r['id'],'assigned_range':[1280,1359],'rows_examined':{'ranges_inclusive':[[1260,1379]],'count':120},'translations':ts,'uncertainties':[],'new_glossary_requests':[]}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','translation_count':len(d['translations']),'sample':[(n,next(v['text'] for v in d['translations'].values() if v['resource_row']==n)) for n in (1280,1309,1332,1346,1359)]},ensure_ascii=False,indent=2));
 if a.write:OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
