/* Warms every typeface at load so nothing swaps in mid-scroll; exposes a `ready` promise. */
(function (GR) {
  'use strict';

  const FACES = [
    '400 1em "Bodoni Moda"',
    'italic 400 1em "Bodoni Moda"',
    '1em "Pinyon Script"',
    '1em "Italiana"',
    '1em "Instrument Serif"',
    'italic 1em "Instrument Serif"',
    '1em Cinzel',
    '1em Marcellus',
    '1em Bellefair',
    '1em "Tenor Sans"',
    '300 1em "Hanken Grotesk"',
    '400 1em "Hanken Grotesk"',
  ];

  const MAX_WAIT_MS = 1500;
  let loading = Promise.resolve();

  if (document.fonts && document.fonts.load) {
    loading = Promise.all(FACES.map((face) => document.fonts.load(face).catch(() => null)));
  }

  // Never hold the intro hostage to a slow font: give up after MAX_WAIT_MS.
  GR.fonts = { ready: Promise.race([loading, new Promise((resolve) => setTimeout(resolve, MAX_WAIT_MS))]) };
})((window.GR = window.GR || {}));
