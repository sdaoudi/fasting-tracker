# PWA Fasting Tracker — Roadmap

## ✅ Fait (PWA Basique)

- `vite-plugin-pwa` installé et configuré
- Manifest Web App (nom, couleurs, display standalone)
- Icônes PNG 192x192 et 512x512 générées depuis le favicon SVG
- Service Worker auto-update via Workbox
- `meta theme-color` + `apple-touch-icon` dans index.html
- L'app est **installable** sur mobile (Android + iOS)

---

## 🔜 Next Steps

### 1. Offline Caching Strategy (Workbox)
**Complexité : Faible (~2-3h)**

- Configurer les stratégies de cache Workbox dans `vite-plugin-pwa` :
  - `CacheFirst` pour les assets statiques (JS, CSS, images)
  - `NetworkFirst` pour les appels API
  - `StaleWhileRevalidate` pour les pages HTML
- Ajouter un fallback offline page
- Précacher les routes principales (`/`, `/start`, `/history`)

### 2. Offline Data Sync avec IndexedDB
**Complexité : Moyenne (~1-2 jours)**

- Installer `idb` ou `Dexie.js` pour IndexedDB
- Stocker localement :
  - Jeûne en cours (timer, état)
  - Logs quotidiens (eau, énergie, faim)
  - Repas enregistrés
- Créer une **sync queue** :
  - Les actions offline sont stockées dans une queue
  - Au retour de la connexion, les actions sont rejouées vers l'API
  - Gestion des conflits (timestamp-based)
- Afficher un indicateur online/offline dans l'UI

### 3. Push Notifications
**Complexité : Moyenne-Haute (~2-3 jours)**

- Configurer un serveur de push (Web Push API + VAPID keys)
- Backend : endpoint pour stocker les subscriptions push
- Types de notifications :
  - ⏰ Rappel de fin de jeûne
  - 💧 Rappels d'hydratation (toutes les 2h pendant un jeûne)
  - 🎯 Objectif atteint (48h, 72h, etc.)
  - 📊 Résumé quotidien
- Permettre à l'utilisateur de configurer ses préférences de notification

### 4. Background Sync
**Complexité : Moyenne (~1 jour)**

- Utiliser la Background Sync API pour :
  - Enregistrer les repas même hors ligne
  - Mettre à jour les logs quotidiens
  - Sync automatique au retour de connexion
- Requiert le service worker Workbox `BackgroundSyncPlugin`

### 5. App Store (TWA - Trusted Web Activity)
**Complexité : Faible-Moyenne (~1 jour)**

- Créer un projet Android avec Bubblewrap ou PWABuilder
- Configurer `assetlinks.json` pour la vérification du domaine
- Publier sur le Google Play Store
- Pour iOS : guide d'installation "Add to Home Screen"

---

## 📋 Ordre recommandé

1. **Offline Caching** → Quick win, améliore l'UX immédiatement
2. **IndexedDB Sync** → Essentiel pour une vraie app offline
3. **Push Notifications** → Killer feature pour le suivi de jeûne
4. **Background Sync** → Complément naturel de l'IndexedDB sync
5. **TWA Play Store** → Nice-to-have, visibilité

## 🛠️ Stack technique recommandée

- `vite-plugin-pwa` (déjà installé) — Workbox intégré
- `idb` ou `Dexie.js` — IndexedDB wrapper
- `web-push` (npm) — Serveur push notifications
- `@nicolo-ribaudo/bubblewrap` — TWA packaging
