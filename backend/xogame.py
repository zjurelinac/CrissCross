import enum
import random
import string


class GameState(enum.Enum):
    """Possible Tic-tac-toe game states"""
    INITIALIZED = 1
    IN_PROGRESS = 2
    PLAYER_X_WIN = 3
    PLAYER_O_WIN = 4
    DRAW = 5


class GameError(Exception):
    pass


class XOGame:
    """Tic-tac-toe game class"""
    SYMBOL = {0: 'X', 1: 'O'}
    EMPTY = '.'

    def __init__(self):
        self.board = [[self.EMPTY] * 3 for _ in range(3)]
        self.state = GameState.INITIALIZED
        self.turn = 0

    def move(self, player, position):
        """Perform a move by `player` on the `position`"""
        if self.state == GameState.INITIALIZED:
            self.state = GameState.IN_PROGRESS

        if self.state != GameState.IN_PROGRESS:
            raise GameError("Game not playable -> is in state: %s!" % self.state)

        if self.turn != player:
            raise GameError("Not this player's turn -> player %s!" % self.SYMBOL[player])

        x, y = position // 3, position % 3

        if self.board[x][y] != self.EMPTY:
            raise GameError("Cannot make this move -> position is already occupied!")

        self.board[x][y] = self.SYMBOL[player]
        self.turn = 1 - self.turn
        self.evaluate()

        return self.state

    def evaluate(self):
        """Evaluate game state - is a win, a draw, or still in progress?"""
        xboard = [[c == self.SYMBOL[0] for c in r] for r in self.board]
        oboard = [[c == self.SYMBOL[1] for c in r] for r in self.board]
        eboard = [[c == self.EMPTY for c in r] for r in self.board]

        if self._test_board(xboard):
            self.state = GameState.PLAYER_X_WIN
        elif self._test_board(oboard):
            self.state = GameState.PLAYER_O_WIN
        elif not any(any(r) for r in eboard):
            self.state = GameState.DRAW

    @staticmethod
    def _test_board(board):
        tboard = list(map(list, zip(*board)))
        diags = [[board[i][i] for i in range(3)], [board[i][2 - i] for i in range(3)]]
        return any(all(r) for r in board) or any(all(r) for r in tboard) or any(all(d) for d in diags)


def draw(board):
    print('\n-+-+-\n'.join('|'.join(r) for r in board))
