/*
 * Rainfall dial: a draggable gauge showing rainfall as a share of an event's reference value.
 * Levels (75% monitor, 100% high risk) are dashboard interface heuristics, not validated thresholds.
 * The dial also drives the intensity of the background rain.
 */
(function (GR) {
  'use strict';

  const CENTER = 200,
    RADIUS = 150;
  const MAX = 130; // dial runs 0..130 % of the reference value
  const START_ANGLE = 135,
    SWEEP = 270;
  const MONITOR_AT = 75,
    HIGH_AT = 100;
  const INITIAL = 62;
  const STATE_LABEL = { below: 'Below monitor', monitor: 'Monitor', high: 'High risk' };

  const angle = (v) => START_ANGLE + (v / MAX) * SWEEP;
  const point = (r, a) => [CENTER + r * Math.cos((a * Math.PI) / 180), CENTER + r * Math.sin((a * Math.PI) / 180)];

  function arc(r, from, to) {
    const a1 = angle(from),
      a2 = angle(to);
    const [x1, y1] = point(r, a1),
      [x2, y2] = point(r, a2);
    return `M${x1.toFixed(2)} ${y1.toFixed(2)}A${r} ${r} 0 ${a2 - a1 > 180 ? 1 : 0} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
  }

  function drawScale() {
    const segments = GR.$('#dSegs'),
      ticks = GR.$('#dTicks'),
      labels = GR.$('#dLabels');
    GR.svg('path', { d: arc(RADIUS, 0, MAX), stroke: 'rgba(214,190,140,.14)', 'stroke-width': 10 }, segments);
    GR.svg('path', { d: arc(RADIUS, 0, MONITOR_AT), stroke: 'rgba(111,156,152,.55)', 'stroke-width': 2 }, segments);
    GR.svg('path', { d: arc(RADIUS, MONITOR_AT, HIGH_AT), stroke: '#D9A441', 'stroke-width': 2 }, segments);
    GR.svg('path', { d: arc(RADIUS, HIGH_AT, MAX), stroke: '#B24A40', 'stroke-width': 2 }, segments);

    for (let v = 0; v <= MAX; v += 5) {
      const major = v % 25 === 0 || v === MAX;
      const [x1, y1] = point(RADIUS + 8, angle(v));
      const [x2, y2] = point(RADIUS + (major ? 17 : 13), angle(v));
      GR.svg(
        'line',
        {
          x1,
          y1,
          x2,
          y2,
          stroke: major ? '#C9A96B' : 'rgba(201,169,107,.4)',
          'stroke-width': major ? 1.2 : 0.8,
        },
        ticks,
      );
    }

    [0, MONITOR_AT, HIGH_AT, MAX].forEach((v) => {
      const [x, y] = point(RADIUS + 34, angle(v));
      GR.svg('text', { x, y: y + 3 }, labels).textContent = String(v);
    });
  }

  // Two offset sine waves; `t60 0` repeats the curve so the CSS slide loops seamlessly.
  function drawWaves() {
    let wave = '';
    for (let i = 0; i < 9; i++) wave += i === 0 ? 'q30 -9 60 0' : 't60 0';
    GR.$('#w1').setAttribute('d', `M-120 0${wave}L520 220L-120 220Z`);
    GR.$('#w2').setAttribute('d', `M-100 4${wave}L520 220L-100 220Z`);
  }

  GR.register(function initRainfallDial() {
    const host = GR.$('#clock');
    if (!host) return;

    const input = GR.$('#rain'),
      svg = GR.$('#dial');
    const progress = GR.$('#dProg'),
      handle = GR.$('#dHandle');
    const valueEl = GR.$('#dVal'),
      stateEl = GR.$('#dState'),
      water = GR.$('#waterG');

    drawScale();
    drawWaves();

    const waterY = (v) => 304 - (v / MAX) * 208;
    let currentWaterY = waterY(INITIAL),
      targetWaterY = currentWaterY;

    function setValue(raw, fromInput) {
      const v = GR.clamp(Math.round(raw), 0, MAX);
      if (!fromInput) input.value = v;

      const state = v >= HIGH_AT ? 'high' : v >= MONITOR_AT ? 'monitor' : 'below';
      host.dataset.state = state;
      valueEl.textContent = v;
      stateEl.textContent = STATE_LABEL[state];

      const [hx, hy] = point(RADIUS, angle(v));
      handle.setAttribute('transform', `translate(${hx.toFixed(2)} ${hy.toFixed(2)})`);
      progress.setAttribute('d', v > 0 ? arc(RADIUS, 0, Math.max(v, 0.2)) : '');
      input.style.setProperty('--v', (v / MAX) * 100 + '%');
      input.setAttribute('aria-valuetext', `${v}% of the reference value, ${STATE_LABEL[state].toLowerCase()}`);

      targetWaterY = waterY(v);
      GR.state.rainTarget = 0.22 + (v / MAX) * 1.05; // heavier dial, heavier rain
    }

    input.addEventListener('input', () => setValue(+input.value, true));
    GR.$$('[data-set]').forEach((btn) => btn.addEventListener('click', () => setValue(+btn.dataset.set)));

    // Dragging the dial itself: convert pointer position to an angle on the 270 degree arc.
    let dragging = false;
    function valueFromPointer(e) {
      const r = svg.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width / 2),
        dy = e.clientY - (r.top + r.height / 2);
      let a = (Math.atan2(dy, dx) * 180) / Math.PI;
      if (a < 0) a += 360;
      if (a < START_ANGLE) a += 360;
      if (a > START_ANGLE + SWEEP) a = a > START_ANGLE + SWEEP + (360 - SWEEP) / 2 ? START_ANGLE : START_ANGLE + SWEEP;
      setValue(((a - START_ANGLE) / SWEEP) * MAX);
    }
    svg.addEventListener('pointerdown', (e) => {
      dragging = true;
      svg.setPointerCapture(e.pointerId);
      valueFromPointer(e);
    });
    svg.addEventListener('pointermove', (e) => {
      if (dragging) valueFromPointer(e);
    });
    ['pointerup', 'pointercancel'].forEach((type) =>
      svg.addEventListener(type, () => {
        dragging = false;
      }),
    );

    setValue(INITIAL);

    // Ease the water surface towards its target level.
    GR.loop.add(() => {
      currentWaterY = GR.lerp(currentWaterY, targetWaterY, 0.1);
      water.setAttribute('transform', `translate(0 ${currentWaterY.toFixed(2)})`);
    });
  });
})((window.GR = window.GR || {}));
