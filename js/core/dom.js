/* DOM + SVG helpers. */
(function (GR) {
  'use strict';

  const SVG_NS = 'http://www.w3.org/2000/svg';

  GR.$ = (selector, root = document) => root.querySelector(selector);
  GR.$$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  /** Create an SVG element with attributes, optionally appended to `parent`. */
  GR.svg = (tag, attrs = {}, parent) => {
    const el = document.createElementNS(SVG_NS, tag);
    Object.keys(attrs).forEach((name) => el.setAttribute(name, attrs[name]));
    if (parent) parent.appendChild(el);
    return el;
  };
})((window.GR = window.GR || {}));
