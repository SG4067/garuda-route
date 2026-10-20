/* System overview, taken from the repository's architecture notes. 1200 x 520 viewBox. */
(function (GR) {
  'use strict';
  GR.data = GR.data || {};

  GR.data.systemDiagram = {
    nodeSize: { width: 224, height: 74 },
    // badgeTone: '' (gold) | 'dim' | 'ox' (gated). highlight: outlines the node in gold.
    nodes: {
      records: { x: 30, y: 40, title: 'Historical records', sub: 'bundled JSON · 10 events', badge: 'Bundled' },
      dashboard: { x: 336, y: 190, title: 'Browser dashboard', sub: 'map · alerts · history', highlight: true },
      maps: {
        x: 642,
        y: 40,
        title: 'Google Maps routes',
        sub: 'route comparison',
        badge: 'Optional',
        badgeTone: 'dim',
      },
      backend: { x: 642, y: 190, title: 'Node backend', sub: 'same-origin proxies' },
      imd: {
        x: 946,
        y: 110,
        title: 'IMD district endpoints',
        sub: 'warnings · rainfall',
        badge: 'Permission required',
        badgeTone: 'ox',
      },
      riskApi: {
        x: 946,
        y: 290,
        title: 'Separate risk API',
        sub: 'M3 API contract',
        badge: 'Runs separately',
        badgeTone: 'dim',
      },
      observations: { x: 30, y: 400, title: 'Rainfall observations', sub: 'simulated in the repo' },
      engine: { x: 336, y: 400, title: 'Python M3 risk engine', sub: 'tracker · comparator', highlight: true },
      assessment: { x: 642, y: 400, title: 'Road risk assessment', sub: 'needs road mappings' },
    },
    // [from, to, tone]
    edges: [
      ['records', 'dashboard', ''],
      ['dashboard', 'maps', 'dim'],
      ['dashboard', 'backend', ''],
      ['backend', 'imd', 'ox'],
      ['backend', 'riskApi', 'dim'],
      ['observations', 'engine', ''],
      ['engine', 'assessment', ''],
    ],
  };
})((window.GR = window.GR || {}));
