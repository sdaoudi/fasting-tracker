# Codebase Structure

**Analysis Date:** 2026-03-09

## Directory Layout

```
fasting-tracker/
├── backend/                  # FastAPI Python backend
│   ├── main.py               # App entry point, all route handlers
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── database.py           # DB engine, session factory, Base
│   ├── crud.py               # All database operations
│   ├── seed.py               # One-time seed runner (meal recommendations)
│   ├── seed_meals.json       # Meal recommendation seed data
│   ├── test_meal_recommendations.py  # Backend test file
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Backend container image
├── frontend/                 # Vue 3 + Vite + TypeScript SPA
│   ├── src/
│   │   ├── main.ts           # Vue app entry point
│   │   ├── App.vue           # Root component (shell, NavBar, offline banner)
│   │   ├── style.css         # Global CSS (CSS custom properties for theming)
│   │   ├── api/
│   │   │   └── client.ts     # All API calls (typed fetch wrappers)
│   │   ├── types/
│   │   │   └── index.ts      # All TypeScript interfaces mirroring backend schemas
│   │   ├── router/
│   │   │   └── index.ts      # Vue Router route definitions
│   │   ├── composables/
│   │   │   ├── useTimer.ts           # Elapsed/remaining time, phase logic
│   │   │   ├── useBodyState.ts       # Fasting phase body state descriptions
│   │   │   ├── useDark.ts            # Dark mode toggle
│   │   │   ├── useOfflineStorage.ts  # localStorage persistence for active fast
│   │   │   ├── useOnlineStatus.ts    # Network online/offline detection
│   │   │   └── useMealRecommendations.ts  # Meal recommendation fetching
│   │   ├── views/
│   │   │   ├── Dashboard.vue     # Home / active fast overview (/)
│   │   │   ├── StartFast.vue     # Start new fast form (/start)
│   │   │   ├── FastDetail.vue    # Active fast detail + logs (/fast/:id)
│   │   │   ├── History.vue       # Past fasts list (/history)
│   │   │   ├── StatsView.vue     # Statistics and charts (/stats)
│   │   │   ├── WeightView.vue    # Weight log and chart (/weight)
│   │   │   └── MealsView.vue     # Meal logging and recommendations (/meals)
│   │   └── components/
│   │       ├── NavBar.vue                    # Bottom (mobile) / sidebar (desktop) nav
│   │       ├── CircularProgress.vue          # Animated SVG circular progress ring
│   │       ├── FastCard.vue                  # Fast summary card for lists
│   │       ├── PhaseIndicator.vue            # Fasting phase badge with color
│   │       ├── StatCard.vue                  # Single stat display card
│   │       ├── WeightChart.vue               # Chart.js line chart wrapper
│   │       ├── MoodSelector.vue              # Emoji mood picker
│   │       ├── SliderInput.vue               # Styled range slider
│   │       ├── BodyStateCard.vue             # Body state info card for current phase
│   │       ├── MealDetailModal.vue           # Meal recommendation detail modal
│   │       ├── MealRecommendationCard.vue    # Single meal recommendation card
│   │       └── MealRecommendationsList.vue   # Filtered list of meal recommendations
│   ├── public/
│   │   └── icons/            # PWA app icons (192x192, 512x512 PNG)
│   ├── index.html            # HTML entry point
│   ├── vite.config.ts        # Vite + PWA config
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript project references
│   ├── tsconfig.app.json     # App-specific TypeScript config
│   ├── tsconfig.node.json    # Node tooling TypeScript config
│   ├── nginx.conf            # Nginx config for production container
│   └── Dockerfile            # Frontend container image (multi-stage: build + nginx)
├── docker-compose.yml        # Local dev: postgres + backend + frontend containers
├── docker-compose.dokploy.yml  # Production deploy config (Dokploy)
├── CLAUDE.md                 # Project instructions and schema documentation
├── MEAL_RECOMMENDATIONS_BRIEF.md  # Feature brief for meal recommendations
├── PWA_NEXT_STEPS.md         # PWA enhancement notes
└── README.md                 # Project overview
```

## Directory Purposes

**`backend/`:**
- Purpose: Entire Python backend — flat structure, no sub-packages
- Contains: One file per layer (main, models, schemas, crud, database), plus seed scripts
- Key files: `backend/main.py` (routes), `backend/crud.py` (DB logic)

**`frontend/src/api/`:**
- Purpose: Single module containing all typed HTTP calls to the backend
- Contains: One file `client.ts` — exports one function per API endpoint
- Key files: `frontend/src/api/client.ts`

**`frontend/src/types/`:**
- Purpose: Shared TypeScript interfaces — single source of type truth for the frontend
- Contains: One file `index.ts` — all interfaces exported from one location
- Key files: `frontend/src/types/index.ts`

