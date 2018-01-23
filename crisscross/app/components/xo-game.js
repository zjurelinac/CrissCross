import Component from '@ember/component';
import { inject } from '@ember/service';
import { computed, observer } from '@ember/object';
import { later } from '@ember/runloop';

const SYMBOL_TABLE = { 0: 'X', 1: 'O' };

export default Component.extend({
    game_service: inject('game'),
    router: inject(),

    side_symbol: computed('game_service.side', function() {
        const side = this.get('game_service.side');
        if (side == null) return null;
        return side == 0 ? 'X' : 'O';
    }),

    board: computed('game_service.board.[]', function() {
        const gsboard = this.get('game_service.board');
        if (gsboard == null) return null;
        let board = gsboard.map(x => x == -1 ? '' : SYMBOL_TABLE[x]);
        console.log('Recomputing ', gsboard, '->', board);
        return board;
    }),

    end_observer: observer('game_service.finished', function() {
        later(this, function() { this.get('router').transitionTo('xo-start'); }, 5000);
    }),

    actions: {
        move(pos) {
            if (this.get('game_service.allow_move'))
                this.get('game_service').move(pos);
        }
    }
});
