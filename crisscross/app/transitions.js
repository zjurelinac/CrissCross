export default function(){
  this.transition(
    this.fromRoute('xo-start'),
    this.toRoute('xo-pick'),
    this.use('toLeft'),
    this.reverse('toRight')
  );

  this.transition(
    this.fromRoute('xo-pick'),
    this.toRoute('xo-wait'),
    this.use('toLeft'),
    this.reverse('toRight')
  );

  this.transition(
    this.fromRoute('xo-start'),
    this.toRoute('xo-wait'),
    this.use('toLeft'),
    this.reverse('toRight')
  );

  this.transition(
    this.fromRoute('xo-wait'),
    this.toRoute('xo-game'),
    this.use('toLeft'),
    this.reverse('toRight')
  );

  this.transition(
    this.fromRoute('xo-game'),
    this.toRoute('xo-start'),
    this.use('toRight'),
    this.reverse('toLeft')
  );
}
