# Requirements: Fasting Tracker

**Defined:** 2026-03-09
**Core Value:** A live, always-accurate dashboard that shows the current fast's progress with phase indicators and elapsed time

## v1 Requirements

### Security

- [ ] **SEC-01**: Application does not contain hardcoded database credentials — `database.py` uses pydantic-settings `BaseSettings` with required `DATABASE_URL` env var; startup fails with clear error if absent
- [ ] **SEC-02**: Git history is scrubbed of the hardcoded credential (git filter-repo or BFG) and production database password is rotated
- [ ] **SEC-03**: CORS `allow_methods` is restricted to explicit list (`GET`, `POST`, `PUT`, `DELETE`) instead of `["*"]`
- [ ] **SEC-04**: All request-only schemas (`*Create`, `*Update`) have `max_length` constraints on text fields; response schemas are unchanged

### Backend Correctness

- [ ] **BCK-01**: `POST /api/fasts` returns HTTP 409 if an active fast already exists (no duplicate active fasts possible)
- [ ] **BCK-02**: `GET /api/fasts/current` correctly returns fasts where `ended IS NULL` regardless of `completed` field nullability
- [ ] **BCK-03**: `GET /api/stats/weekly` returns correct `avg_duration_hours` (non-null) for weeks with completed fasts
- [ ] **BCK-04**: `GET /api/stats/weekly` executes in ≤2 database round-trips (N+1 pattern replaced with SQL GROUP BY aggregation)
- [ ] **BCK-05**: `GET /api/stats` computes `avg_hours` using SQL `func.avg()` instead of loading all fasts into Python memory
- [ ] **BCK-06**: `PUT /api/weight/{id}` endpoint exists and updates a weight entry by ID
- [ ] **BCK-07**: `DELETE /api/weight/{id}` endpoint exists and deletes a weight entry by ID
- [ ] **BCK-08**: Backend startup does not call `seed.run()` or `Base.metadata.create_all()` on every request cycle

### Backend Tests

- [ ] **TST-01**: `test_fasts.py` covers `POST /api/fasts` (create, duplicate guard), `GET /api/fasts/current`, `PUT /api/fasts/{id}` (end fast), `DELETE /api/fasts/{id}`
- [ ] **TST-02**: `test_stats.py` covers `GET /api/stats` (avg_hours calculation) and `GET /api/stats/weekly` (avg_duration_hours, query count ≤2)
- [ ] **TST-03**: `test_weight.py` covers `PUT /api/weight/{id}` and `DELETE /api/weight/{id}`
- [ ] **TST-04**: Integration tests for CRUD-layer functions run against a real PostgreSQL test database (not SQLite or mocks)

### Frontend Error Handling

- [ ] **FEH-01**: `useToast.ts` composable exists with module-level reactive state for displaying error and success toasts
- [ ] **FEH-02**: `ToastContainer.vue` component is mounted in `App.vue` and renders active toasts
- [ ] **FEH-03**: `FastDetail.vue` `endFast` function has a `catch` block that calls `showToast()` with an error message on failure
- [ ] **FEH-04**: `FastDetail.vue` `submitLog` function has a `catch` block that displays an error message on failure
- [ ] **FEH-05**: `FastDetail.vue` `confirmDeleteFast` function has a `catch` block that displays an error message on failure
- [ ] **FEH-06**: `useTimer` composable is called synchronously during component setup using `watchEffect` to react to the loaded fast ref (not called inside `async onMounted` after `await`)
- [ ] **FEH-07**: `WeightView.vue` replaces `alert()` calls with inline error messages styled consistently with the rest of the app
- [ ] **FEH-08**: `StartFast.vue` checks for an active fast on mount and disables the start button with a message if one already exists

### UI Completeness

- [ ] **UIC-01**: `WeightView.vue` has inline tap-to-edit rows — tapping a weight entry expands it to show a pre-filled input with save/cancel
- [ ] **UIC-02**: `WeightView.vue` has a delete action per row with a confirmation step before sending `DELETE /api/weight/{id}`
- [ ] **UIC-03**: `History.vue` has a "Charger plus" load-more button that appends the next page of fasts (using incrementing `skip`), replacing the hard-capped `getFasts(0, 100)` call

## v2 Requirements

### Observability

- **OBS-01**: Backend has structured logging (request/response timing, error logging)
- **OBS-02**: Frontend has error boundary component to prevent blank-screen crashes

### UX Polish

- **UX-01**: Toast notification system replaces all remaining inline error banners for consistent error surface
- **UX-02**: Backend `GET /api/fasts` supports `type` query parameter filter (enables correct paginated type-filtered history)
- **UX-03**: History view shows pagination count indicator ("Affichage de X–Y sur Z")
- **UX-04**: Offline cache has TTL — stale fast data is invalidated after a configurable period

### Performance

- **PERF-01**: Dashboard uses view-level caching with time-based invalidation (avoid 4 parallel API calls on every mount)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Authentication / multi-user | Single-user personal app; network-level protection sufficient |
| Rate limiting (`slowapi`) | Personal app behind nginx; OS/nginx-level rate limiting more appropriate |
| Infinite scroll on History | Loses scroll position on mobile back-navigation; load-more is safer |
| Global Pinia/Vuex store | Architectural complexity explicitly deferred in PROJECT.md |
| Soft-delete for fasts/weight | Schema complexity not justified for single-user app |
| Native mobile app | PWA covers mobile use case |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SEC-01 | Phase 1 | Pending |
| SEC-02 | Phase 1 | Pending |
| SEC-03 | Phase 1 | Pending |
| SEC-04 | Phase 1 | Pending |
| BCK-08 | Phase 1 | Pending |
| BCK-01 | Phase 2 | Pending |
| BCK-02 | Phase 2 | Pending |
| BCK-03 | Phase 2 | Pending |
| BCK-04 | Phase 2 | Pending |
| BCK-05 | Phase 2 | Pending |
| BCK-06 | Phase 2 | Pending |
| BCK-07 | Phase 2 | Pending |
| TST-01 | Phase 3 | Pending |
| TST-02 | Phase 3 | Pending |
| TST-03 | Phase 3 | Pending |
| TST-04 | Phase 3 | Pending |
| FEH-01 | Phase 4 | Pending |
| FEH-02 | Phase 4 | Pending |
| FEH-03 | Phase 4 | Pending |
| FEH-04 | Phase 4 | Pending |
| FEH-05 | Phase 4 | Pending |
| FEH-06 | Phase 4 | Pending |
| FEH-07 | Phase 4 | Pending |
| FEH-08 | Phase 4 | Pending |
| UIC-01 | Phase 5 | Pending |
| UIC-02 | Phase 5 | Pending |
| UIC-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-09 after initial definition*
