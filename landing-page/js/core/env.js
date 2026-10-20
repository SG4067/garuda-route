/* Namespace, environment flags and the boot registry. Must load first. */
(function (GR) {
  'use strict';

  const matches = (query) => window.matchMedia(query).matches;

  GR.env = {
    reduceMotion: matches('(prefers-reduced-motion: reduce)'),
    finePointer: matches('(hover: hover) and (pointer: fine)'),
  };

  /** Mutable state shared between features (pointer, scroll velocity, rain intensity). */
  GR.state = {
    mx: 0,
    my: 0, // pointer, normalised to -1..1
    px: -100,
    py: -100, // pointer, in pixels
    scrollVel: 0,
    rainLevel: 0.55, // eased value used by the canvas
    rainTarget: 0.55, // set by the rainfall dial
  };

  const initFns = [];

  /** Features register an init function; GR.boot() runs them in load order. */
  GR.register = (fn) => initFns.push(fn);

  GR.boot = () => {
    initFns.forEach((fn) => fn());
    GR.loop.start();
  };
})((window.GR = window.GR || {}));
