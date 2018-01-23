import Service, { inject } from '@ember/service';
import { computed, observer } from '@ember/object';

const WEBSOCKET_SUPPORT = 'WebSocket' in window;

export default Service.extend({
    poll: inject(),

    available: WEBSOCKET_SUPPORT,
    running: false,
    _connected: false,
    _collecting: false,

    init() {
        this._super(arguments);

        this.set('stats', {games_active: 0, games_played: 0, wins_x: 0, wins_o: 0, draws: 0});

        if (!WEBSOCKET_SUPPORT) {
            console.log('Websockets unsupported!');
            return;
        }

        const _ws = new WebSocket('ws://localhost:8765/');
        _ws.onopen = () => this.set('_connected', true);
        _ws.onclose = () => this.set('_connected', false);
        _ws.onmessage = (evt) => this.handle_message(evt);

        this.set('_ws', _ws);
    },

    start_stop_observer: observer('running', '_connected', function() {
        console.log('observing...', this.get('_connected'), this.get('running'));

        if (this.get('_connected') && this.get('running')) {
            console.log('Started collecting stats.');
            this.set('_collecting', true);

            this.query_server();
            this.get('poll').addPoll({interval: 1000, callback: () => this.query_server()});
        } else if (this.get('_collecting')) {
            console.log('Stopped collecting stats.');
            this.set('_collecting', false);

            this.get('poll').stopAll();
        }
    }),

    handle_message(evt) {
        const data = JSON.parse(evt.data);
        this.set('stats', data['info']['stats']);
    },

    query_server() {
        this.get('_ws').send(JSON.stringify({type: 'stats'}));
    }
});
