/* Pointer-driven micro-interactions: magnetic buttons and tilting screenshot cards. */
(function (GR) {
  'use strict';

  GR.register(function initInteractions() {
    if (!GR.env.finePointer || GR.env.reduceMotion) return;

    GR.$$('.magnetic').forEach((el) => {
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - r.left - r.width / 2) * 0.22;
        const dy = (e.clientY - r.top - r.height / 2) * 0.32;
        el.style.transform = `translate(${dx}px,${dy}px)`;
      });
      el.addEventListener('pointerleave', () => {
        el.style.transition = 'transform .6s cubic-bezier(.2,.8,.2,1), color .45s';
        el.style.transform = '';
        setTimeout(() => {
          el.style.transition = '';
        }, 600);
      });
    });

    GR.$$('.tilt-in').forEach((el) => {
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        el.style.setProperty('--tilty', (x * 14).toFixed(2) + 'deg');
        el.style.setProperty('--tiltx', (-y * 10).toFixed(2) + 'deg');
      });
      el.addEventListener('pointerleave', () => {
        el.style.setProperty('--tilty', '0deg');
        el.style.setProperty('--tiltx', '0deg');
      });
    });
  });
})((window.GR = window.GR || {}));
