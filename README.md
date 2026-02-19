# Fasting Tracker

Intermittent fasting tracking app. Mobile-first interface with a real-time timer, weight tracking, daily logs, and meal recommendations.

## Stack

- **Backend**: FastAPI (Python) — port `8042`
- **Frontend**: Vue.js 3 + Vite + TypeScript + Tailwind CSS — port `3099`
- **Database**: PostgreSQL 16

## Local setup (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose

### Run the project

```bash
git clone <repo-url>
cd fasting-tracker
docker compose up --build
```

App available at **http://localhost:3099**

API available at **http://localhost:8042**

### Stop the project

```bash
docker compose down
```

To also delete the PostgreSQL data:

```bash
docker compose down -v
```

---

## Local setup (without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16

### Database

Create the database and user:

```sql
CREATE USER fasting_coach WITH PASSWORD 'fasting_local';
CREATE DATABASE fasting_db OWNER fasting_coach;
```

Then create the tables (schema in `CLAUDE.md`).

### Backend

```bash
cd backend
pip install -r requirements.txt
DATABASE_URL=postgresql://fasting_coach:fasting_local@localhost:5432/fasting_db \
  uvicorn main:app --host 0.0.0.0 --port 8042 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host
```

Frontend available at **http://localhost:5173**

---

## Project structure

```
fasting-tracker/
├── backend/
│   ├── main.py         # FastAPI app, CORS, routes
│   ├── models.py       # SQLAlchemy models
│   ├── schemas.py      # Pydantic schemas
│   ├── database.py     # Database connection
│   ├── crud.py         # CRUD operations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/      # Pages (Dashboard, History, Stats…)
│   │   ├── components/ # Reusable components
│   │   ├── composables/# Vue logic (useTimer, useFast…)
│   │   ├── api/        # HTTP client
│   │   └── types/      # TypeScript interfaces
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Local customization

To override settings without modifying the versioned `docker-compose.yml`, create a `docker-compose.override.yml` at the root (it's gitignored and merged automatically by Docker Compose):

```yaml
# docker-compose.override.yml
services:
  backend:
    ports:
      - "9000:8042"   # change port
    environment:
      - DATABASE_URL=postgresql://user:pass@host:5432/db  # use external DB
```

## Environment variables

| Variable       | Description             | Default (local Docker)                                         |
| -------------- | ----------------------- | -------------------------------------------------------------- |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://fasting_coach:fasting_local@db:5432/fasting_db` |

## Deployment (Dokploy / production)

The `docker-compose.yml` includes a PostgreSQL container for local development. In production, override the `DATABASE_URL` environment variable in Dokploy's service settings to point to your external database — the `db` service will be ignored by the backend.
