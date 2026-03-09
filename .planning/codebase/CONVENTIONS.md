# Coding Conventions

**Analysis Date:** 2026-03-09

## Naming Patterns

**Files:**
- Vue components: PascalCase — `CircularProgress.vue`, `FastCard.vue`, `MealRecommendationsList.vue`
- Vue views: PascalCase with View/Detail suffix — `Dashboard.vue`, `StatsView.vue`, `FastDetail.vue`
- TypeScript composables: camelCase with `use` prefix — `useTimer.ts`, `useBodyState.ts`, `useMealRecommendations.ts`
- TypeScript utility modules: camelCase — `client.ts`
- Python modules: snake_case — `main.py`, `crud.py`, `schemas.py`, `database.py`

**Functions:**
- Frontend: camelCase — `getCurrentFast()`, `formatDuration()`, `getPhase()`
- Composables start with `use` — `useTimer()`, `useBodyState()`, `useMealRecommendations()`
- Backend CRUD: snake_case — `get_fasts()`, `create_fast()`, `update_fast()`, `delete_fast()`
- Backend route handlers: snake_case — `list_fasts()`, `current_fast()`, `weight_history()`

**Variables:**
- Frontend: camelCase — `currentFast`, `weightData`, `elapsedHours`
- Backend Python: snake_case — `db_fast`, `fast_id`, `update_data`, `avg_hours`
- Private Python helpers: leading underscore — `_parse_duration_hours()`

**Types/Classes:**
- Frontend TypeScript interfaces: PascalCase — `Fast`, `DailyLog`, `MealRecommendation`, `BodyProcess`
- Backend Pydantic schemas: PascalCase with Create/Update/Response suffix — `FastCreate`, `FastUpdate`, `FastResponse`
- Backend SQLAlchemy models: PascalCase singular — `Fast`, `DailyLog`, `Meal`, `WeightLog`, `MealRecommendation`

**Constants:**
- Frontend export constants: SCREAMING_SNAKE_CASE — `CATEGORY_LABELS`, `DIFFICULTY_LABELS`, `DIGESTIBILITY_COLORS`, `TIMING_LABELS`
- Backend module-level constants: SCREAMING_SNAKE_CASE — `DIGESTIBILITY_ORDER`

## Code Style

**Formatting (Frontend):**
- No dedicated formatter config file detected (no `.prettierrc`, no `biome.json`, no `eslint.config.*`)
- TypeScript strict mode enabled via `tsconfig.app.json` (`strict: true`, `noUnusedLocals: true`, `noUnusedParameters: true`)
- Single quotes for strings in TypeScript
- No semicolons in TypeScript (inferred from existing code patterns)
- Arrow functions for short expressions, named functions for composables

**Formatting (Backend):**
- No linting config detected (no `.flake8`, no `pyproject.toml`, no `setup.cfg`)
- Standard Python style: 4-space indent
- Type hints used consistently on function signatures
- Section separators use `# ── Section Name ──` pattern in both Python (`crud.py`, `main.py`) and TypeScript comments

## Import Organization

**Frontend TypeScript order:**
1. Vue core imports — `import { ref, computed, onMounted } from 'vue'`
2. Vue ecosystem — `import { useRoute, useRouter } from 'vue-router'`
3. Local component imports — `import CircularProgress from '../components/CircularProgress.vue'`
4. Local API imports — `import { getCurrentFast } from '../api/client'`
5. Local composable imports — `import { useTimer } from '../composables/useTimer'`
6. Type-only imports last — `import type { Fast, Stats } from '../types'`

**Backend Python order:**
1. Standard library — `from datetime import datetime, date`
2. Third-party — `from fastapi import FastAPI, Depends`
3. Local modules — `import crud`, `import models`, `import schemas`

**Path Aliases:**
- None configured. All imports use relative paths (`../components/`, `../api/`, `../composables/`, `../types`).

## Error Handling

**Frontend patterns:**
- API calls wrapped in `try/catch` inside `onMounted`:
  ```typescript
  onMounted(async () => {
    try {
      const data = await someApiCall()
      // handle data
    } catch {
      // offline fallback — load from localStorage
    } finally {
      loading.value = false
    }
  })
  ```
- Composables surface errors via reactive `error` ref:
  ```typescript
  const error = ref<string | null>(null)
  error.value = e instanceof Error ? e.message : 'Erreur inconnue'
  ```
- API client throws `Error` with status code on non-OK responses:
  ```typescript
  throw new Error(`${res.status}: ${detail}`)
  ```

**Backend patterns:**
- CRUD functions return `None` or `False` for not-found cases (no exceptions raised in `crud.py`)
- Route handlers check CRUD return values and raise `HTTPException`:
  ```python
  fast = crud.get_fast(db, fast_id)
  if not fast:
      raise HTTPException(status_code=404, detail="Fast not found")
  ```
- Standard HTTP status codes: 404 for not found, 201 for created, default 200 for success

## Logging

**Framework:** None — no logging library used in either frontend or backend.
- Frontend: silent catch blocks used for offline fallback scenarios
- Backend: no structured logging, errors bubble up through HTTP responses

## Comments

**When to Comment:**
- Section delimiters using `# ── Name ──` pattern to group related functions
- Inline comments for non-obvious logic (e.g., `# noqa: F401 — needed so all models are registered before create_all`)
- Docstrings only on helper functions with complex logic (e.g., `_parse_duration_hours`)

**Example docstring pattern:**
```python
def _parse_duration_hours(duration_str: str) -> Optional[int]:
    """Parse a fast duration string like '48h', '16:8', 'OMAD', '7j+' into hours."""
```

## Function Design

**Size:** Functions are kept small and focused. CRUD functions average 5-15 lines. Complex logic (stats, recommendations) split into private helpers.

**Parameters:**
- Backend: `db: Session` always first parameter in CRUD functions
- Optional parameters use Python default `None` with `Optional` type hint
- Frontend composables accept typed parameter objects for flexible filtering

**Return Values:**
- CRUD functions return ORM objects or `None`/`False` for not-found
- Composables return reactive refs and async functions as a plain object
- Route handlers return Pydantic schema instances (auto-serialized by FastAPI)

## Module Design

**Exports (Frontend):**
- Named exports only — no default exports except router (`frontend/src/router/index.ts`)
- Composables export the composable function plus related pure utility functions and constants from the same file (e.g., `useTimer.ts` exports `useTimer`, `formatDuration`, `getPhase`)

**Exports (Backend):**
- No `__all__` declarations — all public by convention
- Internal helpers prefixed with `_` to signal private intent

**Vue Component Structure:**
- Always `<script setup lang="ts">` (Composition API with script setup)
- `defineProps<{}>()` with TypeScript generics (no `withDefaults` pattern observed for required props)
- No `defineEmits` seen in simple presentational components
- Template uses `v-if`/`v-else`, `v-for` with `:key`, and `:style` for dynamic CSS variables

**CSS/Styling:**
- Tailwind utility classes for layout and spacing
- CSS custom properties (`var(--bg-card)`, `var(--text-primary)`, `var(--border-color)`) for theme-aware colors via `:style` bindings
- Inline `:style` used when dynamic theming is needed; Tailwind classes for static styles
- Hard-coded hex color strings in composable logic (e.g., `'#10b981'` in `useTimer.ts`, `'#ef4444'` in `useMealRecommendations.ts`)

---

*Convention analysis: 2026-03-09*
