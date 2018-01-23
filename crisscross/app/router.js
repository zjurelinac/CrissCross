import EmberRouter from '@ember/routing/router';
import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType,
  rootURL: config.rootURL
});

Router.map(function() {
  this.route('xo-start', { path: '/' });
  this.route('xo-pick', { path: '/pick' });
  this.route('xo-wait', { path: '/wait' });
  this.route('xo-game', { path: '/play' });
});

export default Router;
