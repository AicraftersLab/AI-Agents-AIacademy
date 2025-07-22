import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import hashlib
import random
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import fitz  # PyMuPDF
import subprocess
import os
import requests

# Imports locaux
from config import CATEGORIES, DIFFICULTY_LEVELS, POINTS_CONFIG, USER_LEVELS, BADGES, COLORS, CHART_CONFIG, LIMITS, HELP_MESSAGES
from sample_data import initialize_sample_data

# Configuration de la page
st.set_page_config(
    page_title="Agent Social Learning Collaboratif",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enums et classes pour le profiling et la collaboration
class LearningStyle(Enum):
    VISUAL = "Visuel"
    AUDITIF = "Auditif"
    KINESTHESIQUE = "Kinesthésique"
    LECTURE_ECRITURE = "Lecture/Écriture"

class PersonalityType(Enum):
    LEADER = "Leader"
    COLLABORATEUR = "Collaborateur"
    ANALYTIQUE = "Analytique"
    CREATIF = "Créatif"

class CollaborationRole(Enum):
    CHEF_EQUIPE = "Chef d'équipe"
    RECHERCHEUR = "Rechercheur"
    DEVELOPPEUR = "Développeur"
    TESTEUR = "Testeur"
    COMMUNICATEUR = "Communicateur"

@dataclass
class LearnerProfile:
    username: str
    learning_style: LearningStyle
    personality_type: PersonalityType
    skill_levels: Dict[str, int] = field(default_factory=dict)
    collaboration_history: List[str] = field(default_factory=list)
    preferred_subjects: List[str] = field(default_factory=list)
    availability_hours: List[int] = field(default_factory=list)
    language_preference: str = "Français"
    motivation_level: int = 5
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class User:
    username: str
    email: str
    points: int = 0
    challenges_completed: List[str] = field(default_factory=list)
    challenges_created: List[str] = field(default_factory=list)
    level: str = "Débutant"
    badges: List[str] = field(default_factory=list)
    joined_at: datetime = field(default_factory=datetime.now)

@dataclass
class CollaborativeChallenge:
    id: str
    title: str
    description: str
    category: str
    difficulty: str
    required_skills: List[str]
    team_size: int
    roles_needed: List[CollaborationRole]
    points_reward: int
    creator: str
    deadline: datetime
    participants: List[str] = field(default_factory=list)
    teams: List[Dict] = field(default_factory=list)
    submissions: Dict = field(default_factory=dict)
    feedback_given: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    comments: List[Dict] = field(default_factory=list)

class SocialLearningAgent:
    def __init__(self):
        self.challenges = {}
        self.users = {}
        self.profiles = {}
        self.teams = {}
        self.load_data()
    
    def load_data(self):
        """Charger les données depuis la session"""
        if 'challenges' not in st.session_state:
            st.session_state.challenges = {}
        if 'users' not in st.session_state:
            st.session_state.users = {}
        if 'profiles' not in st.session_state:
            st.session_state.profiles = {}
        if 'teams' not in st.session_state:
            st.session_state.teams = {}
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
            
        self.challenges = st.session_state.challenges
        self.users = st.session_state.users
        self.profiles = st.session_state.profiles
        self.teams = st.session_state.teams
    
    def save_data(self):
        """Sauvegarder les données dans la session"""
        st.session_state.challenges = self.challenges
        st.session_state.users = self.users
        st.session_state.profiles = self.profiles
        st.session_state.teams = self.teams
    
    def analyze_learner_profile(self, username: str) -> LearnerProfile:
        """Analyser et créer le profil d'un apprenant"""
        if username in self.profiles:
            return self.profiles[username]
        
        # Simulation d'analyse basée sur l'historique (en réalité, ce serait plus sophistiqué)
        learning_styles = list(LearningStyle)
        personality_types = list(PersonalityType)
        
        profile = LearnerProfile(
            username=username,
            learning_style=random.choice(learning_styles),
            personality_type=random.choice(personality_types),
            skill_levels={cat: random.randint(1, 5) for cat in CATEGORIES},
            preferred_subjects=random.sample(CATEGORIES, k=random.randint(2, 4)),
            availability_hours=random.sample(range(8, 20), k=random.randint(4, 8)),
            motivation_level=random.randint(3, 5)
        )
        
        self.profiles[username] = profile
        self.save_data()
        return profile
    
    def create_personalized_challenge(self, participants: List[str]) -> CollaborativeChallenge:
        """Créer un défi collaboratif personnalisé basé sur les profils"""
        profiles = [self.analyze_learner_profile(user) for user in participants]
        
        # Analyse des compétences communes et complémentaires
        common_subjects = set(profiles[0].preferred_subjects)
        for profile in profiles[1:]:
            common_subjects = common_subjects.intersection(set(profile.preferred_subjects))
        
        if not common_subjects:
            common_subjects = {random.choice(CATEGORIES)}
        
        category = random.choice(list(common_subjects))
        avg_skill = np.mean([profile.skill_levels.get(category, 1) for profile in profiles])
        
        difficulty = "Facile" if avg_skill < 2 else "Moyen" if avg_skill < 4 else "Difficile"
        
        # Défis personnalisés selon la catégorie et le niveau
        challenge_templates = {
            "Programmation": [
                "Développer une application collaborative de gestion de tâches",
                "Créer un jeu multijoueur simple",
                "Construire une API REST avec documentation"
            ],
            "Design": [
                "Concevoir l'interface d'une application mobile",
                "Créer une identité visuelle complète",
                "Développer un prototype d'UX innovant"
            ],
            "Data Science": [
                "Analyser un dataset et présenter les insights",
                "Créer un modèle prédictif collaboratif",
                "Développer un dashboard interactif"
            ]
        }
        
        title = random.choice(challenge_templates.get(category, ["Défi collaboratif personnalisé"]))
        
        challenge_id = hashlib.md5(f"{title}{datetime.now()}".encode()).hexdigest()[:8]
        
        challenge = CollaborativeChallenge(
            id=challenge_id,
            title=title,
            description=f"Défi collaboratif en {category} adapté à votre niveau ({difficulty})",
            category=category,
            difficulty=difficulty,
            required_skills=[category],
            team_size=len(participants),
            roles_needed=self._determine_roles_needed(profiles),
            points_reward=len(participants) * 20,  # Points base pour défis collaboratifs
            creator="SocialLearningAgent",
            deadline=datetime.now() + timedelta(days=7),
            participants=participants
        )
        
        self.challenges[challenge_id] = challenge
        self.save_data()
        return challenge
    
    def _determine_roles_needed(self, profiles: List[LearnerProfile]) -> List[CollaborationRole]:
        """Déterminer les rôles nécessaires basés sur les profils"""
        roles = []
        personality_types = [profile.personality_type for profile in profiles]
        
        if PersonalityType.LEADER in personality_types:
            roles.append(CollaborationRole.CHEF_EQUIPE)
        if PersonalityType.ANALYTIQUE in personality_types:
            roles.append(CollaborationRole.RECHERCHEUR)
        if PersonalityType.CREATIF in personality_types:
            roles.append(CollaborationRole.DEVELOPPEUR)
        
        # Compléter avec des rôles par défaut
        while len(roles) < len(profiles):
            available_roles = [r for r in CollaborationRole if r not in roles]
            if available_roles:
                roles.append(random.choice(available_roles))
            else:
                break
                
        return roles[:len(profiles)]
    
    def form_optimal_pairs(self, available_users: List[str]) -> List[Tuple[str, str]]:
        """Former des binômes optimaux basés sur la compatibilité"""
        if len(available_users) < 2:
            return []
        
        profiles = [self.analyze_learner_profile(user) for user in available_users]
        pairs = []
        used_users = set()
        
        # Algorithme simple de formation de pairs basé sur la complémentarité
        for i, user1 in enumerate(available_users):
            if user1 in used_users:
                continue
                
            best_match = None
            best_score = -1
            
            for j, user2 in enumerate(available_users[i+1:], i+1):
                if user2 in used_users:
                    continue
                
                compatibility_score = self._calculate_compatibility(profiles[i], profiles[j])
                if compatibility_score > best_score:
                    best_score = compatibility_score
                    best_match = user2
            
            if best_match:
                pairs.append((user1, best_match))
                used_users.add(user1)
                used_users.add(best_match)
        
        return pairs
    
    def _calculate_compatibility(self, profile1: LearnerProfile, profile2: LearnerProfile) -> float:
        """Calculer la compatibilité entre deux profils"""
        score = 0.0
        
        # Complémentarité des types de personnalité
        if profile1.personality_type != profile2.personality_type:
            score += 2.0
        
        # Sujets en commun
        common_subjects = set(profile1.preferred_subjects).intersection(set(profile2.preferred_subjects))
        score += len(common_subjects) * 1.5
        
        # Créneaux horaires compatibles
        common_hours = set(profile1.availability_hours).intersection(set(profile2.availability_hours))
        score += len(common_hours) * 0.5
        
        # Niveaux de compétence complémentaires
        for subject in common_subjects:
            skill_diff = abs(profile1.skill_levels.get(subject, 1) - profile2.skill_levels.get(subject, 1))
            if skill_diff == 1:  # Légère différence = bon pour l'entraide
                score += 1.0
        
        return score
    
    def assign_roles_to_team(self, challenge_id: str, team_members: List[str]) -> Dict[str, CollaborationRole]:
        """Attribuer des rôles aux membres d'une équipe"""
        if challenge_id not in self.challenges:
            return {}
        
        challenge = self.challenges[challenge_id]
        profiles = [self.analyze_learner_profile(user) for user in team_members]
        role_assignments = {}
        
        # Attribution basée sur les types de personnalité et compétences
        available_roles = challenge.roles_needed.copy()
        
        for i, member in enumerate(team_members):
            profile = profiles[i]
            best_role = None
            
            if profile.personality_type == PersonalityType.LEADER and CollaborationRole.CHEF_EQUIPE in available_roles:
                best_role = CollaborationRole.CHEF_EQUIPE
            elif profile.personality_type == PersonalityType.ANALYTIQUE and CollaborationRole.RECHERCHEUR in available_roles:
                best_role = CollaborationRole.RECHERCHEUR
            elif profile.personality_type == PersonalityType.CREATIF and CollaborationRole.DEVELOPPEUR in available_roles:
                best_role = CollaborationRole.DEVELOPPEUR
            
            if best_role and best_role in available_roles:
                role_assignments[member] = best_role
                available_roles.remove(best_role)
            elif available_roles:
                role_assignments[member] = available_roles.pop(0)
        
        # Sauvegarder les attributions dans le défi
        if challenge_id not in self.teams:
            self.teams[challenge_id] = {}
        
        team_id = f"team_{len(self.teams[challenge_id])}"
        self.teams[challenge_id][team_id] = {
            'members': team_members,
            'roles': role_assignments,
            'created_at': datetime.now()
        }
        
        self.save_data()
        return role_assignments
    
    def collect_results_and_feedback(self, challenge_id: str, team_id: str, 
                                   results: Dict, peer_feedback: Dict) -> Dict:
        """Recueillir les résultats et donner un feedback"""
        if challenge_id not in self.challenges:
            return {}
        
        challenge = self.challenges[challenge_id]
        
        # Analyser la performance de l'équipe
        team_feedback = {
            'collaboration_score': self._evaluate_collaboration(peer_feedback),
            'technical_score': self._evaluate_technical_results(results),
            'individual_feedback': {},
            'team_feedback': "",
            'recommendations': []
        }
        
        # Feedback individuel basé sur les rôles et contributions
        if challenge_id in self.teams and team_id in self.teams[challenge_id]:
            team_info = self.teams[challenge_id][team_id]
            
            for member in team_info['members']:
                individual_feedback = self._generate_individual_feedback(
                    member, team_info['roles'].get(member), results, peer_feedback
                )
                team_feedback['individual_feedback'][member] = individual_feedback
        
        # Feedback général de l'équipe
        team_feedback['team_feedback'] = self._generate_team_feedback(results, peer_feedback)
        
        # Recommandations pour l'amélioration
        team_feedback['recommendations'] = self._generate_recommendations(challenge_id, results, peer_feedback)
        
        # Sauvegarder le feedback
        challenge.feedback_given[team_id] = team_feedback
        self.save_data()
        
        return team_feedback
    
    def _evaluate_collaboration(self, peer_feedback: Dict) -> float:
        """Évaluer la qualité de la collaboration"""
        if not peer_feedback:
            return 3.0
        
        scores = []
        for feedback in peer_feedback.values():
            if isinstance(feedback, dict) and 'collaboration_rating' in feedback:
                scores.append(feedback['collaboration_rating'])
        
        return np.mean(scores) if scores else 3.0
    
    def _evaluate_technical_results(self, results: Dict) -> float:
        """Évaluer la qualité technique des résultats"""
        # Simulation d'évaluation technique
        criteria = ['completeness', 'quality', 'innovation', 'presentation']
        total_score = 0
        
        for criterion in criteria:
            score = results.get(criterion, 3.0)
            total_score += score
        
        return total_score / len(criteria)
    
    def _generate_individual_feedback(self, member: str, role: CollaborationRole, 
                                    results: Dict, peer_feedback: Dict) -> str:
        """Générer un feedback individuel personnalisé"""
        profile = self.profiles.get(member)
        if not profile:
            return "Feedback non disponible"
        
        feedback_parts = []
        
        # Feedback basé sur le rôle
        role_feedback = {
            CollaborationRole.CHEF_EQUIPE: "Excellent leadership et coordination de l'équipe.",
            CollaborationRole.RECHERCHEUR: "Recherche approfondie et analyse pertinente.",
            CollaborationRole.DEVELOPPEUR: "Implémentation créative et technique solide.",
            CollaborationRole.TESTEUR: "Tests rigoureux et attention aux détails.",
            CollaborationRole.COMMUNICATEUR: "Communication claire et présentation efficace."
        }
        
        if role:
            feedback_parts.append(role_feedback.get(role, "Bonne contribution dans votre rôle."))
        
        # Feedback basé sur le style d'apprentissage
        if profile.learning_style == LearningStyle.VISUAL:
            feedback_parts.append("Vos représentations visuelles ont enrichi le projet.")
        elif profile.learning_style == LearningStyle.AUDITIF:
            feedback_parts.append("Votre participation aux discussions a été précieuse.")
        
        return " ".join(feedback_parts)
    
    def _generate_team_feedback(self, results: Dict, peer_feedback: Dict) -> str:
        """Générer un feedback d'équipe"""
        collaboration_score = self._evaluate_collaboration(peer_feedback)
        technical_score = self._evaluate_technical_results(results)
        
        if collaboration_score >= 4 and technical_score >= 4:
            return "Excellente collaboration et résultats techniques remarquables ! L'équipe a démontré une synergie parfaite."
        elif collaboration_score >= 3 and technical_score >= 3:
            return "Bonne collaboration avec des résultats satisfaisants. Quelques améliorations possibles identifiées."
        else:
            return "La collaboration peut être améliorée. Concentrez-vous sur la communication et la coordination."
    
    def _generate_recommendations(self, challenge_id: str, results: Dict, peer_feedback: Dict) -> List[str]:
        """Générer des recommandations d'amélioration"""
        recommendations = []
        
        collaboration_score = self._evaluate_collaboration(peer_feedback)
        technical_score = self._evaluate_technical_results(results)
        
        if collaboration_score < 3:
            recommendations.append("Améliorer la communication entre les membres de l'équipe")
            recommendations.append("Organiser des réunions régulières pour suivre les progrès")
        
        if technical_score < 3:
            recommendations.append("Approfondir la recherche avant l'implémentation")
            recommendations.append("Demander de l'aide aux mentors pour les aspects techniques")
        
        recommendations.append("Continuer à travailler en équipe pour développer vos compétences collaboratives")
        
        return recommendations
    
    def create_user(self, username: str, email: str) -> bool:
        """Créer un nouvel utilisateur"""
        if username not in self.users:
            self.users[username] = User(username, email)
            self.save_data()
            return True
        return False
    
    def create_challenge(self, title: str, description: str, category: str, 
                        difficulty: str, points: int, creator: str, deadline: datetime = None):
        """Créer un nouveau défi standard"""
        challenge_id = hashlib.md5(f"{title}{creator}{datetime.now()}".encode()).hexdigest()[:8]
        challenge = CollaborativeChallenge(
            id=challenge_id,
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            required_skills=[category],
            team_size=2,  # Par défaut binôme
            roles_needed=[CollaborationRole.CHEF_EQUIPE, CollaborationRole.DEVELOPPEUR],
            points_reward=points,
            creator=creator,
            deadline=deadline if deadline else datetime.now() + timedelta(days=7)
        )
        self.challenges[challenge_id] = challenge
        self.save_data()
        return challenge_id
    
    def join_challenge(self, challenge_id: str, username: str) -> bool:
        """Rejoindre un défi"""
        if challenge_id in self.challenges and username not in self.challenges[challenge_id].participants:
            self.challenges[challenge_id].participants.append(username)
            self.save_data()
            return True
        return False
    
    def submit_solution(self, challenge_id: str, username: str, solution: str) -> bool:
        """Soumettre une solution"""
        if challenge_id in self.challenges:
            self.challenges[challenge_id].submissions[username] = {
                'solution': solution,
                'submitted_at': datetime.now()
            }
            self.save_data()
            return True
        return False
    
    def add_comment(self, challenge_id: str, username: str, comment: str) -> bool:
        """Ajouter un commentaire"""
        if challenge_id in self.challenges:
            self.challenges[challenge_id].comments.append({
                'username': username,
                'comment': comment,
                'timestamp': datetime.now()
            })
            self.save_data()
            return True
        return False
    
    def get_leaderboard(self) -> pd.DataFrame:
        """Obtenir le classement"""
        users_data = []
        for username, user in self.users.items():
            users_data.append({
                'Utilisateur': username,
                'Points': user.points,
                'Défis Complétés': len(user.challenges_completed),
                'Niveau': user.level,
                'Badges': len(user.badges)
            })
        df = pd.DataFrame(users_data)
        if not df.empty:
            return df.sort_values('Points', ascending=False)
        return df

# Initialiser l'agent
@st.cache_resource
def get_agent():
    return SocialLearningAgent()

agent = get_agent()

# Fonction d'initialisation du session state
def initialize_session_state():
    """Initialiser toutes les variables de session state"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'challenges' not in st.session_state:
        st.session_state.challenges = {}
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'profiles' not in st.session_state:
        st.session_state.profiles = {}
    if 'teams' not in st.session_state:
        st.session_state.teams = {}

# Interface utilisateur
def main():
    # Initialiser le session state en premier
    initialize_session_state()
    
    st.title("🎓 Agent Social Learning - Défis Collaboratifs")
    
    # Sidebar pour la navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150/4CAF50/white?text=SL", width=150)
        st.title("Navigation")
        
        # Authentification simple
        if st.session_state.current_user is None:
            st.subheader("🔐 Connexion")
            username = st.text_input("Nom d'utilisateur")
            email = st.text_input("Email")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Se connecter"):
                    if username and email:
                        if username not in agent.users:
                            agent.create_user(username, email)
                        st.session_state.current_user = username
                        st.rerun()
            
            with col2:
                if st.button("Créer compte"):
                    if username and email:
                        if agent.create_user(username, email):
                            st.session_state.current_user = username
                            st.success("Compte créé!")
                            st.rerun()
                        else:
                            st.error("Utilisateur existe déjà")
        else:
            st.success(f"Connecté: {st.session_state.current_user}")
            if st.button("Déconnexion"):
                st.session_state.current_user = None
                st.rerun()
            
            st.divider()
            
            # Bouton pour charger les données d'exemple
            if st.button("📊 Charger Données d'Exemple"):
                num_users, num_challenges = initialize_sample_data(agent)
                st.success(f"Données chargées: {num_users} utilisateurs, {num_challenges} défis")
                st.rerun()
            
            # Menu principal
            menu = st.selectbox(
                "🎯 Menu Principal",
                ["Dashboard", "Défis Disponibles", "Mes Défis", "Créer un Défi", 
                 "Classement", "Profil", "Communauté"]
            )
    
    # Contenu principal
    if st.session_state.current_user is None:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        show_welcome_page()
    else:
        if menu == "Dashboard":
            show_dashboard()
        elif menu == "Défis Disponibles":
            show_available_challenges()
        elif menu == "Mes Défis":
            show_my_challenges()
        elif menu == "Créer un Défi":
            show_create_challenge()
        elif menu == "Classement":
            show_leaderboard()
        elif menu == "Profil":
            show_profile()
        elif menu == "Communauté":
            show_community()

def show_welcome_page():
    """Page d'accueil"""
    st.markdown("""
    ## 🌟 Bienvenue dans l'Agent Social Learning
    
    ### Qu'est-ce que le Social Learning ?
    Le Social Learning est une approche pédagogique qui favorise l'apprentissage par l'interaction sociale,
    la collaboration et le partage d'expériences entre apprenants.
    
    ### 🎯 Fonctionnalités principales:
    - **Défis Collaboratifs**: Participez à des défis créés par la communauté
    - **Système de Points**: Gagnez des points en complétant des défis
    - **Classements**: Comparez vos performances avec d'autres apprenants
    - **Badges et Niveaux**: Débloquez des récompenses selon vos progrès
    - **Communauté**: Échangez et collaborez avec d'autres apprenants
    
    ### 🚀 Pour commencer:
    1. Créez votre compte ou connectez-vous
    2. Explorez les défis disponibles
    3. Rejoignez un défi qui vous intéresse
    4. Collaborez et apprenez avec la communauté!
    """)

def show_dashboard():
    """Dashboard principal"""
    current_user = st.session_state.current_user
    user = agent.users.get(current_user)
    
    st.header(f"📊 Dashboard - {current_user}")
    
    # Statistiques personnelles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Points Total", user.points if user else 0)
    
    with col2:
        st.metric("Défis Complétés", len(user.challenges_completed) if user else 0)
    
    with col3:
        st.metric("Niveau", user.level if user else "Débutant")
    
    with col4:
        st.metric("Badges", len(user.badges) if user else 0)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Évolution des Points")
        # Simuler des données d'évolution
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        points = [i * 10 + (i % 7) * 5 for i in range(30)]
        df_evolution = pd.DataFrame({'Date': dates, 'Points': points})
        
        fig = px.line(df_evolution, x='Date', y='Points', title="Évolution des points")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Défis par Catégorie")
        categories = ['Programmation', 'Mathématiques', 'Science', 'Langues', 'Art']
        values = [8, 5, 3, 4, 2]
        
        fig = px.pie(values=values, names=categories, title="Participation par catégorie")
        st.plotly_chart(fig, use_container_width=True)
    
    # Défis récents
    st.subheader("🔥 Défis Récents")
    if agent.challenges:
        recent_challenges = list(agent.challenges.values())[-3:]
        for challenge in recent_challenges:
            with st.expander(f"{challenge.title} - {challenge.category}"):
                st.write(challenge.description)
                st.caption(f"Créé par: {challenge.creator} | Points: {challenge.points}")
    else:
        st.info("Aucun défi disponible. Créez le premier!")

def show_available_challenges():
    """Afficher les défis disponibles"""
    st.header("🎯 Défis Disponibles")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox("Catégorie", ["Tous"] + CATEGORIES)
    with col2:
        difficulty_filter = st.selectbox("Difficulté", ["Tous"] + DIFFICULTY_LEVELS)
    with col3:
        sort_by = st.selectbox("Trier par", ["Date", "Points", "Participants"])
    
    # Afficher les défis
    if agent.challenges:
        for challenge_id, challenge in agent.challenges.items():
            # Appliquer les filtres
            if category_filter != "Tous" and challenge.category != category_filter:
                continue
            if difficulty_filter != "Tous" and challenge.difficulty != difficulty_filter:
                continue
            
            with st.expander(f"{challenge.title} - {challenge.points} points"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {challenge.description}")
                    st.write(f"**Catégorie:** {challenge.category}")
                    st.write(f"**Difficulté:** {challenge.difficulty}")
                    st.write(f"**Créé par:** {challenge.creator}")
                    st.write(f"**Participants:** {len(challenge.participants)}")
                    
                    if challenge.deadline:
                        st.write(f"**Date limite:** {challenge.deadline.strftime('%d/%m/%Y')}")
                
                with col2:
                    current_user = st.session_state.current_user
                    
                    if current_user not in challenge.participants:
                        if st.button(f"Rejoindre", key=f"join_{challenge_id}"):
                            agent.join_challenge(challenge_id, current_user)
                            st.success("Défi rejoint!")
                            st.rerun()
                    else:
                        st.success("✅ Déjà inscrit")
                        
                        # Soumission de solution
                        st.subheader("📝 Soumettre une solution")
                        solution = st.text_area("Votre solution", key=f"solution_{challenge_id}")
                        if st.button("Soumettre", key=f"submit_{challenge_id}"):
                            agent.submit_solution(challenge_id, current_user, solution)
                            st.success("Solution soumise!")
                
                # Section commentaires
                st.subheader("💬 Commentaires")
                for comment in challenge.comments:
                    st.write(f"**{comment['username']}:** {comment['comment']}")
                    st.caption(comment['timestamp'].strftime('%d/%m/%Y %H:%M'))
                
                # Ajouter un commentaire
                new_comment = st.text_input("Ajouter un commentaire", key=f"comment_{challenge_id}")
                if st.button("Publier", key=f"post_{challenge_id}") and new_comment:
                    agent.add_comment(challenge_id, current_user, new_comment)
                    st.rerun()
    else:
        st.info("Aucun défi disponible. Créez le premier!")

def show_my_challenges():
    """Afficher mes défis"""
    st.header("📚 Mes Défis")
    current_user = st.session_state.current_user
    
    # Défis rejoints
    st.subheader("🎯 Défis Rejoints")
    my_challenges = [c for c in agent.challenges.values() if current_user in c.participants]
    
    if my_challenges:
        for challenge in my_challenges:
            with st.expander(f"{challenge.title} - {challenge.points} points"):
                st.write(challenge.description)
                
                # Statut de soumission
                if current_user in challenge.submissions:
                    st.success("✅ Solution soumise")
                    st.write("**Votre solution:**")
                    st.code(challenge.submissions[current_user]['solution'])
                else:
                    st.warning("⏳ En attente de soumission")
    else:
        st.info("Vous n'avez rejoint aucun défi.")
    
    # Défis créés
    st.subheader("🎨 Défis Créés par Moi")
    created_challenges = [c for c in agent.challenges.values() if c.creator == current_user]
    
    if created_challenges:
        for challenge in created_challenges:
            with st.expander(f"{challenge.title} - {len(challenge.participants)} participants"):
                st.write(challenge.description)
                st.write(f"**Participants:** {', '.join(challenge.participants)}")
                
                # Afficher les soumissions
                if challenge.submissions:
                    st.subheader("📝 Soumissions")
                    for user, submission in challenge.submissions.items():
                        st.write(f"**{user}:**")
                        st.code(submission['solution'])
    else:
        st.info("Vous n'avez créé aucun défi.")

def show_create_challenge():
    """Créer un nouveau défi"""
    st.header("🎨 Créer un Nouveau Défi")
    
    with st.form("create_challenge"):
        title = st.text_input("Titre du défi*")
        description = st.text_area("Description détaillée*")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Catégorie*", CATEGORIES)
            difficulty = st.selectbox("Difficulté*", DIFFICULTY_LEVELS)
        
        with col2:
            points = st.number_input("Points à attribuer*", min_value=1, max_value=100, value=10)
            deadline = st.date_input("Date limite (optionnelle)", value=None)
        
        submitted = st.form_submit_button("Créer le Défi")
        
        if submitted:
            if title and description:
                challenge_id = agent.create_challenge(
                    title, description, category, difficulty, points, 
                    st.session_state.current_user, 
                    datetime.combine(deadline, datetime.min.time()) if deadline else None
                )
                st.success(f"Défi créé avec succès! ID: {challenge_id}")
                st.balloons()
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*)")

def show_leaderboard():
    """Afficher le classement"""
    st.header("🏆 Classement Général")
    
    if agent.users:
        df_leaderboard = agent.get_leaderboard()
        
        # Top 3
        st.subheader("🥇 Podium")
        if len(df_leaderboard) >= 1:
            col1, col2, col3 = st.columns(3)
            
            if len(df_leaderboard) >= 2:
                with col1:
                    st.metric("🥈 2ème place", 
                            df_leaderboard.iloc[1]['Utilisateur'], 
                            f"{df_leaderboard.iloc[1]['Points']} pts")
            
            if len(df_leaderboard) >= 1:
                with col2:
                    st.metric("🥇 1ère place", 
                            df_leaderboard.iloc[0]['Utilisateur'], 
                            f"{df_leaderboard.iloc[0]['Points']} pts")
            
            if len(df_leaderboard) >= 3:
                with col3:
                    st.metric("🥉 3ème place", 
                            df_leaderboard.iloc[2]['Utilisateur'], 
                            f"{df_leaderboard.iloc[2]['Points']} pts")
        
        # Tableau complet
        st.subheader("📊 Classement Complet")
        st.dataframe(df_leaderboard, use_container_width=True)
        
        # Graphique
        fig = px.bar(df_leaderboard.head(10), x='Utilisateur', y='Points',
                    title="Top 10 des utilisateurs")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun utilisateur inscrit pour le moment.")

def show_profile():
    """Afficher le profil utilisateur"""
    st.header("👤 Mon Profil")
    current_user = st.session_state.current_user
    user = agent.users.get(current_user)
    
    if user:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://via.placeholder.com/150x150/2196F3/white?text=USER", width=150)
            st.write(f"**Nom:** {user.username}")
            st.write(f"**Email:** {user.email}")
            st.write(f"**Membre depuis:** {user.joined_at.strftime('%d/%m/%Y')}")
        
        with col2:
            st.subheader("📊 Statistiques")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Points", user.points)
            with col2:
                st.metric("Défis Complétés", len(user.challenges_completed))
            with col3:
                st.metric("Niveau", user.level)
            
            st.subheader("🏅 Badges")
            if user.badges:
                for badge in user.badges:
                    st.write(f"🏆 {badge}")
            else:
                st.info("Aucun badge obtenu pour le moment.")

def show_community():
    """Afficher la communauté"""
    st.header("🌍 Communauté")
    
    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Utilisateurs", len(agent.users))
    with col2:
        st.metric("Défis Actifs", len(agent.challenges))
    with col3:
        total_participants = sum(len(c.participants) for c in agent.challenges.values())
        st.metric("Participations", total_participants)
    with col4:
        total_comments = sum(len(c.comments) for c in agent.challenges.values())
        st.metric("Commentaires", total_comments)
    
    # Activité récente
    st.subheader("📈 Activité Récente")
    
    # Simuler une activité récente
    activities = [
        "🆕 Alice a créé un nouveau défi 'Algorithme de tri'",
        "🎯 Bob a rejoint le défi 'Programmation Python'",
        "💬 Charlie a commenté sur 'Mathématiques avancées'",
        "✅ Diana a soumis une solution pour 'Art numérique'",
        "🏆 Eve a gagné le badge 'Premier pas'"
    ]
    
    for activity in activities:
        st.write(activity)
        st.caption("Il y a quelques minutes")
    
    # Forum de discussion
    st.subheader("💬 Forum de Discussion")
    st.info("Fonctionnalité en développement - Forum pour échanger avec la communauté")

if __name__ == "__main__":
    main() 
