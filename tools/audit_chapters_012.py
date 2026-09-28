"""Audit final source coverage and review bindings; dry run by default."""
import argparse,json,re
from datetime import datetime,timezone
from chapter_patch import ROOT,FOLDER,RESOURCES,chapter_source,expected_rows,read,sha
from prepare_harbor_context import opening_source
from dialogue_encoding import control_tokens

def audit():
    resources=[];inputs={};checks=0
    def bind(path):
        inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
    for number in (65,)+RESOURCES:
        if number==65:
            _,rows,data=opening_source();wanted=set(range(1428))
            path=ROOT/'work/translation/en/opening_stages_0.1.12.targets.json'
            stat=ROOT/'docs/stages_static_0.1.12.json'
        else:
            _,rows,data=chapter_source(number);wanted=expected_rows(number,rows)
            path=FOLDER/f'{number:04d}'/'compiled.targets.json'
            stat=ROOT/f'docs/chapter_{number:04d}_static_0.1.12.json'
        doc=read(path);bind(path);bind(stat)
        expected={rows[n]['id']:rows[n] for n in wanted}
        assert set(doc['translations'])==set(expected),(number,'coverage')
        for identity,t in doc['translations'].items():
            r=expected[identity];original=data[r['source_offset']:r['source_offset']+r['source_byte_length']]
            assert sha(original)==t['source_sha256'],(number,identity,'source')
            assert t['text'].strip() and not re.search('[\u3040-\u30ff\u3400-\u9fff]',t['text']),(number,identity,'untranslated')
            assert control_tokens(t['text'])==control_tokens(original.decode('cp932')),(number,identity,'tokens')
            assert not re.search(r'\b(Freize|Maruru|Beiger|Belfraw|Sonora|Biju|Bijou|Galeor|Azuria|Farzen|Yaffa)\b',t['text']),(number,identity,'alias')
            checks+=4
        for name,digest in doc.get('review_inputs_sha256',{}).items():
            assert sha((ROOT/name).read_bytes())==digest,('stale compiled input',name)
            inputs[name]=digest;checks+=1
        if number!=65:
            accepted=FOLDER/f'{number:04d}'/'accepted_review.json';a=read(accepted);bind(accepted)
            assert set(a['reviewed_rows'])==wanted
            for key in ('draft_inputs_sha256','review_inputs_sha256'):
                for name,digest in a[key].items():
                    assert sha((ROOT/name).read_bytes())==digest,('stale accepted input',name)
                    inputs[name]=digest;checks+=1
            c=read(stat)
            assert c['remaining_in_scope']==0 and c['reviewed'] and c['source_pool_preserved'] and c['unrelated_code_preserved'] and c['all_group_calls_simulated']
        resources.append(dict(resource_id=f'00:{number:05d}',covered_rows=len(expected),complete_in_scope=True))
    total=sum(r['covered_rows'] for r in resources);assert total==6174
    return dict(version='0.1.12',audited_at_utc=datetime.now(timezone.utc).isoformat(),covered_story_fragments=total,new_since_0_1_11=total-641,
        resources=resources,checks_passed=checks,checks_failed=0,inputs_sha256=inputs,
        checked=['Exact scoped source identities','Nonempty final translations','No remaining Japanese in final scoped targets','Runtime control-token preservation','Locked name aliases','Current review and compiler input hashes','Static control-flow/layout reports'],
        not_checked=['Complete three-chapter playthrough','Full-game interface coverage','Text in artwork','Unselected shared library strings'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();d=audit()
    print(json.dumps({k:v for k,v in d.items() if k!='inputs_sha256'},indent=2))
    if a.write:(ROOT/'docs/chapters_coverage_audit_0.1.12.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
