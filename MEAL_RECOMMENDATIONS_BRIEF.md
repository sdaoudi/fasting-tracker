# Brief: Intégration Meal Recommendations dans Fast Tracking App

## Contexte
L'application Fast Tracking permet de suivre les jeûnes intermittents (16h, 24h, 48h, 72h+).  
Une nouvelle table `meal_recommendations` a été créée dans PostgreSQL avec 19 repas adaptés aux différentes phases de jeûne.

## Objectif
Intégrer une fonctionnalité de **recommandations de repas intelligentes** basées sur :
- Le type de jeûne en cours
- La durée du jeûne
- La phase de reprise alimentaire
- Le moment de la journée (petit-déj, déjeuner, dîner, collation)

## Schéma de la table `meal_recommendations`

```sql
CREATE TABLE meal_recommendations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'rupture_jeune', 'repas_fenetre', 'reprise_progressive'
    fast_duration VARCHAR(20), -- '16h', '24h', '48h', '72h', '7j+'
    phase VARCHAR(50), -- 'jour_1', 'jour_2', 'jour_3', etc.
    description TEXT,
    ingredients TEXT[], -- Liste d'ingrédients
    macros JSONB, -- {"calories": 400, "protein": 30, "carbs": 20, "fat": 15}
    preparation_time INT, -- en minutes
    difficulty VARCHAR(20), -- 'facile', 'moyen', 'avancé'
    tips TEXT, -- Conseils de préparation
    digestibility VARCHAR(20), -- 'très_facile', 'facile', 'moyen'
    meal_timing VARCHAR(50), -- 'petit_dejeuner', 'dejeuner', 'diner', 'collation'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Fonctionnalités à développer

### 1. Backend API (FastAPI)

#### Endpoints à créer

**a) GET `/api/v1/meal-recommendations/suggest`**
- Paramètres:
  - `fast_id` (optionnel) : ID du jeûne en cours
  - `fast_duration` : durée du jeûne (16h, 48h, etc.)
  - `phase` (optionnel) : jour_1, jour_2, jour_3
  - `meal_timing` (optionnel) : petit_dejeuner, dejeuner, diner, collation
- Retourne: Liste de repas recommandés triés par pertinence

**b) GET `/api/v1/meal-recommendations/{id}`**
- Retourne: Détails complets d'un repas spécifique

**c) GET `/api/v1/meal-recommendations/categories`**
- Retourne: Liste des catégories disponibles avec le nombre de repas par catégorie

**d) POST `/api/v1/meal-recommendations/favorite`**
- Ajoute un repas aux favoris de l'utilisateur (future feature)

#### Logique de recommandation intelligente

```python
def get_meal_suggestions(fast_id=None, fast_duration=None, phase=None, meal_timing=None):
    """
    Logique de sélection :
    1. Si jeûne en cours (fast_id):
       - Durée < 24h → category='rupture_jeune' OU 'repas_fenetre'
       - 24h-48h → category='rupture_jeune' + digestibility='très_facile'
       - 48h-72h → category='reprise_progressive', phase='jour_1' → 'jour_3'
       - 7j+ → category='reprise_progressive', fast_duration='7j+', phase='jour_1' → 'jour_7'
    
    2. Filtrer par meal_timing si fourni (heure de la journée)
    
    3. Trier par:
       - digestibility (très_facile en premier après jeûne long)
       - preparation_time (repas rapides en priorité)
    
    4. Limiter à 3-5 suggestions max
    """
