/* Builds the left wing of the hero emblem as layered, leaf-shaped feathers into #wingL. */
(function (GR) {
  'use strict';

  GR.register(function buildEmblemWing() {
    const group = GR.$('#wingL');
    if (!group) return;

    const { shoulder, primaries, coverts, leadingEdge } = GR.data.emblemWing;
    const [sx, sy] = shoulder;

    // A curved blade from the shoulder to a tip; `bulge` controls how fat it is.
    const feather = ([tx, ty], bulge) => {
      const mx = (sx + tx) / 2,
        my = (sy + ty) / 2;
      const dx = tx - sx,
        dy = ty - sy,
        len = Math.hypot(dx, dy);
      const nx = (-dy / len) * bulge,
        ny = (dx / len) * bulge;
      return `M${sx} ${sy}Q${mx + nx} ${my + ny} ${tx} ${ty}Q${mx - nx * 0.3} ${my - ny * 0.3} ${sx} ${sy}Z`;
    };

    primaries.tips.forEach((tip) =>
      GR.svg(
        'path',
        {
          d: feather(tip, primaries.width),
          fill: 'url(#wg)',
          stroke: '#C9A96B',
          'stroke-width': 1,
          'stroke-opacity': 0.9,
        },
        group,
      ),
    );

    coverts.tips.forEach((tip) =>
      GR.svg(
        'path',
        {
          d: feather(tip, coverts.width),
          fill: 'rgba(201,169,107,.07)',
          stroke: '#C9A96B',
          'stroke-width': 0.8,
          'stroke-opacity': 0.6,
        },
        group,
      ),
    );

    GR.svg('path', { d: leadingEdge, fill: 'none', stroke: '#E8D3A0', 'stroke-width': 1.5 }, group);
  });
})((window.GR = window.GR || {}));
