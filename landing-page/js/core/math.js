/* Small numeric helpers. */
(function (GR) {
  'use strict';

  GR.clamp = (v, min = 0, max = 1) => Math.min(max, Math.max(min, v));
  GR.lerp = (a, b, t) => a + (b - a) * t;

  /** Cubic ease-in-out for t in 0..1. */
  GR.ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

  GR.round1 = (n) => Math.round(n * 10) / 10;

  /** Deterministic PRNG (mulberry32) so generated artwork is identical on every load. */
  GR.seededRandom = (seed) => () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  /** 0..1 progress of an element entering the viewport from below, over `span` viewport-heights. */
  GR.enterProgress = (el, vh, span = 0.5) => {
    const top = el.getBoundingClientRect().top;
    return GR.clamp((vh * 0.98 - top) / (vh * span));
  };
})((window.GR = window.GR || {}));
