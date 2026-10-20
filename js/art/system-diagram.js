/* Renders the system overview from GR.data.systemDiagram into #sysSvg. */
(function (GR) {
  'use strict';

  GR.register(function buildSystemDiagram() {
    const svg = GR.$('#sysSvg');
    if (!svg) return;

    const { nodes, edges, nodeSize } = GR.data.systemDiagram;
    const { width: w, height: h } = nodeSize;
    let order = 0; // staggers the fade-in via --k

    edges.forEach(([from, to, tone]) => {
      const a = nodes[from],
        b = nodes[to];
      const x1 = a.x + w,
        y1 = a.y + h / 2,
        x2 = b.x,
        y2 = b.y + h / 2;
      const dx = (x2 - x1) * 0.5;
      GR.svg(
        'path',
        {
          d: `M${x1} ${y1}C${x1 + dx} ${y1} ${x2 - dx} ${y2} ${x2} ${y2}`,
          class: `e ${tone}`.trim(),
          style: `--k:${order++}`,
        },
        svg,
      );
      GR.svg(
        'circle',
        { cx: x2, cy: y2, r: 3, class: 'e-dot', style: `--k:${order}`, fill: tone === 'ox' ? '#B24A40' : '' },
        svg,
      );
    });

    Object.values(nodes).forEach((node) => {
      const g = GR.svg(
        'g',
        { class: 'nd', transform: `translate(${node.x} ${node.y})`, style: `--k:${order++ * 0.6}` },
        svg,
      );
      GR.svg('rect', { width: w, height: h, class: node.highlight ? 'n-box hot' : 'n-box' }, g);
      GR.svg('text', { x: 18, y: 32, class: 'n-t' }, g).textContent = node.title;
      GR.svg('text', { x: 18, y: 54, class: 'n-s' }, g).textContent = node.sub;
      if (node.badge) {
        GR.svg('text', { x: 18, y: -10, class: `n-b ${node.badgeTone || ''}`.trim() }, g).textContent = node.badge;
      }
    });
  });
})((window.GR = window.GR || {}));
