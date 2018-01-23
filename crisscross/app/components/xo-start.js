import Component from '@ember/component';
import { inject } from '@ember/service';

export default Component.extend({
    game_service: inject('game'),
    stats_service: inject('stats'),
    router: inject(),
    game_id: null,

    WEBSOCKET_SUPPORT: ('WebSocket' in window),

    didReceiveAttrs() {
        this._super(...arguments);
        this.get('game_service').clear();
        this.set('stats_service.running', true);
    },

    willDestroyElement() {
        this._super(...arguments);
        this.set('stats_service.running', false);
    },

    actions: {
        start_new() {
            console.log('New game!');

            const router = this.get('router');
            const _ws = new WebSocket('ws://localhost:8765/');

            _ws.onopen = () => _ws.send(JSON.stringify({type: 'new_game'}));
            _ws.onmessage = (evt) => {
                const data = JSON.parse(evt.data);
                if ('success' in data) {
                    this.set('game_service.game_id', data.success.game_id);
                    router.transitionTo('xo-pick');
                } else {
                    alert('An error occurred!');
                    console.log(data);
                }
            };

        },

        join_existing() {
            console.log('Join existing!');
            const game_id = this.get('game_id');
            if (game_id && game_id.length == 8) {
                this.set('game_service.game_id', game_id);
                this.get('router').transitionTo('xo-wait');
            } else {
                alert('Incorrect battle code!');
            }
        }
    }
});
