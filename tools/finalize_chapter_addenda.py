"""Preview reviewer-confirmed fragment redistribution and a glossary citation fix."""
import argparse,json,copy
from chapter_patch import ROOT,FOLDER,read
from chapter_source import chapter_source

def prepare():
    _,rows,_=chapter_source(111);p=FOLDER/'0111'/'review_meaning_0000.json';doc=copy.deepcopy(read(p))
    fixes={1:'It feels like',2:"I got a really good night's",3:'sleep!',43:"I've tried",44:'studying it a little',45:'before.'}
    doc['required_corrections']={rows[n]['id']:dict(resource_row=n,source_sha256=rows[n]['source_sha256'],suggested_text=text,rationale='Source/context redistribution independently confirmed by terra_cabin_641 on 2026-09-27; preserves the full spoken group without repeated wording.') for n,text in fixes.items()}
    glossary_path=ROOT/'work/glossary/chapter_terms_0.1.12.json';glossary=read(glossary_path)
    for entry in glossary['entries']:
        if entry['source_name']=='ストラ':entry['evidence']=[dict(url='https://w.atwiki.jp/sn3psp/pages/42.html',supports=['Japanese Kyle skill spelling, not verified English romanization'])]
    glossary['change_log'][0]='Added provisional Stora and sourced Marurur / Summonite Stone entries.'
    return [(p,doc),(glossary_path,glossary)]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    for path,data in prepare():
        print(json.dumps(dict(mode='write' if a.write else 'dry run',path=str(path),changes=data.get('required_corrections',data.get('entries'))),indent=2))
        if a.write:path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if __name__=='__main__':main()