**`frontend/src/composables/`:**
- Purpose: Vue Composition API logic extracted from views — reusable reactive logic
- Contains: `use*.ts` files for timer, offline, dark mode, body state, recommendations

**`frontend/src/views/`:**
- Purpose: Page-level components, one per route
- Contains: Full-page Vue SFCs, fetching their own data on `onMounted`

**`frontend/src/components/`:**
- Purpose: Reusable UI components used across multiple views
- Contains: Presentational and logic components — charts, cards, inputs, navigation

## Key File Locations

**Entry Points:**
- `backend/main.py`: FastAPI app instantiation, all route handlers, CORS, startup
- `frontend/src/main.ts`: Vue app creation and router mounting
- `frontend/index.html`: HTML shell with `<div id="app">`

**Configuration:**
- `frontend/vite.config.ts`: Vite, Vue plugin, Tailwind, PWA manifest and workbox config
- `backend/database.py`: Database URL and SQLAlchemy session configuration
- `backend/requirements.txt`: Python dependencies
- `frontend/package.json`: Node dependencies and build scripts

**Core Logic:**
- `backend/crud.py`: All database queries and mutations
- `backend/models.py`: All SQLAlchemy table definitions
- `backend/schemas.py`: All Pydantic input/output schemas
- `frontend/src/api/client.ts`: All API calls
- `frontend/src/composables/useTimer.ts`: Live timer, elapsed time, fasting phase logic
- `frontend/src/composables/useBodyState.ts`: Detailed body state descriptions per fasting phase

**Type Definitions:**
- `frontend/src/types/index.ts`: All frontend TypeScript interfaces
- `backend/schemas.py`: All backend Pydantic schemas (authoritative shape definition)

## Naming Conventions

**Backend Files:**
- Flat snake_case Python modules: `main.py`, `crud.py`, `models.py`, `schemas.py`, `database.py`
- No sub-packages — everything at `backend/` root level

**Backend Symbols:**
- SQLAlchemy models: PascalCase class names matching table concept (`Fast`, `DailyLog`, `WeightLog`)
- Pydantic schemas: PascalCase with suffix (`FastCreate`, `FastUpdate`, `FastResponse`)
- CRUD functions: snake_case verb-noun (`get_fast`, `create_fast`, `update_fast`, `get_current_fast`)
- Route handler functions: snake_case verb-noun (`list_fasts`, `create_fast`, `current_fast`)

**Frontend Files:**
- Vue SFCs: PascalCase (`Dashboard.vue`, `FastCard.vue`, `NavBar.vue`)
- Composables: camelCase with `use` prefix (`useTimer.ts`, `useBodyState.ts`)
- TypeScript modules: camelCase (`client.ts`, `index.ts`)

**Frontend Symbols:**
- Interfaces: PascalCase (`Fast`, `DailyLog`, `WeightEntry`)
- Composable return values: camelCase refs/computed (`elapsed`, `remaining`, `isOnline`)
- API client exports: camelCase verb-noun (`getCurrentFast`, `createFast`, `logWeight`)
- Vue components: PascalCase matching filename

## Where to Add New Code

**New API Endpoint:**
1. Add Pydantic schema(s) to `backend/schemas.py`
2. Add SQLAlchemy model to `backend/models.py` (if new table needed)
3. Add CRUD function(s) to `backend/crud.py`
4. Add route handler to `backend/main.py`
5. Add typed client function to `frontend/src/api/client.ts`
6. Add TypeScript interface to `frontend/src/types/index.ts`

**New View/Page:**
1. Create `frontend/src/views/NewView.vue`
2. Add route to `frontend/src/router/index.ts` using lazy import
3. Add nav item to `frontend/src/components/NavBar.vue` if needed

**New Reusable Component:**
- Implementation: `frontend/src/components/ComponentName.vue`

**New Composable:**
- Implementation: `frontend/src/composables/useFeatureName.ts`
- Use `use` prefix, return reactive refs/computed values

**New Backend Model:**
- Add to `backend/models.py` as SQLAlchemy class extending `Base`
- Add corresponding Pydantic schemas to `backend/schemas.py`
- `Base.metadata.create_all()` in `backend/main.py` will create the table on startup

**Utilities/Helpers:**
- Backend: Add as module-level functions in the most relevant existing file (no separate utils file exists)
- Frontend composables: Add to relevant composable or create new `use*.ts`

## Special Directories

**`.planning/codebase/`:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (by GSD map-codebase command)
- Committed: Yes

**`.claude/`:**
- Purpose: Claude Code agent definitions, GSD commands and workflows
- Generated: No (configuration)
- Committed: Yes

**`frontend/public/icons/`:**
- Purpose: PWA app icons referenced in `vite.config.ts` manifest
- Generated: No (manually placed assets)
- Committed: Yes

---

*Structure analysis: 2026-03-09*
