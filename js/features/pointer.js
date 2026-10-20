/* Tracks the pointer for every feature that needs it (emblem tilt, rain wind, cursor). */
(function (GR) {
  'use strict';

  GR.register(function trackPointer() {
    const root = document.documentElement;
    window.addEventListener(
      'pointermove',
      (e) => {
        const s = GR.state;
        s.px = e.clientX;
        s.py = e.clientY;
        s.mx = (e.clientX / window.innerWidth) * 2 - 1;
        s.my = (e.clientY / window.innerHeight) * 2 - 1;
        root.classList.remove('cur-off');
      },
      { passive: true },
    );
  });
})((window.GR = window.GR || {}));
