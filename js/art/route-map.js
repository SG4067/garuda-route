/* Renders the illustrative route diagram: street texture, arterials, routes and flagged locations. */
(function (GR) {
  'use strict';

  /** Seeded, slightly broken grid of streets, split into minor and major strokes. */
  function streetTexture(cfg) {
    const rand = GR.seededRandom(cfg.seed);
    const r1 = GR.round1;
    const [x0, x1] = cfg.extent.x,
      [y0, y1] = cfg.extent.y;
    let minor = '',
      major = '';

    // Lay one street as a run of segments with occasional small gaps.
    const run = (from, to, build) => {
      let pos = from,
        d = '';
      while (pos < to) {
        const len = 60 + rand() * 220;
        const gap = rand() < 0.3 ? 6 + rand() * 26 : 0;
        d += build(pos, len);
        pos += len + gap;
      }
      return d;
    };

    let n = 0;
    for (let c = x0; c < x1; c += cfg.spacing.vertical) {
      n++;
      if (rand() < 0.1) continue;
      const d = run(y0, y1, (y, len) => `M${r1(c + (rand() - 0.5) * 3)} ${r1(y)}V${r1(y + len)}`);
      if (n % 5 === 0) major += d;
      else minor += d;
    }
    n = 0;
    for (let c = y0; c < y1; c += cfg.spacing.horizontal) {
      n++;
      if (rand() < 0.1) continue;
      const d = run(x0, x1, (x, len) => `M${r1(x)} ${r1(c + (rand() - 0.5) * 3)}H${r1(x + len)}`);
      if (n % 5 === 0) major += d;
      else minor += d;
    }
    return { minor, major };
  }

  GR.register(function buildRouteMap() {
    const data = GR.data.routeMap;
    const streets = GR.$('#mStreets');
    if (!streets) return;

    const { minor, major } = streetTexture(data.streets);
    const rotated = GR.svg('g', { transform: `rotate(${data.streets.angle} 500 400)` }, GR.svg('g', {}, streets));
    GR.svg('path', { d: minor, class: 'm-street' }, rotated);
    GR.svg('path', { d: major, class: 'm-street mj' }, rotated);

    const arterials = GR.$('#mArt');
    data.arterials.forEach((points) => {
      const d = GR.roundedPath(points, 20);
      GR.svg('path', { d, class: 'm-art-c' }, arterials);
      GR.svg('path', { d, class: 'm-art' }, arterials);
    });

    const direct = GR.roundedPath(data.directRoute, 22);
    const alternative = GR.roundedPath(data.alternativeRoute, 22);
    ['rFastC', 'rFast'].forEach((id) => GR.$('#' + id).setAttribute('d', direct));
    ['rAltG', 'rAltC', 'rAlt'].forEach((id) => GR.$('#' + id).setAttribute('d', alternative));

    const zones = GR.$('#mZones'),
      flags = GR.$('#mFlags');
    data.flaggedLocations.forEach(([x, y]) => {
      GR.svg('circle', { cx: x, cy: y, r: 40, class: 'zone' }, zones);
      const flag = GR.svg('g', { class: 'flag', transform: `translate(${x} ${y})` }, flags);
      GR.svg('circle', { r: 11, class: 'flag-pulse' }, flag);
      GR.svg('circle', { r: 8, class: 'flag-ring' }, flag);
      GR.svg(
        'path',
        {
          d: 'M-3 -3L3 3M3 -3L-3 3',
          stroke: '#E07B6F',
          'stroke-width': 1.6,
          'stroke-linecap': 'round',
          fill: 'none',
        },
        flag,
      );
    });
  });
})((window.GR = window.GR || {}));