```

### 2. Frontend (React/Next.js)

#### Composants à créer

**a) `MealRecommendationCard.tsx`**
- Affiche :
  - Nom du repas
  - Image (placeholder ou intégration Unsplash/autre)
  - Temps de préparation
  - Difficulté
  - Macros (calories, protéines, glucides, lipides)
  - Badge de digestibilité
  - Bouton "Voir la recette"

**b) `MealRecommendationsList.tsx`**
- Liste scrollable de MealRecommendationCard
- Filtres :
  - Par catégorie
  - Par moment de la journée
  - Par difficulté
  - Par temps de préparation

**c) `MealDetailModal.tsx`**
- Modal qui affiche :
  - Nom, description, photo
  - Liste d'ingrédients (avec checkboxes)
  - Instructions de préparation (tips)
  - Informations nutritionnelles détaillées
  - Bouton "J'ai mangé ce repas" → log le repas dans `meals` table

**d) Intégration dans `FastDashboard.tsx`**
- Section "Recommandations de repas" affichée :
  - Pendant un jeûne en cours (suggestions rupture de jeûne)
  - En fenêtre alimentaire (suggestions repas normaux)
  - Après un jeûne long (suggestions reprise progressive avec timeline jour 1-2-3)

#### UX/UI Guidelines

- **Design moderne et appétissant** :
  - Cards avec images de repas (utiliser Unsplash API ou placeholders)
  - Badges colorés pour catégories (vert = très facile, orange = moyen, etc.)
  - Icônes pour temps de préparation, difficulté, macros
  
- **Responsive** : mobile-first design
  
- **Interactions** :
  - Swipe horizontal pour parcourir les suggestions sur mobile
  - Click → ouvre le modal de détails
  - Bouton "J'ai mangé ça" → enregistre dans `meals` table avec timestamp

### 3. Base de données

**Connexion existante** :
```json
{
  "host": "postgresql.host",
  "port": 5432,
  "dbname": "fasting_db",
  "user": "fasting_coach",
  "password": "***REMOVED***"
}
```

**Tables existantes à lier** :
- `fasts` : jeûnes en cours/historique
- `meals` : repas consommés (à étendre pour lier avec meal_recommendations)

**Évolution future de `meals` table** :
Ajouter une colonne `recommendation_id` (foreign key vers `meal_recommendations.id`)

### 4. Améliorations futures (optionnelles)

- **Favoris utilisateur** : table `user_favorite_meals`
- **Ratings** : possibilité de noter les repas
- **Filtres allergènes** : exclure certains ingrédients
- **Génération d'images** : utiliser DALL-E/Stable Diffusion pour générer des photos de repas
- **Export liste de courses** : générer une liste d'ingrédients pour plusieurs repas

## Livrables attendus

1. ✅ Backend API FastAPI avec endpoints fonctionnels
2. ✅ Frontend React avec composants MealRecommendation*
3. ✅ Intégration dans le dashboard principal
4. ✅ Tests unitaires pour l'API
5. ✅ Documentation Swagger mise à jour
6. ✅ README avec instructions d'utilisation

## Stack technique

- **Backend** : FastAPI, PostgreSQL, SQLAlchemy
- **Frontend** : React/Next.js, TypeScript, Tailwind CSS
- **État** : Zustand ou React Query pour la gestion d'état
- **API** : Axios ou Fetch API

## Chemin du projet

```
/root/clawd/skills/fasting-coach/
├── backend/
│   ├── api/
│   │   └── meal_recommendations.py  (nouveaux endpoints)
│   ├── models/
│   │   └── meal_recommendation.py   (nouveau modèle SQLAlchemy)
│   └── services/
│       └── meal_recommendation_service.py (logique métier)
├── frontend/
│   ├── components/
│   │   ├── MealRecommendationCard.tsx
│   │   ├── MealRecommendationsList.tsx
│   │   └── MealDetailModal.tsx
│   ├── pages/
│   │   └── fast-dashboard.tsx (à modifier)
│   └── hooks/
│       └── useMealRecommendations.ts
└── scripts/
    └── track_fast.py (possibilité d'intégrer CLI pour suggestions)
```

## Notes importantes

- **Digestibilité** : critère clé après un jeûne long → prioriser "très_facile" puis "facile"
- **Progressivité** : respecter les phases jour_1 → jour_2 → jour_3 pour jeûnes 48h+
- **Contexte utilisateur** : adapter les suggestions selon l'heure actuelle (matin = petit-déj, etc.)
- **Macros** : afficher de manière claire et attrayante (graphiques circulaires ou barres)

## Validation

Tester avec différents scénarios :
1. Jeûne 16h en cours → suggère repas rupture_jeune
2. Jeûne 48h terminé → suggère repas reprise jour_1
3. En fenêtre alimentaire → suggère repas_fenetre variés
4. Filtrer par moment de la journée (midi vs soir)

---

**Prêt à développer ? Go ! 🚀**
