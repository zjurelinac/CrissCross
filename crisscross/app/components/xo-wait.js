import Component from '@ember/component';
import { inject } from '@ember/service';
import { computed, observer } from '@ember/object';
import { later } from '@ember/runloop';

export default Component.extend({
    game_service: inject('game'),
    router: inject(),

    side_symbol: computed('game_service.side', function() {
        const side = this.get('game_service.side');
        if (side == null) return null;
        return side == 0 ? 'X' : 'O';
    }),

    didReceiveAttrs() {
        this._super(...arguments);
        this.get('game_service').connect();
    },

    game_state_observer: observer('game_service.state', function() {
        const state = this.get('game_service.state');
        if (state > 1)
            later(this, function() { this.get('router').transitionTo('xo-game'); }, 1000);
    })
});
