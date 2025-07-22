# 🎓 Agent de Suivi des Progrès SQL

Une application Streamlit intelligente pour le suivi et l'analyse des performances d'apprentissage SQL, utilisant l'IA générative de Google Gemini pour des recommandations personnalisées.

## 📊 Aperçu

L'Agent de Suivi des Progrès SQL est un outil complet conçu pour monitorer, analyser et optimiser l'apprentissage des bases de données relationnelles et du langage SQL. L'application combine des visualisations de données avancées avec l'intelligence artificielle pour fournir des insights personnalisés et des plans d'action adaptatifs.

## ✨ Fonctionnalités Principales

### 📈 Analyse des Performances
- **Métriques en temps réel** : Score moyen, nombre d'activités, tendances de progression
- **Visualisations interactives** : Graphiques de progression, heatmaps de performance
- **Analyse par chapitre** : Performance détaillée sur 10 modules SQL
- **Suivi temporel** : Évolution des scores dans le temps

### 🎯 Recommandations IA
- **Intelligence artificielle** : Intégration avec Google Gemini API
- **Conseils personnalisés** : Recommandations basées sur les patterns d'apprentissage
- **Plans d'action SMART** : Objectifs spécifiques, mesurables et temporellement définis
- **Adaptation continue** : Suggestions évolutives selon les progrès

### 📊 Analyses Avancées
- **Heatmap de performance** : Visualisation chapitre × type d'activité
- **Corrélation temps/score** : Optimisation du temps d'étude
- **Identification des patterns** : Points forts et axes d'amélioration
- **Analyse comparative** : Performance par type d'exercice

## 🏗️ Architecture Technique

### Technologies Utilisées
- **Frontend** : Streamlit
- **Visualisations** : Plotly Express & Graph Objects
- **Données** : Pandas, NumPy
- **IA** : Google Generative AI (Gemini)

### Structure du Projet
```
agent_suivi1.py
├── Configuration Streamlit
├── Génération de données d'exemple
├── Calculs de métriques de progression
├── Intégration API Gemini
├── Visualisations interactives
└── Interface utilisateur multi-onglets
```

## 🚀 Installation et Configuration

### Prérequis
```bash
pip install streamlit pandas numpy plotly google-generativeai
```

### Configuration de l'API Gemini
1. Obtenez une clé API Google Generative AI
2. Remplacez `GEMINI_API_KEY` dans le code par votre clé :
```python
GEMINI_API_KEY = "VOTRE_CLE_API_ICI"
```

### Lancement de l'Application
```bash
streamlit run agent_suivi1.py
```

## 📚 Modules d'Apprentissage Couverts

1. **Introduction aux BD** - Concepts fondamentaux
2. **Modèle relationnel** - Théorie des bases de données
3. **Langage SQL de base** - Syntaxe et commandes
4. **Requêtes SELECT** - Interrogation de données
5. **Jointures** - Relations entre tables
6. **Fonctions d'agrégation** - Calculs statistiques
7. **Sous-requêtes** - Requêtes imbriquées
8. **Vues et index** - Optimisation
9. **Transactions** - Gestion de la cohérence
10. **Optimisation** - Performance avancée

## 🎯 Fonctionnalités Détaillées

### Onglet "Vue d'ensemble"
- Métriques clés de performance
- Graphique de performance par chapitre
- Indicateurs de tendance

### Onglet "Analyses détaillées"
- Heatmap chapitre × type d'activité
- Points forts et axes d'amélioration
- Corrélation temps d'étude/performance
- Distribution des performances par type d'exercice

### Onglet "Recommandations"
- Recommandations IA personnalisées
- Plan d'action détaillé
- Objectifs SMART générés automatiquement
- Stratégies d'optimisation d'apprentissage

### Onglet "Données brutes"
- Export et filtrage des données
- Statistiques détaillées
- Historique complet des activités

### Types d'Activités Supportés
- **Quiz** : Évaluations rapides
- **Exercice pratique** : Travaux dirigés
- **Projet** : Réalisations complètes
- **Évaluation** : Tests formels

## 🤖 Intégration IA

L'application utilise Google Gemini pour :
- Analyse des patterns d'apprentissage
- Génération de recommandations contextuelles
- Création de plans d'action personnalisés
- Définition d'objectifs SMART

### Prompts IA Optimisés
- Recommandations basées sur les métriques de performance
- Prise en compte des tendances individuelles
- Adaptation selon les points forts/faibles
- Suggestions temporellement pertinentes

