# Feature Research

**Domain:** Personal health tracker — fasting, weight, and wellness logging
**Researched:** 2026-03-09
**Confidence:** HIGH (based on direct codebase audit + CONCERNS.md, supplemented by UX pattern research)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Guard: no duplicate active fasts | Users expect "start fast" to be safe; a second active fast silently corrupts data and hides the first | LOW | Backend: check `get_current_fast()` before `create_fast()`; return HTTP 409 if one already active. Frontend: `StartFast.vue` must check `/api/fasts/current` on load and disable the start button with a clear message if one is active |
| Error messages on fast actions | Ending a fast, submitting logs, deleting a fast — all currently swallow errors silently | LOW | `FastDetail.vue` `endFast`, `submitLog`, `confirmDeleteFast`, `submitMeal` all need `catch` blocks that set a visible error ref. Use inline banner (not browser `alert`) above the relevant form |
| Weight entry edit | Users log wrong values; no correction path exists in the UI or backend | MEDIUM | Requires new `PUT /api/weight/{id}` backend endpoint + Pydantic schema + inline edit row in `WeightView.vue`. Tap-to-edit pattern: row expands to show pre-filled input |
| Weight entry delete | Same as above — a wrong entry with no delete means the chart and trend are permanently polluted | LOW | New `DELETE /api/weight/{id}` backend endpoint. Frontend: swipe-to-reveal or long-press delete button on each row. Requires confirmation (destructive action) |
| History pagination / load-more | Currently hard-capped at 100 fasts with no UI indicator; users with >100 fasts silently lose history | LOW-MEDIUM | "Load more" button pattern preferred over infinite scroll for goal-oriented history browsing. Backend already supports `skip`/`limit`. Frontend: track `offset`, append results, show button only when a full page was returned |
| Correct `avg_duration_hours` in weekly stats | Stats view currently shows null for this field; visible gap destroys trust in the data | LOW | Fix `crud.get_weekly_summary()` to compute the average duration using existing `ended - started` logic per week bucket |
| Error feedback on weight log | `WeightView.vue` currently uses `alert()` for errors — jarring on mobile | LOW | Replace `alert()` with inline error message styled consistently with the rest of the app |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Inline weight edit without modal | Tap a row to edit in-place — faster than a modal for a single numeric field | LOW | Expand row into an editable input + save/cancel. No separate modal needed |
| Pagination count indicator | "Affichage de 1–20 sur 47" — tells user how many fasts are in the database | LOW | Requires a `GET /api/fasts/count` endpoint or a total count returned alongside the list |
| Optimistic UI on log submission | Show the log immediately in the list while the API call completes; revert on error | MEDIUM | Reduces perceived latency on mobile. Requires local ID placeholder and rollback logic |
| Weekly stats avg duration fix + display | The field exists in the schema and UI surface but is always null — fixing it surfaces genuine insight | LOW | Backend-only fix; UI already renders it once the value is non-null |
| Toast notification system | Replace all in-page error banners and success states with a shared composable (`useToast`) | MEDIUM | Single `ToastNotification.vue` component + composable registered at App level. Allows consistent success/error feedback across all views |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Infinite scroll on History | Feels modern, seamless | On mobile, infinite scroll loses scroll position on back-navigation (user loses their place in history); also harder to implement safely with filters active | "Charger plus" (load more) button: user controls when to load, position is preserved, simpler state management |
| Global Pinia/Vuex store for all data | Prevents redundant fetches, shares state | Adds architectural complexity that PROJECT.md explicitly deferred; the app is single-user with few views; stale-while-revalidate at view level is sufficient | Per-view fetch with loading states; only share active fast via existing `useOfflineStorage` composable |
| Modal for weight edit | Familiar pattern | Modals interrupt flow; a numeric edit in a table row benefits from in-place editing (one tap vs two taps + dismiss) | Expandable inline edit row |
| Soft-delete for fasts/weight | "Undo" capability | Adds schema complexity (requires `deleted_at` column, filtered queries everywhere); single-user app with no compliance requirement | Confirmation dialog before hard delete — already implemented for fasts, needed for weight |
| Rate limiting at app layer | Security hardening | `slowapi` adds a dependency; for a personal app behind nginx the OS/nginx level is more appropriate | Nginx `limit_req` directive in the reverse proxy config |

---

## Feature Dependencies

```
Weight entry edit [PUT /api/weight/{id}]
    └──requires──> Weight entry row expands in UI
                       └──requires──> WeightView identifies entry by id (already has it)

Weight entry delete [DELETE /api/weight/{id}]
    └──requires──> Confirmation dialog in WeightView
                       └──requires──> Nothing (pattern already exists in FastDetail delete)

History load-more
    └──requires──> Backend skip/limit (already works)
    └──requires──> Frontend offset state + append logic
                       └──enhances──> Filter by type (filter must reset offset on change)

Duplicate fast guard (backend 409)
    └──enhances──> StartFast.vue preflight check
                       └──requires──> /api/fasts/current (already exists)

Toast notification system
    └──enhances──> All error catch blocks (FastDetail endFast, submitLog, etc.)
    └──can replace──> inline error banners (optional refactor)

Weekly stats avg_duration_hours fix
    └──standalone──> No UI changes needed; field is already rendered when non-null
```

### Dependency Notes

