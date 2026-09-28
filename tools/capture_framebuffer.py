"""Capture the next PSP display buffer from software-rendered VRAM; preview first."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import struct
import time
import zlib
from ppsspp_client import request, ROOT


def png_chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def capture(hold=False):
    status = request('cpu.status')
    if status['stepping']:
        raise ValueError('Resume the existing debugger stop before capturing')
    stats = request('gpu.stats.get')
    if 'Thread enqueues:' not in stats['info']:
        raise ValueError('This capture path requires the software renderer; launch with -Software')
    matches = [f for f in request('hle.func.list')['functions'] if f['name'] == 'zz_sceDisplaySetFrameBuf']
    if len(matches) != 1:
        raise ValueError('Expected exactly one display-buffer import')
    address = matches[0]['address']
    if request('cpu.breakpoint.list')['breakpoints']:
        raise ValueError('Existing debugger breakpoints must be cleared before this capture')
    request('cpu.breakpoint.add', address=address, enabled=True, log=False, condition='a0 != 0')
    stopped_by_us = False
    completed = False
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            status = request('cpu.status')
            if status['stepping']:
                stopped_by_us = status['pc'] == address
                break
            time.sleep(0.05)
        if not stopped_by_us:
            raise ValueError('Did not reach the next display-buffer call')
        regs = request('cpu.getAllRegs')['categories'][0]
        regs = dict(zip(regs['registerNames'], regs['uintValues']))
        framebuffer, stride, pixel_format, sync = (regs[n] for n in ('a0', 'a1', 'a2', 'a3'))
        if stride != 512 or pixel_format not in (0, 1, 2, 3) or not 0x04000000 <= framebuffer < 0x04200000:
            raise ValueError('Unsupported framebuffer parameters: ' + repr((framebuffer, stride, pixel_format)))
        width, height = 480, 272
        bytes_per_pixel = 4 if pixel_format == 3 else 2
        raw = base64.b64decode(request('memory.read', address=framebuffer, size=stride * height * bytes_per_pixel)['base64'])
        scanlines = bytearray()
        for y in range(height):
            scanlines.append(0)
            row = raw[y * stride * bytes_per_pixel:(y * stride + width) * bytes_per_pixel]
            for x in range(0, len(row), bytes_per_pixel):
                if pixel_format == 3:
                    scanlines.extend(row[x:x + 3])
                    continue
                value = struct.unpack_from('<H', row, x)[0]
                if pixel_format == 0:
                    rgb = ((value & 31) * 255 // 31, ((value >> 5) & 63) * 255 // 63, ((value >> 11) & 31) * 255 // 31)
                elif pixel_format == 1:
                    rgb = ((value & 31) * 255 // 31, ((value >> 5) & 31) * 255 // 31, ((value >> 10) & 31) * 255 // 31)
                else:
                    rgb = ((value & 15) * 17, ((value >> 4) & 15) * 17, ((value >> 8) & 15) * 17)
                scanlines.extend(rgb)
        png = b'\x89PNG\r\n\x1a\n'
        png += png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
        png += png_chunk(b'IDAT', zlib.compress(bytes(scanlines)))
        png += png_chunk(b'IEND', b'')
        evidence = {'method': 'software VRAM at sceDisplaySetFrameBuf', 'game': request('game.status')['game'],
                    'framebuffer_address': hex(framebuffer), 'stride_pixels': stride, 'pixel_format': pixel_format,
                    'width': width, 'height': height, 'sync': sync, 'display_import_address': hex(address),
                    'png_bytes': len(png), 'png_sha256': hashlib.sha256(png).hexdigest()}
        evidence['cpu_left_stepping'] = bool(hold)
        completed = True
        return png, evidence
    finally:
        request('cpu.breakpoint.remove', address=address)
        if stopped_by_us and (not hold or not completed):
            request('cpu.resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--hold', action='store_true', help='Leave the captured game paused for inspection')
    args = parser.parse_args()
    target = args.output.resolve()
    if ROOT not in target.parents or target.suffix.lower() != '.png':
        raise ValueError('Output must be a PNG inside this workspace')
    if target.exists() or target.with_suffix('.json').exists():
        raise ValueError('Refusing to overwrite an existing capture')
    png, evidence = capture(hold=args.hold)
    print(json.dumps(dict(evidence, mode='write' if args.write else 'dry run', output=str(target)), indent=2))
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(png)
        target.with_suffix('.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
