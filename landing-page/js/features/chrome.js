/* Page chrome driven by scroll: header hide/solid, progress hairline, section rail. */
(function (GR) {
  'use strict';

  GR.register(function initChrome() {
    const header = GR.$('#top');
    const progress = GR.$('#progress');
    const rail = GR.$('#rail');
    const railFill = GR.$('#railFill');
    const railLinks = GR.$$('#rail a');
    const sections = railLinks.map((a) => document.getElementById(a.dataset.sec));

    GR.loop.add(({ y, dy, vh, docHeight }) => {
      const pageProgress = GR.clamp(y / (docHeight - vh));

      // Header: solid once scrolled, tucked away while scrolling down, back on any upward scroll.
      header.classList.toggle('solid', y > 40);
      header.classList.toggle('hide', dy > 2 && y > vh * 0.6);
      if (dy < -2) header.classList.remove('hide');

      progress.style.transform = `scaleX(${pageProgress})`;

      // Rail: the active node is the last section whose top has passed mid-screen.
      let active = -1;
      sections.forEach((el, i) => {
        if (el && el.getBoundingClientRect().top < vh * 0.5) active = i;
      });
      railLinks.forEach((a, i) => a.classList.toggle('on', i === active));
      railFill.style.height = pageProgress * (rail.querySelector('ol').offsetHeight - 10) + 'px';
    });
  });
})((window.GR = window.GR || {}));
