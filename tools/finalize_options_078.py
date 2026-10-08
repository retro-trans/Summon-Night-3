"""Bind visually reviewed Options captures to the unchanged 078 test image."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def main():
    dest = ROOT/'work/output/0.1.78'
    ui = ROOT/'work/ui/options_0.1.78'
    manifest = json.loads((dest/'manifest.json').read_text('utf8'))
    assert digest(dest/manifest['output_iso']) == manifest['output_sha256']
    cases = [
        ('Music Volume', 'browsing', 'musicBrowseFinal'),
        ('Music Volume', 'editing', 'musicEditFinal'),
        ('Event Voices', 'browsing', 'heldDown'),
        ('Event Voices', 'editing', 'heldVoicesEdit'),
        ('Forecast', 'browsing', 'heldForecast'),
        ('Forecast', 'editing', 'heldForecastEdit'),
        ('Cursor Direction', 'browsing', 'heldCursor'),
        ('Cursor Direction', 'editing', 'heldCursorEdit'),
        ('L/R Function', 'browsing', 'heldLR'),
        ('L/R Function', 'editing', 'heldLREdit'),
        ('Exit Options', 'title screen', 'exitOptions'),
    ]
    reviewed = []
    for label, mode, name in cases:
        png = ui/'reviewed'/f'{name}.png'
        data = json.loads(png.with_suffix('.json').read_text('utf8'))
        assert digest(png) == data['png_sha256']
        assert data['width'] == 480 and data['height'] == 272
        assert data['session']['iso_sha256'] == manifest['output_sha256']
        reviewed.append(dict(label=label, mode=mode, visual_review_passed=True,
            screenshot=png.relative_to(ROOT).as_posix(), png_sha256=digest(png),
            capture_report_sha256=digest(png.with_suffix('.json'))))
    log = (ROOT/'work/scratch/options078-final/runtime.log').read_text('utf8', errors='replace')
    assert 'Bad Execution Address' not in log and 'Game crashed' not in log
    report = dict(version='0.1.78', passed=True, iso_sha256=manifest['output_sha256'],
        emulator='Windows PPSSPP 1.20.4', renderer='software', cpu='JIT',
        fresh_boot=True, entry='title-screen Options', normal_save_loaded=False,
        save_state_used=False, game_memory_writes=False,
        capture_breakpoints_removed=True, emulator_instances=1,
        emulator_closed_after_validation=True, audio_enabled=True,
        audio_playback_validated=False, host_audio_init_error=True,
        reviewed_cases=reviewed, runtime_log_sha256=hashlib.sha256(log.encode()).hexdigest(),
        limitations=['No direct Android device test', 'Scoped Options check, not full gameplay regression'])
    payload = json.dumps(report, indent=2)+'\n'
    (dest/'runtime-validation.json').write_text(payload, encoding='utf8')
    (ui/'runtime-validation.json').write_text(payload, encoding='utf8')
    (ui/'asset-validation.json').write_bytes((dest/'asset-validation.json').read_bytes())
    manifest['static_validation']['runtime_verified'] = True
    manifest['options078_validation'] = dict(
        runtime_report_sha256=digest(dest/'runtime-validation.json'),
        asset_report_sha256=digest(dest/'asset-validation.json'), reviewed_case_count=len(cases))
    (dest/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(passed=True, visually_reviewed_cases=len(cases))))


if __name__ == '__main__':
    main()
