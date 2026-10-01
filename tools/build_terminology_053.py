"""Apply reviewed Teacher terminology without relocating script data or code."""
import argparse, copy, json, re, shutil, struct, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from sn3_archive import ROOT, GameSource, parse_v4, child
from build_candidate import hash_file
from battle_source_024 import sha
from battle_compiler_024 import simulate
from dialogue_encoding import encode_dialogue, control_tokens
from dialogue_layout import latin_width
from font_metrics_014 import collect
from stages_patch import units
from script_strings import parse_pool

BASE = ROOT / 'work/output/0.1.52'
TARGETS = ROOT / 'work/translation/en/terminology_0.1.53/targets.json'
TERM = re.compile(r'\bprofessor\b', re.I)

def replace(text):
    return TERM.sub(lambda m: 'Teacher' if m[0][0].isupper() else 'teacher', text)

def prepare(source, previous):
    reviews = json.loads(TARGETS.read_text())['corrections']
    metrics = copy.deepcopy(collect()[0]['characters'])
    for c, width in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:
        metrics[c] = {'proposed_advance_pixels': width}
    reports = copy.deepcopy(previous['battle024'])
    canonical = {r['index']: r for r in reports if 'groups' in r}
    originals = copy.deepcopy(canonical)
    patched = {}; offsets = []; checks = []
    for number, report in canonical.items():
        relevant = [r for r in reviews if r['resource'] == number]
        if not relevant:
            assert not any(TERM.search(g['text']) for g in report['groups'])
            continue
        parent = source.resource('01.DAT', number)
        before = child(parent, parse_v4(parent), 1)
        assert not any(before[report['output_bytes']:])
        before = before[:report['output_bytes']]
        assert sha(before) == report['output_sha256']
        out = bytearray(before); allowed = set(); changed = []
        for review in relevant:
            group = next(g for g in report['groups'] if g['rows'] == review['rows'])
            assert group['text'] == review['previous_text']
            assert replace(group['text']) == review['text']
            old_pages = simulate(before, *group['original_span'])
            for page in group['pages']:
                for line in page:
                    if not TERM.search(line['text']): continue
                    old, old_display = encode_dialogue(line['text'], ''.join(control_tokens(line['text'])))
                    new_text = replace(line['text'])
                    new, display = encode_dialogue(new_text, ''.join(control_tokens(line['text'])))
                    start = line['new_offset']; end = start + len(old) + 2
                    assert before[start:end] == old + b'\0\0'
                    assert old_display == line['display_text'] and len(new) < len(old)
                    assert latin_width(new_text, metrics) <= line['pixels']
                    out[start:end] = new + bytes(end - start - len(new))
                    allowed.update(range(start,end))
                    line.update(text=new_text, display_text=display, expanded_units=units(new_text), pixels=latin_width(new_text, metrics))
                    changed.append(dict(offset=start, before=old_display, after=display))
            group['text'] = review['text']
            actual = simulate(out, *group['original_span'])
            assert len(old_pages) == len(actual) == len(group['pages'])
            for oldpage, newpage, lines in zip(old_pages, actual, group['pages']):
                assert oldpage['speaker'] == newpage['speaker']
                assert len(oldpage['lines']) == len(newpage['lines'])
                assert newpage['lines'] == [l['display_text'] for l in lines]
        assert len(out) == len(before)
        assert all(a == b or i in allowed for i,(a,b) in enumerate(zip(before,out)))
        assert before[:struct.unpack_from('<I',before,20)[0]*2] == out[:struct.unpack_from('<I',before,20)[0]*2]
        parsed = parse_pool(out)
        assert parsed['vm_statistics'] == report['vm_statistics']
        for g in report['groups']:
            actual = simulate(out,*g['original_span'])
            old = simulate(before,*g['original_span'])
            assert [p['speaker'] for p in old] == [p['speaker'] for p in actual]
            assert [p['lines'] for p in actual] == [[l['display_text'] for l in p] for p in g['pages']]
        for record in report['targets'].values(): record['text'] = replace(record['text'])
        for word in ('Professor','professor','PROFESSOR'):
            assert encode_dialogue(word,'')[0] not in out
        report['output_sha256'] = sha(out)
        patched[number] = bytes(out)
        checks.append(dict(canonical_resource=number, distinct_groups=len(relevant), changed_lines=len(changed), all_groups_simulated=len(report['groups']), code_and_pointers_unchanged=True, page_counts_line_counts_and_speakers_preserved=True, width_nonincreasing=True))
    for report in reports:
        number = report['index']; canonical_number = report.get('canonical_report_index',number)
        if canonical_number not in patched: continue
        parent = source.resource('01.DAT',number); ix = parse_v4(parent); entry = ix['entries'][1]
        before = child(parent,ix,1); wanted = patched[canonical_number]
        assert not any(before[len(wanted):])
        assert sha(before[:len(wanted)]) == originals[canonical_number]['output_sha256']
        report['output_sha256'] = sha(wanted)
        wanted += bytes(len(before)-len(wanted))
        assert len(wanted) == len(before)
        absolute = source.files['01.DAT']['sector']*2048 + source.indexes['01.DAT']['entries'][number]['offset'] + entry['offset']
        offsets.append((absolute,before,wanted,number))
    assert len(reviews) == sum(c['distinct_groups'] for c in checks) == 9
    return reports, sorted(offsets), checks

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true');p.add_argument('--destination',default='work/output/0.1.53');a=p.parse_args()
    dest=(ROOT/a.destination).resolve();assert ROOT in dest.parents and not dest.exists()
    previous=json.loads((BASE/'manifest.json').read_text());prior=BASE/previous['output_iso']
    assert hash_file(prior)==previous['output_sha256']
    for n,h in previous['inputs_sha256'].items(): assert hash_file(ROOT/n)==h,n
    inputs={p.relative_to(ROOT).as_posix():hash_file(p) for p in [Path(__file__).resolve(),TARGETS,ROOT/'work/glossary/terminology_preferences.json']}
    with GameSource(prior) as source: reports,patches,checks=prepare(source,previous)
    print(json.dumps(dict(mode='write' if a.write else 'preview',distinct_passages=9,script_copies=len(patches),checks=checks),indent=2),flush=True)
    if not a.write:return
    dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.53.iso';partial=iso.with_suffix('.iso.partial')
    shutil.copyfile(prior,partial)
    with partial.open('r+b') as f:
        for offset,before,after,number in patches:
            f.seek(offset);assert f.read(len(before))==before
            f.seek(offset);f.write(after)
    # Compare every byte to the prior ISO, allowing only the reviewed script slots.
    with prior.open('rb') as old,partial.open('rb') as new:
        position=0
        while True:
            original=old.read(4*1024*1024);actual=new.read(len(original))
            if not original:assert not new.read(1);break
            expected=bytearray(original)
            for offset,before,after,number in patches:
                lo=max(position,offset);hi=min(position+len(original),offset+len(after))
                if lo<hi:expected[lo-position:hi-position]=after[lo-offset:hi-offset]
            assert actual==expected,position
            position+=len(original)
    with GameSource(partial) as candidate:
        assert len(candidate.indexes)==23
        for offset,before,after,number in patches:
            parent=candidate.resource('01.DAT',number)
            assert child(parent,parse_v4(parent),1)==after
    for n,h in {**previous['inputs_sha256'],**inputs}.items():assert hash_file(ROOT/n)==h,n
    partial.rename(iso)
    report=dict(distinct_passages=9,script_copies=len(patches),changed_script_indices=[p[3] for p in patches],checks=checks,entire_iso_compared=True,only_reviewed_script_slots_changed=True,runtime_scene_verified=False)
    manifest=copy.deepcopy(previous)
    manifest.update(version='0.1.53',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),previous_build_sha256=previous['output_sha256'],battle024=reports,terminology053=report,static_validation=dict(comparison_build='0.1.52',entire_iso_compared=True,only_reviewed_script_slots_changed=True,bank_indexes=23,runtime_verified=False))
    manifest['inputs_sha256'].update(inputs)
    shutil.copyfile(BASE/'EBOOT.elf',dest/'EBOOT.elf')
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (dest/'terminology-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'tools/verify_stability_052.py'),'--build',str(dest),'--report',str(dest/'stability-report.json')],check=True)
    print(json.dumps(dict(iso=str(iso),sha256=manifest['output_sha256'])),flush=True)

if __name__=='__main__':
    from pathlib import Path
    if not __debug__:raise RuntimeError('Assertions required')
    main()