- **Weight edit/delete require new backend endpoints:** `PUT /api/weight/{id}` and `DELETE /api/weight/{id}` do not exist. Frontend work is blocked until these are added. Both are straightforward CRUD additions to `crud.py` and `main.py`.
- **History pagination filter interaction:** If the user has filtered by type and then clicks "load more", the offset must apply to the filtered set. The current backend `get_fasts` does not support type filtering — it is done client-side on the full fetched set. Pagination either requires moving filtering to the backend or accepting that "load more" always loads unfiltered and client-side filter applies. The simpler path: move type filter to a backend query param.
- **Duplicate fast guard enhances StartFast but is independent:** The backend guard (HTTP 409 on `POST /api/fasts` when one is already active) must exist regardless of frontend UI check. Frontend preflight is a UX improvement on top of the backend constraint.
- **Error catch blocks are independent per function:** `endFast`, `submitLog`, `confirmDeleteFast`, and `submitMeal` can each be fixed independently in a single pass without dependencies between them.

---

## MVP Definition

### Must Fix (v1 — this milestone)

These are data integrity and trust issues. Without them, the app is unreliable for its primary use case.

- [ ] Guard against duplicate active fast — `POST /api/fasts` must return HTTP 409 if an active fast exists; `StartFast.vue` must reflect this state
- [ ] Error catch blocks in `FastDetail.vue` — `endFast`, `submitLog`, `confirmDeleteFast`, `submitMeal` must show error messages on failure
- [ ] Weight entry edit — `PUT /api/weight/{id}` backend + inline edit in `WeightView.vue`
- [ ] Weight entry delete — `DELETE /api/weight/{id}` backend + delete action in `WeightView.vue` with confirmation
- [ ] History pagination — "Charger plus" button with incrementing `skip`, replacing the fixed `getFasts(0, 100)` call
- [ ] Fix `avg_duration_hours` always null in weekly stats

### Add After (v1.x)

- [ ] Toast notification system — once error states are wired up, unify into a shared composable for consistency
- [ ] Backend type filter for fasts — required if history pagination is to work correctly alongside active type filter
- [ ] Pagination count indicator ("X sur Y") — quality-of-life, requires count endpoint or count-in-response

### Future Consideration (v2+)

- [ ] Optimistic UI on log submission — meaningful only after the core reliability issues are resolved
- [ ] Stale localStorage TTL for offline cache — nice to have, not blocking any primary flow

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Duplicate fast guard (backend 409 + UI) | HIGH — prevents data corruption | LOW | P1 |
| Error catch blocks in FastDetail | HIGH — currently silent failures on critical actions | LOW | P1 |
| Weight delete (`DELETE /api/weight/{id}` + UI) | HIGH — no correction path exists | LOW | P1 |
| Weight edit (`PUT /api/weight/{id}` + UI) | HIGH — same as delete | MEDIUM | P1 |
| History pagination (load-more) | MEDIUM — only affects users with >100 fasts, but silent data loss | LOW | P1 |
| Fix `avg_duration_hours` in weekly stats | MEDIUM — visible null in stats view, easy fix | LOW | P1 |
| Toast notification system | MEDIUM — UX consistency | MEDIUM | P2 |
| Backend type filter for fasts list | MEDIUM — enables correct paginated filtering | LOW | P2 |
| Pagination count indicator | LOW — informational UX polish | LOW | P3 |
| Optimistic UI on log submission | LOW — perceived performance improvement | MEDIUM | P3 |

**Priority key:**
- P1: Must have — data integrity or broken UX blocking primary workflows
- P2: Should have — polish and consistency
- P3: Nice to have — future consideration

---

## Competitor Feature Analysis

The following patterns are drawn from Zero (fasting app), Noom (weight tracking), and general fasting tracker UX analysis.

| Feature | Zero / Common Fasting Apps | Noom / Weight Apps | Our Approach |
|---------|---------------------------|-------------------|--------------|
| Duplicate fast prevention | One active fast enforced at server + UI | N/A | HTTP 409 backend guard + UI preflight check on dashboard |
| Weight entry correction | Edit and delete both present in all weight trackers | Tap entry → edit/delete options | Inline expand-to-edit row + delete with confirmation dialog |
| History navigation | Infinite scroll or paginated list with visible count | Paginated list | "Charger plus" button — preserves scroll position, compatible with existing client-side filter |
| Error feedback | Toast notifications for all API failures | Inline error messages | Inline error banners per form section; toast system as v1.x upgrade |
| Stats accuracy | All stats fields populated | All weight fields populated | Fix `avg_duration_hours`; no other null fields in stats |

---

## Sources

- Codebase audit: `.planning/codebase/CONCERNS.md` (2026-03-09) — HIGH confidence, direct code inspection
- Project requirements: `.planning/PROJECT.md` — HIGH confidence
- UX pattern research: [Pagination vs Infinite Scroll vs Load More](https://ashishmisal.medium.com/pagination-vs-infinite-scroll-vs-load-more-data-loading-ux-patterns-in-react-53534e23244d) — MEDIUM confidence
- Error state design: [NN/g Error Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) — MEDIUM confidence
- Toast notification guidance: [LogRocket: Toast Notifications UX](https://blog.logrocket.com/ux-design/toast-notifications/) — MEDIUM confidence
- Weight log edit/delete pattern: [Noom weight logging UX](https://www.noom.com/support/faqs/using-the-app/logging-and-tracking/biometrics/2025/10/how-to-log-edit-or-delete-weight-and-change-your-units/) — MEDIUM confidence
- FastAPI idempotency/duplicate prevention: [FastAPI idempotency discussion](https://github.com/fastapi/fastapi/discussions/3555) — MEDIUM confidence

---

*Feature research for: fasting tracker — data integrity and user error recovery milestone*
*Researched: 2026-03-09*
