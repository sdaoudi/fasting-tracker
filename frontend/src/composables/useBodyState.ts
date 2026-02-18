import { computed } from 'vue'

export interface BodyProcess {
  icon: string
  name: string
  status: 'active' | 'starting' | 'inactive'
  detail: string
}

export interface BodyState {
  phase: string
  phaseIcon: string
  phaseColor: string
  headline: string
  description: string
  processes: BodyProcess[]
  tips: string[]
  nextPhase?: {
    name: string
    hoursUntil: number
    preview: string
  }
}

function getBodyState(hours: number): BodyState {
  if (hours < 4) {
    return {
      phase: 'Post-repas',
      phaseIcon: '🍽️',
      phaseColor: '#6b7280',
      headline: 'Digestion en cours',
      description: 'Ton corps traite le dernier repas. L\'insuline est élevée pour stocker le glucose dans les cellules et le glycogène dans le foie et les muscles. Pas encore de brûlure de graisses.',
      processes: [
        { icon: '🍬', name: 'Glycémie', status: 'active', detail: 'Glucose absorbé, insuline élevée' },
        { icon: '💾', name: 'Stockage glycogène', status: 'active', detail: 'Foie et muscles stockent l\'énergie' },
        { icon: '🔥', name: 'Lipolyse', status: 'inactive', detail: 'Pas encore active' },
        { icon: '🧹', name: 'Autophagie', status: 'inactive', detail: 'Inhibée par l\'insuline' },
      ],
      tips: [
        'Hydrate-toi bien (eau, tisanes sans sucre)',
        'Évite tout snack pour ne pas relancer l\'insuline',
        'Le jeûne commence vraiment dans quelques heures',
      ],
      nextPhase: { name: 'Transition', hoursUntil: 4 - hours, preview: 'L\'insuline commence à baisser' },
    }
  }

  if (hours < 8) {
    return {
      phase: 'Transition',
      phaseIcon: '⚡',
      phaseColor: '#3b82f6',
      headline: 'Ton corps passe en mode économie',
      description: 'L\'insuline baisse, le glucagon monte. Le foie commence à libérer du glycogène dans le sang. Les graisses commencent timidement à être mobilisées.',
      processes: [
        { icon: '📉', name: 'Insuline', status: 'active', detail: 'En baisse progressive' },
        { icon: '📈', name: 'Glucagon', status: 'starting', detail: 'Commence à monter' },
        { icon: '🏦', name: 'Glycogène hépatique', status: 'active', detail: 'Libéré dans le sang' },
        { icon: '🔥', name: 'Mobilisation graisses', status: 'starting', detail: 'Légère activation' },
      ],
      tips: [
        'Continue à bien t\'hydrater',
        'Une légère faim est normale — elle passera',
        'Marcher favorise la vidange du glycogène',
      ],
      nextPhase: { name: 'Début du vrai jeûne', hoursUntil: 8 - hours, preview: 'Glycogène en épuisement, cétones qui commencent' },
    }
  }

  if (hours < 12) {
    return {
      phase: 'Début du jeûne',
      phaseIcon: '🌅',
      phaseColor: '#10b981',
      headline: 'Le vrai jeûne commence !',
      description: 'Le glycogène s\'épuise. Ton corps active la gluconéogenèse (fabrication de glucose à partir des acides aminés et graisses). Les premières cétones apparaissent.',
      processes: [
        { icon: '⚗️', name: 'Gluconéogenèse', status: 'active', detail: 'Production de glucose depuis les graisses' },
        { icon: '🧪', name: 'Cétones', status: 'starting', detail: 'Premières traces détectables' },
        { icon: '💧', name: 'Glycogène', status: 'active', detail: 'Presque épuisé' },
        { icon: '🔄', name: 'Adaptation métabolique', status: 'starting', detail: 'Changement de carburant en cours' },
      ],
      tips: [
        'C\'est souvent le moment où la faim est la plus forte — tiens bon !',
        'Sel + eau si tu as des crampes (électrolytes)',
        'Le café noir ou thé vert aident à passer ce cap',
      ],
      nextPhase: { name: 'Cétose légère', hoursUntil: 12 - hours, preview: 'Cétones 0.5-1 mmol/L, autophagie démarre' },
    }
  }

  if (hours < 16) {
    return {
      phase: 'Cétose légère',
      phaseIcon: '🌟',
      phaseColor: '#f59e0b',
      headline: 'Cétose démarrée ! Graisses en feu 🔥',
      description: 'Glycogène quasi épuisé. Ton corps bascule sur les graisses comme carburant principal. Les cétones atteignent 0.5-1 mmol/L. L\'autophagie s\'enclenche — nettoyage cellulaire en cours !',
      processes: [
        { icon: '🧪', name: 'Cétones (0.5-1 mmol/L)', status: 'active', detail: 'Carburant cérébral alternatif' },
        { icon: '🔥', name: 'Lipolyse', status: 'active', detail: 'Graisses brûlées activement' },
        { icon: '🧹', name: 'Autophagie', status: 'starting', detail: 'Nettoyage des cellules endommagées' },
        { icon: '🧠', name: 'Mental clarity', status: 'starting', detail: 'Cerveau qui s\'adapte aux cétones' },
      ],
      tips: [
        'Électrolytes importants : sodium, magnésium, potassium',
        'Tu peux ressentir une légère fatigue — c\'est normal',
        'L\'haleine peut changer (cétones) — c\'est bon signe !',
      ],
      nextPhase: { name: 'Cétose installée', hoursUntil: 16 - hours, preview: 'HGH monte, clarity mentale maximale' },
    }
  }

  if (hours < 24) {
    return {
      phase: 'Cétose installée',
      phaseIcon: '💫',
      phaseColor: '#8b5cf6',
      headline: 'Pleine cétose — ton cerveau adore ça !',
      description: 'Corps en cétose nutritionnelle. Les cétones alimentent efficacement le cerveau. L\'hormone de croissance (HGH) commence à augmenter significativement. Autophagie bien active — tes cellules font le grand nettoyage.',
      processes: [
        { icon: '🧪', name: 'Cétose nutritionnelle', status: 'active', detail: '>0.5 mmol/L — carburant principal' },
        { icon: '🧹', name: 'Autophagie', status: 'active', detail: 'Recyclage cellulaire intense' },
        { icon: '💉', name: 'HGH (hormone croissance)', status: 'starting', detail: '+100-300% vs normal' },
        { icon: '🧠', name: 'BDNF', status: 'starting', detail: 'Facteur neurotrophique en hausse' },
        { icon: '📊', name: 'Insuline', status: 'active', detail: 'Au plus bas — sensibilité améliorée' },
      ],
      tips: [
        'Période de grande clarté mentale pour beaucoup',
        'Léger exercice possible (marche, yoga)',
        'Sel marin dans l\'eau pour les électrolytes',
        'Tu passes la barre cruciale des 16h — bravo !',
      ],
      nextPhase: { name: 'Cétose profonde', hoursUntil: 24 - hours, preview: 'Autophagie maximale, HGH +500%' },
    }
  }

  if (hours < 36) {
    return {
      phase: 'Cétose profonde',
      phaseIcon: '🚀',
      phaseColor: '#ec4899',
      headline: 'Mode régénération activé !',
      description: 'Cétones entre 1-3 mmol/L. Autophagie à son maximum. HGH peut atteindre +300-500% de la normale. Le BDNF monte — excellent pour la santé cérébrale. Ton corps est en mode réparation intensive.',
      processes: [
        { icon: '🧪', name: 'Cétones (1-3 mmol/L)', status: 'active', detail: 'Niveau thérapeutique' },
        { icon: '🧹', name: 'Autophagie maximale', status: 'active', detail: 'Nettoyage profond des cellules' },
        { icon: '💉', name: 'HGH +300-500%', status: 'active', detail: 'Régénération musculaire et tissulaire' },
        { icon: '🧠', name: 'BDNF élevé', status: 'active', detail: 'Neuroplasticité améliorée' },
        { icon: '🔥', name: 'Anti-inflammation', status: 'active', detail: 'Marqueurs inflammatoires en baisse' },
      ],
      tips: [
        'Période où beaucoup ressentent une énergie étonnante',
        'Bon moment pour méditer ou travailler sur des projets créatifs',
        'Continue à boire 2-3L d\'eau avec électrolytes',
        'Évite les exercices intenses',
      ],
      nextPhase: { name: 'Adaptation complète', hoursUntil: 36 - hours, preview: 'Adaptation totale au jeûne prolongé' },
    }
  }

  if (hours < 48) {
    return {
      phase: 'Adaptation complète',
      phaseIcon: '⚡',
      phaseColor: '#f97316',
      headline: 'Corps fully adapted — niveau expert !',
      description: 'Ton corps est pleinement adapté au jeûne. Cétones 3-5 mmol/L. Régénération cellulaire intense. Inflammation systémique réduite. Mitochondries optimisées pour la production d\'énergie.',
      processes: [
        { icon: '🧪', name: 'Cétones (3-5 mmol/L)', status: 'active', detail: 'Niveau élevé, stable' },
        { icon: '⚡', name: 'Mitochondries', status: 'active', detail: 'Production d\'énergie optimisée' },
        { icon: '🛡️', name: 'Système immunitaire', status: 'starting', detail: 'Début de régénération' },
        { icon: '🔬', name: 'mTOR supprimé', status: 'active', detail: 'Effets anti-vieillissement potentiels' },
        { icon: '🩸', name: 'Glycémie', status: 'active', detail: 'Basse et stable, sans hypoglycémie' },
      ],
      tips: [
        'Tu es dans les 10% des jeûneurs qui vont aussi loin — respect !',
        'Repos important — pas d\'efforts physiques intenses',
        'Bouillon de os ou eau salée pour les minéraux',
        'Surveille tes signaux corporels attentivement',
      ],
      nextPhase: { name: 'Jeûne prolongé (48h+)', hoursUntil: 48 - hours, preview: 'Régénération immunitaire et stem cells' },
    }
  }

  if (hours < 72) {
    return {
      phase: 'Jeûne prolongé',
      phaseIcon: '🌙',
      phaseColor: '#7c3aed',
      headline: 'Régénération immunitaire en cours',
      description: 'Territoire du jeûne prolongé. Les cellules souches (stem cells) s\'activent. Régénération du système immunitaire. Autophagie à son niveau le plus profond. Le corps recycle et régénère à l\'échelle systémique.',
      processes: [
        { icon: '🌱', name: 'Stem cells activées', status: 'active', detail: 'Régénération immunitaire' },
        { icon: '🧹', name: 'Autophagie systémique', status: 'active', detail: 'Nettoyage profond, organes inclus' },
        { icon: '🛡️', name: 'Immuno-régénération', status: 'active', detail: 'Renouvellement des cellules immunitaires' },
        { icon: '🔬', name: 'mTOR inhibé', status: 'active', detail: 'Signalisation anti-vieillissement' },
        { icon: '🩸', name: 'IGF-1 réduit', status: 'active', detail: 'Facteur protecteur long-terme' },
      ],
      tips: [
        'Écoute ton corps — sortie possible si signaux d\'alarme',
        'Repos complet recommandé',
        'Eau + électrolytes toutes les heures',
        'Surveille ta tension et ton état général',
        'Prépare une sortie douce (jus, bouillon) pour rompre le jeûne',
      ],
      nextPhase: { name: 'Jeûne thérapeutique (72h+)', hoursUntil: 72 - hours, preview: 'Reset métabolique et neurogenèse' },
    }
  }

  return {
    phase: 'Jeûne thérapeutique',
    phaseIcon: '🏆',
    phaseColor: '#dc2626',
    headline: 'Territoire extrême — reset total',
    description: 'Au-delà de 72h, le corps entre en mode régénération profonde. Neurogenèse potentielle, reset métabolique complet, régénération immunitaire avancée. Ce niveau est réservé aux personnes expérimentées avec suivi médical.',
    processes: [
      { icon: '🧠', name: 'Neurogenèse', status: 'starting', detail: 'Formation potentielle de nouveaux neurones' },
      { icon: '🌱', name: 'Stem cells max', status: 'active', detail: 'Régénération multi-systémique' },
      { icon: '⚕️', name: 'Reset métabolique', status: 'active', detail: 'Remise à zéro de la sensibilité insuline' },
      { icon: '🔬', name: 'Épigénétique', status: 'starting', detail: 'Modifications de l\'expression génique' },
      { icon: '🧹', name: 'Autophagie profonde', status: 'active', detail: 'Nettoyage au niveau des organes' },
    ],
    tips: [
      '⚠️ Suivi médical fortement recommandé à ce stade',
      'Signaux d\'arrêt : vertiges sévères, confusion, douleurs cardiaques',
      'Sortie douce obligatoire : jus dilué → bouillon → fruits → normal',
      'Félicitations pour ta discipline — c\'est exceptionnel',
    ],
  }
}

export function useBodyState(elapsedHoursRef: Readonly<{ value: number }>) {
  const state = computed(() => getBodyState(elapsedHoursRef.value))
  return { state }
}
