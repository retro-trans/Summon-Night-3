"""Draft exact Chapter 6 main-tail rows 160--239; preview before writing."""
raise SystemExit('OBSOLETE: this draft has positional errors. Use tools/draft_c6_remaining_014.py with draft_0160_0479.txt instead.')
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source_014 import load
OUT=Path(__file__).with_name('slice_0160.targets.json')
TEXT={
160:'Resto Menie\'s',161:'Imperial court cuisine?',162:"Yes, that's it!",163:"You've eaten there too,",164:'Scarrel?',165:'Of course I have.',166:"If you've been to the capital,",167:'that restaurant is essential.',
168:'A place like that was new to me,',169:'but the sautéed guinea fowl?',170:"You can't really eat",171:'that anywhere else.',172:'The sauce has a secret.',173:'Apparently they draw flavor',174:'out of the bones...',175:'...',
176:'...',177:"Let's stop",178:'talking about this...',179:'Yeah...',180:"or we'll desperately want it",181:'and suffer...',182:'Sigh...',183:"Then I'd love to eat",
184:"Then I'd love to eat",185:'as much fruit as I want...',186:'Nauba fruit,',187:'Sild fruit,',188:'or Darima fruit.',189:'Even without a meal,',190:'those alone might',191:'be enough for me...',
192:'Oh, I know exactly',193:'what you mean...',194:'For me, it would absolutely be cake',195:'and sweets. ♪ The Empire',196:'has so many confectioners.',197:"Resto Menie's",198:'fruit orchard tart?',199:'Do you know it?',
200:'I do, I do!',201:"It's the one that comes",202:'at the end of the course, right?',203:"It's piled with",204:'so much fruit...',205:'And layers of crisp',206:'pastry...',207:'...',
208:'...',209:"Let's stop",210:'talking about this...',211:'Yes...',212:"or I'll desperately want it",213:'and suffer...',214:'Sigh...',215:'Lady Misumi, you are close',
216:'with Genji, but',217:'how did you',218:'come to know each other?',219:'My curiosity is',220:'stronger than most.',221:'I wished to hear tales',222:"of the old man's world, so as a guest",223:'I invited him to this village.',
224:'That does sound like Lady Misumi...',225:'That does sound',226:'like Lady Misumi...',227:'Then I somehow learned',228:'the country where the old man lived,',229:'called Japan,',230:'is much like',231:'the Siltarn where we lived,',
232:'or so it seems.',233:'Really...',234:'Is that so?',235:'So I thought it would',236:'be easier for him to live here...',237:'I gave him a hermitage',238:'on the edge of the village, and have him',239:'live there.'}
def build():
 r,rows,_=load(180);assert set(TEXT)==set(range(160,240));t={}
 for rel,x in TEXT.items():
  p=3957+rel;z=rows[p];t[z['id']]={'id':z['id'],'source_sha256':z['source_sha256'],'source_offset':z['source_offset'],'source_byte_length':z['source_byte_length'],'reference_instructions':z['reference_instructions'],'resource_row':rel,'physical_ordered_index':p,'text':x,'status':'draft','notes':'Self-checked draft; physical rows 4097-4296 examined. Pending independent meaning review.'}
 return {'resource_id':r['id'],'section':'main-tail','assigned_range':[160,239],'physical_ordered_index_range':[4117,4196],'rows_examined':{'ranges_inclusive':[[4097,4296]],'count':200},'translations':t}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','rows':len(d['translations']),'relative_rows':sorted(v['resource_row'] for v in d['translations'].values())},ensure_ascii=False));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
