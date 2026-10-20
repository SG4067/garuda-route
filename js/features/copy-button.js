/* "Copy" button on the quick-start terminal block. */
(function (GR) {
  'use strict';

  const COMMANDS = [
    'git clone https://github.com/SG4067/garuda-route.git',
    'cd garuda-route',
    'node backend/server.js',
  ].join('\n');

  GR.register(function initCopyButton() {
    const button = GR.$('#copyBtn');
    if (!button) return;

    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(COMMANDS);
        button.textContent = 'Copied';
      } catch (err) {
        button.textContent = 'Select & copy'; // clipboard API unavailable (e.g. file://)
      }
      setTimeout(() => {
        button.textContent = 'Copy';
      }, 1800);
    });
  });
})((window.GR = window.GR || {}));
