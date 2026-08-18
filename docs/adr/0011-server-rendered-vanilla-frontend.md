# ADR-0011: Server-rendered Jinja with vanilla JavaScript

- **Status:** Accepted
- **Date:** 2026-08-18 (documented retroactively)

## Context

DMX Life has four screens: a scene selection page and three setup pages
(network, fixtures, scenes). The scene page is a grid of buttons. The setup
pages are forms and sliders. There is one user, on a local network, usually on
a tablet or laptop at the back of the room.

## Decision

Render pages server-side with Jinja templates and enhance them with plain
JavaScript — no framework, no build step, no bundler, no `package.json`.

Each page loads exactly one page-specific script from `app/static/js/`
(`main.js`, `fixtures.js`, `scenes.js`, `network.js`), plus two shared ones
(`connection-status.js`, `dmx-monitor.js`). Scripts talk to the backend with
`fetch()` against JSON endpoints and manipulate the DOM directly. There is no
shared client-side state between scripts.

## Consequences

**Good:**

- No toolchain. Clone, `pip install -r requirements.txt`, run. Nothing to
  compile, nothing to keep up to date, no npm audit noise.
- Deployment is copying files; the PyInstaller build in `dmx-life.spec` bundles
  templates and static assets directly.
- Page loads are a single request with the scene state already rendered — the
  buttons show the correct highlights before any JavaScript runs.
- The whole frontend is small enough to read in one sitting.

**Bad:**

- **State is expressed twice** for the scene page: Jinja renders the initial
  `active` classes, and `main.js` recomputes them after every toggle. The two
  must agree, and keeping them in sync is manual — this was a real source of
  bugs when the layered model landed.
- **`scenes.js` and `fixtures.js` are large** (506 and 428 lines) and manage
  fixture lists, slider grids, link synchronisation, and DMX-map rendering by
  direct DOM manipulation. This is where the complexity of the app now lives,
  and it has no tests.
- Error handling is `alert()`, which is blocking and looks crude.
- No client-side routing or partial updates; every setup navigation is a full
  page load.

## Alternatives considered

- **React/Vue SPA.** Would centralise client state and make the scene grid
  trivially reactive, at the cost of a build step, a dependency tree, and a
  bundle to ship inside the PyInstaller binary. Not justified for four screens.
- **HTMX.** A good middle ground — server-rendered fragments would remove the
  duplicated highlight logic entirely, with one small script and no build step.
  Genuinely attractive if the frontend is ever revisited.
- **Server-Sent Events or WebSockets** for live state instead of polling. The
  DMX monitor currently polls `/api/dmx/values` once a second. Worth
  considering if more live views are added.
