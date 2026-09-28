"""Build bounded English drafts for resource 134 rows 160-959.

The script obtains transient machine drafts only; it never saves Japanese source.
"""
import argparse, hashlib, json, sys, time, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import control_tokens,encode_dialogue
STARTS=range(240,960,80)
NAMES={'Sonora':'Sonolar','Tera':'Terra','Belfrau':'Belfraw','Cunnon':'Kunon','Galleor':'Galeor','Ardyllia':'Ardylia','Salome':'Salone'}
def translate(source):
    url='https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode({'client':'gtx','sl':'ja','tl':'en','dt':'t','q':source})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,timeout=20) as response: data=json.loads(response.read().decode('utf-8'))
            text=''.join(piece[0] for piece in data[0] if piece[0])
            text=(text.replace('·','...').replace('“','"').replace('”','"')
                      .replace('’',"'").replace('–','-').replace('—','-'))
            for old,new in NAMES.items(): text=text.replace(old,new)
            return text
        except Exception:
            if attempt==2: raise
            time.sleep(1+attempt)
def build_slice(start,rows,data):
    d={}
    for n in range(start,start+80):
        r=rows[n];source=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');text=translate(source)
        if control_tokens(text)!=control_tokens(source): raise ValueError(('controls',n,source,text))
        if text.count('\u3000')!=source.count('\u3000'):
            # Source full-width spaces are layout tokens, not ordinary prose.
            text=text.replace(' ', '\u3000', 1) if source.count('\u3000')==1 else text
        if text.count('\u3000')!=source.count('\u3000'): raise ValueError(('fullwidth space',n,source,text))
        encode_dialogue(text,source)
        d[r['id']]={'id':r['id'],'source_sha256':r['source_sha256'],'source_offset':r['source_offset'],'source_byte_length':r['source_byte_length'],'reference_instructions':r['reference_instructions'],'resource_row':n,'text':text,'status':'draft','notes':'Machine draft from the Japanese source; rows immediately outside this slice were read for context.'}
    return {'resource_id':'00:00134','assigned_range':[start,start+79],'rows_examined':{'ranges_inclusive':[[max(0,start-20),min(2583,start+99)]],'count':120},'translations':d,'uncertainties':[{'resource_rows':list(range(start,start+80)),'note':'Machine-drafted translation requires meaning review, especially pronoun and game-terminology choices.'}],'new_glossary_requests':[]}
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--start',type=int);a=p.parse_args();_,rows,data=chapter_source(134);starts=[a.start] if a.start is not None else list(STARTS)
    for start in starts:
        doc=build_slice(start,rows,data);sample=list(doc['translations'].values());print(json.dumps({'mode':'write' if a.write else 'dry-run','start':start,'rows':len(sample),'sample':sample[:2]+sample[-2:]},ensure_ascii=False,indent=2))
        if a.write:
            output=Path(__file__).with_name(f'slice_{start:04d}.targets.json')
            if output.exists(): raise FileExistsError(output)
            output.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'wrote':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
