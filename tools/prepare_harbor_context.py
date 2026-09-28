"""Preserve screenshot anchors and researched terms for the opening harbor dialogue."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from sn3_archive import ROOT, GameSource
from sn3_codec import decompress

WIKI = 'https://summonnight.wiki.gg/wiki/Summon_Night_3'
FANDOM = 'https://summonnight.fandom.com/wiki/'
RENOTE = 'https://renote.net/articles/17584'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def opening_source():
    index = json.loads((ROOT / 'work/translation/en/script_strings.index.json').read_text())
    resource = next(r for r in index['resources'] if r['id'] == '00:00065')
    with GameSource() as source:
        raw = source.resource('00.DAT', 65)
    if sha(raw) != resource['sha256']:
        raise ValueError('Original opening resource changed')
    data = decompress(raw, 0xa695)[0]
    if sha(data) != resource['compression']['decoded_sha256']:
        raise ValueError('Decoded opening resource changed')
    rows = sorted(resource['strings'], key=lambda r: min(r['reference_instructions']))
    start = next(i for i, r in enumerate(rows) if r['id'] == '00:00065:text:0002646e')
    rows = rows[start:]
    for row in rows:
        if sha(data[row['source_offset']:row['source_offset'] + row['source_byte_length']]) != row['source_sha256']:
            raise ValueError('Source row hash mismatch')
    return resource, rows, data


def evidence(url, supports):
    return {'url': url, 'supports': supports, 'checked_on': '2026-09-26'}


def glossary():
    entries = [
        {'id': 'family.martini', 'category': 'family', 'source_name': 'マルティーニ', 'target_name': 'Martini',
         'role': 'Merchant family employing the protagonist as a private tutor.', 'status': 'wiki_verified',
         'evidence': [evidence(FANDOM + 'Rexx', ['name', 'role'])]},
        {'id': 'polity.old_kingdom', 'category': 'polity', 'source_name': '旧王国', 'target_name': 'Old Kingdom',
         'status': 'wiki_verified', 'evidence': [evidence(FANDOM + 'Rexx', ['name'])]},
        {'id': 'character.nup', 'category': 'character', 'source_name': 'ナップ', 'target_name': 'Nup',
         'full_name': 'Nup Martini', 'aliases': ['Napp', 'Nap'], 'gender': 'male',
         'personality': 'Energetic, admires strength; can be rude, but has a kind core.',
         'role': 'One of four selectable pupils; the Martini heir in this route.', 'nickname': None,
         'nickname_status': 'No distinct nickname established by the sources checked.', 'status': 'wiki_verified',
         'evidence': [evidence(WIKI, ['name']), evidence(FANDOM + 'Nup_Martini', ['name', 'gender', 'personality', 'role'])]},
        {'id': 'character.will', 'category': 'character', 'source_name': 'ウィル', 'target_name': 'Will',
         'full_name': 'Will Martini', 'aliases': [], 'gender': 'male', 'personality': None,
         'personality_status': 'External profile not retrieved; local quiz dialogue suggests an exacting manner, not yet generalized as a profile.',
         'role': 'One of four selectable pupils; the Martini heir in this route.', 'nickname': None,
         'nickname_status': 'Not established.', 'status': 'wiki_name_and_gender_verified_profile_incomplete',
         'evidence': [evidence(WIKI, ['name']), evidence(FANDOM + 'Nup_Martini', ['gender', 'selectable_student_role'])]},
        {'id': 'character.belfrau', 'category': 'character', 'source_name': 'ベルフラウ', 'target_name': 'Belfrau',
         'full_name': 'Belfrau Martini', 'aliases': ['Belfraw'], 'gender': 'female',
         'personality': 'Proud and demanding at first; works hard and wants to make her father proud.',
         'role': 'One of four selectable pupils; the Martini heir in this route.', 'nickname': None,
         'nickname_status': 'None established for this opening context.', 'status': 'wiki_verified',
         'notes': 'Current Wiki.gg roster uses Belfrau; archived Fandom and existing Latin art use Belfraw. Current wiki spelling takes priority.',
         'evidence': [evidence(WIKI, ['name']), evidence(FANDOM + 'Belfraw_Martini', ['gender', 'personality', 'role', 'older_spelling'])]},
        {'id': 'character.alieze', 'category': 'character', 'source_name': 'アリーゼ', 'target_name': 'Alieze',
         'full_name': 'Alieze Martini', 'aliases': ['Alize', 'Arlyze', 'Arize'], 'gender': 'female',
         'personality': 'Shy with strangers; enjoys stories and becomes talkative with trusted people.',
         'role': 'One of four selectable pupils; the Martini heir in this route.', 'nickname': None,
         'nickname_status': 'Not established.', 'status': 'wiki_verified',
         'evidence': [evidence(WIKI, ['name']), evidence(FANDOM + 'Alieze_Martini', ['gender', 'personality', 'role'])]},
        {'id': 'character.salome', 'category': 'character', 'source_name': 'サローネ', 'target_name': 'Salome',
         'aliases': ['Salone', 'Sarone'], 'gender': 'female', 'personality': 'Strict in the observed harbor conversation.',
         'personality_status': 'Local scene observation; not a general external profile.',
         'role': 'Martini head maid and the pupil\'s caregiver.', 'nickname': 'Nanny',
         'nickname_source': 'Opening dialogue address ばあや; project translation of caregiver address, not a personal name.',
         'status': 'wiki_name_verified_with_source_discrepancy',
         'notes': 'The source spells サローネ; current Wiki.gg roster spells Salome. Retain Salome under the project wiki-priority rule; do not silently normalize back to a literal romanization.',
         'evidence': [evidence(WIKI, ['name']), evidence(RENOTE, ['gender', 'caregiver_role'])],
         'local_source_rows': [333, 334, 335, 336, 337, 338, 352]},
        {'id': 'location.adnias_harbor', 'category': 'location', 'source_name': 'アドニアス港', 'target_name': 'Adnias Harbor',
         'aliases': [], 'status': 'project_romanization_japanese_location_verified',
         'notes': 'No attested English spelling found in the checked sources. Adnias is a project romanization, not an official English localization claim.',
         'evidence': [evidence(RENOTE, ['Japanese_name', 'Empire_location', 'harbor_scene'])]},
        {'id': 'location.pastis', 'category': 'location', 'source_name': 'パスティス', 'target_name': 'Pastis',
         'aliases': [], 'status': 'project_romanization_japanese_location_verified',
         'notes': 'No attested English spelling found in the checked sources. Keep generic industrial/shipbuilding descriptions separate from the proper name.',
         'evidence': [evidence(RENOTE, ['Japanese_name', 'destination'])]},
    ]
    return {'schema_version': 1, 'language': 'en', 'status': 'researched_terms_for_harbor_drafts',
            'policy': 'Meaning review first; normalize spelling by script afterward. Prefer current Wiki.gg over its Fandom archive when spellings differ. Never replace generic Teacher/Nanny addresses with character names.',
            'entries': entries, 'do_not_touch_after_normalization': [r['target_name'] for r in entries]}


def collect():
    from PIL import Image
    resource, rows, data = opening_source()
    screenshots = []
    definitions = [
        ('cold_hunger', '744403c1-531f-46f4-b511-e745c00d43e2', [121, 122, 123]),
        ('ship_memory', '4c421ce9-9bad-4814-a856-a5f14d3b8eec', [109, 110]),
        ('adnias_harbor', '2e80515e-b66a-4431-9994-0e142c7530aa', []),
        ('sudden_teaching', '62458619-1a54-4f52-930c-ea5eb8a64383', [158, 159, 160]),
    ]
    # The first two anchors are checked by meaning-bearing source fragments, without storing dialogue transcripts.
    needles = {'cold_hunger': ['しかし、寒いな', 'おまけに、なんだか', '腹まですいてきた'],
               'ship_memory': ['そうだ、俺はたしか', '船に乗っていたんだ！'],
               'sudden_teaching': ['それにしても', 'いきなりのことで', '本当に驚いたな']}
    for name, suffix, numbers in definitions:
        source = Path('C:/Users/Binh/AppData/Local/Temp/codex-clipboard-' + suffix + '.png')
        with Image.open(source) as image:
            width, height = image.size
        actual = [data[rows[n]['source_offset']:rows[n]['source_offset'] + rows[n]['source_byte_length']].decode('cp932') for n in numbers]
        if numbers and actual != needles[name]:
            raise ValueError('Screenshot anchor does not match source rows: ' + name)
        screenshots.append({'id': name, 'source_path': str(source), 'image_file': name + '.png',
                            'sha256': sha(source.read_bytes()), 'width': width, 'height': height,
                            'screen_type': 'full_screen' if name == 'adnias_harbor' else 'cropped_dialogue_box',
                            'inspection_rect': [180, 190, 610, 170] if name == 'adnias_harbor' else [0, 0, width, height],
                            'coordinate_space': 'supplied_image_pixels', 'opening_rows': numbers,
                            'source_ids': [rows[n]['id'] for n in numbers],
                            'source_hashes': [rows[n]['source_sha256'] for n in numbers]})
    manifest = {'schema_version': 1, 'resource_id': resource['id'], 'source_resource_sha256': resource['sha256'],
                'source_decoded_sha256': sha(data), 'screenshots': screenshots,
                'scope': 'Opening beach recollection, harbor introductions and departure reflection. All protagonist and student alternatives retained.',
                'intended_complete_row_range': [0, 640],
                'next_scene_first_row': 641, 'next_scene_note': 'The first cabin conversation begins with the pupil answering the door; later ship/pirate scenes are outside this initial harbor pass.',
                'cropped_screenshot_limit': 'Dialogue crops do not establish full-screen coordinates or maximum width. Existing native dialogue layout profile remains the rendering evidence.',
                'location_title': {'source_visible': '帝国領・アドニアス港', 'target_full': 'Imperial Territory: Adnias Harbor',
                                   'status': 'screenshot_translation_native_asset_not_yet_identified',
                                   'glossary_id': 'location.adnias_harbor'},
                'source_rows': [{**row, 'opening_row': n} for n, row in enumerate(rows[:641])]}
    return glossary(), manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    terms, context = collect()
    gp = ROOT / 'work/glossary/opening_harbor.json'
    directory = ROOT / 'work/ui/harbor_dialogue'
    if gp.exists() or directory.exists():
        parser.error('Preserve existing glossary and screenshot evidence')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'glossary_path': str(gp),
                      'glossary': terms, 'screenshots': context['screenshots'],
                      'range': context['intended_complete_row_range'], 'location': context['location_title']}, ensure_ascii=False, indent=2))
    if args.write:
        with gp.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(terms, ensure_ascii=False, indent=2) + '\n')
        directory.mkdir()
        for row in context['screenshots']:
            target = directory / row['image_file']
            shutil.copyfile(row['source_path'], target)
            if sha(target.read_bytes()) != row['sha256']:
                raise ValueError('Copied screenshot changed')
        (directory / 'index.json').write_text(json.dumps(context, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
