#!/usr/bin/env python3
# pip install aiohttp
import asyncio, json, os, random
from aiohttp import web, WSMsgType

PORT = int(os.environ.get("PORT", 4600))
BASE = os.path.dirname(os.path.abspath(__file__))
WINS = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

rooms = {}

def check_win(b):
    for combo in WINS:
        a, bb, c = combo
        if b[a] and b[a] == b[bb] == b[c]:
            return combo
    return None

def new_code():
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    while True:
        code = ''.join(random.choices(chars, k=6))
        if code not in rooms:
            return code

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    room_id = None
    sym = None

    async for msg in ws:
        if msg.type != WSMsgType.TEXT:
            break
        try:
            data = json.loads(msg.data)
        except Exception:
            continue
        act = data.get('action')

        if act == 'create':
            room_id = new_code()
            rooms[room_id] = {
                'players': [ws],
                'board': [None] * 9,
                'current': 'X',
                'syms': {id(ws): 'X'},
                'scores': {'X': 0, 'O': 0, 'D': 0},
            }
            sym = 'X'
            await ws.send_json({'t': 'created', 'room': room_id, 'sym': 'X'})

        elif act == 'join':
            code = data.get('room', '').strip().upper()
            r = rooms.get(code)
            if not r or len(r['players']) >= 2:
                await ws.send_json({'t': 'error', 'msg': 'Room not found or already full'})
            else:
                room_id = code
                r['players'].append(ws)
                r['syms'][id(ws)] = 'O'
                sym = 'O'
                await ws.send_json({'t': 'joined', 'room': room_id, 'sym': 'O',
                    'board': r['board'], 'current': r['current'], 'scores': r['scores']})
                await r['players'][0].send_json({'t': 'opponent_joined'})

        elif act == 'move':
            if not room_id or room_id not in rooms:
                continue
            r = rooms[room_id]
            cell = data.get('cell')
            if not isinstance(cell, int) or r['current'] != sym or r['board'][cell]:
                continue
            r['board'][cell] = sym
            win = check_win(r['board'])
            if win:
                r['scores'][sym] += 1
                r['current'] = None
            elif all(r['board']):
                r['scores']['D'] += 1
                r['current'] = None
            else:
                r['current'] = 'O' if sym == 'X' else 'X'
            payload = {'t': 'move', 'cell': cell, 'sym': sym,
                       'board': r['board'], 'current': r['current'],
                       'win': win, 'scores': r['scores']}
            for p in r['players']:
                try:
                    await p.send_json(payload)
                except Exception:
                    pass

        elif act == 'reset':
            if not room_id or room_id not in rooms:
                continue
            r = rooms[room_id]
            r['board'] = [None] * 9
            r['current'] = 'X'
            for p in r['players']:
                try:
                    await p.send_json({'t': 'reset', 'scores': r['scores']})
                except Exception:
                    pass

    # Cleanup on disconnect
    if room_id and room_id in rooms:
        r = rooms[room_id]
        if ws in r['players']:
            r['players'].remove(ws)
        for p in r['players']:
            try:
                await p.send_json({'t': 'left'})
            except Exception:
                pass
        if not r['players']:
            del rooms[room_id]
    return ws

async def static_handler(request):
    path = request.match_info.get('path', '')
    if not path:
        path = 'index.html'
    fp = os.path.join(BASE, path)
    if os.path.isfile(fp):
        return web.FileResponse(fp)
    return web.FileResponse(os.path.join(BASE, 'index.html'))

app = web.Application()
app.router.add_get('/ws', ws_handler)
app.router.add_get('/{path:.*}', static_handler)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=PORT, access_log=None,
                print=lambda *a: print(f"tictactoe on :{PORT}", flush=True))
