# Fasting Tracker App

## Architecture

- **Backend:** FastAPI (Python) → `backend/`
- **Frontend:** Vue.js 3 + Vite + TypeScript → `frontend/`
- **Database:** PostgreSQL (existing)

## Database Connection

```
Host: postgresql.host
Port: 5432
Database: fasting_db
User: fasting_coach
Password: FastingCoach2026!
```

## Existing Database Schema

```sql
CREATE TABLE fasts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL DEFAULT '48h',
    started TIMESTAMPTZ NOT NULL,
    ended TIMESTAMPTZ,
    target_hours INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    weight_before DECIMAL(5,1),
    weight_after DECIMAL(5,1),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE daily_logs (
    id SERIAL PRIMARY KEY,
    fast_id INTEGER REFERENCES fasts(id),
    log_date DATE NOT NULL,
    water_liters DECIMAL(3,1),
    electrolytes BOOLEAN DEFAULT FALSE,
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    hunger_level INTEGER CHECK (hunger_level BETWEEN 1 AND 10),
    mood VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE meals (
    id SERIAL PRIMARY KEY,
    fast_id INTEGER REFERENCES fasts(id),
    meal_type VARCHAR(20) NOT NULL,
    meal_name VARCHAR(100),
    ingredients TEXT[],
    calories INTEGER,
    meal_time TIMESTAMPTZ,
    is_breaking_fast BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE weight_log (
    id SERIAL PRIMARY KEY,
    weigh_date DATE NOT NULL UNIQUE,
    weight DECIMAL(5,1) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**NOTE:** There is already 1 active fast in the database. Do NOT drop or recreate tables. Use the existing schema as-is.

## Backend Requirements (FastAPI)

### Setup
- Use `uvicorn` as ASGI server
- Use `psycopg2-binary` for PostgreSQL
- Use `sqlalchemy` as ORM
- CORS enabled for `http://localhost:5173` and `https://openclaw.host`
- Run on port `8042`

### API Endpoints

#### Fasts
- `GET /api/fasts` — List all fasts (with pagination, most recent first)
- `GET /api/fasts/current` — Get current active fast (or null)
- `GET /api/fasts/{id}` — Get fast by ID
- `POST /api/fasts` — Start a new fast (type, notes, weight_before optional, started optional - defaults to now)
- `PUT /api/fasts/{id}` — Update a fast (end it, update weights, notes)
- `DELETE /api/fasts/{id}` — Delete a fast

#### Daily Logs
- `GET /api/fasts/{fast_id}/logs` — Get logs for a fast
- `POST /api/fasts/{fast_id}/logs` — Add daily log (water, electrolytes, energy, hunger, mood, notes)

#### Meals
- `GET /api/fasts/{fast_id}/meals` — Get meals for a fast
- `POST /api/fasts/{fast_id}/meals` — Log a meal
- `GET /api/meals/recent` — Recent meals across all fasts

#### Weight
- `GET /api/weight` — Weight history (with date range filter)
- `POST /api/weight` — Log weight for today
- `GET /api/weight/trend` — Weight trend data (for charts)

#### Stats
- `GET /api/stats` — Overall statistics (total fasts, completed, avg duration, total weight lost, by type)
- `GET /api/stats/weekly` — Weekly summary

### Data Validation
- Use Pydantic models for all request/response schemas
- Proper error handling with HTTP status codes
- Timestamps in ISO 8601 format

## Frontend Requirements (Vue.js 3 + Vite + TypeScript)

### Vite Config
- Allow host `openclaw.host` in server config:
```js
server: {
  host: '0.0.0.0',
  port: 5173,
  allowedHosts: ['openclaw.host', 'localhost']
}
```

### UI Framework
- Use **Tailwind CSS** for styling
- Mobile-first responsive design (primary use is on phone)
- Dark mode support
- Use emoji for visual indicators

### Pages / Views

