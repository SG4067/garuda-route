/*
 * Route comparison scene: a pinned stage whose scroll progress p (0..1) drives
 *   plane tilt   rotateX 62deg -> 12deg over p 0 - 0.62
 *   direct route draws          p 0.00 - 0.26
 *   flagged locations appear    p 0.24 - 0.38
 *   drier route draws           p 0.56 - 0.90
 * and steps the caption list (1 / 2 / 3). Styling: sections/routes.css.
 */
(function (GR) {
  'use strict';

  const { clamp, ease, lerp } = GR;

  GR.register(function initRouteScene() {
    const scene = GR.$('#routes'),
      plane = GR.$('#plane'),
      steps = GR.$$('.step');

    GR.loop.add(({ vh }) => {
      const rect = scene.getBoundingClientRect();
      const p = GR.env.reduceMotion ? 1 : clamp(-rect.top / (rect.height - vh));
      const flatten = ease(clamp(p / 0.62));
      const direct = clamp(p / 0.26);

      const set = (name, value) => plane.style.setProperty(name, value);
      set('--rx', lerp(62, 12, flatten).toFixed(2) + 'deg');
      set('--rz', lerp(-22, -3, flatten).toFixed(2) + 'deg');
      set('--sc', lerp(0.86, 1, flatten).toFixed(3));
      set('--rf', ease(direct).toFixed(3));
      set('--rz2', ease(clamp((p - 0.24) / 0.14)).toFixed(3));
      set('--ra', ease(clamp((p - 0.56) / 0.34)).toFixed(3));
      set('--tf', direct > 0.35 ? 1 : 0);

      const step = p < 0.3 ? 1 : p < 0.56 ? 2 : 3;
      if (+scene.dataset.step !== step) {
        scene.dataset.step = step;
        steps.forEach((el, i) => el.classList.toggle('on', i === step - 1));
      }
    });
  });
})((window.GR = window.GR || {}));
