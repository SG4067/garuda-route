/* Screenshot cards open from a stacked, angled pile into a flat row as the section scrolls in. */
(function (GR) {
  'use strict';

  // Closed-pile pose per card: [rotateY deg, translateX px, translateZ px].
  const CLOSED = [
    [36, 150, -120],
    [0, 0, 90],
    [-36, -150, -120],
  ];

  GR.register(function initGalleryFan() {
    const fan = GR.$('#fan');
    const cards = GR.$$('.card', fan);
    if (cards.length !== CLOSED.length) return;

    GR.loop.add(({ vh }) => {
      const open = GR.env.reduceMotion
        ? 1
        : GR.ease(GR.clamp((vh * 1.05 - fan.getBoundingClientRect().top) / (vh * 0.9)));
      const k = 1 - open;
      cards.forEach((card, i) => {
        const [ry, tx, tz] = CLOSED[i];
        card.style.setProperty('--ry', (ry * k).toFixed(2) + 'deg');
        card.style.setProperty('--tx', (tx * k).toFixed(1) + 'px');
        card.style.setProperty('--tz', (tz * k).toFixed(1) + 'px');
      });
    });
  });
})((window.GR = window.GR || {}));
