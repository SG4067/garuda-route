/* Hero emblem: feather geometry for the left wing (the right wing is mirrored in the markup). */
(function (GR) {
  'use strict';
  GR.data = GR.data || {};

  GR.data.emblemWing = {
    shoulder: [292, 290],
    // Long primaries, outermost last. [tipX, tipY]
    primaries: {
      width: 20,
      tips: [
        [236, 420],
        [172, 384],
        [114, 334],
        [74, 272],
        [52, 206],
        [48, 138],
      ],
    },
    // Shorter coverts layered over the primaries.
    coverts: {
      width: 15,
      tips: [
        [248, 374],
        [206, 342],
        [166, 298],
        [136, 246],
        [126, 190],
      ],
    },
    leadingEdge: 'M292 288C238 224 146 170 48 138',
  };
})((window.GR = window.GR || {}));
