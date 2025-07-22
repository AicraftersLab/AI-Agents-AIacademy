import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2
from io import StringIO
import json
import random
from datetime import datetime

# Configuration
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
MODEL_CONFIG = {
    'temperature': 0.3,
    'top_p': 0.8,
    'top_k': 40,
    'max_output_tokens': 1500,
}

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

class CourseProcessor:
    """Classe pour traiter différents types de fichiers de cours"""
    
    def __init__(self):
        self.content = ""
        self.sections = []
        self.course_title = ""
    
    def load_txt_file(self, uploaded_file):
        """Charge un fichier TXT"""
        try:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            content = stringio.read()
            return content
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier TXT: {str(e)}")
            return ""
    
    def load_pdf_file(self, uploaded_file):
        """Charge un fichier PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
            return content
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier PDF: {str(e)}")
            return ""
    
    def process_content(self, content):
        """Traite le contenu du cours"""
        self.content = content
        self.sections = [section.strip() for section in content.split('\n\n') if section.strip()]
        
        # Extrait le titre du cours
        lines = content.split('\n')
        if lines:
            self.course_title = lines[0][:100] + "..." if len(lines[0]) > 100 else lines[0]
        
        return len(self.sections) > 0
    
    def get_relevant_content(self, query, max_sections=3):
        """Trouve le contenu pertinent basé sur la requête"""
        if not self.sections:
            return [self.content[:2000]]
        
        query_words = query.lower().split()
        relevant_sections = []
        
        # Recherche par mots-clés
        for section in self.sections:
            section_lower = section.lower()
            score = sum(1 for word in query_words if word in section_lower)
            if score > 0:
                relevant_sections.append((section, score))
        
        # Trie par pertinence
        relevant_sections.sort(key=lambda x: x[1], reverse=True)
        
        # Retourne les sections les plus pertinentes
        result = [section[0] for section in relevant_sections[:max_sections]]
        
        # Si aucune section pertinente, retourne les premières sections
        if not result:
            result = self.sections[:max_sections]
        
        return result

class SummaryGenerator:
    """Générateur de résumés adaptatifs selon le niveau de l'étudiant"""
    
    def __init__(self, model):
        self.model = model
        self.summary_styles = {
            'debutant': {
                'style': 'simple et accessible',
                'focus': 'concepts de base, définitions claires, exemples concrets',
                'length': 'court (300-500 mots)',
                'tone': 'encourageant et bienveillant',
                'structure': 'points essentiels numérotés'
            },
            'intermediaire': {
                'style': 'structuré et analytique',
                'focus': 'relations entre concepts, applications pratiques, analyses',
                'length': 'modéré (500-800 mots)',
                'tone': 'informatif et engageant',
                'structure': 'sections thématiques avec sous-points'
            },
            'avance': {
                'style': 'critique et synthétique',
                'focus': 'enjeux complexes, perspectives multiples, implications',
                'length': 'détaillé (800-1200 mots)',
                'tone': 'académique et nuancé',
                'structure': 'analyse approfondie avec perspectives critiques'
            }
        }
    
    def generate_summary(self, course_content, level, topic=None, summary_type='general'):
        if not self.model:
            return None
        
        try:
            # Prépare le contenu à résumer
            if topic:
                # Filtre par sujet si spécifié
                relevant_sections = []
                for section in course_content.sections:
                    if topic.lower() in section.lower():
                        relevant_sections.append(section)
                content_text = '\n\n'.join(relevant_sections[:5])
            else:
                # Utilise tout le contenu disponible
                content_text = course_content.content
            
            # Limite la taille du contenu pour éviter les erreurs
            if len(content_text) > 4000:
                content_text = content_text[:4000] + "..."
            
            # Crée le prompt pour générer le résumé
            prompt = self._create_summary_prompt(content_text, level, topic, summary_type)
            
            # Génère le résumé
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**MODEL_CONFIG),
                safety_settings=SAFETY_SETTINGS
            )
            
            return {
                'content': response.text,
                'level': level,
                'topic': topic,
                'type': summary_type,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            st.error(f"Erreur lors de la génération du résumé : {str(e)}")
            return None
    
    def _create_summary_prompt(self, content, level, topic=None, summary_type='general'):
        """Crée le prompt pour générer un résumé adapté"""
        style_config = self.summary_styles[level]
        
        topic_instruction = f" sur le sujet '{topic}'" if topic else ""
        
        prompt = f"""
Tu es un expert en pédagie adaptative. Crée un résumé{topic_instruction} basé EXCLUSIVEMENT sur le contenu du cours fourni, adapté au niveau {level.upper()}.

CONTENU DU COURS :
{content}

NIVEAU CIBLE : {level.upper()}
STYLE REQUIS : {style_config['style']}
FOCUS : {style_config['focus']}
LONGUEUR : {style_config['length']}
TONE : {style_config['tone']}
STRUCTURE : {style_config['structure']}

INSTRUCTIONS SPÉCIFIQUES POUR LE NIVEAU {level.upper()} :
"""

        if level == 'debutant':
            prompt += """
- Utilise un vocabulaire simple et accessible
- Explique les termes techniques avec des définitions claires
- Donne des exemples concrets et familiers
- Structure avec des puces ou numérotation
- Évite les concepts trop abstraits
- Sois encourageant et rassurant
- Mets l'accent sur la compréhension de base
"""
        
        elif level == 'intermediaire':
            prompt += """
- Utilise un vocabulaire précis mais accessible
- Établis des liens entre les différents concepts
- Inclus des applications pratiques
- Structure en sections thématiques
- Propose des analyses modérées
- Équilibre théorie et pratique
- Encourage l'approfondissement
"""
        
        else:  # avancé
            prompt += """
- Utilise un vocabulaire académique approprié
- Présente les enjeux complexes et les débats
- Analyse les implications et conséquences
- Structure avec une logique argumentative
- Inclus des perspectives critiques multiples
- Établis des connexions interdisciplinaires
- Stimule la réflexion critique
"""

        prompt += f"""

FORMAT DE RÉPONSE :
# 📚 Résumé du Cours - Niveau {level.title()}

[Ton résumé ici, respectant exactement les critères ci-dessus]

## 🎯 Points Clés à Retenir
[Liste des points essentiels]

## 💡 Pour Aller Plus Loin
[Suggestions adaptées au niveau]

Assure-toi que le résumé soit parfaitement adapté au niveau {level} et respecte le style et la longueur demandés.
"""
        
        return prompt

class ExerciseGenerator:
    """Générateur d'exercices adaptatifs basé sur le cours"""
    
    def __init__(self, model):
        self.model = model
        self.exercise_types = {
            'debutant': ['QCM', 'Vrai/Faux', 'Completion'],
            'intermediaire': ['QCM', 'Questions courtes', 'Analyse', 'Application'],
            'avance': ['Analyse critique', 'Synthèse', 'Problème complexe', 'Étude de cas']
        }
    
    def generate_exercises(self, course_content, level, num_exercises=3, topic=None):
        """Génère des exercices basés sur le cours et le niveau"""
        if not self.model:
            return []
        
        try:
            # Sélectionne le contenu pertinent
            if topic:
                # Filtre par sujet si spécifié
                relevant_sections = []
                for section in course_content.sections:
                    if topic.lower() in section.lower():
                        relevant_sections.append(section)
                content_text = '\n\n'.join(relevant_sections[:2])
            else:
                # Utilise tout le contenu disponible
                content_text = '\n\n'.join(course_content.sections[:3])
            
            if len(content_text) > 2500:
                content_text = content_text[:2500] + "..."
            
            # Définit les types d'exercices selon le niveau
            exercise_types = self.exercise_types[level]
            
            # Crée le prompt pour générer les exercices
            prompt = self._create_exercise_prompt(content_text, level, num_exercises, exercise_types)
            
            # Génère les exercices
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**MODEL_CONFIG),
                safety_settings=SAFETY_SETTINGS
            )
            
            # Parse la réponse
            exercises = self._parse_exercise_response(response.text, level)
            return exercises
            
        except Exception as e:
            st.error(f"Erreur lors de la génération des exercices : {str(e)}")
            return []
    
    def _create_exercise_prompt(self, content, level, num_exercises, exercise_types):
        """Crée le prompt pour générer des exercices"""
        level_descriptions = {
            'debutant': 'questions simples de compréhension et de mémorisation',
            'intermediaire': 'questions d\'application et d\'analyse modérée',
            'avance': 'questions complexes d\'analyse critique et de synthèse'
        }
        
        prompt = f"""
Tu es un expert en pédagogie. Crée {num_exercises} exercices de niveau {level} basés EXCLUSIVEMENT sur le contenu du cours fourni.

CONTENU DU COURS :
{content}

NIVEAU : {level.upper()}
DESCRIPTION : {level_descriptions[level]}
TYPES D'EXERCICES AUTORISÉS : {', '.join(exercise_types)}

INSTRUCTIONS :
1. Base-toi UNIQUEMENT sur le contenu du cours fourni
2. Adapte la difficulté au niveau {level}
3. Varie les types d'exercices
4. Pour chaque exercice, fournis :
   - Type d'exercice
   - Question/Énoncé
   - Options de réponse (si applicable)
   - Réponse correcte
   - Explication détaillée

FORMAT DE RÉPONSE (respecte exactement ce format) :
EXERCICE 1:
Type: [Type d'exercice]
Question: [Question complète]
Options: [Si QCM: A) option1, B) option2, C) option3, D) option4]
Réponse: [Réponse correcte]
Explication: [Explication détaillée]

EXERCICE 2:
[Même format...]

Assure-toi que les exercices testent la compréhension du cours et sont adaptés au niveau {level}.
"""
        return prompt
    
    def _parse_exercise_response(self, response_text, level):
        """Parse la réponse de l'IA pour extraire les exercices"""
        exercises = []
        
        try:
            # Divise par exercices
            exercise_blocks = response_text.split('EXERCICE ')[1:]  # Retire la partie avant le premier exercice
            
            for i, block in enumerate(exercise_blocks):
                exercise = {
                    'id': i + 1,
                    'level': level,
                    'type': '',
                    'question': '',
                    'options': [],
                    'correct_answer': '',
                    'explanation': '',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Parse chaque champ
                lines = block.strip().split('\n')
                current_field = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('Type:'):
                        exercise['type'] = line.replace('Type:', '').strip()
                    elif line.startswith('Question:'):
                        exercise['question'] = line.replace('Question:', '').strip()
                        current_field = 'question'
                    elif line.startswith('Options:'):
                        options_text = line.replace('Options:', '').strip()
                        if options_text:
                            # Parse les options (format: A) option1, B) option2, etc.)
                            exercise['options'] = self._parse_options(options_text)
                        current_field = 'options'
                    elif line.startswith('Réponse:'):
                        exercise['correct_answer'] = line.replace('Réponse:', '').strip()
                        current_field = 'answer'
                    elif line.startswith('Explication:'):
                        exercise['explanation'] = line.replace('Explication:', '').strip()
                        current_field = 'explanation'
                    elif current_field == 'question' and line:
                        exercise['question'] += ' ' + line
                    elif current_field == 'explanation' and line:
                        exercise['explanation'] += ' ' + line
                
                if exercise['question']:  # Ajoute seulement si la question n'est pas vide
                    exercises.append(exercise)
        
        except Exception as e:
            st.error(f"Erreur lors du parsing des exercices : {str(e)}")
        
        return exercises
    
    def _parse_options(self, options_text):
        """Parse les options d'un QCM"""
        options = []
        
        # Cherche les patterns A) B) C) D) ou 1) 2) 3) 4)
        import re
        patterns = [
            r'[A-D]\)\s*([^,]+)',  # A) option,
            r'\d\)\s*([^,]+)',     # 1) option,
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, options_text)
            if matches:
                options = [match.strip() for match in matches]
                break
        
        # Si aucun pattern trouvé, divise par virgules
        if not options:
            options = [opt.strip() for opt in options_text.split(',') if opt.strip()]
        
        return options[:4]  # Max 4 options

class EducationalChatbot:
    """Chatbot éducatif utilisant l'API Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash') if GEMINI_API_KEY else None
        self.course_processor = CourseProcessor()
        self.exercise_generator = ExerciseGenerator(self.model)
        self.summary_generator = SummaryGenerator(self.model)
        self.conversation_history = []
    
    def load_course(self, uploaded_file):
        """Charge un cours depuis un fichier uploadé"""
        if uploaded_file is None:
            return False
        
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'txt':
            content = self.course_processor.load_txt_file(uploaded_file)
        elif file_extension == 'pdf':
            content = self.course_processor.load_pdf_file(uploaded_file)
        else:
            st.error("Format de fichier non supporté. Utilisez TXT ou PDF.")
            return False
        
        if content:
            return self.course_processor.process_content(content)
        return False
    
    def create_system_prompt(self, user_question, relevant_content):
        """Crée le prompt système pour Gemini"""
        system_prompt = f"""
Tu es un assistant pédagogique expert et bienveillant. Tu dois aider l'étudiant en te basant EXCLUSIVEMENT sur le contenu du cours fourni.

CONTENU DU COURS PERTINENT :
{relevant_content}

RÈGLES IMPORTANTES :
1. Base tes réponses UNIQUEMENT sur le contenu du cours fourni ci-dessus
2. Si l'information demandée n'est pas dans le cours, réponds : "Cette information n'est pas couverte dans le cours fourni"
3. Sois pédagogique, clair et encourageant
4. Utilise des exemples tirés du cours quand c'est possible
5. Structure ta réponse de manière logique avec des titres et sous-titres si nécessaire
6. Si l'étudiant a besoin de clarifications, demande des précisions
7. Encourage toujours l'apprentissage et propose des exercices si approprié

QUESTION DE L'ÉTUDIANT : {user_question}

Réponds de manière claire, structurée et pédagogique :
"""
        return system_prompt
    
    def generate_response(self, user_question):
        """Génère une réponse basée sur le cours"""
        if not self.model:
            return "⚠️ Clé API Gemini non configurée. Veuillez ajouter votre clé API dans un fichier .env"
        
        try:
            # Trouve le contenu pertinent
            relevant_content = self.course_processor.get_relevant_content(user_question)
            
            if not relevant_content:
                return "❌ Aucun contenu de cours n'est disponible. Veuillez charger un fichier de cours."
            
            # Limite la taille du contenu
            content_text = '\n\n'.join(relevant_content)
            if len(content_text) > 3000:
                content_text = content_text[:3000] + "..."
            
            # Crée le prompt
            prompt = self.create_system_prompt(user_question, content_text)
            
            # Génère la réponse avec Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**MODEL_CONFIG),
                safety_settings=SAFETY_SETTINGS
            )
            
            # Sauvegarde dans l'historique
            self.conversation_history.append({
                'question': user_question,
                'response': response.text
            })
            
            return response.text
            
        except Exception as e:
            return f"❌ Erreur lors de la génération de la réponse : {str(e)}"

def display_exercise(exercise, exercise_index):
    """Affiche un exercice avec interaction"""
    st.markdown(f"###  Exercice {exercise['id']} - {exercise['type']} ({exercise['level'].title()})")
    st.markdown(f"**Question :** {exercise['question']}")
    
    user_answer = None
    
    # Interface selon le type d'exercice
    if exercise['options'] and len(exercise['options']) > 1:
        # QCM ou choix multiple
        user_answer = st.radio(
            "Choisissez votre réponse :",
            exercise['options'],
            key=f"exercise_{exercise_index}_{exercise['id']}"
        )
    elif 'vrai' in exercise['type'].lower() or 'faux' in exercise['type'].lower():
        # Vrai/Faux
        user_answer = st.radio(
            "Votre réponse :",
            ['Vrai', 'Faux'],
            key=f"exercise_{exercise_index}_{exercise['id']}"
        )
    else:
        # Question ouverte
        user_answer = st.text_area(
            "Votre réponse :",
            key=f"exercise_{exercise_index}_{exercise['id']}",
            height=100
        )
    
    # Boutons d'action
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"✅ Vérifier", key=f"check_{exercise_index}_{exercise['id']}"):
            if user_answer:
                st.session_state[f"show_answer_{exercise_index}_{exercise['id']}"] = True
            else:
                st.warning("Veuillez fournir une réponse avant de vérifier.")
    
    with col2:
        if st.button(f"💡 Voir la réponse", key=f"show_{exercise_index}_{exercise['id']}"):
            st.session_state[f"show_answer_{exercise_index}_{exercise['id']}"] = True
    
    # Affichage de la réponse et explication
    if st.session_state.get(f"show_answer_{exercise_index}_{exercise['id']}", False):
        st.markdown("---")
        
        if user_answer:
            # Évaluation simple de la réponse
            is_correct = False
            if exercise['options']:
                is_correct = user_answer.lower().strip() in exercise['correct_answer'].lower()
            else:
                # Pour les questions ouvertes, on affiche juste la réponse attendue
                st.info(f"**Votre réponse :** {user_answer}")
        
        st.success(f"**✅ Réponse correcte :** {exercise['correct_answer']}")
        
        if exercise['explanation']:
            st.info(f"**💡 Explication :** {exercise['explanation']}")
        
        if user_answer and exercise['options']:
            if is_correct:
                st.balloons()
                st.success("🎉 Excellente réponse !")
            else:
                st.error(" Ce n'est pas la bonne réponse. Relisez l'explication ci-dessus.")

def display_summary(summary):
    """Affiche un résumé généré"""
    if summary:
        st.markdown("---")
        st.subheader(f" Résumé - Niveau {summary['level'].title()}")
        
        # Métadonnées
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f" Niveau : {summary['level'].title()}")
        with col2:
            if summary['topic']:
                st.caption(f" Sujet : {summary['topic']}")
        with col3:
            st.caption(f" Généré : {summary['timestamp']}")
        
        # Contenu du résumé
        st.markdown(summary['content'])
        
        # Boutons d'action
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(" Télécharger le résumé"):
                # Crée le contenu à télécharger
                download_content = f"""
# Résumé de Cours - Niveau {summary['level'].title()}
Généré le {summary['timestamp']}
{f"Sujet: {summary['topic']}" if summary['topic'] else ""}

{summary['content']}
"""
                st.download_button(
                    label=" Télécharger (Markdown)",
                    data=download_content,
                    file_name=f"resume_cours_{summary['level']}_{summary['timestamp'][:10]}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button(" Régénérer"):
                st.session_state.regenerate_summary = True
                st.rerun()
        
        with col3:
            if st.button(" Créer des exercices basés sur ce résumé"):
                st.session_state.exercises_from_summary = True
                st.rerun()

def main():
    # Configuration de la page
    st.set_page_config(
        page_title=" Agent tutorat IA",
        page_icon="🎓",
        layout="wide"
    )
    
    # Titre principal
    st.title("🎓Agent tutorat IA")
    st.markdown("### Votre assistant personnel pour l'apprentissage et la pratique")
    
    # Vérification de la clé API
    if not GEMINI_API_KEY:
        st.error("⚠️ Clé API Gemini manquante ! Créez un fichier .env avec GEMINI_API_KEY=votre_cle")
        st.info("Obtenez votre clé API gratuite sur : https://makersuite.google.com")
        return
    
    # Initialisation du chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = EducationalChatbot()
    
    # Initialisation des états
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'course_loaded' not in st.session_state:
        st.session_state.course_loaded = False
    if 'generated_exercises' not in st.session_state:
        st.session_state.generated_exercises = []
    if 'generated_summary' not in st.session_state:
        st.session_state.generated_summary = None
    if 'student_level' not in st.session_state:
        st.session_state.student_level = 'intermediaire'
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header(" Configuration")
        
        # Chargement du cours
        st.subheader("Chargement du cours")
        uploaded_file = st.file_uploader(
            "Choisissez votre fichier de cours",
            type=['txt', 'pdf'],
            help="Formats supportés : TXT, PDF"
        )
        
        if uploaded_file is not None:
            if st.button(" Charger le cours", type="primary"):
                with st.spinner("Chargement du cours..."):
                    if st.session_state.chatbot.load_course(uploaded_file):
                        st.session_state.course_loaded = True
                        st.success("✅ Cours chargé avec succès !")
                        # Reset des messages, exercices et résumés
                        st.session_state.messages = []
                        st.session_state.generated_exercises = []
                        st.session_state.generated_summary = None
                    else:
                        st.error(" Erreur lors du chargement du cours")
        
        # Statut du cours
        if st.session_state.course_loaded:
            st.success(" Cours actif")
            course_title = st.session_state.chatbot.course_processor.course_title
            if course_title:
                st.caption(f"**Titre :** {course_title}")
        else:
            st.warning(" Aucun cours chargé")
        
        st.markdown("---")
        
        # Configuration du niveau d'étudiant
        st.subheader(" Profil étudiant")
        st.session_state.student_level = st.selectbox(
            "Votre niveau :",
            ['debutant', 'intermediaire', 'avance'],
            index=['debutant', 'intermediaire', 'avance'].index(st.session_state.student_level)
        )
        
        level_descriptions = {
            'debutant': " Concepts de base, mémorisation",
            'intermediaire': " Application, analyse modérée",
            'avance': " Analyse critique, synthèse complexe"
        }
        
        st.caption(level_descriptions[st.session_state.student_level])
        
        st.markdown("---")
        
        # Actions rapides
        st.subheader(" Actions rapides")
        
        if st.button(" Nouvelle conversation"):
            st.session_state.messages = []
            st.rerun()
        
        if st.button(" Effacer les exercices"):
            st.session_state.generated_exercises = []
            st.rerun()
        
        if st.button(" Effacer le résumé"):
            st.session_state.generated_summary = None
            st.rerun()
        
        st.markdown("---")
        
        # Guide d'utilisation
        st.subheader("ℹ Guide d'utilisation")
        st.markdown("""
        **Chatbot :**
        - Posez des questions sur votre cours
        - Demandez des explications
        - Obtenez de l'aide personnalisée
        
        ** Résumés :**
        - Résumés adaptés à votre niveau
        - Par sujet ou complet
        - Téléchargeable en Markdown
        
        ** Exercices :**
        - Exercices adaptés à votre niveau
        - Correction automatique
        - Explications détaillées
        
        ** Conseils :**
        - Soyez précis dans vos questions
        - Pratiquez régulièrement
        - Progressez graduellement
        """)
    
    # Interface principale avec onglets
    if not st.session_state.course_loaded:
        st.info("👈 Commencez par charger un fichier de cours dans la barre latérale")
    else:
        # Onglets principaux
        tab1, tab2, tab3 = st.tabs(["💬 Chatbot", "📋 Résumés", "📝 Exercices"])
        
        with tab1:
            st.header("💬 Assistant ")
            
            # Affichage de l'historique des messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Zone de saisie du chat
            if prompt := st.chat_input("Posez votre question sur le cours..."):
                # Affiche la question de l'utilisateur
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Génère et affiche la réponse
                with st.chat_message("assistant"):
                    with st.spinner("Réflexion en cours..."):
                        response = st.session_state.chatbot.generate_response(prompt)
                    st.markdown(response)
                
                # Ajoute la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})
        
        with tab2:
            st.header("Générateur de Résumés")
            
            # Interface de génération de résumés
            col1, col2 = st.columns([2, 1])
            
            with col1:
                summary_topic = st.text_input(
                    " Sujet spécifique (optionnel)",
                    placeholder="Ex: théorèmes, révolution française, photosynthèse...",
                    help="Laissez vide pour un résumé complet du cours"
                )
            
            with col2:
                summary_type = st.selectbox(
                    "Type de résumé",
                    ['general', 'detaille', 'rapide'],
                    format_func=lambda x: {
                        'general': '📖 Général',
                        'detaille': '🔍 Détaillé', 
                        'rapide': '⚡ Rapide'
                    }[x]
                )
            
            # Affichage des caractéristiques selon le niveau
            st.markdown("###  Caractéristiques du résumé selon votre niveau :")
            level_config = st.session_state.chatbot.summary_generator.summary_styles[st.session_state.student_level]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Style :** {level_config['style']}")
            with col2:
                st.info(f"**Longueur :** {level_config['length']}")
            with col3:
                st.info(f"**Focus :** {level_config['focus'][:50]}...")
            
            # Bouton de génération
            if st.button(" Générer un résumé", type="primary"):
                with st.spinner(f"Génération d'un résumé de niveau {st.session_state.student_level}..."):
                    summary = st.session_state.chatbot.summary_generator.generate_summary(
                        st.session_state.chatbot.course_processor,
                        st.session_state.student_level,
                        summary_topic if summary_topic.strip() else None,
                        summary_type
                    )
                    
                    if summary:
                        st.session_state.generated_summary = summary
                        st.success("✅ Résumé généré avec succès !")
                    else:
                        st.error(" Erreur lors de la génération du résumé. Vérifiez votre cours ou réessayez.")
            
            # Gestion de la régénération
            if st.session_state.get('regenerate_summary', False):
                with st.spinner("Régénération du résumé..."):
                    summary = st.session_state.chatbot.summary_generator.generate_summary(
                        st.session_state.chatbot.course_processor,
                        st.session_state.student_level,
                        summary_topic if summary_topic.strip() else None,
                        summary_type
                    )
                    
                    if summary:
                        st.session_state.generated_summary = summary
                        st.success("✅ Résumé régénéré !")
                
                st.session_state.regenerate_summary = False
            
            # Affichage du résumé
            if st.session_state.generated_summary:
                display_summary(st.session_state.generated_summary)
            else:
                st.info("Aucun résumé généré. Cliquez sur 'Générer un résumé' pour commencer.")
        
        with tab3:
            st.header(" Générateur d'Exercices")
            
            # Interface de génération
            col1, col2 = st.columns([2, 1])
            
            with col1:
                topic_filter = st.text_input(
                    " Sujet spécifique (optionnel)",
                    placeholder="Ex: théorèmes, révolution française...",
                    help="Laissez vide pour des exercices sur tout le cours"
                )
            
            with col2:
                num_exercises = st.number_input(
                    "Nombre d'exercices",
                    min_value=1,
                    max_value=10,
                    value=3
                )
            
            # Gestion des exercices basés sur le résumé
            if st.session_state.get('exercises_from_summary', False):
                with st.spinner("Génération d'exercices basés sur le résumé..."):
                    # Utilise le sujet du résumé si disponible
                    topic_from_summary = st.session_state.generated_summary.get('topic') if st.session_state.generated_summary else None
                    
                    exercises = st.session_state.chatbot.exercise_generator.generate_exercises(
                        st.session_state.chatbot.course_processor,
                        st.session_state.student_level,
                        3,
                        topic_from_summary
                    )
                    
                    if exercises:
                        st.session_state.generated_exercises = exercises
                        st.success("✅ Exercices générés à partir du résumé !")
                
                st.session_state.exercises_from_summary = False
            
            # Bouton de génération
            if st.button("✨ Générer des exercices", type="primary"):
                with st.spinner(f"Génération d'exercices de niveau {st.session_state.student_level}..."):
                    exercises = st.session_state.chatbot.exercise_generator.generate_exercises(
                        st.session_state.chatbot.course_processor,
                        st.session_state.student_level,
                        num_exercises,
                        topic_filter if topic_filter.strip() else None
                    )
                    
                    if exercises:
                        st.session_state.generated_exercises = exercises
                        st.success(f"✅ {len(exercises)} exercice(s) généré(s) !")
                    else:
                        st.error("❌ Aucun exercice généré. Vérifiez votre cours ou réessayez.")
            
            # Affichage des exercices
            if st.session_state.generated_exercises:
                st.markdown("---")
                st.subheader(f" Exercices - Niveau {st.session_state.student_level.title()}")
                
                for i, exercise in enumerate(st.session_state.generated_exercises):
                    with st.container():
                        display_exercise(exercise, i)
                        st.markdown("---")
            else:
                st.info("Aucun exercice généré. Cliquez sur 'Générer des exercices' pour commencer.")


# Point d'entrée
if __name__ == "__main__":
    main()