#### 1. Dashboard (Home `/`)
- **Current fast status** (if active):
  - Circular progress ring (like the screenshot reference)
  - Elapsed time (HH:MM:SS, updating live)
  - Remaining time
  - Current phase indicator with color (green/yellow/red)
  - Phase description (Facile/Transition Cétose/Difficile/Stabilisation)
  - Button: "Terminer le Jeûne"
- **If no active fast:**
  - Quick start buttons: "48h", "72h", "Custom"
  - Last fast summary
- **Weight chart** (mini line chart, last 30 days)
- **Quick stats** (total fasts, current streak, total weight lost)

#### 2. Start Fast (`/start`)
- Select fast type (16:8, 18:6, 20:4, OMAD, 48h, 72h, Custom)
- Optional: Weight before
- Optional: Notes
- Optional: Custom start time (defaults to now)
- Button: "Démarrer le Jeûne"

#### 3. Active Fast Detail (`/fast/:id`)
- Full progress view with circular timer
- Phase timeline (visual)
- Daily log form:
  - Water intake (slider 0-5L)
  - Electrolytes taken? (toggle)
  - Energy level (1-10 slider)
  - Hunger level (1-10 slider)
  - Mood selector (emoji: 😊😐😣🤮😴💪)
  - Notes
- Log history for this fast
- Meals logged during/after this fast
- Button: "Terminer le Jeûne" (with weight_after prompt)

#### 4. History (`/history`)
- List of all past fasts
- Filter by type, date range
- Each card shows: type, dates, duration, weight loss, status
- Click to see detail

#### 5. Stats (`/stats`)
- Total fasts completed
- Average duration
- Total weight lost
- Weight chart (line chart, full history)
- Fasts by type (bar chart)
- Monthly summary
- Current streak

#### 6. Weight Log (`/weight`)
- Weight input (quick log for today)
- Weight history chart (line)
- Table with all entries
- Goal weight line on chart (optional)

#### 7. Meals (`/meals`)
- Log a meal (type, name, calories, is breaking fast?)
- Recent meals list
- Meal suggestions (from predefined healthy meals)

### Components
- `CircularProgress.vue` — Animated circular progress ring
- `FastCard.vue` — Fast summary card for lists
- `PhaseIndicator.vue` — Shows current fasting phase with color
- `StatCard.vue` — Stat display card
- `WeightChart.vue` — Line chart for weight (use Chart.js or similar lightweight lib)
- `MoodSelector.vue` — Emoji mood picker
- `SliderInput.vue` — Styled range slider for levels
- `NavBar.vue` — Bottom navigation (mobile) / sidebar (desktop)

### Navigation
- Bottom tab bar (mobile):
  - 🏠 Accueil
  - ⏱️ Jeûne
  - 📊 Stats
  - ⚖️ Poids
  - 📝 Repas

### Design Guidelines
- **Primary color:** Teal/green (like the reference app screenshot)
- **Accent:** Orange/red for alerts
- **Font:** System font stack
- **Border radius:** Rounded (12-16px)
- **Shadows:** Subtle, soft
- **Animations:** Smooth transitions, progress ring animation
- **Language:** French for all UI labels and text

## Project Structure

```
fasting-app/
├── backend/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB connection
│   ├── crud.py              # CRUD operations
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── router/index.ts
│   │   ├── api/             # API client (axios/fetch)
│   │   ├── views/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── composables/     # Vue composables (useTimer, useFast, etc.)
│   │   └── types/           # TypeScript interfaces
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
├── CLAUDE.md
└── README.md
```

## Running

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8042 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host
```

## Important Notes

1. **DO NOT drop or recreate database tables** — use existing schema
2. **Mobile-first** — the app will primarily be used on a phone
3. **French language** — all UI text in French
4. **API prefix** — all backend routes under `/api/`
5. **Existing data** — there is already 1 active fast in the database, the app should display it
6. **Live timer** — the dashboard must show a live updating timer for active fasts
7. **CORS** — must allow both localhost:5173 and openclaw.host origins
8. Backend on port **8042**, Frontend on port **5173**
