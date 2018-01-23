import asyncio
import atexit
import enum
import json

from xogame import *


def rand_str(n, symbols=string.ascii_letters + string.digits):
    """Return a random string of length `n`"""
    return ''.join(random.choice(symbols) for _ in range(n))


class WSGame:
    def __init__(self):
        self.game = XOGame()
        self.game_id = rand_str(8)

        self.players = {}
        self.players_count = 0

        self.started = asyncio.Event()

    async def add_player(self, ws, player_id, side=None):
        if self.players_count == 2:
            raise GameError("Two players already connected!")

        elif self.players_count == 0:
            side = side or 0
            self.players[player_id] = side
            self.players_count += 1
            print('Adding player %d to game %s {%s}' % (player_id, self.game_id, self.players))

            await ws.send({'success': {'type': 'wait_opponent', 'side': side, 'messages': ['You successfuly joined the game as side %s.' % XOGame.SYMBOL[side], 'Waiting for the opponent...']}})
            await self.started.wait()
            await ws.send({'success': {'type': 'game_started', 'messages': ['Your opponent has joined the game.', 'The game can now start.']}})

        elif self.players_count == 1:
            side = 0 if 1 in self.players.values() else 1
            self.players[player_id] = side
            self.players_count += 1
            print('Adding player %d to game %s {%s}' % (player_id, self.game_id, self.players))

            await ws.send({'success': {'type': 'game_started', 'side': side, 'messages': ['You successfuly joined the game as side %s.' % XOGame.SYMBOL[side], 'The game can now start.']}})
            self.started.set()


class State:
    STATE_FILE = 'app_state.json'

    def __init__(self):
        self.connections = {}
        self.players_count = 0

        self.games = {}
        self.game_lock = asyncio.Lock()

        self._load_stats()

        atexit.register(lambda: self._save_stats)

    def _save_stats(self):
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.stats, f)

    def _load_stats(self):
        try:
            with open(self.STATE_FILE, 'r') as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            self.stats = {'games_active': 0, 'games_played': 0, 'wins_x': 0, 'wins_o': 0, 'draws': 0}

    def get_new_player_id(self):
        self.players_count += 1
        return self.players_count

    def register_player_connection(self, player_id, ws):
        self.connections[player_id] = ws

    async def create_game(self):
        await self.game_lock.acquire()

        wsgame = WSGame()
        self.games[wsgame.game_id] = wsgame

        self.stats['games_active'] += 1

        self.game_lock.release()
        return wsgame

    async def join_game(self, game_id, player_id, preferred_side=None):
        if game_id in self.games:
            await self.games[game_id].add_player(self.connections[player_id], player_id, preferred_side)
        else:
            await self.connections[player_id].send({'error': {'description': 'Unknown game, probably wrong code!'}})

    async def perform_move(self, game_id, player_id, move):
        wsgame = self.games[game_id]
        player_side = wsgame.players[player_id]
        other_player = [k for k, v in wsgame.players.items() if v == 1 - player_side][0]

        try:
            wsgame.game.move(player_side, move)
        except GameError as ge:
            await self.connections[player_id].send({'error': {'type': 'invalid_move', 'description': str(ge)}})

        game_state = {
            GameState.IN_PROGRESS: {'type': 'in_progress'},
            GameState.DRAW: {'type': 'finished', 'winner': -1},
            GameState.PLAYER_X_WIN: {'type': 'finished', 'winner': 0},
            GameState.PLAYER_O_WIN: {'type': 'finished', 'winner': 1}
        }[wsgame.game.state]

        if game_state['type'] == 'finished':
            self.stats['games_active'] -= 1
            self.stats['games_played'] += 1
            if game_state['winner'] == -1:
                self.stats['draws'] += 1
            elif game_state['winner'] == 0:
                self.stats['wins_x'] += 1
            elif game_state['winner'] == 1:
                self.stats['wins_o'] += 1

            self._save_stats()

        await self.connections[player_id].send({'success': {'type': 'your_move', 'move': move, 'game_state': game_state}})
        await self.connections[other_player].send({'info': {'type': 'opponent_move', 'move': move, 'game_state': game_state}})

    async def player_quit_game(self, player_id, game_id):
        if game_id in self.games:
            wsgame = self.games[game_id]
            player_side = wsgame.players[player_id]
            other_player = [k for k, v in wsgame.players.items() if v == 1 - player_side][0]

            del self.games[game_id]

            await self.connections[other_player].send({'info': {'type': 'opponent_quitted'}})

        del self.connections[player_id]
