# Documentation Technique — Fasting Tracker App

> Application web de suivi du jeûne intermittent et prolongé. Interface en français, mobile-first, Progressive Web App (PWA).

---

## Table des matières

1. [Architecture générale](#1-architecture-générale)
2. [Stack technique](#2-stack-technique)
3. [Structure des dossiers](#3-structure-des-dossiers)
4. [Base de données](#4-base-de-données)
5. [Backend — API FastAPI](#5-backend--api-fastapi)
6. [Frontend — Vue.js 3](#6-frontend--vuejs-3)
7. [Docker & déploiement](#7-docker--déploiement)
8. [Flux utilisateur principal](#8-flux-utilisateur-principal)
9. [Fonctionnalités avancées](#9-fonctionnalités-avancées)
10. [Variables d'environnement & configuration](#10-variables-denvironnement--configuration)

---

## 1. Architecture générale

```
┌─────────────────────────────────────────────────────────┐
│                      Navigateur / PWA                   │
│   Vue.js 3 + TypeScript + Tailwind CSS (port 5173)     │
│   Service Worker (offline cache, PWA)                   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI (Python) — port 8042               │
│   CORS : localhost:5173 + openclaw.host                │
│   Routes : /api/*                                       │
└────────────────────────┬────────────────────────────────┘
                         │ SQLAlchemy / psycopg2
                         ▼
┌─────────────────────────────────────────────────────────┐
│            PostgreSQL — postgresql.host:5432            │
│            Base : fasting_db / user : fasting_coach    │
└─────────────────────────────────────────────────────────┘
```

- Le frontend appelle l'API REST via un client fetch centralisé (`src/api/client.ts`).
- Le backend est stateless — toute persistance passe par PostgreSQL.
- Un cache localStorage maintient l'état du jeûne actif en cas de perte de réseau.
- Le frontend est déployé comme PWA (Service Worker Workbox) pour un usage hors-ligne partiel.

---

## 2. Stack technique

### Backend

| Composant        | Technologie              | Version  |
|------------------|--------------------------|----------|
| Langage          | Python                   | 3.11+    |
| Framework API    | FastAPI                  | latest   |
| Serveur ASGI     | Uvicorn                  | latest   |
| ORM              | SQLAlchemy               | latest   |
| Driver PostgreSQL | psycopg2-binary         | latest   |
| Validation       | Pydantic v2              | latest   |
| Tests            | pytest + httpx           | latest   |

### Frontend

| Composant        | Technologie              | Version  |
|------------------|--------------------------|----------|
| Framework UI     | Vue.js 3 (Composition API) | 3.5.25 |
| Build            | Vite                     | latest   |
| Langage          | TypeScript               | latest   |
| CSS              | Tailwind CSS             | 4.1.18   |
| Routing          | Vue Router               | 4.6.4    |
| Graphiques       | Chart.js                 | 4.5.1    |
| PWA              | vite-plugin-pwa (Workbox) | latest  |

### Infrastructure

| Composant        | Technologie              |
|------------------|--------------------------|
| Base de données  | PostgreSQL               |
| Reverse proxy    | Nginx (dans le container frontend) |
| Conteneurisation | Docker + Docker Compose  |

---

## 3. Structure des dossiers

```
fasting-app/
├── backend/
│   ├── main.py                  # Application FastAPI, CORS, routes, démarrage
│   ├── models.py                # Modèles SQLAlchemy (ORM)
│   ├── schemas.py               # Schémas Pydantic (validation entrée/sortie)
│   ├── database.py              # Connexion PostgreSQL, SessionLocal, Base
│   ├── crud.py                  # Opérations CRUD sur tous les modèles
│   ├── requirements.txt         # Dépendances Python
│   ├── seed.py                  # Script de peuplement initial des données
│   ├── seed_meals.json          # Données de repas recommandés (JSON)
│   └── Dockerfile               # Image Docker pour le backend
│
├── frontend/
│   ├── index.html               # Point d'entrée HTML
│   ├── vite.config.ts           # Config Vite (PWA, Tailwind, server)
│   ├── tailwind.config.js       # Config Tailwind CSS
│   ├── tsconfig.json            # Config TypeScript racine
│   ├── tsconfig.app.json        # Config TS pour le code applicatif
│   ├── tsconfig.node.json       # Config TS pour les outils Node
│   ├── package.json             # Dépendances et scripts npm
│   ├── nginx.conf               # Config Nginx (prod)
│   ├── Dockerfile               # Image Docker pour le frontend
│   ├── public/                  # Assets statiques (icônes PWA, etc.)
│   └── src/
│       ├── main.ts              # Point d'entrée Vue (montage app, router)
│       ├── App.vue              # Composant racine (NavBar, RouterView, dark mode)
│       ├── style.css            # Styles globaux + imports Tailwind
│       │
│       ├── api/
│       │   └── client.ts        # Client HTTP centralisé (fetch wrapper)
│       │
│       ├── types/
│       │   └── index.ts         # Interfaces TypeScript (Fast, Meal, Weight…)
│       │
│       ├── router/
│       │   └── index.ts         # Routes Vue Router
│       │
│       ├── composables/
│       │   ├── useTimer.ts              # Timer live pour le jeûne actif
│       │   ├── useDark.ts               # Gestion du mode sombre
│       │   ├── useBodyState.ts          # État physiologique par phase
│       │   ├── useMealRecommendations.ts # Suggestions de repas
│       │   ├── useOfflineStorage.ts     # Cache localStorage (offline)
│       │   └── useOnlineStatus.ts       # Détection connexion réseau
│       │
│       ├── components/
│       │   ├── CircularProgress.vue     # Anneau de progression SVG animé
│       │   ├── FastCard.vue             # Carte résumé d'un jeûne
│       │   ├── PhaseIndicator.vue       # Indicateur de phase avec couleur
│       │   ├── StatCard.vue             # Carte statistique (icône + valeur)
│       │   ├── WeightChart.vue          # Graphique poids (Chart.js)
│       │   ├── MoodSelector.vue         # Sélecteur d'humeur (emojis)
│       │   ├── SliderInput.vue          # Curseur stylisé (eau, énergie, faim)
│       │   ├── NavBar.vue               # Navigation bas de page (mobile) / sidebar
│       │   ├── BodyStateCard.vue        # Carte état corporel par phase
│       │   ├── MealDetailModal.vue      # Modal détail d'un repas (bottom sheet)
│       │   ├── MealRecommendationCard.vue # Carte repas recommandé
│       │   └── MealRecommendationsList.vue # Liste filtrée de recommandations
│       │
│       └── views/
│           ├── Dashboard.vue    # Accueil (jeûne actif ou démarrage rapide)
│           ├── StartFast.vue    # Formulaire de démarrage de jeûne
│           ├── FastDetail.vue   # Détail d'un jeûne (timer, logs, repas)
│           ├── History.vue      # Historique de tous les jeûnes
│           ├── StatsView.vue    # Statistiques globales + graphiques
│           ├── WeightView.vue   # Journal de poids + graphique
│           └── MealsView.vue    # Repas recommandés + journal alimentaire
│
├── CLAUDE.md                    # Spécifications du projet
├── DOCUMENTATION.md             # Ce fichier
├── MEAL_RECOMMENDATIONS_BRIEF.md
├── PWA_NEXT_STEPS.md
└── README.md
```

---

## 4. Base de données

### Connexion

```
Host     : postgresql.host
Port     : 5432
Database : fasting_db
User     : fasting_coach
```

### Schéma complet

```sql
-- Jeûnes
CREATE TABLE fasts (
    id             SERIAL PRIMARY KEY,
    type           VARCHAR(20)    NOT NULL DEFAULT '48h',
    started        TIMESTAMPTZ    NOT NULL,
    ended          TIMESTAMPTZ,
    target_hours   INTEGER        NOT NULL,
    completed      BOOLEAN        DEFAULT FALSE,
    notes          TEXT,
    weight_before  DECIMAL(5,1),
    weight_after   DECIMAL(5,1),
    created_at     TIMESTAMPTZ    DEFAULT NOW(),
    updated_at     TIMESTAMPTZ    DEFAULT NOW()
);

-- Journaux quotidiens (associés à un jeûne)
CREATE TABLE daily_logs (
    id           SERIAL PRIMARY KEY,
    fast_id      INTEGER        REFERENCES fasts(id),
    log_date     DATE           NOT NULL,
    water_liters DECIMAL(3,1),
    electrolytes BOOLEAN        DEFAULT FALSE,
    energy_level INTEGER        CHECK (energy_level BETWEEN 1 AND 10),
    hunger_level INTEGER        CHECK (hunger_level BETWEEN 1 AND 10),
    mood         VARCHAR(20),
    notes        TEXT,
    created_at   TIMESTAMPTZ    DEFAULT NOW()
);

-- Repas (avant, pendant ou après le jeûne)
CREATE TABLE meals (
    id              SERIAL PRIMARY KEY,
    fast_id         INTEGER        REFERENCES fasts(id),
    meal_type       VARCHAR(20)    NOT NULL,
    meal_name       VARCHAR(100),
    ingredients     TEXT[],
    calories        INTEGER,
    meal_time       TIMESTAMPTZ,
    is_breaking_fast BOOLEAN       DEFAULT FALSE,
    notes           TEXT,
    created_at      TIMESTAMPTZ    DEFAULT NOW()
);

-- Journal de poids (1 entrée max par jour)
CREATE TABLE weight_log (
    id          SERIAL PRIMARY KEY,
    weigh_date  DATE           NOT NULL UNIQUE,
    weight      DECIMAL(5,1)   NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMPTZ    DEFAULT NOW()
);

-- Recommandations de repas (peuplée via seed_meals.json)
CREATE TABLE meal_recommendations (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100)   NOT NULL,
    category        VARCHAR(50),
    description     TEXT,
    ingredients     TEXT[],
    prep_time       INTEGER,        -- en minutes
    calories        INTEGER,
    protein_g       DECIMAL(5,1),
    carbs_g         DECIMAL(5,1),
    fat_g           DECIMAL(5,1),
    fiber_g         DECIMAL(5,1),
    difficulty      VARCHAR(20),    -- facile / moyen / difficile
    digestibility   VARCHAR(20),    -- légère / modérée / riche
    best_timing     TEXT[],         -- ['breaking_fast', 'post_fast', ...]
    suitable_for    TEXT[],         -- types de jeûne compatibles
    tips            TEXT,
    created_at      TIMESTAMPTZ    DEFAULT NOW()
);
```

### Relations

```
fasts ──< daily_logs   (1 jeûne → N journaux quotidiens)
fasts ──< meals        (1 jeûne → N repas)
weight_log             (table indépendante, 1 entrée par date)
meal_recommendations   (table indépendante, données de référence)
```

---

## 5. Backend — API FastAPI

### Démarrage

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8042 --reload
```

### Organisation du code

| Fichier        | Rôle                                                    |
|----------------|---------------------------------------------------------|
| `main.py`      | Instance FastAPI, CORS, inclusion des routes, événements de démarrage |
| `database.py`  | `engine`, `SessionLocal`, `Base` — connexion PostgreSQL |
| `models.py`    | Classes SQLAlchemy mappées sur les tables               |
| `schemas.py`   | Modèles Pydantic pour validation des requêtes/réponses  |
| `crud.py`      | Fonctions de lecture/écriture pour tous les modèles     |

### Configuration CORS

```python
origins = [
    "http://localhost:5173",
    "https://openclaw.host",
]
```

---

### Endpoints

#### Jeûnes — `/api/fasts`

| Méthode | URL                  | Description                                              |
|---------|----------------------|----------------------------------------------------------|
| GET     | `/api/fasts`         | Liste paginée de tous les jeûnes (plus récent en premier) |
| GET     | `/api/fasts/current` | Jeûne actif en cours (ou `null`)                         |
| GET     | `/api/fasts/{id}`    | Détail d'un jeûne par ID                                 |
| POST    | `/api/fasts`         | Démarrer un nouveau jeûne                                |
| PUT     | `/api/fasts/{id}`    | Modifier un jeûne (terminer, poids, notes)               |
| DELETE  | `/api/fasts/{id}`    | Supprimer un jeûne                                       |

**POST `/api/fasts` — Corps de la requête :**
```json
{
  "type": "48h",
  "target_hours": 48,
  "notes": "Optionnel",
  "weight_before": 82.5,
  "started": "2026-03-15T08:00:00Z"
}
```

**PUT `/api/fasts/{id}` — Corps de la requête :**
```json
{
  "ended": "2026-03-17T08:00:00Z",
  "completed": true,
  "weight_after": 80.3,
  "notes": "Très bien passé"
}
```

---

#### Journaux quotidiens — `/api/fasts/{fast_id}/logs`

| Méthode | URL                           | Description                     |
|---------|-------------------------------|---------------------------------|
| GET     | `/api/fasts/{fast_id}/logs`   | Journaux d'un jeûne             |
| POST    | `/api/fasts/{fast_id}/logs`   | Ajouter un journal journalier   |

**POST — Corps :**
```json
{
  "log_date": "2026-03-15",
  "water_liters": 2.5,
  "electrolytes": true,
  "energy_level": 7,
  "hunger_level": 4,
  "mood": "😊",
  "notes": "Bonne journée"
}
```

---

#### Repas — `/api/fasts/{fast_id}/meals` et `/api/meals`

| Méthode | URL                             | Description                          |
|---------|---------------------------------|--------------------------------------|
| GET     | `/api/fasts/{fast_id}/meals`    | Repas d'un jeûne                     |
| POST    | `/api/fasts/{fast_id}/meals`    | Enregistrer un repas                 |
| GET     | `/api/meals/recent`             | Repas récents (tous jeûnes confondus)|

**POST — Corps :**
```json
{
  "meal_type": "diner",
  "meal_name": "Bouillon de légumes",
  "ingredients": ["carottes", "céleri", "sel"],
  "calories": 120,
  "meal_time": "2026-03-17T19:30:00Z",
  "is_breaking_fast": true,
  "notes": "Repas de rupture"
}
```

---

#### Poids — `/api/weight`

| Méthode | URL                  | Description                                 |
|---------|----------------------|---------------------------------------------|
| GET     | `/api/weight`        | Historique (filtre `?start=&end=`)          |
| POST    | `/api/weight`        | Enregistrer le poids du jour (upsert)       |
| GET     | `/api/weight/trend`  | Données de tendance pour graphique          |

**POST — Corps :**
```json
{
  "weigh_date": "2026-03-15",
  "weight": 81.2,
  "notes": "Après réveil"
}
```

---

#### Statistiques — `/api/stats`

| Méthode | URL                  | Description                                    |
|---------|----------------------|------------------------------------------------|
| GET     | `/api/stats`         | Stats globales                                 |
| GET     | `/api/stats/weekly`  | Résumé hebdomadaire                            |

**Réponse `/api/stats` :**
```json
{
  "total_fasts": 12,
  "completed_fasts": 10,
  "avg_duration_hours": 52.3,
  "total_weight_lost": 4.2,
  "fasts_by_type": {"48h": 8, "72h": 4},
  "current_streak": 2
}
```

---

#### Recommandations de repas — `/api/meals/recommendations`

| Méthode | URL                                      | Description                               |
|---------|------------------------------------------|-------------------------------------------|
| GET     | `/api/meals/recommendations`             | Liste filtrée de recommandations          |
| GET     | `/api/meals/recommendations/categories`  | Nombre de repas par catégorie             |

**Paramètres de filtre :**
```
?fast_type=48h      # Type de jeûne (adapte les suggestions)
?category=soupe     # Catégorie de repas
?timing=breaking_fast # Moment de consommation
?difficulty=facile  # Niveau de difficulté
?digestibility=légère # Digestibilité
?limit=20           # Nombre max de résultats
```

---

### Modèles Pydantic (schémas)

| Schéma                    | Usage                                 |
|---------------------------|---------------------------------------|
| `FastCreate`              | Créer un jeûne                        |
| `FastUpdate`              | Modifier / terminer un jeûne          |
| `FastResponse`            | Réponse API (avec durée calculée)     |
| `DailyLogCreate`          | Créer un journal                      |
| `DailyLogResponse`        | Réponse journal                       |
| `MealCreate`              | Créer un repas                        |
| `MealResponse`            | Réponse repas                         |
| `WeightCreate`            | Enregistrer le poids                  |
| `WeightResponse`          | Réponse poids                         |
| `WeightTrend`             | Données de tendance                   |
| `StatsResponse`           | Statistiques globales                 |
| `WeeklySummary`           | Résumé hebdomadaire                   |
| `MealRecommendationResponse` | Recommandation de repas            |
| `CategoryCount`           | Comptage par catégorie                |
| `Macros`                  | Valeurs nutritionnelles               |

---

## 6. Frontend — Vue.js 3

### Démarrage

```bash
cd frontend
npm install
npm run dev -- --host
```

### Configuration Vite (`vite.config.ts`)

```typescript
server: {
  host: '0.0.0.0',
  port: 5173,
  allowedHosts: ['openclaw.host', 'localhost']
}
```

PWA configurée avec Workbox pour le cache des appels API (`/api/fasts/current`, `/api/weight`).

---

### Routes (`src/router/index.ts`)

| Route         | Vue             | Description                          |
|---------------|-----------------|--------------------------------------|
| `/`           | Dashboard       | Accueil — jeûne actif ou démarrage   |
| `/start`      | StartFast       | Formulaire de nouveau jeûne          |
| `/fast/:id`   | FastDetail      | Détail et gestion d'un jeûne         |
| `/history`    | History         | Historique de tous les jeûnes        |
| `/stats`      | StatsView       | Statistiques et graphiques           |
| `/weight`     | WeightView      | Journal de poids                     |
| `/meals`      | MealsView       | Repas recommandés et journal         |

---

### Navigation (`NavBar.vue`)

Navigation adaptive :
- **Mobile** : barre de navigation en bas de l'écran (5 onglets)
- **Desktop** : sidebar latérale gauche

| Onglet    | Route      | Icône |
|-----------|------------|-------|
| Accueil   | `/`        | 🏠    |
| Jeûne     | `/start`   | ⏱️    |
| Stats     | `/stats`   | 📊    |
| Poids     | `/weight`  | ⚖️    |
| Repas     | `/meals`   | 📝    |

---

### Vues

#### `Dashboard.vue` — Accueil

**Si jeûne actif :**
- Anneau de progression circulaire (`CircularProgress.vue`)
- Timer en direct HH:MM:SS (mis à jour chaque seconde via `useTimer`)
- Temps écoulé et temps restant
- Indicateur de phase (`PhaseIndicator.vue`)
- Bouton "Terminer le Jeûne"

**Si aucun jeûne actif :**
- Boutons de démarrage rapide : 48h, 72h, Personnalisé
- Résumé du dernier jeûne

**Toujours visible :**
- Cartes de stats rapides (total jeûnes, complétés, durée moy., poids perdu)
- Repas recommandés (mode compact)
- Mini graphique de poids (30 derniers jours)

---

#### `StartFast.vue` — Démarrer un jeûne

Champs du formulaire :
- Type de jeûne : `16:8`, `18:6`, `20:4`, `OMAD`, `48h`, `72h`, `Personnalisé`
- Durée personnalisée (si type = Personnalisé)
- Poids avant (optionnel)
- Notes (optionnel)
- Heure de début personnalisée (défaut : maintenant)

---

#### `FastDetail.vue` — Détail d'un jeûne

- Anneau de progression avec timer live (si actif)
- Chronologie des phases (visuelle)
- Carte état corporel (`BodyStateCard.vue`) — processus physiologiques en cours
- **Section journaux quotidiens :**
  - Eau consommée (curseur 0–5 L)
  - Électrolytes pris (toggle)
  - Niveau d'énergie (curseur 1–10)
  - Niveau de faim (curseur 1–10)
  - Humeur (sélecteur emoji)
  - Notes libres
- Historique des journaux
- Formulaire d'ajout de repas + liste des repas
- Bouton "Terminer le Jeûne" (avec saisie du poids final)
- Bouton de suppression du jeûne

---

#### `History.vue` — Historique

- Liste de tous les jeûnes passés
- Filtre par type (16:8, 48h, 72h…)
- Chaque jeûne affiché avec `FastCard.vue` (type, dates, durée, perte de poids, statut)

---

#### `StatsView.vue` — Statistiques

- 4 cartes de stats (`StatCard.vue`) : total, complétés, durée moy., poids perdu
- Graphique barre : jeûnes par type (Chart.js)
- Graphique ligne : évolution du poids (historique complet)

---

#### `WeightView.vue` — Journal de poids

- Saisie rapide du poids du jour
- Graphique ligne poids (Chart.js)
- Tableau de toutes les entrées

---

#### `MealsView.vue` — Repas

- Liste complète des recommandations de repas avec filtres
- Journal des repas récents

---

### Composants

#### `CircularProgress.vue`
Anneau SVG animé. Props : `progress` (0–1), `size`, `strokeWidth`, `color`.
Utilise `stroke-dasharray` / `stroke-dashoffset` pour l'animation.

#### `FastCard.vue`
Carte cliquable pour un jeûne. Affiche : type, date de début, durée, delta de poids, badge statut (complété / en cours / abandonné). Lien vers `/fast/:id`.

#### `PhaseIndicator.vue`
Badge coloré indiquant la phase actuelle du jeûne :

| Phase              | Heures    | Couleur  | Description                    |
|--------------------|-----------|----------|--------------------------------|
| Facile             | 0–12h     | Vert     | Corps utilise le glucose       |
| Transition Cétose  | 12–24h    | Orange   | Glycogène épuisé, début cétose |
| Difficile          | 24–36h    | Rouge    | Phase d'adaptation             |
| Stabilisation      | 36h+      | Violet   | Cétose établie, autophagie     |

#### `StatCard.vue`
Carte simple : icône + libellé + valeur. Utilisée pour les statistiques rapides.

#### `WeightChart.vue`
Graphique ligne avec Chart.js. Mode `mini` pour le dashboard (sans axes, points réduits). Mode normal pour la vue poids avec axes complets.

#### `MoodSelector.vue`
Sélecteur d'humeur avec 6 emojis : 😊 😐 😣 🤮 😴 💪.

#### `SliderInput.vue`
Curseur stylisé (`<input type="range">`) avec libellé et unité. Compatible `v-model`. Utilisé pour eau, énergie, faim.

#### `NavBar.vue`
Navigation responsive. Toggle dark mode intégré dans la sidebar desktop. Met en surbrillance la route active.

#### `BodyStateCard.vue`
Carte éducative sur l'état physiologique selon la phase :
- Icône et couleur de phase
- Titre et description
- Liste des processus actifs (glucose, glycogène, lipolyse, autophagie, cétones, HGH, BDNF…) avec badges de statut
- Section de conseils pratiques
- Aperçu de la prochaine phase avec barre de progression et compte à rebours

#### `MealRecommendationCard.vue`
Carte repas : nom, catégorie, digestibilité (badge coloré), description résumée, macros, temps de préparation, difficulté. Déclenche `MealDetailModal.vue` au clic.

#### `MealDetailModal.vue`
Bottom sheet modal pour le détail complet d'un repas :
- Nom, catégorie, description
- Macros avec barres de pourcentage
- Temps de prep, difficulté, digestibilité
- Liste d'ingrédients avec cases à cocher
- Conseils de préparation
- Bouton "Enregistrer ce repas" (logue dans le jeûne actif)

#### `MealRecommendationsList.vue`
Conteneur pour les recommandations avec :
- Filtres : catégorie, timing de consommation
- Grille de `MealRecommendationCard`
- États de chargement et d'erreur
- Mode compact (dashboard)

---

### Composables

#### `useTimer.ts`
```typescript
const { elapsed, remaining, progress, isOvertime,
        elapsedFormatted, remainingFormatted,
        start, stop } = useTimer(startedAt, targetHours)
```
- `elapsed` / `remaining` : durées en secondes
- `progress` : nombre entre 0 et 1
- `isOvertime` : booléen si le jeûne dépasse la cible
- `elapsedFormatted` / `remainingFormatted` : format HH:MM:SS
- Se met à jour chaque seconde via `setInterval`

#### `useDark.ts`
```typescript
const { isDark, toggle } = useDark()
```
- Lit `localStorage` pour la préférence de thème
- Fallback sur la préférence système (`prefers-color-scheme`)
- Ajoute/retire la classe `dark` sur `<html>`

#### `useBodyState.ts`
```typescript
const bodyState = useBodyState(elapsedHours)
```
Retourne l'état physiologique détaillé pour un nombre d'heures de jeûne donné. Données couvrant les phases 0–4h, 4–12h, 12–24h, 24–36h, 36–48h, 48–72h, 72h+.

#### `useMealRecommendations.ts`
```typescript
const { suggestions, categories, fetchSuggestions, fetchCategories } = useMealRecommendations()
```
Gère les appels à `/api/meals/recommendations` avec filtrage. Expose les constantes de labels : `CATEGORY_LABELS`, `TIMING_LABELS`, `DIFFICULTY_LABELS`, `DIGESTIBILITY_COLORS`.

#### `useOfflineStorage.ts`
```typescript
const { saveActiveFast, loadActiveFast, clearActiveFast } = useOfflineStorage()
```
Persiste le jeûne actif en `localStorage` pour un affichage offline partiel.

#### `useOnlineStatus.ts`
```typescript
const { isOnline } = useOnlineStatus()
```
Réactif à `navigator.onLine` et aux événements `online`/`offline`. Utilisé dans `App.vue` pour afficher une bannière de déconnexion.

---

### Client API (`src/api/client.ts`)

Wrapper fetch centralisé pointant vers `http://localhost:8042` (dev) ou `/api` (prod via Nginx).

Fonctions exportées :

```typescript
// Jeûnes
getFasts(page?, limit?)
getCurrentFast()
getFast(id)
createFast(data)
updateFast(id, data)
deleteFast(id)

// Journaux
getLogs(fastId)
createLog(fastId, data)

// Repas
getMeals(fastId)
createMeal(fastId, data)
getRecentMeals()

// Recommandations
getMealRecommendations(params)
getMealRecommendationCategories()

// Poids
getWeightHistory(start?, end?)
logWeight(data)
getWeightTrend()

// Stats
getStats()
getWeeklyStats()
```

---

### Types TypeScript (`src/types/index.ts`)

```typescript
interface Fast {
  id: number
  type: string
  started: string
  ended?: string
  target_hours: number
  completed: boolean
  notes?: string
  weight_before?: number
  weight_after?: number
  created_at: string
  updated_at: string
}

interface DailyLog {
  id: number
  fast_id: number
  log_date: string
  water_liters?: number
  electrolytes?: boolean
  energy_level?: number
  hunger_level?: number
  mood?: string
  notes?: string
  created_at: string
}

interface Meal {
  id: number
  fast_id?: number
  meal_type: string
  meal_name?: string
  ingredients?: string[]
  calories?: number
  meal_time?: string
  is_breaking_fast?: boolean
  notes?: string
  created_at: string
}

interface WeightEntry {
  id: number
  weigh_date: string
  weight: number
  notes?: string
  created_at: string
}

interface Stats {
  total_fasts: number
  completed_fasts: number
  avg_duration_hours: number
  total_weight_lost: number
  fasts_by_type: Record<string, number>
  current_streak: number
}

interface MealRecommendation {
  id: number
  name: string
  category: string
  description: string
  ingredients: string[]
  prep_time: number
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  difficulty: string
  digestibility: string
  best_timing: string[]
  suitable_for: string[]
  tips: string
}
```

---

## 7. Docker & déploiement

### Dockerfile Backend (`backend/Dockerfile`)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8042"]
```

### Dockerfile Frontend (`frontend/Dockerfile`)

Build multi-stage : Vite build → Nginx serve.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Configuration Nginx (`frontend/nginx.conf`)

Nginx sert les fichiers statiques et proxifie `/api/*` vers le backend :

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8042;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Compose

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    container_name: fasting_backend
    restart: unless-stopped
    ports:
      - "8042:8042"
    environment:
      - DATABASE_URL=postgresql://fasting_coach:PASSWORD@postgresql.host:5432/fasting_db
    networks:
      - fasting_net

  frontend:
    build: ./frontend
    container_name: fasting_frontend
    restart: unless-stopped
    ports:
      - "5173:80"
    depends_on:
      - backend
    networks:
      - fasting_net

networks:
  fasting_net:
    driver: bridge
```

**Lancement :**
```bash
docker compose up -d --build
```

---

## 8. Flux utilisateur principal

### Scénario : démarrer et terminer un jeûne de 48h

```
Utilisateur                  Frontend                      Backend / DB
    │                            │                              │
    │  Ouvre l'app               │                              │
    │ ─────────────────────────► │  GET /api/fasts/current      │
    │                            │ ────────────────────────────►│
    │                            │      ◄── null (pas de jeûne) │
    │                            │                              │
    │  Clique "48h" (démarrage   │                              │
    │  rapide sur Dashboard)     │                              │
    │ ─────────────────────────► │  POST /api/fasts             │
    │                            │  { type: "48h",              │
    │                            │    target_hours: 48,         │
    │                            │    started: now }            │
    │                            │ ────────────────────────────►│
    │                            │      ◄── FastResponse (id=2) │
    │                            │                              │
    │  Dashboard affiche :       │                              │
    │  ● Anneau de progression   │                              │
    │  ● Timer 00:00:01…         │  (useTimer démarre)          │
    │  ● Phase: Facile           │                              │
    │                            │                              │
    │  (Le lendemain)            │                              │
    │  Renseigne le journal      │                              │
    │  Eau: 2.5L, Énergie: 7    │                              │
    │ ─────────────────────────► │  POST /api/fasts/2/logs      │
    │                            │ ────────────────────────────►│
    │                            │      ◄── DailyLogResponse    │
    │                            │                              │
    │  Clique "Terminer le       │                              │
    │  Jeûne", saisit poids: 80 │                              │
    │ ─────────────────────────► │  PUT /api/fasts/2            │
    │                            │  { ended: now,               │
    │                            │    completed: true,          │
    │                            │    weight_after: 80.0 }      │
    │                            │ ────────────────────────────►│
    │                            │      ◄── FastResponse (MAJ)  │
    │                            │                              │
    │  Dashboard affiche :       │                              │
    │  ● Boutons démarrage rapide│                              │
    │  ● Résumé: 48h, -2.5kg    │                              │
```

---

### Flux de navigation typique

```
Dashboard (/))
   │
   ├── Jeûne actif → FastDetail (/fast/:id)
   │       ├── Logger journal quotidien
   │       ├── Logger un repas
   │       └── Terminer le jeûne → Dashboard
   │
   ├── Pas de jeûne → StartFast (/start)
   │       └── Formulaire → POST /api/fasts → Dashboard
   │
   ├── NavBar: Stats (/stats)
   │       ├── Graphique poids
   │       └── Graphique par type de jeûne
   │
   ├── NavBar: Poids (/weight)
   │       ├── Saisie poids du jour
   │       └── Graphique historique
   │
   ├── NavBar: Repas (/meals)
   │       ├── Recommandations filtrées
   │       └── Modal détail repas
   │
   └── NavBar: Historique (/history)
           └── Liste tous les jeûnes → FastDetail
```

---

## 9. Fonctionnalités avancées

### Phases de jeûne et état corporel

L'application affiche des informations physiologiques détaillées selon l'avancement du jeûne :

| Phase              | Heures    | Processus clés                                      |
|--------------------|-----------|-----------------------------------------------------|
| Facile             | 0–12h     | Utilisation du glucose, début d'épuisement du glycogène |
| Transition Cétose  | 12–24h    | Glycogène épuisé, lipolyse, début de production de cétones |
| Difficile          | 24–36h    | Pleine cétose, autophagie déclenchée, HGH augmenté  |
| Stabilisation      | 36–48h    | Cétose établie, BDNF, régénération cellulaire       |
| Jeûne prolongé     | 48–72h    | Autophagie profonde, réinitialisation immunitaire   |
| Jeûne étendu       | 72h+      | Effets métaboliques maximaux                        |

### Progressive Web App (PWA)

- Service Worker configuré via Workbox
- Cache des ressources statiques (offline)
- Cache des appels API clés (`/api/fasts/current`, `/api/weight`)
- Installable sur mobile (manifest PWA)
- Bannière d'état hors-ligne via `useOnlineStatus`

### Recommandations de repas intelligentes

Le backend filtre les repas recommandés selon :
- Le **type de jeûne** en cours (16:8, 48h, 72h…) → adapte les suggestions au profil nutritionnel approprié
- La **catégorie** (soupe, salade, protéine…)
- Le **timing** (`breaking_fast`, `post_fast`, `pre_fast`)
- La **digestibilité** (légère, modérée, riche)
- La **difficulté** de préparation

### Mode hors-ligne partiel

Via `useOfflineStorage` : le jeûne actif est sauvegardé en `localStorage`. Si le réseau est perdu, le timer continue à fonctionner et les données de base restent affichées.

### Mode sombre

Supporté via la classe Tailwind `dark:`. Persisté en `localStorage`. Détection automatique de la préférence système. Toggle disponible dans la sidebar.

---

## 10. Variables d'environnement & configuration

### Backend

| Variable      | Valeur par défaut                                                    |
|---------------|----------------------------------------------------------------------|
| `DATABASE_URL`| `postgresql://fasting_coach:PASSWORD@postgresql.host:5432/fasting_db` |
| Port          | `8042` (hardcodé dans Uvicorn)                                       |

### Frontend (dev)

| Paramètre     | Valeur          |
|---------------|-----------------|
| Port Vite     | `5173`          |
| API base URL  | `http://localhost:8042` |
| Hosts autorisés | `localhost`, `openclaw.host` |

### Frontend (prod via Nginx)

En production, le frontend et le backend sont dans le même réseau Docker. Nginx proxifie `/api/*` → `http://backend:8042`. Pas besoin de configurer l'URL de l'API dans le build.

---

*Documentation générée le 2026-03-15 — Fasting Tracker App v1.0*
