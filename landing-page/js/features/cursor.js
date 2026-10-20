/* Custom cursor: dot + lagging ring that labels what it hovers, and gold ripples on click/move. */
(function (GR) {
  'use strict';

  GR.register(function initCursor() {
    if (!GR.env.finePointer || GR.env.reduceMotion) return;

    const root = document.documentElement;
    const dot = GR.$('#curDot');
    const ring = GR.$('#curRing');
    const label = GR.$('span', ring);
    let rx = -100,
      ry = -100,
      lastRipple = 0;

    root.classList.add('has-cursor');
    document.addEventListener('mouseleave', () => root.classList.add('cur-off'));

    // Mode + label come from data-cursor / data-label on the hovered element.
    document.addEventListener('pointerover', (e) => {
      const target = e.target.closest ? e.target.closest('[data-cursor], a, button, input, summary') : null;
      if (!target) {
        ring.dataset.mode = '';
        label.textContent = '';
        return;
      }
      ring.dataset.mode = target.dataset.cursor || 'link';
      label.textContent = target.dataset.label || '';
    });

    window.addEventListener('pointerdown', (e) => {
      const pulse = document.createElement('span');
      pulse.className = 'click-ring';
      pulse.style.left = e.clientX + 'px';
      pulse.style.top = e.clientY + 'px';
      document.body.appendChild(pulse);
      pulse.addEventListener('animationend', () => pulse.remove());
      GR.rain.addRipple(e.clientX, e.clientY, true, e.clientY / window.innerHeight);
    });

    // The pointer leaves a faint gold wake in the rain.
    window.addEventListener(
      'pointermove',
      (e) => {
        const now = performance.now();
        if (now - lastRipple < 70) return;
        lastRipple = now;
        if (Math.random() < 0.55) GR.rain.addRipple(e.clientX, e.clientY, true, e.clientY / window.innerHeight);
      },
      { passive: true },
    );

    GR.loop.add(() => {
      const s = GR.state;
      rx = GR.lerp(rx, s.px, 0.17);
      ry = GR.lerp(ry, s.py, 0.17);
      dot.style.transform = `translate3d(${s.px}px,${s.py}px,0)`;
      ring.style.transform = `translate3d(${rx}px,${ry}px,0)`;
    });
  });
})((window.GR = window.GR || {}));
