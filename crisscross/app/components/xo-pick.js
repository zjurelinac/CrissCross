import Component from '@ember/component';
import { inject } from '@ember/service';

export default Component.extend({
    game_service: inject('game'),
    router: inject(),

    actions: {
        pick_x() {
            this.set('game_service.side', 0);
            this.get('router').transitionTo('xo-wait');
        },

        pick_o() {
            this.set('game_service.side', 1);
            this.get('router').transitionTo('xo-wait');
        }
    }
});
