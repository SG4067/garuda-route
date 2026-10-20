/* Stat rows and "Candour" rows flip up from the page plane as they enter (--p: 0..1). */
(function (GR) {
  'use strict';

  GR.register(function initDepthRows() {
    if (GR.env.reduceMotion) return; // CSS shows them flat and fully visible
    const stats = GR.$$('.stat'),
      limits = GR.$$('.limit');

    GR.loop.add(({ vh }) => {
      stats.forEach((el) => el.style.setProperty('--p', GR.ease(GR.enterProgress(el, vh, 0.55)).toFixed(3)));
      limits.forEach((el) => el.style.setProperty('--p', GR.ease(GR.enterProgress(el, vh, 0.5)).toFixed(3)));
    });
  });
})((window.GR = window.GR || {}));
