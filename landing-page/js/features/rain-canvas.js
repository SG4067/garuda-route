/* Live background: layered rain streaks that land as ripples on a perspective "water plane". */
(function (GR) {
  'use strict';

  const MAX_DROPS = 260;
  const MAX_RIPPLES = 90;
  const drops = [];
  const ripples = [];
  let canvas,
    ctx,
    width = 0,
    height = 0;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function resetDrop(d, fromTop) {
    const far = Math.random() < 0.6;
    d.far = far;
    d.x = Math.random() * (width + 200) - 100;
    d.y = fromTop ? -Math.random() * height * 0.4 : Math.random() * height;
    d.speed = far ? 5 + Math.random() * 3 : 9 + Math.random() * 5;
    d.length = far ? 10 + Math.random() * 14 : 22 + Math.random() * 26;
    d.alpha = far ? 0.06 + Math.random() * 0.07 : 0.13 + Math.random() * 0.14;
    d.groundY = height * (0.42 + Math.random() * 0.56); // where this drop lands
    d.depth = d.groundY / height;
    return d;
  }

  function seedDrops() {
    drops.length = 0;
    for (let i = 0; i < MAX_DROPS; i++) drops.push(resetDrop({}, false));
  }

  /** @param {boolean} gold  pointer-made ripples are gold, rain ripples are pale green-grey */
  function addRipple(x, y, gold, depth) {
    if (ripples.length > MAX_RIPPLES) ripples.shift();
    ripples.push({
      x,
      y,
      r: 0,
      gold,
      max: (gold ? 44 : 14 + Math.random() * 22) * (0.5 + depth * 0.7),
      alpha: gold ? 0.5 : 0.24,
    });
  }

  function draw(vel) {
    const s = GR.state;
    ctx.clearRect(0, 0, width, height);
    s.rainLevel = GR.lerp(s.rainLevel, s.rainTarget, 0.04);

    const active = Math.round(GR.clamp((width * height) / 8500, 70, MAX_DROPS) * (0.25 + s.rainLevel * 0.9));
    const wind = -2.2 - vel * 0.12 - s.mx * 1.2;
    ctx.lineCap = 'round';

    for (let i = 0; i < Math.min(active, drops.length); i++) {
      const d = drops[i];
      d.y += d.speed;
      d.x += wind * (d.far ? 0.5 : 1);
      if (d.y >= d.groundY) {
        if (Math.random() < 0.55) addRipple(d.x, d.groundY, false, d.depth);
        resetDrop(d, true);
        continue;
      }
      ctx.strokeStyle = `rgba(226,230,218,${d.alpha})`;
      ctx.lineWidth = d.far ? 0.7 : 1.1;
      ctx.beginPath();
      ctx.moveTo(d.x, d.y);
      ctx.lineTo(d.x - wind * d.length * 0.35, d.y - d.length);
      ctx.stroke();
    }

    for (let i = ripples.length - 1; i >= 0; i--) {
      const p = ripples[i];
      p.r += p.gold ? 1.1 : 0.55;
      const t = p.r / p.max;
      if (t >= 1) {
        ripples.splice(i, 1);
        continue;
      }
      const a = p.alpha * (1 - t) * (1 - t);
      ctx.strokeStyle = p.gold ? `rgba(232,211,160,${a})` : `rgba(190,208,200,${a})`;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(p.x, p.y, p.r, p.r * 0.32, 0, 0, Math.PI * 2);
      ctx.stroke();
      if (t > 0.25) {
        ctx.beginPath();
        ctx.ellipse(p.x, p.y, p.r * 0.62, p.r * 0.2, 0, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
  }

  GR.rain = { addRipple };

  GR.register(function initRain() {
    canvas = GR.$('#bg');
    ctx = canvas.getContext('2d');
    resize();
    seedDrops();
    window.addEventListener('resize', () => {
      resize();
      seedDrops();
    });

    if (GR.env.reduceMotion) {
      // A single still frame of settled ripples; no animation.
      for (let i = 0; i < 14; i++) {
        const y = height * (0.5 + Math.random() * 0.45);
        addRipple(Math.random() * width, y, false, y / height);
        const last = ripples[ripples.length - 1];
        last.r = last.max * 0.4;
      }
      draw(0);
      return;
    }
    GR.loop.add((frame) => {
      if (!document.hidden) draw(frame.vel);
    });
  });
})((window.GR = window.GR || {}));
