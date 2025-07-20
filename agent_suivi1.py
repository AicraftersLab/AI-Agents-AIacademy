import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

# Import the Google Generative AI library
import google.generativeai as genai

# --- Gemini API Configuration (Replace with your actual API key) ---
# It's recommended to store your API key securely, e.g., in Streamlit secrets
# For demonstration purposes, I'll show it directly, but for production, use st.secrets
# st.secrets["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"
# genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# For immediate testing, you can paste your key here:
GEMINI_API_KEY = "AIzaSyC4dN5xboMC4Ls_JJEoHyoHf41FyVP-uCw" # Replace with your actual Gemini API key
genai.configure(api_key=GEMINI_API_KEY)
# ------------------------------------------------------------------

# Configuration de la page
st.set_page_config(
    page_title="Agent de Suivi des Progrès SQL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Données fictives pour démonstration
@st.cache_data
def load_sample_data():
    """Charge des données d'exemple pour la démonstration"""

    # Chapitres du cours SQL
    chapters = [
        "Introduction aux BD",
        "Modèle relationnel",
        "Langage SQL de base",
        "Requêtes SELECT",
        "Jointures",
        "Fonctions d'agrégation",
        "Sous-requêtes",
        "Vues et index",
        "Transactions",
        "Optimisation"
    ]

    # Types d'activités
    activity_types = ["Quiz", "Exercice pratique", "Projet", "Évaluation"]

    # Génération de données d'exemple
    data = []
    students = ["ALI", "JAMILA", "IMANE", "SOUKAINA"]

    for student in students:
        for chapter in chapters:
            for activity_type in activity_types:
                # Simulation de progression réaliste
                base_score = random.uniform(0.4, 0.95)
                num_attempts = random.randint(1, 3)

                for attempt in range(num_attempts):
                    score = min(1.0, base_score + attempt * 0.1 + random.uniform(-0.1, 0.1))

                    data.append({
                        'student_name': student,
                        'chapter': chapter,
                        'activity_type': activity_type,
                        'score': score,
                        'max_score': 1.0,
                        'attempt': attempt + 1,
                        'date': datetime.now() - timedelta(days=random.randint(0, 60)),
                        'time_spent': random.randint(10, 120),  # minutes
                        'difficulty': random.choice(['Facile', 'Moyen', 'Difficile'])
                    })

    return pd.DataFrame(data)

def calculate_progress_metrics(df: pd.DataFrame, student: str) -> Dict:
    """Calcule les métriques de progression pour un étudiant"""
    student_data = df[df['student_name'] == student]

    # Score moyen global
    avg_score = student_data['score'].mean()

    # Progression par chapitre
    chapter_progress = student_data.groupby('chapter').agg({
        'score': ['mean', 'count'],
        'time_spent': 'sum'
    }).round(3)

    # Tendances récentes (derniers 30 jours)
    recent_data = student_data[
        student_data['date'] >= datetime.now() - timedelta(days=30)
    ]

    # Identification des points forts et faibles
    chapter_scores = student_data.groupby('chapter')['score'].mean()
    strengths = chapter_scores.nlargest(3).index.tolist()
    weaknesses = chapter_scores.nsmallest(3).index.tolist()

    return {
        'avg_score': avg_score,
        'total_activities': len(student_data),
        'recent_activities': len(recent_data),
        'strengths': strengths,
        'weaknesses': weaknesses,
        'chapter_progress': chapter_progress
    }

def identify_learning_patterns(df: pd.DataFrame, student: str) -> Dict:
    """Identifie les patterns d'apprentissage"""
    student_data = df[df['student_name'] == student].sort_values('date')

    # Tendance générale (régression linéaire simple)
    if len(student_data) > 1:
        x = np.arange(len(student_data))
        y = student_data['score'].values
        trend = np.polyfit(x, y, 1)[0]  # Coefficient de la pente
    else:
        trend = 0

    # Performance par type d'activité
    activity_performance = student_data.groupby('activity_type')['score'].mean()

    # Temps d'apprentissage optimal
    time_score_correlation = student_data['time_spent'].corr(student_data['score'])

    return {
        'trend': 'Progression' if trend > 0.01 else 'Régression' if trend < -0.01 else 'Stable',
        'trend_value': trend,
        'best_activity_type': activity_performance.idxmax() if not activity_performance.empty else "N/A",
        'time_correlation': time_score_correlation if not pd.isna(time_score_correlation) else 0
    }

@st.cache_data(show_spinner="Génération des recommandations AI...")
def get_gemini_recommendations(prompt: str) -> str:
    """Interagit avec l'API Gemini pour obtenir des recommandations."""
    try:
        # IMPORTANT: Replace 'gemini-pro' below with an available model name
        # that supports 'generateContent' as found in your Streamlit sidebar's debug output.
        # Example: model = genai.GenerativeModel('gemini-1.0-pro')
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erreur lors de la communication avec Gemini API: {e}. Vérifiez votre clé API et le nom du modèle.")
        return "Impossible de générer des recommandations pour le moment. Veuillez vérifier la disponibilité du modèle ou votre clé API."

def generate_recommendation_prompt(metrics: Dict, patterns: Dict, student_name: str) -> str:
    """Génère le prompt pour les recommandations personnalisées."""
    prompt = f"""
    En tant qu'agent de suivi des progrès pour un apprenant SQL, je dois générer des recommandations personnalisées pour {student_name}.
    Voici les données de performance de l'apprenant:

    - Score moyen global: {metrics['avg_score']:.1%}
    - Nombre total d'activités complétées: {metrics['total_activities']}
    - Nombre d'activités récentes (derniers 30 jours): {metrics['recent_activities']}
    - Tendance de progression: {patterns['trend']} (valeur: {patterns['trend_value']:.3f})
    - Points forts (chapitres): {', '.join(metrics['strengths']) if metrics['strengths'] else 'Aucun'}
    - Points faibles (chapitres): {', '.join(metrics['weaknesses']) if metrics['weaknesses'] else 'Aucun'}
    - Meilleur type d'activité: {patterns['best_activity_type']}
    - Corrélation entre temps passé et score: {patterns['time_correlation']:.2f} (positive signifie plus de temps = meilleur score, négative l'inverse)

    Sur la base de ces informations, proposez 3 à 5 recommandations CONCISES et SPÉCIFIQUES pour améliorer l'apprentissage de {student_name}. Utilisez des emojis pertinents.
    Les recommandations doivent être claires et actionnables.
    """
    return prompt

def generate_action_plan_prompt(metrics: Dict, patterns: Dict, student_name: str) -> str:
    """Génère le prompt pour le plan d'action détaillé."""
    prompt = f"""
    En tant qu'agent de suivi des progrès pour un apprenant SQL, je dois générer un plan d'action détaillé et des objectifs SMART pour {student_name}.
    Voici les données de performance de l'apprenant:

    - Score moyen global: {metrics['avg_score']:.1%}
    - Tendance de progression: {patterns['trend']}
    - Points faibles (chapitres): {', '.join(metrics['weaknesses']) if metrics['weaknesses'] else 'Aucun'}
    - Meilleur type d'activité: {patterns['best_activity_type']}
    - Corrélation temps passé/score: {patterns['time_correlation']:.2f}

    Proposez un "Plan d'Action Recommandé" avec des étapes concrètes, et ensuite, définissez 2 "Objectifs SMART" (Spécifiques, Mesurables, Atteignables, Réalistes, Temporellement définis) pour {student_name}.
    Le plan d'action devrait inclure des conseils pour les points faibles, la tendance de progression et l'utilisation optimale du temps d'étude.
    Les objectifs SMART doivent être ambitieux mais réalisables sur une période de 2-3 semaines.
    Utilisez un format clair avec des tirets pour les étapes du plan et des phrases complètes pour les objectifs SMART.
    """
    return prompt


def recommend_learning_path(df: pd.DataFrame, student: str, metrics: Dict, patterns: Dict) -> List[str]:
    """Récupère les recommandations de l'API Gemini."""
    prompt = generate_recommendation_prompt(metrics, patterns, student)
    response_text = get_gemini_recommendations(prompt)
    # Simple parsing: assume each line is a recommendation
    recommendations = [rec.strip() for rec in response_text.split('\n') if rec.strip()]
    return recommendations

def create_chapter_heatmap(df: pd.DataFrame, student: str):
    """Crée une heatmap des performances par chapitre"""
    student_data = df[df['student_name'] == student]

    # Matrice chapitre x type d'activité
    heatmap_data = student_data.pivot_table(
        values='score',
        index='chapter',
        columns='activity_type',
        aggfunc='mean'
    )

    fig = px.imshow(
        heatmap_data,
        title=f"Performance par chapitre et type d'activité - {student}",
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )

    fig.update_layout(height=500)

    return fig

def main():
    """Interface principale de l'application"""

    # Titre principal
    st.title("🎓 Agent de Suivi des Progrès SQL")
    st.markdown("### Surveillance et Analyse des Performances d'Apprentissage")

    # Chargement des données
    df = load_sample_data()

    # Sidebar pour la sélection
    st.sidebar.header("🔧 Configuration")

    # Sélection de l'étudiant
    students = df['student_name'].unique()
    selected_student = st.sidebar.selectbox(
        "Sélectionner un apprenant:",
        students
    )

    # Filtre par période
    date_range = st.sidebar.date_input(
        "Période d'analyse:",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )

    # Filtrer les données selon la période
    if len(date_range) == 2:
        mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
        filtered_df = df[mask]
    else:
        filtered_df = df

    # Calcul des métriques
    metrics = calculate_progress_metrics(filtered_df, selected_student)
    patterns = identify_learning_patterns(filtered_df, selected_student)

    # Generate recommendations using Gemini API
    recommendations = recommend_learning_path(filtered_df, selected_student, metrics, patterns)

    # Generate action plan and SMART goals using Gemini API
    action_plan_and_smart_goals_prompt = generate_action_plan_prompt(metrics, patterns, selected_student)
    action_plan_and_smart_goals_response = get_gemini_recommendations(action_plan_and_smart_goals_prompt)

    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Vue d'ensemble",
        "📈 Analyses détaillées",
        "🎯 Recommandations",
        "📋 Données brutes"
    ])

    with tab1:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Score Moyen",
                f"{metrics['avg_score']:.1%}",
                delta=f"{patterns['trend_value']:.3f}" if patterns['trend_value'] != 0 else None
            )

        with col2:
            st.metric(
                "Activités Totales",
                metrics['total_activities']
            )

        with col3:
            st.metric(
                "Activités Récentes",
                metrics['recent_activities']
            )

        with col4:
            st.metric(
                "Tendance",
                patterns['trend'],
                delta_color="normal"
            )

        # Graphiques principaux
        # The 'Progression temporelle' chart and its associated column are completely removed
        # The remaining chart (Performance par Chapitre) will now take the full width of this section.
        student_data = filtered_df[filtered_df['student_name'] == selected_student]
        chapter_scores = student_data.groupby('chapter')['score'].mean().sort_values(ascending=True)

        fig_bar = px.bar(
            x=chapter_scores.values,
            y=chapter_scores.index,
            orientation='h',
            title="Performance par Chapitre",
            labels={'x': 'Score Moyen', 'y': 'Chapitre'},
            color=chapter_scores.values,
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig_bar, use_container_width=True)


    with tab2:
        # Analyses détaillées
        st.subheader("🔍 Analyse Approfondie")

        # Heatmap des performances
        heatmap = create_chapter_heatmap(filtered_df, selected_student)
        st.plotly_chart(heatmap, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💪 Points Forts")
            for strength in metrics['strengths']:
                st.success(f"✅ {strength}")

            st.subheader("📊 Performance par Type d'Activité")
            student_data = filtered_df[filtered_df['student_name'] == selected_student]
            activity_perf = student_data.groupby('activity_type')['score'].mean()

            fig_pie = px.pie(
                values=activity_perf.values,
                names=activity_perf.index,
                title="Répartition des Performances"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("⚠️ Points à Améliorer")
            for weakness in metrics['weaknesses']:
                st.warning(f"📚 {weakness}")

            st.subheader("⏱️ Temps d'Étude vs Performance")
            fig_scatter = px.scatter(
                student_data,
                x='time_spent',
                y='score',
                color='chapter',
                title="Relation Temps/Performance",
                labels={'time_spent': 'Temps (min)', 'score': 'Score'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        # Recommandations personnalisées
        st.subheader("🎯 Parcours d'Apprentissage Personnalisé")

        st.info(f"**Profil d'apprentissage:** {selected_student}")

        # Affichage des recommandations générées par Gemini
        st.markdown("#### ✨ Recommandations Personnalisées")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"- {rec}")

        # Plan d'action détaillé et objectifs SMART générés par Gemini
        st.subheader("📋 Plan d'Action Recommandé & Objectifs SMART")
        st.markdown(action_plan_and_smart_goals_response)


    with tab4:
        # Données brutes et export
        st.subheader("📋 Données Détaillées")

        # Filtres supplémentaires
        col1, col2 = st.columns(2)
        with col1:
            selected_chapters = st.multiselect(
                "Filtrer par chapitres:",
                options=filtered_df['chapter'].unique(),
                default=filtered_df['chapter'].unique()
            )

        with col2:
            selected_activity_types = st.multiselect(
                "Filtrer par types d'activité:",
                options=filtered_df['activity_type'].unique(),
                default=filtered_df['activity_type'].unique()
            )

        # Données filtrées
        display_data = filtered_df[
            (filtered_df['student_name'] == selected_student) &
            (filtered_df['chapter'].isin(selected_chapters)) &
            (filtered_df['activity_type'].isin(selected_activity_types))
        ].sort_values('date', ascending=False)

        # Affichage du tableau
        st.dataframe(
            display_data[['date', 'chapter', 'activity_type', 'score', 'time_spent', 'attempt']],
            use_container_width=True
        )

        # Statistiques résumées
        if len(display_data) > 0:
            st.subheader("📈 Statistiques Résumées")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Nombre d'activités", len(display_data))
                st.metric("Score minimum", f"{display_data['score'].min():.1%}")

            with col2:
                st.metric("Temps total (heures)", f"{display_data['time_spent'].sum()/60:.1f}")
                st.metric("Score maximum", f"{display_data['score'].max():.1%}")

            with col3:
                st.metric("Temps moyen/activité", f"{display_data['time_spent'].mean():.0f} min")
                st.metric("Écart-type", f"{display_data['score'].std():.3f}")

    # Footer avec informations
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        🤖 Agent de Suivi des Progrès SQL - Développé pour l'optimisation de l'apprentissage
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()