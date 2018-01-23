#! /usr/bin/env python3
import asyncio
import sys
import websockets

from xogame import *
from ws import *


async def handle_opponent_move(ws, game, opponent):
    print('Waiting for opponent move...')
    has_moved = False
    while not has_moved:
        try:
            move_resp = await ws.recv()
            move = int(move_resp['info']['move'])
            game.move(opponent, move)
            has_moved = True
        except GameError as ge:
            print('Unexpected condition:', ge)

    print('Opponent\'s move>', move)
    draw(game.board)
    return move_resp['info']['game_state']


async def send_own_move(ws, move):
    await ws.send({'type': 'move', 'move': move})
    move_resp = await ws.recv()
    if 'error' in move_resp:
        print('Error!', move_resp)
    else:
        return move_resp['success']['game_state']


async def game_client(game_id=None):
    async with websockets.connect('ws://localhost:8765') as websocket:
        ws = WS(websocket)
        print('Connected to / (asking for stats)')
        await ws.send({'type': 'stats'})
        stats_response = await ws.recv()
        print('Stats:', stats_response)

    if game_id is None:
        async with websockets.connect('ws://localhost:8765') as websocket:
            ws = WS(websocket)
            print('Connected to /')
            await ws.send({'type': 'new_game'})
            response = await ws.recv()
            print('Got message:', response)
            game_id = response['success']['game_id']

    async with websockets.connect('ws://localhost:8765/%s' % game_id) as websocket:
        ws = WS(websocket)
        print('Connected to /%s' % game_id)
        await ws.send({'type': 'join', 'preferred_side': 1})

        join_resp = await ws.recv()
        side = join_resp['success']['side']
        print('\n'.join(join_resp['success']['messages']))

        if join_resp['success']['type'] == 'wait_opponent':
            join_resp = await ws.recv()

        print('Game started!')

        game = XOGame()
        state = {'type': 'in_progress'}

        while state['type'] == 'in_progress':
            if side != game.turn:
                state = await handle_opponent_move(ws, game, 1 - side)
                continue

            has_moved = False
            while not has_moved:
                print('Your move> ', end='')
                try:
                    move = int(input())
                    game.move(side, move)
                    has_moved = True
                except GameError as ge:
                    print(ge)

            draw(game.board)
            state = await send_own_move(ws, move)  # TODO: Try validating move on the server

        print('=' * 20)
        if state['winner'] == -1:
            print('It\'s a draw!')
        elif state['winner'] == side:
            print('Congradulations, you won!')
        elif state['winner'] == 1 - side:
            print('Sorry, you lost!')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(game_client(sys.argv[1] if len(sys.argv) > 1 else None))