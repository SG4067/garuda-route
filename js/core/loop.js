/* One requestAnimationFrame loop shared by every scroll/pointer-driven feature. */
(function (GR) {
  'use strict';

  const tasks = [];
  let lastY = window.scrollY;

  function frame() {
    const y = window.scrollY;
    GR.state.scrollVel = GR.lerp(GR.state.scrollVel, y - lastY, 0.15);

    const ctx = {
      y,
      dy: y - lastY,
      vh: window.innerHeight,
      docHeight: document.documentElement.scrollHeight,
      vel: GR.state.scrollVel,
    };
    tasks.forEach((task) => task(ctx));

    lastY = y;
    requestAnimationFrame(frame);
  }

  GR.loop = {
    /** Register a per-frame callback. Receives { y, dy, vh, docHeight, vel }. */
    add: (task) => tasks.push(task),
    start: () => requestAnimationFrame(frame),
  };
})((window.GR = window.GR || {}));
