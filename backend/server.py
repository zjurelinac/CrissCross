#! /usr/bin/env python3

import asyncio
import functools
import websockets

from ws import *
from state import State


STATE = State()


async def player_quit(player_id, game_id):
    print('Player %d quitted game %s' % (player_id, game_id))
    await STATE.player_quit_game(player_id, game_id)


async def index_handler(request, ws):
    if request['type'] == 'new_game':
        game = await STATE.create_game()
        print('Created new game %s' % game.game_id)
        await ws.send({'success': {'type': 'game_created', 'game_id': game.game_id}})
    elif request['type'] == 'stats':
        await ws.send({'info': {'type': 'stats_report', 'stats': STATE.stats}})
    else:
        raise TypeError('Unknown request type')


async def game_handler(request, _, game_id, player_id):
    if request['type'] == 'join':
        await STATE.join_game(game_id, player_id, request.get('preferred_side', None))
    elif request['type'] == 'move':
        await STATE.perform_move(game_id, player_id, request.get('move'))
    elif request['type'] == 'quit':
        await player_quit(player_id, game_id)
    else:
        raise TypeError('Unknown request type')


async def game_server(websocket, path):
    print('New client connected to %s' % path)

    ws = WS(websocket)

    if path == '/':
        await ws.serve(index_handler)
    elif path[1:] in STATE.games:
        game_id = path[1:]
        player_id = STATE.get_new_player_id()
        STATE.register_player_connection(player_id, ws)
        ws.close_handler = functools.partial(player_quit, player_id=player_id, game_id=game_id)
        await ws.serve(functools.partial(game_handler, game_id=game_id, player_id=player_id))
    else:
        await ws.send({'error': {'description': 'Unknown route path'}})


asyncio.get_event_loop().run_until_complete(websockets.serve(game_server, 'localhost', 8765))

print('XO game server started.')

asyncio.get_event_loop().run_forever()
