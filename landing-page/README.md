# Garuda Route: landing page

A static landing page for [Garuda Route](https://github.com/SG4067/garuda-route), a rainfall-aware road
waterlogging dashboard for Kanpur and Gurugram. No build step, no dependencies, no network requests at runtime.

## Run it

Open `index.html` in a browser. Or serve the folder:

```bash
npx serve .          # or: python3 -m http.server 8080
```

## Structure

```
index.html
css/
  tokens.css          colour, type families, spacing, easing (custom properties)
  fonts.css           @font-face for the self-hosted fonts
  base.css            reset, document defaults, a11y helpers
  ambient.css         fixed layers: canvas, vignette, film grain, progress bar
  layout.css          section layout, headings, split columns
  reveal.css          scroll-reveal styles (only active when JS is present)
  components/         buttons, header, section rail, cursor, footer
  sections/           one file per page section; each sets its own display typeface
  reduced-motion.css  prefers-reduced-motion overrides
js/
  core/               namespace + boot registry, math, DOM/SVG helpers, geometry, shared rAF loop
  data/               geometry and diagram definitions (no logic)
  art/                generators that turn data into SVG (emblem wing, route map, system diagram)
  features/           one behaviour per file: rain canvas, cursor, hero/route/gallery scroll scenes, dial, ...
  main.js             boots every registered module
assets/
  fonts/              WOFF2 files + OFL licences
  img/                optimised screenshots (WebP) and the social cover
  svg/                logo mark, favicon, film-grain tile
```

### How the JavaScript fits together

Scripts are plain deferred files (not ES modules) so the page also works when opened from disk. They share one
namespace, `window.GR`. Each feature calls `GR.register(init)`; `main.js` runs the registered inits in load order
and starts a single `requestAnimationFrame` loop. Features that react to scroll or pointer add a per-frame callback
with `GR.loop.add(fn)` and write their progress to CSS custom properties, so the styling stays in the CSS.

Load order matters and is set in `index.html`: core, then data, then art, then features, then `main.js`.

### Typography

Each section has its own display face, set by custom properties at the top of its stylesheet
(`--disp`, `--em`, `--h2-size`, `--h2-ls`, `--h2-lh`). The shared `h2` rule in `css/layout.css` reads them.

## Accessibility and motion

- Skip link, landmarks, visible focus styles, labelled controls, keyboard-operable dial (native range input).
- `prefers-reduced-motion`: no animation; pinned scenes become normal static sections.
- The custom cursor only runs for fine pointers (mouse/trackpad), never on touch.

## Deploying

Everything is relative-path static files. For GitHub Pages, put this folder's contents in `docs/` (or the repo root)
and enable Pages. For link previews, change the `og:image` value in `index.html` to an absolute URL after deploying.

## Content and credits

Facts on the page come from the project README (10 event records, 7 locations, two cities; the 75% and 100% levels
are the dashboard's interface heuristics). The route diagram is illustrative, not real geography. Screenshots are from
the project repository. Fonts: see `assets/fonts/licenses/README.md`.
