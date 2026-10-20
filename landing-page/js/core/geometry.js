/* Path helpers for the generated SVG artwork. */
(function (GR) {
  'use strict';

  /**
   * Polyline through `points` with each interior corner rounded by a quadratic curve.
   * @param {number[][]} points  [[x, y], ...]
   * @param {number} radius      maximum corner radius
   */
  GR.roundedPath = (points, radius = 16) => {
    const r1 = GR.round1;
    let d = `M${points[0][0]} ${points[0][1]}`;

    for (let i = 1; i < points.length - 1; i++) {
      const [a, b, c] = [points[i - 1], points[i], points[i + 1]];
      const lenAB = Math.hypot(a[0] - b[0], a[1] - b[1]);
      const lenBC = Math.hypot(c[0] - b[0], c[1] - b[1]);
      const k = Math.min(radius, lenAB / 2, lenBC / 2);

      const inX = r1(b[0] + ((a[0] - b[0]) * k) / lenAB);
      const inY = r1(b[1] + ((a[1] - b[1]) * k) / lenAB);
      const outX = r1(b[0] + ((c[0] - b[0]) * k) / lenBC);
      const outY = r1(b[1] + ((c[1] - b[1]) * k) / lenBC);
      d += ` L${inX} ${inY} Q${b[0]} ${b[1]} ${outX} ${outY}`;
    }

    const last = points[points.length - 1];
    return `${d} L${last[0]} ${last[1]}`;
  };
})((window.GR = window.GR || {}));
