import Service from '@ember/service';
import { computed, observer } from '@ember/object';

const GAME_STATE = {
    UNINITIALIZED: -1,
    CONNECTING: 0,
    WAITING_START: 1,
    DOING_MOVE: 2,
    WAITING_CONFIRM: 3,
    WAITING_MOVE: 4,
    FINISHED: 5,
    INTERRUPTED: 6
};

export default Service.extend({
    game_id: null,

    state: GAME_STATE.UNINITIALIZED,
    board: null,
    side: null,
    turn: null,
    messages: [],
    move_error: null,
    winner: null,

    _ws: null,
    _pending_move: null,

    user_turn: computed('side', 'turn', function() {
        return this.get('side') != null && this.get('side') == this.get('turn');
    }),

    allow_move: computed('users_turn', 'state', '_pending_move', function() {
        return this.get('user_turn') && this.get('state') == GAME_STATE.DOING_MOVE && this.get('_pending_move') == null;
    }),

    finished: computed('winner', function() {
        return this.get('winner') != null;
    }),

    outcome_victory: computed('winner', function() {
        return this.get('winner') == this.get('side');
    }),

    outcome_loss: computed('winner', function() {
        return this.get('winner') == 1 - this.get('side');
    }),

    outcome_draw: computed('winner', function() {
        return this.get('winner') == -1;
    }),

    debug_state_observer: observer('state', function() {
        console.log('Game state change: ', this.get('state'),
                    '; turn = ', this.get('turn'),
                    '; side = ', this.get('side'),
                    '; user_turn = ', this.get('user_turn'),
                    '; allow_move = ', this.get('allow_move'),
                    '; winner = ', this.get('winner'),
                    '; finished = ', this.get('finished'),
                    '; outcome_victory = ', this.get('outcome_victory'),
                    '; outcome_loss = ', this.get('outcome_loss'),
                    '; outcome_draw = ', this.get('outcome_draw'),
                    '; _pending_move = ', this.get('_pending_move'),
                    '; move_error = ', this.get('move_error'));
    }),

    clear() {
        this.set('game_id', null);
        this.set('state', GAME_STATE.UNINITIALIZED);
        this.set('board', null);
        this.set('side', null);
        this.set('turn', null);
        this.set('messages', []);
        this.set('move_error', null);
        this.set('winner', null);
        this.set('_pending_move', null);

        if (this.get('_ws') != null) {
            this.get('_ws').close();
            this.set('_ws', null);
        }
    },

    connect() {
        const _ws = new WebSocket('ws://localhost:8765/' + this.get('game_id'));
        _ws.onopen = () => this._join_game();
        _ws.onmessage = (evt) => this._handle_message(evt);

        this.set('_ws', _ws);
    },

    move(position) {
        if (!this.get('allow_move')) {
            console.log('Attempted move when it\'s not allowed!');
            return;
        } else if (this.get('board')[position] != -1) {
            console.log('Position already occupied!');
            this.set('move_error', true);
            return;
        }
        this.set('_pending_move', position);
        this.set('move_error', null);
        this.set('state', GAME_STATE.WAITING_CONFIRM);
        this.get('_ws').send(JSON.stringify({type: 'move', move: position}));
    },

    end_game() {
        alert('Ending game!');
        console.log('Ending game.');
        this.get('_ws').close();
    },

    _init_game() {
        this.set('board', [-1, -1, -1, -1, -1, -1, -1, -1, -1]);
        this.set('turn', 0);
    },

    _join_game() {
        this._init_game();
        this.get('_ws').send(JSON.stringify({type: 'join', preferred_side: this.get('side')}));
        this.set('state', GAME_STATE.CONNECTING);
    },

    _perform_move(move, player) {
        let board = this.get('board').slice();
        board.set('' + move, player);

        console.log('Moving', board);
        this.set('board', board);
        this.set('turn', 1 - player);
    },

    _finish(game_state) {
        console.log('Finishing: ', game_state, game_state.winner);
        this.set('winner', game_state.winner);
        this.set('state', GAME_STATE.FINISHED);
    },

    _handle_message(evt) {
        const data = JSON.parse(evt.data);
        const state = this.get('state');
        console.log(state, data);

        if (data.info && data.info.type == 'opponent_quitted') {
            alert('Your opponent quitted!');
            return;
        }

        if (state == GAME_STATE.CONNECTING) {
            this.set('side', data.success.side);
            this.set('messages', data.success.messages);

            if (data.success.type == 'wait_opponent')
                this.set('state', GAME_STATE.WAITING_START);
            else if (data.success.type == 'game_started')
                this.set('state', this.get('turn') == this.get('side') ? GAME_STATE.DOING_MOVE : GAME_STATE.WAITING_MOVE);
            else
                console.log('Unknown message: ', data);

        } else if (state == GAME_STATE.WAITING_START) {
            this.set('messages', this.get('messages').concat(data.success.messages));

            if (data.success.type == 'game_started')
                this.set('state', this.get('turn') == this.get('side') ? GAME_STATE.DOING_MOVE : GAME_STATE.WAITING_MOVE);
            else
                console.log('Unknown message: ', data);

        } else if (state == GAME_STATE.WAITING_MOVE) {

            if (data.info && data.info.type == 'opponent_move') {
                this._perform_move(data.info.move, 1 - this.get('side'));

                if (data.info.game_state.type == 'in_progress')
                    this.set('state', GAME_STATE.DOING_MOVE);
                else
                    this._finish(data.info.game_state);
            }

        } else if (state == GAME_STATE.WAITING_CONFIRM) {

            if (data.success) {
                this._perform_move(data.success.move, this.get('side'));
                this.set('_pending_move', null);

                if (data.success.game_state.type == 'in_progress')
                    this.set('state', GAME_STATE.WAITING_MOVE);
                else
                    this._finish(data.success.game_state);
            } else {
                this.set('move_error', true);
            }
        }
    }
});
