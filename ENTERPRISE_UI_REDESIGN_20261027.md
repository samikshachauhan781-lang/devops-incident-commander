# Enterprise UI Redesign — October 27, 2026

## Summary
Full visual refresh of the DevOps Incident Commander frontend: indigo/slate design system, DM Sans typography, redesigned shell (sidebar, top bar), metric cards, incident feeds, and consistent page headers. Dashboard metrics now come from the **analytics API** and recent incidents from **sorted list API** (no fabricated stats).

## Visual changes
- **Design system**: Indigo primary palette, `shadow-card`, `page-stack` rhythm, refined badges
- **Layout**: Gradient app shell, premium dark sidebar with active indicator + AI assist callout
- **Dashboard**: Real demo incidents (e.g. Payment Gateway Timeout), platform health from `/health`
- **Pages updated**: Dashboard, Incidents, Incident Detail, Analytics, Timeline (+ shared Card/Button/Badge)

## Data integrity
- Removed fake “+12% from previous period” analytics copy
- Dashboard no longer filters only `status=open` (which hid demo variety)

## Tests
| Check | Result |
|-------|--------|
| `npm run build` | Pass |
| `npx playwright test browser-test.spec.ts` | 9/9 (after selector updates) |

## Sidebar layout (follow-up session)
- **Fixed** `position: fixed` sidebar at `100dvh`, `overflow: hidden` (no sidebar scrollbar)
- Main column uses `margin-left: var(--sidebar-current)` on desktop; **only** `.app-main-scroll` scrolls
- `body.app-layout-active { overflow: hidden }` prevents double document scroll
- Mobile drawer overlay; desktop collapse toggles `--sidebar-current` width

## Release polish (follow-up)
- Route-level code splitting + `manualChunks` — recharts ~413 KB, vendor ~363 KB, app entry ~24 KB (warning resolved)
- Responsive Playwright suite: 375 / 768 / 1280 / 1920 — 24 tests pass
- User menu button is visual-only (auth not implemented; sign-out uses sidebar control)

## Verification (2026-10-27 afternoon)
| Check | Result |
|-------|--------|
| `npm run build` | Pass |
| `npx playwright test browser-test.spec.ts` | 9/9 pass |
| `pytest test_app.py test_demo_mode.py` | 9 passed, 19 skipped (demo skips in pytest) |
| Sidebar overflow (CDP: scrollHeight === clientHeight) | Verified on dashboard |
