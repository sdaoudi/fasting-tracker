# Roadmap: Fasting Tracker — Quality Hardening

## Overview

This milestone hardens a fully operational fasting tracker app by fixing known defects in dependency order: security first (credentials in git history), then backend correctness (duplicate fast guard, nullable predicate bug, N+1 query, missing weight endpoints), then tests written against correct behavior, then frontend error handling infrastructure (toast system, catch blocks, timer lifecycle fix), and finally UI completeness (weight edit/delete rows, history pagination). Each phase unblocks the next — tests cannot encode correct behavior until bugs are fixed; catch blocks cannot call `showToast()` until the toast system exists.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Security Hardening** - Remove hardcoded DB credentials, restrict CORS methods, add input length constraints
- [ ] **Phase 2: Backend Correctness** - Fix known backend bugs and add missing weight CRUD endpoints
- [ ] **Phase 3: Backend Test Coverage** - Write tests against correct behavior using two-layer strategy
- [ ] **Phase 4: Frontend Error Handling** - Toast infrastructure, catch blocks, timer lifecycle fix
- [ ] **Phase 5: UI Completeness** - Weight edit/delete UI and history load-more pagination

## Phase Details

### Phase 1: Security Hardening
**Goal**: Credentials are no longer hardcoded in the codebase or git history, and the API surface is restricted to known-safe inputs and methods
**Depends on**: Nothing (first phase)
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, BCK-08
**Success Criteria** (what must be TRUE):
  1. Starting the backend without a `DATABASE_URL` environment variable fails with a clear error message at startup — no silent fallback to a hardcoded credential
  2. The production database password has been rotated and git history contains no plaintext credential (verified with `git log -S <old_password>` returning no results)
  3. Submitting a text field longer than the defined max_length to any `*Create` or `*Update` endpoint returns HTTP 422, not a database error
  4. CORS preflight for a disallowed method (e.g., PATCH) is rejected by the backend
  5. Backend startup does not call `seed.run()` or `Base.metadata.create_all()` on the hot-reload cycle
**Plans**: TBD

### Phase 2: Backend Correctness
**Goal**: All known backend bugs are fixed and weight entries can be fully managed via the API
**Depends on**: Phase 1
**Requirements**: BCK-01, BCK-02, BCK-03, BCK-04, BCK-05, BCK-06, BCK-07
**Success Criteria** (what must be TRUE):
  1. Attempting to start a second fast while one is active returns HTTP 409 from `POST /api/fasts`
  2. `GET /api/fasts/current` returns the active fast correctly when `completed` is NULL (not just when it is FALSE)
  3. `GET /api/stats/weekly` returns a non-null `avg_duration_hours` for any week that contains at least one completed fast
  4. `GET /api/stats/weekly` completes with at most 2 database round-trips (confirmed via query logging or test assertion)
  5. `PUT /api/weight/{id}` and `DELETE /api/weight/{id}` return successful responses for valid weight entry IDs
**Plans**: TBD

### Phase 3: Backend Test Coverage
**Goal**: Core fast lifecycle and stats logic are verified by automated tests against a real PostgreSQL database
**Depends on**: Phase 2
**Requirements**: TST-01, TST-02, TST-03, TST-04
**Success Criteria** (what must be TRUE):
  1. Running `pytest` produces a green suite covering `POST /api/fasts` duplicate guard, `GET /api/fasts/current`, `PUT /api/fasts/{id}` end-fast, and `DELETE /api/fasts/{id}`
  2. The test suite asserts that `GET /api/stats/weekly` returns a non-null `avg_duration_hours` and executes in ≤2 queries
  3. The test suite covers `PUT /api/weight/{id}` and `DELETE /api/weight/{id}` happy paths and not-found cases
  4. CRUD-layer integration tests execute against a real PostgreSQL test database (not SQLite or mocked sessions)
**Plans**: TBD

### Phase 4: Frontend Error Handling
**Goal**: All user-facing async operations show error feedback via a consistent toast system, and the timer composable does not leak intervals
**Depends on**: Phase 2
**Requirements**: FEH-01, FEH-02, FEH-03, FEH-04, FEH-05, FEH-06, FEH-07, FEH-08
**Success Criteria** (what must be TRUE):
  1. When ending a fast fails (network error simulated), a toast message appears on screen with the error — no silent failure
  2. When submitting a daily log fails, a toast error message is visible to the user
  3. When deleting a fast fails, a toast error message is visible to the user
  4. Navigating to FastDetail and immediately away does not leave a running `setInterval` in the browser (no timer leak on unmount)
  5. Navigating to StartFast when an active fast exists shows a disabled start button with an explanatory message
  6. Weight entry errors display as inline messages, not browser `alert()` dialogs
**Plans**: TBD

### Phase 5: UI Completeness
**Goal**: Users can edit and delete individual weight entries inline, and can browse all historical fasts without a hard cap
**Depends on**: Phase 2, Phase 4
**Requirements**: UIC-01, UIC-02, UIC-03
**Success Criteria** (what must be TRUE):
  1. Tapping a weight entry row in WeightView expands it to an editable input pre-filled with the current value; saving updates the entry in the database
  2. A delete action per weight row prompts for confirmation before sending `DELETE /api/weight/{id}`; after deletion the row disappears from the list
  3. The History view shows a "Charger plus" button when more fasts exist beyond the current page; clicking it appends the next page without replacing existing results
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

Note: Phase 3 (tests) and Phase 4 (frontend) both depend on Phase 2 and are independent of each other — they can be executed in either order.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Security Hardening | 0/? | Not started | - |
| 2. Backend Correctness | 0/? | Not started | - |
| 3. Backend Test Coverage | 0/? | Not started | - |
| 4. Frontend Error Handling | 0/? | Not started | - |
| 5. UI Completeness | 0/? | Not started | - |
