/* Entry point. Every module has already registered itself; start them in load order. */
(function (GR) {
  'use strict';

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', GR.boot);
  } else {
    GR.boot();
  }
})(window.GR);
