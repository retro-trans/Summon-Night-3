"""Workspace PPSSPP debugger client. Python 3.9+; writes/actions preview by default."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/vendor/websocket-client-1.9.2'))
import websocket


def request(event, **params):
    ticket = str(uuid.uuid4())
    connection = websocket.create_connection('ws://127.0.0.1:19380/debugger', timeout=15, suppress_origin=True)
    try:
        connection.send(json.dumps(dict(params, event=event, ticket=ticket)))
        while True:
            response = json.loads(connection.recv())
            if response.get('ticket') == ticket or (event in ('cpu.stepping', 'cpu.resume') and response.get('event') == event):
                if response.get('event') == 'error':
                    raise RuntimeError(response)
                return response
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    shot = sub.add_parser('screenshot')
    shot.add_argument('output', type=Path)
    shot.add_argument('--write', action='store_true')
    press = sub.add_parser('press')
    press.add_argument('button')
    press.add_argument('--frames', type=int, default=2)
    press.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.command == 'status':
        print(json.dumps({'version': request('version'), 'game': request('game.status'),
                          'cpu': request('cpu.status')}, indent=2))
    elif args.command == 'screenshot':
        stepping = request('cpu.status')['stepping']
        try:
            if not stepping:
                request('cpu.stepping')
            response = request('gpu.buffer.screenshot')
        finally:
            if not stepping:
                request('cpu.resume')
        payload = base64.b64decode(response['uri'].split(',', 1)[1])
        target = args.output.resolve()
        if ROOT not in target.parents:
            raise ValueError('Screenshot must stay in the workspace')
        print(json.dumps({'mode': 'write' if args.write else 'dry run', 'path': str(target),
                          'width': response['width'], 'height': response['height'],
                          'png_bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}, indent=2))
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(payload)
    elif args.command == 'press':
        print(json.dumps({'mode': 'execute' if args.execute else 'dry run',
                          'button': args.button, 'duration_frames': args.frames}))
        if args.execute:
            print(json.dumps(request('input.buttons.press', button=args.button, duration=args.frames)))


if __name__ == '__main__':
    main()
