import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE / 'review_common_0400_0799.json'

CORRECTIONS = {
    641: ('Rough, but tenacious...', 'Corrects 無骨 (rough, unrefined), which was mistranslated as “boneless.”'),
    654: ('Put that dangerous thing away', 'Restores the source’s warning about a dangerous object/weapon, rather than a merely noisy one.'),
    677: ('I said it was just', 'Restores the first half of the split “youthful indiscretion” line.'),
    678: ('youthful indiscretion!', 'Restores the second half; the draft instead contained the next speaker’s line.'),
    679: ('Do not get carried away on your own...', 'Repairs the one-row displacement beginning after the youthful-indiscretion exchange.'),
    680: ('Could stress be the cause?', 'Repairs displaced dialogue.'),
    681: ('Your hair roots are weak. At this rate,', 'Repairs displaced dialogue.'),
    682: ('before long, certainly...', 'Repairs displaced dialogue.'),
    683: ('D-Do not say iiiit!!', 'Repairs displaced dialogue.'),
    684: ('Come, Lady Arumine.', 'Repairs displaced dialogue.'),
    685: ('Together, let us show this world', 'Repairs displaced dialogue.'),
    686: ('the light of justice!', 'Repairs displaced dialogue.'),
    687: ('That is why I said, not Arumine -', 'Restores the correction of the speaker’s name.'),
    688: ('please call me Amel.', 'Completes the source’s name correction.'),
    689: ('Honestly...', 'Repairs displaced dialogue.'),
    690: ('Now then...', 'Repairs displaced dialogue.'),
    691: ('Let us finish this quickly and get back', 'Repairs displaced dialogue.'),
    692: ('to my nap, shall we?', 'Repairs displaced dialogue.'),
    693: ('Hear, hear!♪', 'Repairs displaced dialogue.'),
    694: ('Let us finish it quickly, then', 'Repairs displaced dialogue.'),
    695: ('lounge around lazily.', 'Repairs displaced dialogue.'),
    696: ('...Are you two idiots?', 'Repairs displaced dialogue.'),
    697: ('If we were siblings,', 'Repairs displaced dialogue.'),
    698: ('I would clearly be the dependable brother,', 'Repairs displaced dialogue.'),
    699: ('would I not?', 'Repairs displaced dialogue.'),
    700: ('Hmm, no matter how you look at it,', 'Repairs displaced dialogue.'),
    701: ('we are the useless little brother', 'Repairs displaced dialogue.'),
    702: ('and dependable big sister.', 'Repairs displaced dialogue.'),
    703: ('Then, let us settle on', 'Repairs displaced dialogue.'),
    704: ('the unreliable older brother', 'Repairs displaced dialogue.'),
    705: ('and the careless younger sister.', 'Repairs displaced dialogue.'),
    706: ('A vessel made as a counterpart...', 'Repairs displaced dialogue.'),
    707: ('I do not know whose work it was,', 'Repairs displaced dialogue.'),
    708: ('but it is cruel indeed.', 'Repairs displaced dialogue.'),
    709: ('Huh?', 'Repairs displaced dialogue.'),
    710: ('What do you mean...?', 'Repairs displaced dialogue.'),
    711: ('You are Magna, are you not?', 'Repairs displaced dialogue.'),
    712: ('Thank you very much', 'Repairs displaced dialogue.'),
    713: ('for helping my student.', 'Repairs displaced dialogue.'),
    714: ('Oh, no...', 'Repairs displaced dialogue.'),
    715: ('(Somehow,', 'Repairs displaced dialogue.'),
    716: ('my heart is racing...)', 'Repairs displaced dialogue.'),
    717: ('You are Magna, right?', 'Repairs displaced dialogue.'),
    718: ('I have heard about you from her.', 'Repairs displaced dialogue.'),
    719: ('I will be counting on you.', 'Restores the source’s request for support.'),
    760: ('A tsukumogami? ...No, that is not it.', 'Uses the source’s specific artifact-spirit term instead of “guardian deity.”'),
    761: ('I see... Mechanical World technology', 'Restores the first half of the split statement.'),
    762: ('is a cruel thing indeed...', 'Restores the conclusion of the statement.'),
    763: ('.......', 'Restores the source-only pause.'),
    764: ('Do not be so tense.', 'Repairs the subsequent one-row displacement.'),
    765: ('Take it easy... okay?', 'Repairs displaced dialogue.'),
    766: ('If I could do that easily,', 'Repairs displaced dialogue.'),
    767: ('I would not be having this trouble.', 'Repairs displaced dialogue.'),
    768: ('Honestly...', 'Repairs displaced dialogue.'),
    769: ('Come on, snap out of it!', 'Repairs displaced dialogue.'),
    770: ('The battle has already begun,', 'Repairs displaced dialogue.'),
    771: ('you know!?', 'Repairs displaced dialogue.'),
    772: ('I-I know!', 'Repairs displaced dialogue.'),
    773: ('Ugh... I think this is worse', 'Repairs displaced dialogue.'),
    774: ('than being scolded by Ness...', 'Repairs displaced dialogue.'),
    775: ('Honestly, I hate fighting.', 'Repairs displaced dialogue.'),
    776: ('Is there not some way', 'Repairs displaced dialogue.'),
    777: ('to avoid fighting somehow?', 'Repairs displaced dialogue.'),
    778: ('Really, you are just like', 'Repairs displaced dialogue.'),
    779: ('someone I know...', 'Repairs displaced dialogue.'),
    780: ('...right?', 'Restores the final tag of the comparison.'),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    inputs = {str(Path('work/translation/en/battle_0.1.24') / f'common_{start:04d}.targets.json'): sha256(BASE / f'common_{start:04d}.targets.json') for start in (400, 480, 640, 720)}
    rows = {}
    for start in (400, 480, 640, 720):
        document = json.loads((BASE / f'common_{start:04d}.targets.json').read_text(encoding='utf8'))
        rows.update({item['resource_row']: item for item in document['translations'].values()})
    corrections = [
        {'resource': 175, 'resource_row': row, 'source_sha256': rows[row]['source_sha256'], 'text': text, 'reason': reason}
        for row, (text, reason) in sorted(CORRECTIONS.items())
    ]
    return {
        'build_version': '0.1.24',
        'review_kind': 'independent_meaning_review',
        'source': 'work/source/original.iso, 01.DAT V4 SCRIPT child 1, resource 175',
        'draft_inputs_sha256': inputs,
        'slice_ranges_inclusive': [[400, 479], [480, 559], [640, 719], [720, 799]],
        'examined_rows': {
            'ranges_inclusive': [[395, 484], [475, 564], [635, 724], [715, 804]],
            'assigned_row_count': 320,
            'context_rows_each_side': 5,
            'total_rows_examined_with_overlaps': 360,
        },
        'review_policy': 'Compared every requested draft row with its CP932 source and five adjacent rows at each slice edge. Corrections repair meaning, source-line boundaries, and actual row displacement; preference-only rewrites are omitted.',
        'not_reviewed': [[560, 639]],
        'corrections': corrections,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    document = build()
    print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'correction_count': len(document['corrections'])}))
    if args.write:
        OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
