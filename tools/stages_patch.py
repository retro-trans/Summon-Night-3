"""Relocate and paginate all remaining Chapter 1 story rows; preview first."""
import argparse,copy,json,hashlib,struct,re
from pathlib import Path
from sn3_archive import ROOT,GameSource
from sn3_codec import decompress,compress
from prepare_harbor_context import opening_source
from script_strings import parse_pool
from script_repack import relocate_script
from dialogue_layout import operand_instruction,verify_layout,latin_width
from dialogue_encoding import encode_dialogue,control_tokens
from verify_dialogue_layout import simulate_group
from sn3_vm import instructions
from font_metrics import collect

PRIOR=ROOT/'work/output/0.1.11'
FOLDER=ROOT/'work/translation/en/stages_0.1.12'
TARGET='work/translation/en/opening_stages_0.1.12.targets.json'
DIRECT=set([785,786,787,1003,1004,1005,1006,1007,1008,1327,1328,1329]+list(range(1248,1253)))
PROFILES={2030:(208,1),2044:(208,1),2058:(208,1),2259:(208,1),2273:(208,1),2128:(448,0),2141:(448,0),2180:(448,0),2193:(448,0)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def punctuation(t):return t.translate(str.maketrans({'—':'--','–':'-','…':'...','‘':"'",'’':"'",'“':'"','”':'"'}))
def units(t):return sum(8 if c=='▲' else 6 if c=='●' else 1 for c in t)
def wrap(text,width,metrics):
    words=text.split(' ');assert text and all(words),repr(text)
    def fits(t):return units(t)<=31 and latin_width(t,metrics)<=width
    assert all(fits(w) for w in words),('word exceeds capacity',text)
    lines=[];line=''
    for word in words:
        joined=line+(' ' if line else '')+word
        if fits(joined):line=joined
        else:lines.append(line);line=word
    lines.append(line);assert ' '.join(lines)==text
    return lines

def drafts(rows,original,require_reviews):
    result={};inputs={}
    for path in sorted(FOLDER.glob('slice_*.targets.json')):
        doc=read(path);inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        for identity,t in doc['translations'].items():
            n=t['opening_row'];r=rows[n];assert identity==r['id'] and n not in result
            assert t['source_sha256']==r['source_sha256'] and t['source_offset']==r['source_offset']
            source=original[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
            encode_dialogue(punctuation(t['text']),source);result[n]=copy.deepcopy(t)
    assert set(result)==set(range(641,1428)),sorted(set(range(641,1428))-set(result))
    # Independent reviews are converted to a single auditable, source-bound file.
    review=FOLDER/'accepted_review.json'
    if require_reviews:
        accepted=read(review);assert accepted['reviewed_rows']==list(range(641,1428))
        assert accepted['draft_inputs_sha256']==inputs
        for fix in accepted['corrections']:
            n=fix['opening_row'];assert fix['source_sha256']==rows[n]['source_sha256']
            result[n]['text']=fix['text']
        inputs[str(review.relative_to(ROOT)).replace('\\','/')]=sha(review.read_bytes())
    # Apply locked spelling only AFTER meaning review. No content substitutions.
    replacements={'Sonora':'Sonolar','Biju':'Vijue','Bijou':'Vijue','Galeor':'Galleor','Azuria':'Azlier','Azria':'Azlier'}
    for n,t in result.items():
        t['text']=punctuation(t['text'])
        prefix='　' if t['text'].startswith('　') else ''
        t['text']=prefix+' '.join(t['text'].replace('　',' ').split())
        for old,new in replacements.items():t['text']=re.sub(r'\b'+old+r'\b',new,t['text'])
        r=rows[n];source=original[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
        encode_dialogue(t['text'],source)
    return result,inputs

def prepare(source,require_reviews=True):
    previous=read(PRIOR/'manifest.json');report=copy.deepcopy(previous['script_changes'][0])
    before=decompress(source.resource('00.DAT',65),0xa695)[0];assert sha(before)==report['decoded_sha256']
    resource,rows,original=opening_source();translated,inputs=drafts(rows,original,require_reviews)
    selection=read(ROOT/'work/translation/en/opening_harbor_0.1.11.targets.json')
    metrics=copy.deepcopy(collect()[0]['characters'])
    for c,advance in [('▲',128),('●',96),('♪',16),('　',6)]:metrics[c]={'proposed_advance_pixels':advance}
    pool=parse_pool(before)['pool_offset'];delta=pool-parse_pool(original)['pool_offset']
    targets={};identity={}
    for n,t in translated.items():
        r=rows[n];target=dict(source_offset=r['source_offset'],source_sha256=r['source_sha256'],text=t['text'],status='meaning_reviewed' if require_reviews else 'draft',encoding_profile='dialogue_fullwidth_cp932')
        assert r['id'] not in selection['translations'];selection['translations'][r['id']]=target
        current=r['source_offset']+delta;targets[current]=target;identity[current]=r
    moved,changes=relocate_script(before,targets)
    code=instructions(before);at={i['offset']:i for i in code};destinations={i['target_word']*2 for i in code if 'target_word' in i}
    plans=[];done=set();direct=[]
    for n in range(641,1428):
        if n in done:continue
        r=rows[n];assert len(r['reference_instructions'])==1
        pos=r['reference_instructions'][0]
        if n in DIRECT:
            text=translated[n]['text'];limit=280 if n<1247 or n>1252 else 208
            assert units(text)<=31 and latin_width(text,metrics)<=limit,('direct text too wide',n,text)
            direct.append(dict(row=n,text=text,reference=pos,pixel_limit=limit));done.add(n);continue
        ns=[n]
        while ns[-1]+1<1428 and ns[-1]+1 not in DIRECT and rows[ns[-1]+1]['reference_instructions']==[pos+8*len(ns)]:ns.append(ns[-1]+1)
        for k in ns:
            p=rows[k]['reference_instructions'][0]
            assert at[p]['opcode']==5 and at[p]['mode']==4 and at[p+4]['opcode']==7 and at[p+4]['target_word']==2003
        tail_start=pos+8*len(ns);end=tail_start;argc=0
        while at[end]['opcode']==5:
            assert at[end]['mode'] in (5,9,10),(ns,at[end]);argc+=1;end+=at[end]['size']
        inst=at[end];helper=inst.get('target_word');assert inst['opcode']==7 and helper in PROFILES,(ns,inst)
        width,expected_argc=PROFILES[helper];assert inst['mode']==argc==expected_argc
        end+=inst['size'];assert not any(pos<x<end for x in destinations),(ns,'branch into group')
        text=' '.join(translated[k]['text'] for k in ns);lines=wrap(text,width,metrics);pages=[lines[i:i+3] for i in range(0,len(lines),3)]
        for page in pages:assert sum(units(line) for line in page)<=192
        plans.append(dict(id='stages_'+'_'.join(map(str,ns)),opening_rows=ns,source_offsets=[rows[k]['source_offset'] for k in ns],original_span=[pos,end],original_span_sha256=sha(before[pos:end]),tail=before[tail_start:end],display_helper_word=helper,text=text,page_texts=pages,code_size=sum(8*len(p)+end-tail_start for p in pages)+4,measured_pixel_limit=width))
        done.update(ns)
    assert done==set(range(641,1428))
    growth=sum(p['code_size'] for p in plans);new_pool=pool+growth
    out=bytearray(moved[:pool]+bytes(growth)+moved[pool:]);struct.pack_into('<I',out,20,new_pool//2)
    for c in report['changes']:c['new_offset']+=growth
    for g in report['layout_groups']:
        for p in g['pages']:
            for c in p:c['new_offset']+=growth
    for c in changes:
        r=identity[c['old_offset']];c.update(id=r['id'],prior_build_source_offset=c['old_offset'],old_offset=r['source_offset'],new_offset=c['new_offset']+growth)
    cursor=pool;groups=[]
    for plan in plans:
        emitted=bytearray();pages=[]
        for pi,texts in enumerate(plan['page_texts']):
            fragments=[]
            for li,text in enumerate(texts):
                encoded,display=encode_dialogue(text,''.join(control_tokens(text)));offset=len(out);word=(offset-new_pool)//2;ref=cursor+len(emitted)
                out.extend(encoded+b'\0\0');emitted.extend(operand_instruction(5,4,word)+operand_instruction(7,1,2003))
                fragments.append(dict(id=f"{plan['id']}:page:{pi}:line:{li}",text=text,display_text=display,new_offset=offset,new_byte_length=len(encoded),pool_word_offset=word,reference_instructions=[ref],expanded_units=units(text)))
            emitted.extend(plan['tail']);pages.append(fragments)
        start,end=plan['original_span'];emitted.extend(operand_instruction(10,0,end//2));assert len(emitted)==plan['code_size']
        out[cursor:cursor+len(emitted)]=emitted;out[start:end]=operand_instruction(10,0,cursor//2)+bytes(end-start-4)
        for c in changes:
            if c['old_offset'] in plan['source_offsets']:
                c['original_reference_instructions']=c['reference_instructions'];c['reference_instructions']=[];c['layout_group_id']=plan['id']
        group={k:v for k,v in plan.items() if k not in ('tail','page_texts')}
        group.update(trampoline_offset=cursor,return_instruction=end,pages=pages,max_display_units=31,max_lines_per_page=3,layout_profile='chapter1_expanded_tokens_v1',maximum_measured_pixels=max(latin_width(r['text'],metrics) for p in pages for r in p))
        groups.append(group);cursor+=len(emitted)
    assert out[new_pool:new_pool+len(before)-pool]==before[pool:]
    allowed=set(range(20,24))|{i for p in plans for i in range(*p['original_span'])}|{i for d in direct for i in range(d['reference'],d['reference']+4)}
    assert all(before[i]==out[i] for i in range(pool) if i not in allowed)
    report['changes'].extend(changes);report['layout_groups'].extend(groups)
    verify_layout(bytes(out),report['changes'],report['layout_groups'])
    for g in groups:
        old=simulate_group(before,*g['original_span']);new=simulate_group(out,*g['original_span']);assert len(old)==1 and len(new)==len(g['pages'])
        for p,expected in zip(new,g['pages']):assert p['helper']==old[0]['helper'] and p['args']==old[0]['args'] and p['lines']==[r['display_text'] for r in expected]
    assert {r['id'] for r in rows}==set(selection['translations'])=={c['id'] for c in report['changes']}
    assert len(out)<0x78000
    packed=compress(bytes(out),0xa695);assert decompress(packed,0xa695)[0]==out
    report.update(decoded_size=len(out),encoded_size=len(packed),decoded_sha256=sha(out),runtime_allocation_verified=False)
    selection.update(scope='All1428 unique Chapter1 story fragments in resource00:00065: opening plus cabin, pirate attack/escape, storm/shipwreck/reunion. Common and later-chapter scripts outside scope.',excluded_groups=[])
    for g in selection.get('incremental_layout_groups',[]):
        for p in g['pages']:
            for c in p:c['new_offset']+=growth
    selection.setdefault('incremental_layout_groups',[]).extend(groups)
    inputs['tools/stages_patch.py']=sha(Path(__file__).read_bytes());selection['review_inputs_sha256'].update(inputs)
    checks=dict(added_source_rows=787,covered_source_rows=1428,remaining_in_scope=0,new_reflow_groups=len(groups),new_pages=sum(len(g['pages']) for g in groups),new_code_bytes=growth,decoded_script_bytes=len(out),direct_rows=direct,token_expansion_budget={'▲':dict(cells=8,pixels=128),'●':dict(cells=6,pixels=96)},helper_profiles={str(k):dict(pixels=v[0],caller_args=v[1]) for k,v in PROFILES.items()},prior_translations_preserved=True,source_pool_preserved=True,all_group_calls_simulated=True,samples=[dict(rows=g['opening_rows'],pages=[[r['text'] for r in p] for p in g['pages']]) for g in groups if g['opening_rows'][0] in (641,673,785,922,1078,1201,1246,1361,1405)])
    return packed,report,selection,checks

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--draft-preview',action='store_true');a=p.parse_args();assert not(a.write and a.draft_preview)
    with GameSource(PRIOR/'Summon_Night_3_EN_0.1.11.iso') as source:_,report,selection,checks=prepare(source,not a.draft_preview)
    print(json.dumps(dict(mode='write' if a.write else 'dry run',**checks),indent=2))
    if a.write:
        (ROOT/TARGET).write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8')
        (ROOT/'docs/stages_static_0.1.12.json').write_text(json.dumps(checks,indent=2)+'\n')
if __name__=='__main__':main()
