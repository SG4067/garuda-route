/*
 * Hero scroll sequence. The hero is pinned for ~0.9 viewport-heights of scrolling (see sections/hero.css):
 *   0.00 - 0.40  headline and cue fade up and away
 *   0.00 - 0.62  emblem drifts to centre and grows
 *   0.00 - 0.85  wings lift, then settle
 *   0.46 - 1.00  wings and drop dissolve; the rings ripple outward
 * Progress is written to CSS custom properties on .emblem; the styling lives in sections/hero.css.
 */
(function (GR) {
  'use strict';

  const { clamp, ease, lerp } = GR;

  GR.register(function initHeroScroll() {
    const hero = GR.$('#hero'),
      pin = GR.$('.hero-pin'),
      copy = GR.$('#heroCopy'),
      emblem = GR.$('#emblem');
    const cue = GR.$('.cue'),
      note = GR.$('.hero-note');
    let tiltX = 0,
      tiltY = 0;

    GR.loop.add(({ y, vh }) => {
      const s = GR.state;
      tiltX = lerp(tiltX, s.mx, 0.06);
      tiltY = lerp(tiltY, s.my, 0.06);

      const p = GR.env.reduceMotion ? 0 : clamp(y / Math.max(1, hero.offsetHeight - vh));
      const copyOut = ease(clamp(p / 0.4));
      const drift = ease(clamp(p / 0.62));

      copy.style.transform = `translate3d(0,${(-copyOut * 70).toFixed(1)}px,0)`;
      copy.style.opacity = (1 - copyOut).toFixed(3);
      cue.style.opacity = note.style.opacity = clamp(1 - copyOut * 1.6).toFixed(3);

      // Distance from the emblem's resting place to the centre of the pinned frame (wide screens only).
      const shift = window.innerWidth >= 960 ? emblem.offsetLeft + emblem.offsetWidth / 2 - pin.clientWidth / 2 : 0;
      const flap = ease(clamp(p / 0.45)) - ease(clamp((p - 0.45) / 0.4));

      const set = (name, value) => emblem.style.setProperty(name, value);
      set('--mx', tiltX.toFixed(3));
      set('--my', tiltY.toFixed(3));
      set('--sp', drift.toFixed(3));
      set('--ex', (-shift * drift).toFixed(1) + 'px');
      set('--es', (1 + 0.34 * drift).toFixed(3));
      set('--fl', (flap * 10).toFixed(2));
      set('--dis', ease(clamp((p - 0.5) / 0.45)).toFixed(3));
      set('--dw', ease(clamp((p - 0.46) / 0.4)).toFixed(3));
    });
  });
})((window.GR = window.GR || {}));
