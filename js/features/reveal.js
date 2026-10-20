/* Scroll reveal: adds .in to .reveal / .heading / .diagram once they enter the viewport. */
(function (GR) {
  'use strict';

  GR.register(function initReveal() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('in');
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.18, rootMargin: '0px 0px -6% 0px' },
    );

    GR.$$('.reveal, .heading, .diagram').forEach((el) => observer.observe(el));

    // The hero intro waits for fonts so the headline never reveals in a fallback face.
    GR.fonts.ready.then(() =>
      setTimeout(() => {
        GR.$('.hero-copy').classList.add('in');
        GR.$$('.hero .reveal').forEach((el) => el.classList.add('in'));
      }, 80),
    );
  });
})((window.GR = window.GR || {}));
