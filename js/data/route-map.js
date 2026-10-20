/* Illustrative route diagram. Coordinates are in a 1000 x 800 viewBox and are NOT real geography. */
(function (GR) {
  'use strict';
  GR.data = GR.data || {};

  GR.data.routeMap = {
    // Neighbourhood street texture (rotated grid, seeded so it never changes between loads).
    streets: {
      seed: 21,
      angle: -14,
      extent: { x: [-260, 1260], y: [-260, 1060] },
      spacing: { vertical: 26, horizontal: 22 },
    },
    // Arterial roads, drawn over the street texture.
    arterials: [
      [
        [-10, 250],
        [300, 260],
        [560, 240],
        [1010, 230],
      ],
      [
        [-10, 640],
        [300, 650],
        [760, 610],
        [1010, 620],
      ],
      [
        [250, -10],
        [270, 300],
        [300, 650],
        [290, 810],
      ],
      [
        [560, -10],
        [550, 240],
        [560, 400],
        [540, 810],
      ],
      [
        [800, -10],
        [790, 230],
        [800, 420],
        [770, 610],
        [790, 810],
      ],
      [
        [130, 640],
        [330, 520],
        [500, 420],
        [545, 335],
        [700, 250],
      ],
    ],
    directRoute: [
      [130, 640],
      [330, 520],
      [500, 420],
      [545, 335],
      [700, 250],
      [870, 170],
    ],
    alternativeRoute: [
      [130, 640],
      [250, 700],
      [520, 720],
      [760, 610],
      [800, 420],
      [830, 270],
      [870, 170],
    ],
    // Flagged locations: two sit on the direct route, one beside the alternative.
    flaggedLocations: [
      [545, 335],
      [360, 505],
      [640, 590],
    ],
  };
})((window.GR = window.GR || {}));
