import streamlit as st
import os
from dotenv import load_dotenv
import time
import random
import json
from typing import Dict, List, Tuple
import requests


# Configure page
st.set_page_config(
    page_title="Learning Profiling AI Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv()
# Get Groq API key from environment variable
groq_api_key = os.environ.get('GROQ_API_KEY')

# Custom CSS for beautiful design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f2ff 50%, #dbeafe 100%);
        min-height: 100vh;
        animation: gentleShift 12s ease-in-out infinite;
    }
    
    @keyframes gentleShift {
        0% { background: linear-gradient(135deg, #f0f4ff 0%, #e8f2ff 50%, #dbeafe 100%); }
        33% { background: linear-gradient(135deg, #ede9fe 0%, #e0e7ff 50%, #e8f2ff 100%); }
        66% { background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 50%, #f0f4ff 100%); }
        100% { background: linear-gradient(135deg, #f0f4ff 0%, #e8f2ff 50%, #dbeafe 100%); }
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 40px rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(196, 181, 253, 0.2);
        animation: floatIn 1.2s cubic-bezier(0.23, 1, 0.32, 1);
    }
    
    @keyframes floatIn {
        from { 
            transform: translateY(60px); 
            opacity: 0;
            backdrop-filter: blur(0px);
        }
        to { 
            transform: translateY(0); 
            opacity: 1;
            backdrop-filter: blur(20px);
        }
    }
    
    .course-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 24px rgba(139, 92, 246, 0.06);
        border: 1px solid rgba(196, 181, 253, 0.15);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative;
        overflow: hidden;
        animation: slideInCard 0.8s cubic-bezier(0.23, 1, 0.32, 1);
        animation-fill-mode: both;
    }
    
    .course-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        transition: all 0.4s ease;
    }
    
    .course-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(135deg, #c4b5fd, #a5b4fc, #ddd6fe);
        border-radius: 22px;
        z-index: -1;
        opacity: 0;
        transition: all 0.4s ease;
    }
    
    .course-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(139, 92, 246, 0.15);
        backdrop-filter: blur(25px);
    }
    
    .course-card:hover::before {
        height: 8px;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    }
    
    .course-card:hover::after {
        opacity: 0.1;
    }
    
    @keyframes slideInCard {
        from { 
            transform: translateY(40px) scale(0.95); 
            opacity: 0; 
        }
        to { 
            transform: translateY(0) scale(1); 
            opacity: 1; 
        }
    }
    
    .course-card.locked {
        background: linear-gradient(135deg, rgba(241, 245, 249, 0.8) 0%, rgba(226, 232, 240, 0.8) 100%);
        opacity: 0.6;
        animation: pulseGently 3s ease-in-out infinite;
    }
    
    .course-card.locked::before {
        background: linear-gradient(135deg, #cbd5e1, #94a3b8);
    }
    
    @keyframes pulseGently {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 0.7; }
    }
    
    .course-card.unlocked {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: shimmer 2s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { box-shadow: 0 4px 24px rgba(139, 92, 246, 0.2); }
        50% { box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3); }
    }
    
    .learning-style-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(237, 233, 254, 0.7) 100%);
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(196, 181, 253, 0.2);
        animation: breathe 4s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .learning-style-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(196, 181, 253, 0.1) 0%, transparent 70%);
        animation: rotate 8s linear infinite;
        z-index: -1;
    }
    
    @keyframes breathe {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 8px 32px rgba(139, 92, 246, 0.08);
        }
        50% { 
            transform: scale(1.02);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.12);
        }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .question-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(224, 231, 255, 0.6) 100%);
        color: #4c1d95;
        border-radius: 18px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #a5b4fc;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.06);
        animation: slideInLeft 0.6s cubic-bezier(0.23, 1, 0.32, 1);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    }
    
    .question-card:hover {
        transform: translateX(8px) translateY(-2px);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.12);
        border-left-color: #8b5cf6;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(196, 181, 253, 0.2) 100%);
    }
    
    @keyframes slideInLeft {
        from { 
            transform: translateX(-40px); 
            opacity: 0; 
        }
        to { 
            transform: translateX(0); 
            opacity: 1; 
        }
    }
    
    .progress-container {
        background: rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(196, 181, 253, 0.2);
        animation: fadeInUp 0.8s ease-out;
    }
    
    @keyframes fadeInUp {
        from { 
            transform: translateY(20px); 
            opacity: 0; 
        }
        to { 
            transform: translateY(0); 
            opacity: 1; 
        }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 50%, #ddd6fe 100%);
        color: #4c1d95;
        border: none;
        border-radius: 14px;
        padding: 0.9rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        box-shadow: 0 4px 20px rgba(165, 180, 252, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4);
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%);
        color: white;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .title-header {
        text-align: center;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 3rem;
        animation: titleFloat 4s ease-in-out infinite;
        position: relative;
    }
    
    .title-header::after {
        content: '';
        position: absolute;
        bottom: -16px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
        border-radius: 2px;
        animation: underlineGlow 2s ease-in-out infinite;
    }
    
    @keyframes titleFloat {
        0%, 100% { 
            transform: translateY(0px);
            filter: brightness(1);
        }
        50% { 
            transform: translateY(-5px);
            filter: brightness(1.1);
        }
    }
    
    @keyframes underlineGlow {
        0%, 100% { 
            box-shadow: 0 0 10px rgba(165, 180, 252, 0.3);
            width: 80px;
        }
        50% { 
            box-shadow: 0 0 20px rgba(196, 181, 253, 0.6);
            width: 100px;
        }
    }
    
    .success-message {
        background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
        color: #4c1d95;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 24px rgba(165, 180, 252, 0.3);
        font-weight: 600;
        animation: successWave 1.5s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative;
        overflow: hidden;
    }
    
    .success-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: successShine 2s ease-out;
    }
    
    @keyframes successWave {
        0% { transform: scale(0.9) translateY(10px); opacity: 0; }
        50% { transform: scale(1.05) translateY(-2px); }
        100% { transform: scale(1) translateY(0); opacity: 1; }
    }
    
    @keyframes successShine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .floating-particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        background: radial-gradient(circle, rgba(196, 181, 253, 0.6) 0%, rgba(165, 180, 252, 0.3) 50%, transparent 100%);
        border-radius: 50%;
        animation: gentleFloat 8s ease-in-out infinite;
    }
    
    .particle:nth-child(odd) {
        background: radial-gradient(circle, rgba(165, 180, 252, 0.6) 0%, rgba(196, 181, 253, 0.3) 50%, transparent 100%);
        animation-direction: reverse;
    }
    
    @keyframes gentleFloat {
        0%, 100% { 
            transform: translateY(0px) translateX(0px) rotate(0deg); 
            opacity: 0.4;
        }
        25% { 
            transform: translateY(-15px) translateX(10px) rotate(90deg); 
            opacity: 0.7;
        }
        50% { 
            transform: translateY(-25px) translateX(-5px) rotate(180deg); 
            opacity: 0.5;
        }
        75% { 
            transform: translateY(-10px) translateX(-15px) rotate(270deg); 
            opacity: 0.6;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(135deg, #f0f4ff, #e8f2ff);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
        border-radius: 6px;
        border: 2px solid #f0f4ff;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6, #a855f7);
    }
    
    /* Smooth transitions for all elements */
    * {
        transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    /* Enhanced focus states */
    .stButton > button:focus,
    .course-card:focus {
        outline: 3px solid rgba(165, 180, 252, 0.5);
        outline-offset: 2px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-container {
            margin: 0.5rem;
            padding: 1.5rem;
        }
        
        .title-header {
            font-size: 2.5rem;
        }
        
        .course-card, .question-card {
            padding: 1.5rem;
        }
        
        .learning-style-card {
            padding: 2rem;
        }
    }
</style>

<div class="floating-particles">
    <div class="particle" style="left: 10%; top: 20%; width: 12px; height: 12px; animation-delay: 0s;"></div>
    <div class="particle" style="left: 80%; top: 15%; width: 18px; height: 18px; animation-delay: 2s;"></div>
    <div class="particle" style="left: 60%; top: 70%; width: 10px; height: 10px; animation-delay: 4s;"></div>
    <div class="particle" style="left: 30%; top: 80%; width: 14px; height: 14px; animation-delay: 1s;"></div>
    <div class="particle" style="left: 90%; top: 60%; width: 16px; height: 16px; animation-delay: 3s;"></div>
    <div class="particle" style="left: 20%; top: 50%; width: 8px; height: 8px; animation-delay: 5s;"></div>
</div>
""", unsafe_allow_html=True)


# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'learning_style' not in st.session_state:
    st.session_state.learning_style = None
if 'unlocked_courses' not in st.session_state:
    st.session_state.unlocked_courses = set()
if 'course_progress' not in st.session_state:
    st.session_state.course_progress = {}
if 'questions_cache' not in st.session_state:
    st.session_state.questions_cache = {}
if 'learning_style_questions' not in st.session_state:
    st.session_state.learning_style_questions = None

# Course Information
COURSES = {
    "Cybersecurity": {
        "description": "Learn about network security, ethical hacking, and data protection",
        "icon": "🛡️",
        "color": "linear-gradient(135deg, #6c5ce7, #5f3dc4)"
    },
    "Statistics": {
        "description": "Master statistical analysis, probability, and data interpretation",
        "icon": "📊",
        "color": "linear-gradient(135deg, #74b9ff, #0984e3)"
    },
    "Deep Learning": {
        "description": "Explore neural networks, AI algorithms, and machine learning",
        "icon": "🧠",
        "color": "linear-gradient(135deg, #a29bfe, #6c5ce7)"
    },
    "SQL": {
        "description": "Database management, queries, and data manipulation",
        "icon": "💾",
        "color": "linear-gradient(135deg, #4c6ef5, #364fc7)"
    },
    "Python Programming": {
        "description": "Programming fundamentals, data structures, and algorithms",
        "icon": "🐍",
        "color": "linear-gradient(135deg, #7c3aed, #5b21b6)"
    },
    "Data Science": {
        "description": "Data analysis, visualization, and predictive modeling",
        "icon": "📈",
        "color": "linear-gradient(135deg, #8b5cf6, #7c2d12)"
    }
}


def generate_learning_style_questions_with_groq() -> List[Dict]:
    """Generate learning style assessment questions using Groq API (free and fast)"""
    
    if groq_api_key is None:
        st.warning("Groq API key not configured. Using fallback questions.")
        return get_fallback_learning_style_questions()
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",  
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educational psychologist. You must return responses in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": """Create a comprehensive learning style assessment based on the Felder-Soloman Index of Learning Styles (ILS). This assessment identifies four key learning style dimensions:

1. **ACTIVE vs REFLECTIVE**: How students process information
   - Active learners learn by trying things out, discussing, explaining to others
   - Reflective learners learn by thinking things through quietly first

2. **SENSING vs INTUITIVE**: What type of information students prefer
   - Sensing learners prefer concrete, practical, factual information
   - Intuitive learners prefer abstract concepts, theories, and meanings

3. **VISUAL vs VERBAL**: How students prefer to receive information
   - Visual learners prefer pictures, diagrams, flow charts, time lines, films, demonstrations
   - Verbal learners prefer written and spoken explanations

4. **SEQUENTIAL vs GLOBAL**: How students understand information
   - Sequential learners learn in linear steps, each building on the previous
   - Global learners learn in large jumps, absorbing material randomly until they suddenly "get it"

**REQUIREMENTS:**
- Generate EXACTLY 12 questions (3 per dimension)
- Each question has exactly 2 options: A and B
- Option A represents the first learning style in each dimension pair
- Option B represents the second learning style in each dimension pair
- Questions must be practical, relatable scenarios
- Use clear, simple language
- Each question should clearly differentiate between the two learning preferences

**DIMENSION ORDER:**
- Questions 1-3: "active_reflective" (A=Active, B=Reflective)
- Questions 4-6: "sensing_intuitive" (A=Sensing, B=Intuitive) 
- Questions 7-9: "visual_verbal" (A=Visual, B=Verbal)
- Questions 10-12: "sequential_global" (A=Sequential, B=Global)

Return ONLY this exact JSON format:
[
  {
    "question": "When I learn something new, I prefer to",
    "options": {
      "A": "Jump right in and start experimenting with it",
      "B": "Think it through carefully before trying it"
    },
    "dimension": "active_reflective"
  }
]

Generate all 12 questions now in this exact format:"""
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2500,
                "top_p": 1,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Clean up the response and extract JSON
            generated_text = generated_text.strip()
            
            # Find JSON array bounds
            json_start = generated_text.find('[')
            json_end = generated_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = generated_text[json_start:json_end]
                
                try:
                    questions_data = json.loads(json_text)
                    
                    # Validate the structure
                    if isinstance(questions_data, list) and len(questions_data) == 12:
                        valid_questions = []
                        
                        for i, q in enumerate(questions_data):
                            if all(key in q for key in ['question', 'options', 'dimension']):
                                if 'A' in q['options'] and 'B' in q['options']:
                                    valid_questions.append({
                                        'question': q['question'],
                                        'options': q['options'],
                                        'dimension': q['dimension']
                                    })
                        
                        if len(valid_questions) == 12:
                            st.success("✅ Successfully generated questions with Groq!")
                            return valid_questions
                
                except json.JSONDecodeError as e:
                    st.error(f"JSON parsing error: {e}")
        
        else:
            st.error(f"Groq API error: {response.status_code} - {response.text}")
        
        # Fallback if anything goes wrong
        st.warning("Using fallback questions due to API issues.")
        return get_fallback_learning_style_questions()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Network error with Groq API: {e}")
        return get_fallback_learning_style_questions()
    except Exception as e:
        st.error(f"Unexpected error with Groq: {e}")
        return get_fallback_learning_style_questions()

def get_fallback_learning_style_questions() -> List[Dict]:
    """Fallback learning style questions based on ILS principles"""
    return [
        # Active vs Reflective (Questions 1-3)
        {
            "question": "When I encounter a new software or app, I prefer to:",
            "options": {
                "A": "Jump right in and start exploring the features",
                "B": "Read the documentation or watch tutorials first"
            },
            "dimension": "active_reflective"
        },
        {
            "question": "In a study group, I am more likely to:",
            "options": {
                "A": "Actively participate in discussions and explain concepts to others",
                "B": "Listen carefully and think through ideas before contributing"
            },
            "dimension": "active_reflective"
        },
        {
            "question": "When learning a new skill, I prefer to:",
            "options": {
                "A": "Practice immediately and learn through trial and error",
                "B": "Understand the theory and principles before attempting practice"
            },
            "dimension": "active_reflective"
        },
        
        # Sensing vs Intuitive (Questions 4-6)
        {
            "question": "I am more interested in:",
            "options": {
                "A": "Practical applications and real-world examples",
                "B": "Theoretical concepts and abstract ideas"
            },
            "dimension": "sensing_intuitive"
        },
        {
            "question": "When solving problems, I prefer:",
            "options": {
                "A": "Step-by-step procedures with clear, proven methods",
                "B": "Creative approaches and exploring new possibilities"
            },
            "dimension": "sensing_intuitive"
        },
        {
            "question": "I learn best from courses that focus on:",
            "options": {
                "A": "Facts, data, and concrete information",
                "B": "Concepts, theories, and big-picture thinking"
            },
            "dimension": "sensing_intuitive"
        },
        
        # Visual vs Verbal (Questions 7-9)
        {
            "question": "When someone gives me directions, I prefer:",
            "options": {
                "A": "A map or visual diagram",
                "B": "Written or spoken step-by-step instructions"
            },
            "dimension": "visual_verbal"
        },
        {
            "question": "I understand information better when it's presented through:",
            "options": {
                "A": "Charts, graphs, diagrams, and images",
                "B": "Text descriptions and verbal explanations"
            },
            "dimension": "visual_verbal"
        },
        {
            "question": "When studying, I find it most helpful to:",
            "options": {
                "A": "Create visual summaries like mind maps or flowcharts",
                "B": "Write detailed notes and summaries in words"
            },
            "dimension": "visual_verbal"
        },
        
        # Sequential vs Global (Questions 10-12)
        {
            "question": "When learning new material, I prefer to:",
            "options": {
                "A": "Follow a logical sequence, building understanding step by step",
                "B": "Get an overview first, then fill in the details"
            },
            "dimension": "sequential_global"
        },
        {
            "question": "I understand complex topics better when:",
            "options": {
                "A": "Each part is explained thoroughly before moving to the next",
                "B": "I see how all the pieces connect to the whole picture"
            },
            "dimension": "sequential_global"
        },
        {
            "question": "When working on projects, I typically:",
            "options": {
                "A": "Complete tasks in order, finishing one before starting the next",
                "B": "Work on multiple parts simultaneously and see how they fit together"
            },
            "dimension": "sequential_global"
        }
    ]





def generate_course_questions_with_groq(course_name: str) -> List[Dict]:
    """Generate course-specific questions using Groq API"""
    
    if groq_api_key is None:
        st.warning("Groq API key not configured. Using fallback questions.")
        return get_fallback_course_questions(course_name)
    
    try:
        course_details = {
            "Cybersecurity": "network security, ethical hacking, data protection, firewalls, encryption, malware, vulnerability assessment, penetration testing, security protocols",
            "Statistics": "statistical analysis, probability theory, data interpretation, hypothesis testing, regression analysis, descriptive statistics, inferential statistics, sampling",
            "Deep Learning": "neural networks, artificial intelligence, machine learning algorithms, backpropagation, convolutional networks, recurrent networks, optimization, model training",
            "SQL": "database management, query writing, data manipulation, joins, indexing, normalization, stored procedures, database design",
            "Python Programming": "programming fundamentals, data structures, algorithms, object-oriented programming, functions, libraries, debugging, code optimization",
            "Data Science": "data analysis, data visualization, predictive modeling, data cleaning, statistical modeling, pandas, matplotlib, scikit-learn"
        }
        
        topics = course_details.get(course_name, "general programming and computer science concepts")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",  # Current available models
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert instructor and assessment creator. You must return responses in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": f"""Create a comprehensive assessment quiz for {course_name} with 6 multiple-choice questions that test different levels of understanding.

**COURSE FOCUS:** {course_name}
**KEY TOPICS TO COVER:** {topics}

**REQUIREMENTS:**
1. Create EXACTLY 6 questions with varying difficulty levels:
   - 2 EASY questions (fundamental concepts)
   - 2 MEDIUM questions (application and analysis)  
   - 2 HARD questions (advanced concepts and problem-solving)

2. Each question must have:
   - Clear, specific question text
   - Exactly 4 multiple choice options
   - One correct answer
   - Options that test real understanding (avoid obviously wrong choices)

3. Questions should:
   - Test practical knowledge relevant to {course_name}
   - Be answerable by someone with intermediate knowledge in the field
   - Include real-world scenarios where appropriate
   - Avoid trick questions or ambiguous wording

4. Cover diverse aspects of {course_name}, not just one narrow topic

**OUTPUT FORMAT:**
Return ONLY a valid JSON array with this exact structure:

[
  {{
    "question": "What is the primary purpose of a firewall in network security?",
    "options": ["To encrypt data", "To filter network traffic", "To store passwords", "To create backups"],
    "correct": 1,
    "difficulty": "easy"
  }}
]

**IMPORTANT RULES:**
- "correct" should be the index (0-3) of the correct answer
- "difficulty" should be exactly "easy", "medium", or "hard"
- Each question must have exactly 4 options
- Questions should be practical and relevant to {course_name}

Generate 6 high-quality questions for {course_name} now:"""
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 3000,
                "top_p": 1,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Clean up the response and extract JSON
            generated_text = generated_text.strip()
            
            # Find JSON array bounds
            json_start = generated_text.find('[')
            json_end = generated_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = generated_text[json_start:json_end]
                
                try:
                    questions_data = json.loads(json_text)
                    
                    # Validate the structure
                    if isinstance(questions_data, list) and len(questions_data) == 6:
                        valid_questions = []
                        
                        for q in questions_data:
                            if all(key in q for key in ['question', 'options', 'correct', 'difficulty']):
                                if isinstance(q['options'], list) and len(q['options']) == 4:
                                    if isinstance(q['correct'], int) and 0 <= q['correct'] <= 3:
                                        if q['difficulty'] in ['easy', 'medium', 'hard']:
                                            valid_questions.append({
                                                'question': q['question'],
                                                'options': q['options'],
                                                'correct': q['correct'],
                                                'difficulty': q['difficulty']
                                            })
                        
                        if len(valid_questions) == 6:
                            st.success(f"✅ Successfully generated {course_name} questions with Groq!")
                            return valid_questions
                
                except json.JSONDecodeError as e:
                    st.error(f"JSON parsing error: {e}")
        
        else:
            st.error(f"Groq API error: {response.status_code} - {response.text}")
        
        # Fallback if anything goes wrong
        st.warning("Using fallback questions due to API issues.")
        return get_fallback_course_questions(course_name)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Network error with Groq API: {e}")
        return get_fallback_course_questions(course_name)
    except Exception as e:
        st.error(f"Unexpected error with Groq: {e}")
        return get_fallback_course_questions(course_name)


    
    
def display_quiz():
    """Display course-specific quiz"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Check if we have a current course set
    if 'current_course' not in st.session_state or not st.session_state.current_course:
        st.error("❌ No course selected for quiz. Please go back to courses and select a quiz to take.")
        if st.button("🏠 Back to Courses"):
            st.session_state.current_page = 'courses'
            st.rerun()
        return
    
    course_name = st.session_state.current_course
    st.markdown(f'<h2 class="title-header">📝 {course_name} Assessment Quiz</h2>', unsafe_allow_html=True)
    
    # Initialize quiz state if not exists
    if 'quiz_questions' not in st.session_state:
        with st.spinner(f"🔄 Generating personalized {course_name} quiz questions..."):
            st.session_state.quiz_questions = generate_course_questions_with_groq(course_name)
            st.session_state.current_question = 0
            st.session_state.quiz_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.quiz_score = 0
    
    # Check if questions were generated successfully
    if not st.session_state.quiz_questions or len(st.session_state.quiz_questions) == 0:
        st.error(f"❌ Unable to load quiz questions for {course_name}. Please try again.")
        if st.button("🔄 Retry Quiz Generation"):
            # Clear the failed quiz state and try again
            if 'quiz_questions' in st.session_state:
                del st.session_state.quiz_questions
            st.rerun()
        if st.button("🏠 Back to Courses"):
            st.session_state.current_page = 'courses'
            # Clear quiz state
            for key in ['quiz_questions', 'current_question', 'quiz_answers', 'quiz_completed', 'quiz_score', 'current_course']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return
    
    questions = st.session_state.quiz_questions
    current_q = st.session_state.current_question
    
    # Quiz completed
    if st.session_state.quiz_completed:
        display_quiz_results(course_name)
        return
    
    # Display progress
    progress = (current_q + 1) / len(questions)
    st.progress(progress)
    st.markdown(f"**Question {current_q + 1} of {len(questions)}**")
    
    # Display current question
    question = questions[current_q]
    
    # Add difficulty indicator
    difficulty_colors = {
        'easy': '🟢 Easy',
        'medium': '🟡 Medium', 
        'hard': '🔴 Hard'
    }
    difficulty_display = difficulty_colors.get(question.get('difficulty', 'medium'), '🟡 Medium')
    st.markdown(f"**Difficulty:** {difficulty_display}")
    
    st.markdown("---")
    st.markdown(f"### {question['question']}")
    
    # Display options
    selected_answer = st.radio(
        "Select your answer:",
        options=range(len(question['options'])),
        format_func=lambda x: f"{chr(65 + x)}. {question['options'][x]}",
        key=f"q_{current_q}_answer"
    )
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏠 Exit Quiz", help="Return to courses (progress will be lost)"):
            # Clear quiz state
            for key in ['quiz_questions', 'current_question', 'quiz_answers', 'quiz_completed', 'quiz_score', 'current_course']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_page = 'courses'
            st.rerun()
    
    with col2:
        if current_q > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col3:
        if st.button("➡️ Next" if current_q < len(questions) - 1 else "✅ Submit Quiz"):
            # Save current answer
            st.session_state.quiz_answers[current_q] = selected_answer
            
            if current_q < len(questions) - 1:
                st.session_state.current_question += 1
                st.rerun()
            else:
                # Calculate final score
                correct_answers = 0
                for q_idx, user_answer in st.session_state.quiz_answers.items():
                    if user_answer == questions[q_idx]['correct']:
                        correct_answers += 1
                
                st.session_state.quiz_score = correct_answers
                st.session_state.quiz_completed = True
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_quiz_results(course_name):
    """Display quiz results and handle course unlocking - all students get access"""
    questions = st.session_state.quiz_questions
    total_questions = len(questions)
    score = st.session_state.quiz_score
    percentage = (score / total_questions) * 100
   
    st.markdown(f"## 🎉 Quiz Results - {course_name}")
    st.markdown("---")
   
    # Determine level and display message (but don't restrict access)
    if percentage >= 90:
        level = "Expert"
        level_emoji = "🏆"
        st.success(f"🏆 Expert Level! You scored {score}/{total_questions} ({percentage:.1f}%)")
        success_message = "Outstanding mastery! You've demonstrated expert-level understanding of the material."
        color = "#28a745"
    elif percentage >= 80:
        level = "Advanced"
        level_emoji = "🌟"
        st.success(f"🌟 Advanced Level! You scored {score}/{total_questions} ({percentage:.1f}%)")
        success_message = "Excellent performance! You have advanced understanding of the concepts."
        color = "#17a2b8"
    elif percentage >= 70:
        level = "Intermediate"
        level_emoji = "📈"
        st.info(f"📈 Intermediate Level! You scored {score}/{total_questions} ({percentage:.1f}%)")
        success_message = "Good job! You have solid intermediate knowledge of the material."
        color = "#ffc107"
    elif percentage >= 0:
        level = "Beginner"
        level_emoji = "✅"
        st.info(f"✅ Beginner Level! You scored {score}/{total_questions} ({percentage:.1f}%)")
        success_message = "Nice work! You're developing a good foundation in this subject."
        color = "#6c757d"
    
   
    # Always unlock the course - learning should be accessible to everyone
    if course_name not in st.session_state.unlocked_courses:
        st.session_state.unlocked_courses.add(course_name)
        st.balloons()
        st.success(f"🔓 Congratulations! You now have full access to {course_name}!")
    
    # Display encouraging message
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                border-left: 4px solid {color}; 
                padding: 1rem; 
                border-radius: 5px; 
                margin: 1rem 0;">
        <h4 style="color: {color}; margin: 0;">{level_emoji} {success_message}</h4>
        <p style="margin: 0.5rem 0 0 0;">🔓 <strong>Course Access:</strong> Unlocked! You can now access all course materials.</p>
    </div>
    """, unsafe_allow_html=True)
   
    # Performance insights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Score", f"{score}/{total_questions}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        st.metric("Level Achieved", level)
   
    # Detailed results
    with st.expander("📊 Detailed Question Review"):
        correct_count = 0
        for i, question in enumerate(questions):
            user_answer = st.session_state.quiz_answers.get(i, -1)
            correct_answer = question['correct']
           
            if user_answer == correct_answer:
                correct_count += 1
                st.markdown(f"✅ **Question {i+1}**: Correct")
                st.markdown(f"   - **Question**: {question['question']}")
                st.markdown(f"   - **Your answer**: {question['options'][user_answer]}")
            else:
                st.markdown(f"❌ **Question {i+1}**: Incorrect")
                st.markdown(f"   - **Question**: {question['question']}")
                st.markdown(f"   - **Your answer**: {question['options'][user_answer] if user_answer != -1 else 'No answer selected'}")
                st.markdown(f"   - **Correct answer**: {question['options'][correct_answer]}")
            st.markdown("---")
   
    # Store enhanced course score data for profile
    if 'course_scores' not in st.session_state:
        st.session_state.course_scores = {}
    
    # Import datetime if not already imported
    from datetime import datetime
    
    # Store comprehensive results
    st.session_state.course_scores[course_name] = {
        'score': score,
        'total': total_questions,
        'percentage': percentage,
        'level': level,
        'level_emoji': level_emoji,
        'passed': percentage >= 60,  # For display purposes only
        'attempts': st.session_state.course_scores.get(course_name, {}).get('attempts', 0) + 1,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'improvement': None  # Will be calculated if retaking
    }
    
    # Check for improvement if this is a retake
    if st.session_state.course_scores[course_name]['attempts'] > 1:
        # You could store previous scores and show improvement here
        st.info(f"📈 This is attempt #{st.session_state.course_scores[course_name]['attempts']} - great persistence!")
   
    # Learning recommendations based on performance
    st.markdown("---")
    st.markdown("### 💡 Personalized Learning Recommendations")
    
    if percentage >= 90:
        recommendations = [
            "🎯 Consider helping other students or becoming a peer tutor",
            "🔬 Explore advanced topics or related subjects",
            "📝 Try creating study materials for others"
        ]
    elif percentage >= 80:
        recommendations = [
            "📚 Review the questions you missed for deeper understanding",
            "🔄 Consider retaking the quiz to reach expert level",
            "🎯 Focus on the specific areas where you lost points"
        ]
    elif percentage >= 70:
        recommendations = [
            "📖 Spend more time with the course materials",
            "👥 Form a study group with other learners",
            "🔄 Retake the quiz after additional review"
        ]
    else:
        recommendations = [
            "📚 Take your time reviewing each concept thoroughly",
            "🎯 Break down complex topics into smaller parts",
            "💪 Don't worry - improvement comes with practice!",
            "🔄 Feel free to retake the quiz anytime"
        ]
    
    for rec in recommendations:
        st.markdown(f"• {rec}")
   
    # Action buttons with enhanced options
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
   
    with col1:
        if st.button("🔄 Retake Quiz", key="retake_quiz_btn"):
            # Clear quiz state for retake
            for key in ['quiz_questions', 'current_question', 'quiz_answers', 'quiz_completed', 'quiz_score']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
   
    with col2:
        if st.button("📖 Start Learning", key="start_learning_btn"):
            st.success(f"🎓 Welcome to {course_name}! Your learning journey begins now.")
            st.info("💡 Course content would be displayed here in a full implementation.")
            # You can redirect to actual course content page here
   
    with col3:
        if st.button("👤 View Profile", key="view_profile_btn"):
            st.session_state.current_page = 'profile'
            st.rerun()
   
    with col4:
        if st.button("📚 All Courses", key="all_courses_btn"):
            # Clear quiz state
            for key in ['quiz_questions', 'current_question', 'quiz_answers', 'quiz_completed', 'quiz_score', 'current_course']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_page = 'courses'
            st.rerun()
            
    with col5:
        if st.button("🏠 Home", key="home_btn"):
            # Clear quiz state
            for key in ['quiz_questions', 'current_question', 'quiz_answers', 'quiz_completed', 'quiz_score', 'current_course']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_page = 'home'
            st.rerun()
    
    # Additional motivation
    if percentage < 80:
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 1rem; 
                    border-radius: 8px; 
                    border-left: 4px solid #2196f3;">
            <h4 style="color: #1976d2; margin: 0;">🌟 Remember</h4>
            <p style="margin: 0.5rem 0 0 0;">Learning is a journey, not a destination. Every attempt helps you grow stronger. You have full access to continue learning and improving!</p>
        </div>
        """, unsafe_allow_html=True)
        
        
# Updated function to always unlock courses after assessment
def complete_assessment_and_unlock_course(learning_style_results, current_course=None):
    """Complete assessment and unlock courses - students get access regardless of performance"""
    
    # Store the learning style results
    st.session_state.learning_style = learning_style_results
    
    # If this was a course-specific assessment, unlock that specific course
    if current_course and current_course not in st.session_state.unlocked_courses:
        st.session_state.unlocked_courses.add(current_course)
        st.success(f"🎉 Great job! You now have access to {current_course}!")
    
    # For the main assessment, unlock all courses
    elif not current_course:
        # Unlock all courses after main assessment
        for course_name in COURSES.keys():
            st.session_state.unlocked_courses.add(course_name)
        st.success("🎉 Assessment completed! All courses are now accessible!")


# Updated function to record quiz results but still maintain course access
def record_quiz_results(course_name, score, total_questions, passed=None):
    """Record quiz results for profile display - access maintained regardless of score"""
    
    if 'course_scores' not in st.session_state:
        st.session_state.course_scores = {}
    
    percentage = (score / total_questions) * 100
    
    # Determine level based on percentage (for display purposes only)
    if percentage >= 90:
        level = "Expert"
        level_emoji = "🏆"
    elif percentage >= 80:
        level = "Advanced"
        level_emoji = "🌟"
    elif percentage >= 70:
        level = "Intermediate"
        level_emoji = "📈"
    elif percentage >= 60:
        level = "Beginner"
        level_emoji = "✅"
    
    
    # Store comprehensive results
    st.session_state.course_scores[course_name] = {
        'score': score,
        'total': total_questions,
        'percentage': percentage,
        'level': level,
        'level_emoji': level_emoji,
        'passed': percentage >= 60,  # For display purposes
        'attempts': st.session_state.course_scores.get(course_name, {}).get('attempts', 0) + 1,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # Course remains accessible regardless of score
    if course_name not in st.session_state.unlocked_courses:
        st.session_state.unlocked_courses.add(course_name)
    
    return level, percentage


def display_complete_profile():
    """Display complete user profile with course scores and learning style"""
    
    # Enhanced CSS styling with purple-blue theme
    st.markdown("""
    <style>
    .main-container {
        background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.1);
        margin-bottom: 2rem;
    }
    
    .title-header {
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(108, 92, 231, 0.1);
    }
    
    .learning-style-card {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 50%, #74b9ff 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(108, 92, 231, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .style-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    
    .style-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .style-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #e8f2ff 0%, #f3f0ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(108, 92, 231, 0.1);
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.15);
    }
    
    .course-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
        border: 1px solid rgba(108, 92, 231, 0.15);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 20px rgba(108, 92, 231, 0.08);
        transition: all 0.3s ease;
    }
    
    .course-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.15);
        border-color: rgba(108, 92, 231, 0.3);
    }
    
    .level-badge {
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .progress-summary-card {
        background: linear-gradient(135deg, #fdfdff 0%, #f0f4ff 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(108, 92, 231, 0.1);
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.08);
    }
    
    .action-button {
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
        background: linear-gradient(135deg, #5a4fcf 0%, #5fa8e6 100%);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff8e1 0%, #f3f0ff 100%);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .divider {
        height: 2px;
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
        border: none;
        border-radius: 2px;
        margin: 2rem 0;
        opacity: 0.3;
    }
    
    .achievement-item {
        background: linear-gradient(135deg, #f8faff 0%, #fff 100%);
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #6c5ce7, #74b9ff) 1;
        box-shadow: 0 2px 8px rgba(108, 92, 231, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="title-header">👤 Complete Learning Profile</h2>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
   
    # User Learning Style Section
    st.markdown("### 🧠 Learning Style Analysis")
    if st.session_state.learning_style:
        # Create profile dictionary
        profile = {
            'processing': st.session_state.learning_style.get('active_reflective', 'Active'),
            'perception': st.session_state.learning_style.get('sensing_intuitive', 'Sensing'),
            'input': st.session_state.learning_style.get('visual_verbal', 'Visual'),
            'understanding': st.session_state.learning_style.get('sequential_global', 'Sequential')
        }
        
        style_summary = f"{profile['processing']} | {profile['perception']} | {profile['input']} | {profile['understanding']}"
        
        st.markdown(f"""
        <div class="learning-style-card">
            <h4 style="margin: 0 0 1rem 0; font-size: 1.5rem;">🧠 Your Learning Style: {style_summary}</h4>
            <div class="style-grid">
                <div class="style-item">
                    <strong>🔄 Processing:</strong><br>{profile['processing']}
                </div>
                <div class="style-item">
                    <strong>👁️ Perception:</strong><br>{profile['perception']}
                </div>
                <div class="style-item">
                    <strong>📥 Input:</strong><br>{profile['input']}
                </div>
                <div class="style-item">
                    <strong>🧩 Understanding:</strong><br>{profile['understanding']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Get personalized recommendations
        recommendations = get_study_recommendations(profile)
        with st.expander("💡 Your Personalized Study Tips", expanded=False):
            recommendation_lines = recommendations.split('\n')
            for rec in recommendation_lines:
                if rec.strip():
                    st.markdown(f'<div class="achievement-item">{rec}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-card">
            <h4>⚠️ Learning style assessment not completed yet.</h4>
            <p>Complete your assessment to unlock personalized learning recommendations!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Take Learning Style Assessment", key="take_assessment_from_profile"):
            st.session_state.current_page = 'assessment'
            st.rerun()
   
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
   
    # Course Performance Section
    st.markdown("### 📊 Course Performance & Access")
   
    if 'course_scores' in st.session_state and st.session_state.course_scores:
        # Create performance overview
        total_courses = len(st.session_state.course_scores)
        courses_with_expert = sum(1 for score in st.session_state.course_scores.values() if score['percentage'] >= 90)
        courses_with_advanced = sum(1 for score in st.session_state.course_scores.values() if score['percentage'] >= 80)
        avg_score = sum(score['percentage'] for score in st.session_state.course_scores.values()) / total_courses
       
        # Overview metrics with enhanced styling
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            ("📚 Courses Attempted", total_courses, col1),
            ("🏆 Expert Level", courses_with_expert, col2),
            ("🌟 Advanced Level", courses_with_advanced, col3),
            ("📈 Average Score", f"{avg_score:.1f}%", col4)
        ]
        
        for title, value, col in metrics_data:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: #6c5ce7; margin: 0 0 0.5rem 0;">{title}</h4>
                    <h2 style="color: #2d3436; margin: 0; font-size: 2rem;">{value}</h2>
                </div>
                """, unsafe_allow_html=True)
       
        st.markdown("#### Detailed Course Performance:")
       
        # Display each course result with enhanced styling
        for course_name, score_data in st.session_state.course_scores.items():
            # Enhanced level colors with gradients
            level_gradients = {
                'Expert': 'linear-gradient(135deg, #00b894 0%, #00cec9 100%)',
                'Advanced': 'linear-gradient(135deg, #0984e3 0%, #74b9ff 100%)',  
                'Intermediate': 'linear-gradient(135deg, #fdcb6e 0%, #f39c12 100%)',
                'Developing': 'linear-gradient(135deg, #fd79a8 0%, #e84393 100%)',
                'Beginning': 'linear-gradient(135deg, #636e72 0%, #2d3436 100%)',
                'Beginner': 'linear-gradient(135deg, #636e72 0%, #2d3436 100%)'
            }
            
            level_gradient = level_gradients.get(score_data['level'], level_gradients['Beginning'])
            
            with st.expander(f"{score_data['level_emoji']} {course_name} - {score_data['level']} Level ({score_data['percentage']:.1f}%)", expanded=False):
                # Enhanced level badge
                st.markdown(f"""
                <div class="level-badge" style="background: {level_gradient};">
                    {score_data['level_emoji']} {score_data['level'].upper()} LEVEL - {score_data['percentage']:.1f}%
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
               
                with col1:
                    st.markdown(f"""
                    <div class="course-card">
                        <p><strong>📊 Score:</strong> {score_data['score']}/{score_data['total']} ({score_data['percentage']:.1f}%)</p>
                        <p><strong>🎯 Performance Level:</strong> {score_data['level_emoji']} <strong>{score_data['level']}</strong></p>
                        <p><strong>🔄 Attempts:</strong> {score_data['attempts']}</p>
                        <p><strong>📅 Last Attempt:</strong> {score_data['date']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Performance status with enhanced styling
                    if score_data['percentage'] >= 90:
                        st.success("🏆 Expert Performance - Outstanding mastery of the subject!")
                    elif score_data['percentage'] >= 80:
                        st.success("🌟 Advanced Performance - Excellent understanding and application!")
                    elif score_data['percentage'] >= 70:
                        st.info("📈 Intermediate Performance - Good grasp of key concepts!")
                    elif score_data['percentage'] >= 60:
                        st.info("✅ Developing Performance - Building solid foundations!")
                    else:
                        st.info("📚 Beginning Level - Great start on your learning journey!")
               
                with col2:
                    # Enhanced progress visualization
                    progress = min(score_data['percentage'] / 100, 1.0)
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem;">
                        <div style="background: linear-gradient(135deg, #ddd6fe 0%, #e0e7ff 100%); 
                                   border-radius: 20px; padding: 0.5rem; margin-bottom: 1rem;">
                            <div style="background: {level_gradient}; 
                                       width: {progress * 100}%; 
                                       height: 20px; 
                                       border-radius: 15px; 
                                       transition: all 0.3s ease;
                                       box-shadow: 0 2px 10px rgba(108, 92, 231, 0.3);"></div>
                        </div>
                        <h4 style="color: #6c5ce7; margin: 0;">Level: {score_data['level']}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success("🔓 **Accessible**")
                   
                # Additional insights with enhanced styling
                if score_data['attempts'] > 1:
                    st.markdown("""
                    <div class="achievement-item" style="border-left-color: #fd79a8;">
                        💪 <strong>Persistent Learner</strong> - Multiple attempts show dedication to reaching higher levels!
                    </div>
                    """, unsafe_allow_html=True)
                
                # Level progression guidance
                if score_data['percentage'] < 90:
                    if score_data['percentage'] >= 80:
                        points_needed = (90 - score_data['percentage']) * score_data['total'] / 100
                        st.info(f"💡 To reach Expert level, aim for {points_needed:.0f} more points on your next attempt!")
                    elif score_data['percentage'] < 80:
                        points_needed = (80 - score_data['percentage']) * score_data['total'] / 100
                        st.info(f"💡 To reach Advanced level, aim for {points_needed:.0f} more points on your next attempt!")
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
                   padding: 2rem; border-radius: 15px; text-align: center;">
            <h4>🎯 No quiz results available yet.</h4>
            <p>All courses are accessible - start your learning journey!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show available courses
        if st.session_state.unlocked_courses:
            st.markdown("#### Your Accessible Courses:")
            course_cols = st.columns(3)
            for idx, course_name in enumerate(st.session_state.unlocked_courses):
                with course_cols[idx % 3]:
                    if course_name in COURSES:
                        st.markdown(f"""
                        <div class="course-card" style="text-align: center;">
                            <h4>{COURSES[course_name]['icon']} {course_name}</h4>
                            <p style="color: #00b894;">🔓 Ready to start</p>
                        </div>
                        """, unsafe_allow_html=True)
   
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
   
    # Enhanced Learning Progress Summary
    if 'course_scores' in st.session_state and st.session_state.course_scores:
        st.markdown("### 📈 Learning Progress Summary")
        
        # Calculate progress metrics
        total_possible_points = sum(score['total'] for score in st.session_state.course_scores.values())
        total_earned_points = sum(score['score'] for score in st.session_state.course_scores.values())
        overall_progress = (total_earned_points / total_possible_points) * 100 if total_possible_points > 0 else 0
        
        # Level distribution
        level_counts = {}
        for score_data in st.session_state.course_scores.values():
            level = score_data['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        st.markdown(f"""
        <div class="progress-summary-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                <div style="text-align: center;">
                    <h3 style="color: #6c5ce7; margin-bottom: 1rem;">Overall Progress</h3>
                    <h2 style="color: #2d3436; font-size: 3rem; margin: 0;">{overall_progress:.1f}%</h2>
                    <p style="color: #636e72;">Total Points: {total_earned_points}/{total_possible_points}</p>
                </div>
                <div>
                    <h4 style="color: #6c5ce7; margin-bottom: 1rem;">🏆 Achievement Levels:</h4>
        """, unsafe_allow_html=True)
        
        # Level distribution with enhanced styling
        level_order = {
            'Expert': 5, 'Advanced': 4, 'Intermediate': 3, 
            'Developing': 2, 'Beginning': 1, 'Beginner': 1
        }
        
        sorted_levels = sorted(level_counts.items(), key=lambda x: level_order.get(x[0], 0), reverse=True)
        
        level_content = ""
        for level, count in sorted_levels:
            level_emoji = {
                'Expert': '🏆', 'Advanced': '🌟', 'Intermediate': '📈', 
                'Developing': '✅', 'Beginning': '📚', 'Beginner': '📚'
            }.get(level, '📚')
            level_content += f'<div class="achievement-item">{level_emoji} <strong>{level}:</strong> {count} course{"s" if count != 1 else ""}</div>'
        
        st.markdown(level_content + "</div></div>", unsafe_allow_html=True)
        
        # Enhanced progress bar
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ddd6fe 0%, #e0e7ff 100%); 
                   border-radius: 25px; padding: 0.5rem; margin: 1rem 0;">
            <div style="background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%); 
                       width: {overall_progress}%; 
                       height: 25px; 
                       border-radius: 20px; 
                       transition: all 0.8s ease;
                       box-shadow: 0 3px 15px rgba(108, 92, 231, 0.4);"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if overall_progress >= 80:
            st.success("🎯 Excellent overall progress! You're mastering the material at a high level!")
        elif overall_progress >= 60:
            st.info("📚 Good progress! Keep up the consistent learning to reach higher levels!")
        else:
            st.info("🌱 You're building a strong foundation! Every step counts toward higher achievement levels!")
   
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
   
    # Enhanced action buttons
    col1, col2, col3, col4 = st.columns(4)
   
    button_configs = [
        ("🏠 Back to Home", "home_from_profile", 'home', col1),
        ("📚 View Courses", "courses_from_profile", 'courses', col2),
        ("📝 Retake Assessment", "retake_assessment", 'assessment', col3),
        ("🔄 Reset Progress", "reset_progress", None, col4)
    ]
    
    for button_text, key, page, col in button_configs:
        with col:
            if key == "reset_progress":
                if st.button(button_text, key=key):
                    if st.checkbox("I understand this will clear all my progress", key="confirm_reset"):
                        st.session_state.course_scores = {}
                        st.success("Progress reset successfully!")
                        st.rerun()
            else:
                if st.button(button_text, key=key):
                    st.session_state.current_page = page
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    
# Updated quiz completion function
def complete_quiz(course_name, score, total_questions):
    """Complete quiz and record results - course access maintained regardless of performance"""
    
    # Record the results
    level, percentage = record_quiz_results(course_name, score, total_questions)
    
    # Show results with encouraging message
    st.balloons()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🎯 Quiz Results for {course_name}")
        st.markdown(f"**Score:** {score}/{total_questions} ({percentage:.1f}%)")
        st.markdown(f"**Level:** {level}")
        
        if percentage >= 90:
            st.success("🏆 Outstanding! Expert level performance!")
        elif percentage >= 80:
            st.success("🌟 Excellent! Advanced understanding!")
        elif percentage >= 70:
            st.info("📈 Good job! Solid intermediate knowledge!")
        elif percentage >= 60:
            st.info("✅ Nice work! You're developing well!")
        else:
            st.info("📚 Great start! Keep practicing and learning!")
    
    with col2:
        st.markdown("### 🔓 Course Access")
        st.success(f"{course_name} remains fully accessible!")
        st.info("💡 You can retake quizzes anytime to improve your level!")
        
        if st.button("🔄 Retake Quiz", key=f"retake_{course_name}"):
            # Reset to quiz page for this course
            st.rerun()
        
        if st.button("📚 Continue Learning", key=f"continue_{course_name}"):
            st.session_state.current_page = 'courses'
            st.rerun()
            
def get_fallback_course_questions(course_name: str) -> List[Dict]:
    """Fallback questions for courses when GROQ is not available"""
    
    fallback_questions = {
        "Cybersecurity": [
            {
                "question": "What is the primary purpose of a firewall in network security?",
                "options": ["Store passwords securely", "Filter and monitor network traffic", "Encrypt email messages", "Backup system files"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "Which encryption standard is currently recommended for securing sensitive data?",
                "options": ["DES", "MD5", "AES-256", "SHA-1"],
                "correct": 2,
                "difficulty": "medium"
            },
            {
                "question": "What characterizes a zero-day vulnerability?",
                "options": ["A vulnerability that has been patched", "A vulnerability unknown to security vendors", "A vulnerability that occurs daily", "A vulnerability in zero-cost software"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "What does HTTPS provide that HTTP does not?",
                "options": ["Faster loading times", "Better search engine ranking", "Encrypted data transmission", "Reduced server load"],
                "correct": 2,
                "difficulty": "easy"
            },
            {
                "question": "In penetration testing, what is social engineering primarily used for?",
                "options": ["Testing network speed", "Manipulating people to reveal information", "Analyzing code vulnerabilities", "Monitoring system performance"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What is the primary difference between symmetric and asymmetric encryption?",
                "options": ["Speed of encryption", "Use of same vs different keys for encryption/decryption", "Level of security provided", "Type of data that can be encrypted"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "What does SQL injection attack target?",
                "options": ["Network protocols", "Database queries", "Email systems", "File systems"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What is multi-factor authentication (MFA)?",
                "options": ["Using multiple passwords", "Authentication using multiple methods", "Having multiple user accounts", "Multiple security questions"],
                "correct": 1,
                "difficulty": "easy"
            }
        ],
        "Statistics": [
            {
                "question": "What does the mean represent in a dataset?",
                "options": ["The middle value when data is ordered", "The most frequently occurring value", "The arithmetic average of all values", "The difference between highest and lowest values"],
                "correct": 2,
                "difficulty": "easy"
            },
            {
                "question": "What does a p-value less than 0.05 typically indicate in hypothesis testing?",
                "options": ["The null hypothesis is true", "The result is statistically significant", "There is no relationship between variables", "The sample size is too small"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "In a normal distribution, what percentage of data falls within two standard deviations of the mean?",
                "options": ["68%", "95%", "99%", "50%"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "What is the purpose of standard deviation?",
                "options": ["To find the average value", "To measure the spread of data", "To identify the median", "To count the number of observations"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is the difference between correlation and causation?",
                "options": ["There is no difference", "Correlation implies causation", "Correlation shows relationship, causation shows cause-effect", "Causation is weaker than correlation"],
                "correct": 2,
                "difficulty": "medium"
            },
            {
                "question": "What is a Type II error in hypothesis testing?",
                "options": ["Rejecting a true null hypothesis", "Accepting a false null hypothesis", "Using the wrong test statistic", "Having insufficient sample size"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "What is the mode of a dataset?",
                "options": ["The average value", "The middle value", "The most frequently occurring value", "The range of values"],
                "correct": 2,
                "difficulty": "easy"
            },
            {
                "question": "What is a confidence interval?",
                "options": ["A range of values likely to contain the population parameter", "The probability of making an error", "The correlation between variables", "The sample size needed"],
                "correct": 0,
                "difficulty": "medium"
            }
        ],
        "Deep Learning": [
            {
                "question": "What is the primary function of an activation function in a neural network?",
                "options": ["To initialize weights", "To introduce non-linearity", "To prevent overfitting", "To normalize inputs"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is the vanishing gradient problem in deep learning?",
                "options": ["Gradients become too large", "Gradients become too small in deeper layers", "Learning rate is too high", "Network architecture is too simple"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "Which technique is most effective for preventing overfitting in deep networks?",
                "options": ["Increasing learning rate", "Adding more layers", "Dropout regularization", "Reducing batch size"],
                "correct": 2,
                "difficulty": "hard"
            },
            {
                "question": "What does CNN stand for in deep learning?",
                "options": ["Convolutional Neural Network", "Computational Neural Network", "Complex Neural Network", "Cascading Neural Network"],
                "correct": 0,
                "difficulty": "easy"
            },
            {
                "question": "What is backpropagation used for in neural networks?",
                "options": ["Forward pass computation", "Weight initialization", "Gradient computation and weight updates", "Activation function selection"],
                "correct": 2,
                "difficulty": "medium"
            },
            {
                "question": "What is the key innovation of transformer architecture?",
                "options": ["Convolutional layers", "Recurrent connections", "Self-attention mechanism", "Pooling operations"],
                "correct": 2,
                "difficulty": "hard"
            },
            {
                "question": "What is a tensor in deep learning?",
                "options": ["A type of neural network", "A multi-dimensional array", "An activation function", "A loss function"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is transfer learning?",
                "options": ["Moving data between systems", "Using pre-trained models for new tasks", "Converting between model formats", "Transferring weights manually"],
                "correct": 1,
                "difficulty": "medium"
            }
        ],
        "SQL": [
            {
                "question": "What does SQL stand for?",
                "options": ["Structured Query Language", "Simple Query Language", "Standard Query Language", "Sequential Query Language"],
                "correct": 0,
                "difficulty": "easy"
            },
            {
                "question": "Which SQL clause is used to filter rows based on a condition?",
                "options": ["ORDER BY", "GROUP BY", "WHERE", "HAVING"],
                "correct": 2,
                "difficulty": "medium"
            },
            {
                "question": "What is the difference between INNER JOIN and LEFT JOIN?",
                "options": ["No difference", "LEFT JOIN returns all rows from left table", "INNER JOIN is faster", "LEFT JOIN only works with primary keys"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "Which command is used to add new data to a table?",
                "options": ["ADD", "INSERT", "UPDATE", "CREATE"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is a primary key in a database table?",
                "options": ["The first column", "A unique identifier for each row", "The most important column", "A column with the most data"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "Which SQL function would you use to find the second highest salary from a table?",
                "options": ["MAX(salary) - 1", "SELECT salary ORDER BY salary DESC LIMIT 1,1", "MIN(MAX(salary))", "SECOND_MAX(salary)"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "What is normalization in database design?",
                "options": ["Making data normal", "Organizing data to reduce redundancy", "Sorting data alphabetically", "Converting data types"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "Which SQL command removes all data from a table?",
                "options": ["DELETE", "TRUNCATE", "DROP", "REMOVE"],
                "correct": 1,
                "difficulty": "easy"
            }
        ],
        "Python Programming": [
            {
                "question": "What is the correct way to define a function in Python?",
                "options": ["function myFunc():", "def myFunc():", "define myFunc():", "func myFunc():"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is list comprehension in Python?",
                "options": ["A way to compress lists", "A concise way to create lists", "A method to sort lists", "A technique to merge lists"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What is the Global Interpreter Lock (GIL) in Python?",
                "options": ["A security feature", "A mechanism that prevents true multithreading", "A memory management tool", "A debugging utility"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "Which data type is mutable in Python?",
                "options": ["String", "Tuple", "List", "Integer"],
                "correct": 2,
                "difficulty": "easy"
            },
            {
                "question": "What does the '*args' parameter do in a Python function?",
                "options": ["Multiplies arguments", "Accepts variable number of arguments", "Creates argument arrays", "Validates arguments"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What is a decorator in Python?",
                "options": ["A design pattern", "A function that modifies another function", "A data structure", "A loop construct"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "What is the difference between '==' and 'is' in Python?",
                "options": ["No difference", "'==' checks value, 'is' checks identity", "'is' is faster", "'==' works with strings only"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "How do you create a virtual environment in Python?",
                "options": ["python -m venv myenv", "create venv myenv", "python venv myenv", "virtualenv create myenv"],
                "correct": 0,
                "difficulty": "easy"
            }
        ],
        "Data Science": [
            {
                "question": "What is the first step in the data science process?",
                "options": ["Data modeling", "Data collection and understanding", "Data visualization", "Algorithm selection"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is feature engineering in data science?",
                "options": ["Building software features", "Creating new variables from existing data", "Engineering team management", "Database design"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What is the curse of dimensionality?",
                "options": ["Too many data points", "Performance degradation with high-dimensional data", "Lack of storage space", "Slow processing speed"],
                "correct": 1,
                "difficulty": "hard"
            },
            {
                "question": "Which Python library is most commonly used for data manipulation?",
                "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is cross-validation used for in machine learning?",
                "options": ["Data cleaning", "Model evaluation and selection", "Feature selection", "Data visualization"],
                "correct": 1,
                "difficulty": "medium"
            },
            {
                "question": "What is the difference between supervised and unsupervised learning?",
                "options": ["Supervised uses labeled data, unsupervised doesn't", "Supervised is faster", "No significant difference", "Supervised requires more data"],
                "correct": 0,
                "difficulty": "hard"
            },
            {
                "question": "What does EDA stand for in data science?",
                "options": ["Enhanced Data Analysis", "Exploratory Data Analysis", "External Data Access", "Efficient Data Algorithms"],
                "correct": 1,
                "difficulty": "easy"
            },
            {
                "question": "What is A/B testing used for?",
                "options": ["Testing two different algorithms", "Comparing two versions to determine which performs better", "Testing database connections", "Validating data quality"],
                "correct": 1,
                "difficulty": "medium"
            }
        ]
    }
    
    # Return questions for the specific course or empty list if not found
    return fallback_questions.get(course_name, [])



def determine_learning_style(answers: List[str], questions: List[Dict]) -> Dict[str, str]:
    """Determine learning style based on answers using ILS methodology"""
    
    # Count responses for each dimension
    dimension_counts = {
        "active_reflective": {"A": 0, "B": 0},
        "sensing_intuitive": {"A": 0, "B": 0},
        "visual_verbal": {"A": 0, "B": 0},
        "sequential_global": {"A": 0, "B": 0}
    }
    
    # Count answers for each dimension
    for i, answer in enumerate(answers):
        if i < len(questions):
            dimension = questions[i]["dimension"]
            dimension_counts[dimension][answer] += 1
    
    # Determine dominant style for each dimension
    styles = {}
    style_names = {
        "active_reflective": {"A": "Active", "B": "Reflective"},
        "sensing_intuitive": {"A": "Sensing", "B": "Intuitive"},
        "visual_verbal": {"A": "Visual", "B": "Verbal"},
        "sequential_global": {"A": "Sequential", "B": "Global"}
    }
    
    for dimension, counts in dimension_counts.items():
        if counts["A"] > counts["B"]:
            styles[dimension] = style_names[dimension]["A"]
        elif counts["B"] > counts["A"]:
            styles[dimension] = style_names[dimension]["B"]
        else:
            # Tie - default to first option
            styles[dimension] = style_names[dimension]["A"]
    
    return styles


def get_learning_style_summary(styles: Dict[str, str] = None) -> str:
    """
    Generate an enhanced, styled summary of the user's learning style based on Felder-Soloman ILS
    """
    if styles:
        # If styles dictionary is provided directly, use it
        learning_profile = {
            'processing': styles['active_reflective'],
            'perception': styles['sensing_intuitive'],
            'input': styles['visual_verbal'],
            'understanding': styles['sequential_global']
        }
    elif 'learning_style_summary' in st.session_state:
        return st.session_state.learning_style_summary
    elif 'learning_style_responses' in st.session_state and 'learning_style_questions' in st.session_state:
        
        responses = st.session_state.learning_style_responses
        questions = st.session_state.learning_style_questions
        
        # Initialize dimension scores
        dimension_scores = {
            'active_reflective': {'A': 0, 'B': 0},  # A=Active, B=Reflective
            'sensing_intuitive': {'A': 0, 'B': 0},  # A=Sensing, B=Intuitive
            'visual_verbal': {'A': 0, 'B': 0},      # A=Visual, B=Verbal
            'sequential_global': {'A': 0, 'B': 0}   # A=Sequential, B=Global
        }
        
        # Count responses for each dimension
        for i, response in enumerate(responses):
            if i < len(questions):
                dimension = questions[i]['dimension']
                if response in dimension_scores:
                    dimension_scores[dimension][response] += 1
        
        # Determine dominant learning style for each dimension
        learning_profile = {}
        
        # Active vs Reflective
        if dimension_scores['active_reflective']['A'] >= dimension_scores['active_reflective']['B']:
            learning_profile['processing'] = 'Active'
        else:
            learning_profile['processing'] = 'Reflective'
        
        # Sensing vs Intuitive
        if dimension_scores['sensing_intuitive']['A'] >= dimension_scores['sensing_intuitive']['B']:
            learning_profile['perception'] = 'Sensing'
        else:
            learning_profile['perception'] = 'Intuitive'
        
        # Visual vs Verbal
        if dimension_scores['visual_verbal']['A'] >= dimension_scores['visual_verbal']['B']:
            learning_profile['input'] = 'Visual'
        else:
            learning_profile['input'] = 'Verbal'
        
        # Sequential vs Global
        if dimension_scores['sequential_global']['A'] >= dimension_scores['sequential_global']['B']:
            learning_profile['understanding'] = 'Sequential'
        else:
            learning_profile['understanding'] = 'Global'
    else:
        return """
        <div style='
            text-align: center; 
            padding: 0; 
            margin: 20px 0;
            position: relative;
        '>
            <div style='
                display: inline-block;
                position: relative;
                padding: 0;
                margin-bottom: 12px;
            '>
                <h3 style='
                    margin: 0; 
                    font-size: 1.8em;
                    font-weight: 600;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    position: relative;
                    display: inline-block;
                    text-shadow: none;
                '>🧠 Learning Style Assessment</h3>
                
                <div style='
                    position: absolute;
                    bottom: -4px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 60%;
                    height: 3px;
                    background: linear-gradient(90deg, transparent 0%, #667eea 20%, #764ba2 80%, transparent 100%);
                    border-radius: 2px;
                    opacity: 0.6;
                '></div>
            </div>
            
            <p style='
                margin: 0; 
                opacity: 0.8;
                color: #555;
                font-size: 1.1em;
                font-weight: 400;
                max-width: 400px;
                margin: 0 auto;
                line-height: 1.4;
            '>Take the assessment to discover your personalized learning profile!</p>
        </div>
        """
    
    # Create enhanced styled summary
    style_emoji = get_style_emoji(learning_profile)
    style_colors = get_style_colors(learning_profile)
    
    summary = f"""
    <div style='background: linear-gradient(135deg, {style_colors['primary']} 0%, {style_colors['secondary']} 100%); 
                padding: 25px; border-radius: 20px; color: white; margin: 15px 0; box-shadow: 0 8px 25px rgba(0,0,0,0.2);'>
        
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='margin: 0; font-size: 1.8em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                {style_emoji} Your Learning Style Profile
            </h2>
            <div style='background: rgba(255,255,255,0.2); padding: 10px; border-radius: 25px; 
                        margin: 15px auto; display: inline-block; backdrop-filter: blur(10px);'>
                <strong style='font-size: 1.3em; letter-spacing: 2px;'>
                    {learning_profile['processing'][:3].upper()}-{learning_profile['perception'][:3].upper()}-{learning_profile['input'][:3].upper()}-{learning_profile['understanding'][:3].upper()}
                </strong>
            </div>
        </div>
        
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 25px;'>
            
            <div style='background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);'>
                <h4 style='margin: 0 0 10px 0; color: #FFE066; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
                    🔄 Processing: {learning_profile['processing']} Learner
                </h4>
                <p style='margin: 0; line-height: 1.6; opacity: 0.95;'>
                    {get_processing_description(learning_profile['processing'])}
                </p>
            </div>
            
            <div style='background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);'>
                <h4 style='margin: 0 0 10px 0; color: #66D9EF; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
                    🎯 Perception: {learning_profile['perception']} Learner
                </h4>
                <p style='margin: 0; line-height: 1.6; opacity: 0.95;'>
                    {get_perception_description(learning_profile['perception'])}
                </p>
            </div>
            
            <div style='background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);'>
                <h4 style='margin: 0 0 10px 0; color: #A6E22E; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
                    📡 Input: {learning_profile['input']} Learner
                </h4>
                <p style='margin: 0; line-height: 1.6; opacity: 0.95;'>
                    {get_input_description(learning_profile['input'])}
                </p>
            </div>
            
            <div style='background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);'>
                <h4 style='margin: 0 0 10px 0; color: #F92672; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
                    🧩 Understanding: {learning_profile['understanding']} Learner
                </h4>
                <p style='margin: 0; line-height: 1.6; opacity: 0.95;'>
                    {get_understanding_description(learning_profile['understanding'])}
                </p>
            </div>
            
        </div>
        
        <div style='background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; 
                    margin-top: 25px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);'>
            <h4 style='margin: 0 0 20px 0; color: #FFE066; text-align: center; font-size: 1.3em; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
                📚 Your Personalized Study Toolkit
            </h4>
            <div style='line-height: 1.8; opacity: 0.95;'>
                {get_study_recommendations_styled(learning_profile)}
            </div>
        </div>
        
    </div>
    """
    
    # Cache the summary if using session state
    if not styles:
        st.session_state.learning_style_summary = summary
    
    return summary


def get_style_emoji(profile: Dict[str, str]) -> str:
    """Get appropriate emoji based on learning profile"""
    emoji_map = {
        'Active': '⚡', 'Reflective': '🤔',
        'Sensing': '🔍', 'Intuitive': '💡',
        'Visual': '👁️', 'Verbal': '📝',
        'Sequential': '📊', 'Global': '🌐'
    }
    
    emojis = [emoji_map.get(style, '🧠') for style in profile.values()]
    return ' '.join(emojis[:2])  # Use first two emojis


def get_style_colors(profile: Dict[str, str]) -> Dict[str, str]:
    """Get gradient colors based on learning profile combination"""
    color_combinations = {
        ('Active', 'Sensing'): {
            'primary': '#FF6B6B', 
            'secondary': '#FF8E53'
        },
        ('Active', 'Intuitive'): {
            'primary': '#4ECDC4', 
            'secondary': '#44A08D'
        },
        ('Reflective', 'Sensing'): {
            'primary': '#667eea', 
            'secondary': '#764ba2'
        },
        ('Reflective', 'Intuitive'): {
            'primary': '#f093fb', 
            'secondary': '#f5576c'
        },
        ('Visual', 'Sequential'): {
            'primary': '#43e97b', 
            'secondary': '#38f9d7'
        },
        ('Visual', 'Global'): {
            'primary': '#fa709a', 
            'secondary': '#fee140'
        },
        ('Verbal', 'Sequential'): {
            'primary': '#a8edea', 
            'secondary': '#fed6e3'
        },
        ('Verbal', 'Global'): {
            'primary': '#d299c2', 
            'secondary': '#fef9d7'
        },
    }
    
    # Try to match primary combinations first
    key1 = (profile['processing'], profile['perception'])
    key2 = (profile['input'], profile['understanding'])
    
    if key1 in color_combinations:
        return color_combinations[key1]
    elif key2 in color_combinations:
        return color_combinations[key2]
    else:
        # Default gradient
        return {'primary': '#667eea', 'secondary': '#764ba2'}


def get_study_recommendations_styled(profile: Dict[str, str]) -> str:
    """Generate styled study recommendations"""
    recommendations = []
    
    # Processing recommendations
    if profile['processing'] == 'Active':
        recommendations.extend([
            "🤝 Form study groups and discuss concepts with peers",
            "🔄 Use flashcards and quiz yourself frequently", 
            "🛠️ Apply concepts through hands-on practice and projects"
        ])
    else:
        recommendations.extend([
            "🧘 Schedule quiet study time for deep reflection",
            "📝 Take detailed notes and create personal summaries",
            "⏰ Review material before joining group discussions"
        ])
    
    # Perception recommendations
    if profile['perception'] == 'Sensing':
        recommendations.extend([
            "🌍 Focus on real-world applications and concrete examples",
            "📚 Use detailed case studies and practical scenarios",
            "🔧 Break complex theories into step-by-step procedures"
        ])
    else:
        recommendations.extend([
            "🔗 Explore connections between different concepts",
            "🎯 Look for patterns and underlying principles",
            "🔍 Consider multiple perspectives and theoretical frameworks"
        ])
    
    # Input recommendations
    if profile['input'] == 'Visual':
        recommendations.extend([
            "🗺️ Create mind maps, diagrams, and flowcharts",
            "🎨 Use color coding and visual organizers",
            "📺 Watch educational videos and visual demonstrations"
        ])
    else:
        recommendations.extend([
            "🔊 Read materials aloud or use text-to-speech",
            "💬 Participate in discussions and verbal explanations",
            "📖 Write comprehensive notes and detailed summaries"
        ])
    
    # Understanding recommendations
    if profile['understanding'] == 'Sequential':
        recommendations.extend([
            "📋 Follow structured learning paths and curricula",
            "⚡ Master each concept before advancing to the next",
            "📅 Use detailed study schedules and organized plans"
        ])
    else:
        recommendations.extend([
            "🎯 Start with overviews and big-picture concepts",
            "🧩 Connect new information to existing knowledge",
            "⏳ Allow time for sudden insights - don't rush understanding"
        ])
    
    # Format recommendations with enhanced styling
    formatted_recs = []
    for i, rec in enumerate(recommendations):
        if i < 6:  # Limit to 6 most relevant recommendations
            styled_rec = f"""
            <div style='
                margin: 18px 0; 
                padding: 24px 28px; 
                background: linear-gradient(135deg, 
                    rgba(147, 112, 219, 0.08) 0%, 
                    rgba(138, 43, 226, 0.06) 25%,
                    rgba(123, 104, 238, 0.05) 50%,
                    rgba(106, 90, 205, 0.04) 75%,
                    rgba(72, 61, 139, 0.03) 100%
                );
                border: 1px solid rgba(147, 112, 219, 0.15);
                border-radius: 16px;
                border-left: 5px solid #9370DB;
                backdrop-filter: blur(20px);
                box-shadow: 
                    0 8px 32px rgba(106, 90, 205, 0.12),
                    0 4px 16px rgba(147, 112, 219, 0.08),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                font-size: 16px;
                line-height: 1.6;
                color: #2d1b69;
                position: relative;
                overflow: hidden;
                transform: translateY(0);
            '>
                <div style='
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, 
                        #9370DB 0%, 
                        #BA55D3 25%, 
                        #8A2BE2 50%, 
                        #7B68EE 75%, 
                        #6A5ACD 100%
                    );
                    opacity: 0.8;
                '></div>
                
                <div style='
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 100px;
                    height: 100px;
                    background: radial-gradient(circle, rgba(186, 85, 211, 0.1) 0%, transparent 70%);
                    border-radius: 50%;
                '></div>
                
                <div style='
                    display: flex;
                    align-items: flex-start;
                    gap: 16px;
                    font-weight: 500;
                    position: relative;
                    z-index: 2;
                '>
                    <div style='
                        background: linear-gradient(135deg, rgba(147, 112, 219, 0.15) 0%, rgba(138, 43, 226, 0.1) 100%);
                        padding: 8px;
                        border-radius: 12px;
                        border: 1px solid rgba(147, 112, 219, 0.2);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-width: 44px;
                        height: 44px;
                        box-shadow: 0 4px 12px rgba(106, 90, 205, 0.15);
                    '>
                        <span style='
                            font-size: 22px;
                            filter: drop-shadow(0 2px 4px rgba(106, 90, 205, 0.3));
                        '>{rec.split(' ', 1)[0]}</span>
                    </div>
                    <div style='
                        flex: 1;
                        padding-top: 4px;
                    '>
                        <span style='
                            color: #483d8b;
                            font-weight: 500;
                            font-size: 16px;
                            text-shadow: 0 1px 2px rgba(147, 112, 219, 0.1);
                            line-height: 1.5;
                        '>{' '.join(rec.split(' ')[1:])}</span>
                    </div>
                </div>
                
                <div style='
                    position: absolute;
                    bottom: 0;
                    left: 5px;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, 
                        #9370DB 0%, 
                        rgba(147, 112, 219, 0.4) 30%, 
                        rgba(147, 112, 219, 0.1) 70%, 
                        transparent 100%
                    );
                    border-radius: 0 0 16px 0;
                '></div>
                
                <div style='
                    position: absolute;
                    top: 50%;
                    left: -20px;
                    width: 40px;
                    height: 1px;
                    background: linear-gradient(90deg, transparent 0%, rgba(186, 85, 211, 0.4) 100%);
                    transform: translateY(-50%) rotate(45deg);
                '></div>
            </div>
            """
            formatted_recs.append(styled_rec.strip())
    
    return "".join(formatted_recs)

def get_processing_description(style):
    """Get description for processing dimension"""
    if style == 'Active':
        return "🔄 You learn by **doing and discussing**. You prefer group work, hands-on activities, and explaining concepts to others."
    else:
        return "🤔 You learn by **thinking and reflecting**. You prefer to process information quietly before discussing and need time to consider new concepts."


def get_perception_description(style):
    """Get description for perception dimension"""
    if style == 'Sensing':
        return "🔍 You prefer **concrete, practical information**. You like facts, data, real-world examples, and step-by-step procedures."
    else:
        return "💡 You prefer **abstract concepts and theories**. You enjoy exploring possibilities, meanings, and relationships between ideas."


def get_input_description(style):
    """Get description for input dimension"""
    if style == 'Visual':
        return "👁️ You learn best through **visual presentations**. Diagrams, charts, pictures, and demonstrations help you understand concepts."
    else:
        return "📝 You learn best through **written and spoken explanations**. You prefer detailed text, discussions, and verbal instructions."


def get_understanding_description(style):
    """Get description for understanding dimension"""
    if style == 'Sequential':
        return "📊 You learn in **logical, linear steps**. You prefer information presented in a clear, ordered sequence with each step building on the previous."
    else:
        return "🌐 You learn by seeing the **big picture first**. You prefer to understand the overall concept before focusing on details and can make sudden leaps in understanding."



def display_assessment():
    """Display learning style assessment with enhanced styling"""
    
    # Enhanced CSS styling for assessment
    st.markdown("""
    <style>
    .assessment-container {
        background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(108, 92, 231, 0.12);
        margin-bottom: 2rem;
        min-height: 60vh;
    }
    
    .assessment-title {
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2.5rem;
        text-shadow: 0 2px 4px rgba(108, 92, 231, 0.1);
    }
    
    .progress-container {
        background: linear-gradient(135deg, #e8f2ff 0%, #f3f0ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(108, 92, 231, 0.15);
        box-shadow: 0 8px 20px rgba(108, 92, 231, 0.08);
    }
    
    .progress-text {
        color: #6c5ce7;
        font-weight: 600;
        font-size: 1.2rem;
        margin-top: 1rem;
    }
    
    .enhanced-progress-bar {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3f0ff 100%);
        height: 12px;
        border-radius: 25px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(108, 92, 231, 0.1);
        margin-bottom: 1rem;
    }
    
    .progress-fill {
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
        height: 100%;
        border-radius: 25px;
        transition: width 0.8s ease;
        box-shadow: 0 2px 8px rgba(108, 92, 231, 0.4);
        position: relative;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.3), 
            transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .question-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(108, 92, 231, 0.15);
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .question-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
    }
    
    .question-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(108, 92, 231, 0.15);
    }
    
    .question-card h3 {
        color: #2d3436;
        font-size: 1.4rem;
        line-height: 1.6;
        margin: 0;
        font-weight: 600;
    }
    
    .radio-options {
        margin-top: 2rem;
    }
    
    .stRadio > div {
        background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(108, 92, 231, 0.1);
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.05);
    }
    
    .nav-button {
        background: linear-gradient(135deg, #6c5ce7 0%, #74b9ff 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
        min-width: 200px;
    }
    
    .nav-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(108, 92, 231, 0.4);
        background: linear-gradient(135deg, #5a4fcf 0%, #5fa8e6 100%);
    }
    
    .completion-card {
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 50%, #74b9ff 100%);
        color: white;
        padding: 3rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(108, 92, 231, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .completion-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
        pointer-events: none;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .completion-card h2, .completion-card h3, .completion-card h4 {
        position: relative;
        z-index: 2;
    }
    
    .completion-card h2 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .completion-card h3 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .completion-card h4 {
        font-size: 1.3rem;
        font-weight: 400;
        margin-bottom: 1rem;
        opacity: 0.8;
    }
    
    .breakdown-section {
        background: linear-gradient(135deg, #fdfdff 0%, #f0f4ff 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(108, 92, 231, 0.1);
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.08);
    }
    
    .dimension-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border-left: 4px solid;
        border-image: linear-gradient(135deg, #6c5ce7, #74b9ff) 1;
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.08);
        transition: all 0.3s ease;
    }
    
    .dimension-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.12);
    }
    
    .dimension-title {
        color: #6c5ce7;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .dimension-style {
        color: #2d3436;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .dimension-description {
        color: #636e72;
        font-style: italic;
        line-height: 1.5;
    }
    
    .recommendations-section {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f2ff 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(108, 92, 231, 0.15);
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.1);
    }
    
    .recommendation-item {
        background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 3px solid #74b9ff;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.08);
        transition: all 0.3s ease;
    }
    
    .recommendation-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(108, 92, 231, 0.12);
        border-left-color: #6c5ce7;
    }
    
    .back-button {
        background: linear-gradient(135deg, #636e72 0%, #2d3436 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(45, 52, 54, 0.2);
    }
    
    .back-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(45, 52, 54, 0.3);
        background: linear-gradient(135deg, #5a6268 0%, #212529 100%);
    }
    
    .section-title {
        color: #6c5ce7;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="assessment-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="assessment-title">🧠 Learning Style Assessment</h2>', unsafe_allow_html=True)
    
    # Initialize or get questions
    if st.session_state.learning_style_questions is None:
        st.session_state.learning_style_questions = generate_learning_style_questions_with_groq()
    
    questions = st.session_state.learning_style_questions
    
    if 'assessment_answers' not in st.session_state:
        st.session_state.assessment_answers = []
        st.session_state.current_question = 0
    
    current_q = st.session_state.current_question
    
    if current_q < len(questions):
        question_data = questions[current_q]
        
        # Enhanced progress bar
        progress = (current_q + 1) / len(questions)
        
        st.markdown(f"""
        <div class="progress-container">
            <div class="enhanced-progress-bar">
                <div class="progress-fill" style="width: {progress * 100}%;"></div>
            </div>
            <div class="progress-text">Question {current_q + 1} of {len(questions)}</div>
            <p style="color: #636e72; margin-top: 0.5rem;">
                {int(progress * 100)}% Complete • {len(questions) - current_q - 1} questions remaining
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced question display
        st.markdown(f"""
        <div class="question-card">
            <h3>💭 {question_data['question']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced answer options with custom styling
        st.markdown('<div class="radio-options">', unsafe_allow_html=True)
        
        answer = st.radio(
            "Choose the option that best describes you:",
            options=list(question_data['options'].keys()),
            format_func=lambda x: f"{x}. {question_data['options'][x]}",
            key=f"q_{current_q}"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced navigation with better centering
        st.markdown('<div style="text-align: center; margin-top: 3rem;">', unsafe_allow_html=True)
        
        if st.button("Next Question ➡️", key="next_question", help="Continue to the next question"):
            st.session_state.assessment_answers.append(answer)
            st.session_state.current_question += 1
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Enhanced assessment complete section
        learning_styles = determine_learning_style(st.session_state.assessment_answers, questions)
        st.session_state.learning_style = learning_styles
        
        # Create profile dictionary
        profile = {
            'processing': learning_styles.get('active_reflective', 'Active'),
            'perception': learning_styles.get('sensing_intuitive', 'Sensing'),
            'input': learning_styles.get('visual_verbal', 'Visual'),
            'understanding': learning_styles.get('sequential_global', 'Sequential')
        }
        
        recommendations = get_study_recommendations(profile)
        style_summary = f"{profile['processing']} | {profile['perception']} | {profile['input']} | {profile['understanding']}"
        
        # Enhanced completion announcement
        st.markdown(f"""
        <div class="completion-card">
            <h2>🎉 Assessment Complete!</h2>
            <h3>🧠 Your Learning Style Profile</h3>
            <h4>{style_summary}</h4>
            <p style="position: relative; z-index: 2; font-size: 1.1rem; opacity: 0.9;">
                Based on your responses, we've identified your preferred learning approaches across four key dimensions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced detailed breakdown
        st.markdown('<h3 class="section-title">📊 Your Learning Style Breakdown</h3>', unsafe_allow_html=True)
        
        dimension_descriptions = {
            "processing": {
                "Active": "You learn by trying things out and discussing with others",
                "Reflective": "You learn by thinking things through quietly first"
            },
            "perception": {
                "Sensing": "You prefer concrete, practical information and real-world examples",
                "Intuitive": "You prefer abstract concepts, theories, and innovative ideas"
            },
            "input": {
                "Visual": "You learn best from visual representations like diagrams and charts",
                "Verbal": "You learn best from written and spoken explanations"
            },
            "understanding": {
                "Sequential": "You learn in logical, step-by-step progressions",
                "Global": "You learn by seeing the big picture and making connections"
            }
        }
        
        dimension_icons = {
            "processing": "🔄",
            "perception": "👁️", 
            "input": "📥",
            "understanding": "🧩"
        }
        
        st.markdown('<div class="breakdown-section">', unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, (dimension, style) in enumerate(profile.items()):
            with cols[idx % 2]:
                dimension_name = dimension.replace('_', ' ').title()
                icon = dimension_icons.get(dimension, "📋")
                
                st.markdown(f"""
                <div class="dimension-card">
                    <div class="dimension-title">{icon} {dimension_name}</div>
                    <div class="dimension-style">{style}</div>
                    <div class="dimension-description">{dimension_descriptions[dimension][style]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced personalized recommendations
        st.markdown('<h3 class="section-title">📝 Your Personalized Study Recommendations</h3>', unsafe_allow_html=True)
        
        st.markdown('<div class="recommendations-section">', unsafe_allow_html=True)
        
        recommendation_lines = [line.strip() for line in recommendations.split('\n') if line.strip()]
        
        # Display recommendations in a more organized way
        cols = st.columns(2)
        for idx, rec in enumerate(recommendation_lines):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="recommendation-item">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced action buttons
        st.markdown('<div style="text-align: center; margin-top: 3rem;">', unsafe_allow_html=True)
        
        if st.button("🚀 Explore Courses", key="explore_courses", help="Start exploring courses tailored to your learning style"):
            st.session_state.current_page = 'courses'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced back button with better positioning
    st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
    
    if st.button("🏠 Back to Home", key="back_home_assessment", help="Return to the home page"):
        st.session_state.current_page = 'home'
        if 'assessment_answers' in st.session_state:
            del st.session_state.assessment_answers
            del st.session_state.current_question
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    
def get_study_recommendations(profile):
    """Generate personalized study recommendations based on learning profile (legacy function)"""
    recommendations = []
    
    # Processing recommendations
    if profile['processing'] == 'Active':
        recommendations.append("• Form study groups and discuss concepts with peers")
        recommendations.append("• Use flashcards and quiz yourself frequently")
        recommendations.append("• Apply concepts through practice problems and projects")
    else:
        recommendations.append("• Schedule quiet study time to reflect on material")
        recommendations.append("• Take notes and summarize key concepts in your own words")
        recommendations.append("• Review material before participating in discussions")
    
    # Perception recommendations
    if profile['perception'] == 'Sensing':
        recommendations.append("• Focus on real-world applications and concrete examples")
        recommendations.append("• Use case studies and practical scenarios")
        recommendations.append("• Break down complex theories into step-by-step procedures")
    else:
        recommendations.append("• Explore connections between different concepts")
        recommendations.append("• Look for patterns and underlying principles")
        recommendations.append("• Consider multiple perspectives and theoretical frameworks")
    
    # Input recommendations
    if profile['input'] == 'Visual':
        recommendations.append("• Create mind maps, diagrams, and flowcharts")
        recommendations.append("• Use color coding and visual organizers")
        recommendations.append("• Watch educational videos and visual demonstrations")
    else:
        recommendations.append("• Read materials aloud or use text-to-speech")
        recommendations.append("• Participate in discussions and verbal explanations")
        recommendations.append("• Write detailed notes and summaries")
    
    # Understanding recommendations
    if profile['understanding'] == 'Sequential':
        recommendations.append("• Follow structured learning paths and curricula")
        recommendations.append("• Master each concept before moving to the next")
        recommendations.append("• Use detailed outlines and organized study schedules")
    else:
        recommendations.append("• Start with overviews and general concepts")
        recommendations.append("• Connect new information to what you already know")
        recommendations.append("• Allow time for concepts to 'click' - don't rush the process")
    
    return "\n".join(recommendations)


    
def display_courses():
    """Display course dashboard"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="title-header">📚 Course Dashboard</h2>', unsafe_allow_html=True)
   
    if not st.session_state.learning_style:
        st.warning("Please complete the learning style assessment first!")
        if st.button("Take Assessment"):
            st.session_state.current_page = 'assessment'
            st.rerun()
        return
   
    # Create profile dictionary for the new function
    profile = {
        'processing': st.session_state.learning_style.get('active_reflective', 'Active'),
        'perception': st.session_state.learning_style.get('sensing_intuitive', 'Sensing'),
        'input': st.session_state.learning_style.get('visual_verbal', 'Visual'),
        'understanding': st.session_state.learning_style.get('sequential_global', 'Sequential')
    }
    
    recommendations = get_study_recommendations(profile)
    style_summary = f"{profile['processing']} | {profile['perception']} | {profile['input']} | {profile['understanding']}"
    
    # Display learning style info
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h4>🧠 Your Learning Style: {style_summary}</h4>
        <p>Your personalized learning approach based on your assessment results.</p>
    </div>
    """, unsafe_allow_html=True)
   
    st.markdown("---")
   
    # Display courses in a grid
    cols = st.columns(2)
    for idx, (course_name, course_info) in enumerate(COURSES.items()):
        with cols[idx % 2]:
            is_unlocked = course_name in st.session_state.unlocked_courses
            card_class = "unlocked" if is_unlocked else "locked"
           
            st.markdown(f"""
            <div class="course-card {card_class}" style="background: {course_info['color']};">
                <h3>{course_info['icon']} {course_name}</h3>
                <p>{course_info['description']}</p>
                <p><strong>Status:</strong> {'🔓 Unlocked' if is_unlocked else '🔒 Locked'}</p>
            </div>
            """, unsafe_allow_html=True)
           
            if is_unlocked:
                if st.button(f"📖 Study {course_name}", key=f"study_{course_name}"):
                    st.success(f"Welcome to {course_name}! Course content would be displayed here.")
                    # Show personalized study tip based on their specific learning style dimensions
                    recommendation_lines = recommendations.split('\n')
                    primary_tip = recommendation_lines[0].replace('• ', '') if recommendation_lines else "Study consistently and practice regularly."
                    st.info(f"💡 **Personalized Learning Tip**: {primary_tip}")
            else:
                if st.button(f"🎯 Take Assessment for {course_name}", key=f"assess_{course_name}"):
                    st.session_state.current_page = 'quiz'
                    st.session_state.current_course = course_name
                    st.rerun()
   
    # Learning style specific tips section
    st.markdown("---")
    with st.expander(f"💡 Personalized Learning Tips for Your {style_summary} Profile"):
       
        # Show breakdown by dimension
        dimension_names = {
            'processing': 'Active/Reflective',
            'perception': 'Sensing/Intuitive', 
            'input': 'Visual/Verbal',
            'understanding': 'Sequential/Global'
        }
        
        for dimension, style in profile.items():
            display_name = dimension_names.get(dimension, dimension.title())
            st.markdown(f"**{display_name}:** {style}")
       
        st.markdown("---")
       
        st.markdown("**Your Personalized Study Recommendations:**")
        # Display all recommendations from the function
        recommendation_lines = recommendations.split('\n')
        for rec in recommendation_lines:
            if rec.strip():  # Skip empty lines
                st.markdown(rec)
   
    # Back to home button
    if st.button("🏠 Back to Home", key="back_home_courses"):
        st.session_state.current_page = 'home'
        st.rerun()
   
    st.markdown('</div>', unsafe_allow_html=True)
    
    
def display_home_page():
    """Display the main home page"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="title-header">🧠 Learning Profiling AI Agent</h1>', unsafe_allow_html=True)
   
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3>Welcome to Your Personalized Learning Journey!</h3>
            <p>Discover your unique learning style and unlock customized courses designed just for you.</p>
        </div>
        """, unsafe_allow_html=True)
       
        if st.button("🎯 Start Learning Style Assessment", key="start_assessment"):
            st.session_state.current_page = 'assessment'
            st.rerun()
       
        if st.session_state.learning_style:
            # Create profile dictionary for the function (same as in display_courses)
            profile = {
                'processing': st.session_state.learning_style.get('active_reflective', 'Active'),
                'perception': st.session_state.learning_style.get('sensing_intuitive', 'Sensing'),
                'input': st.session_state.learning_style.get('visual_verbal', 'Visual'),
                'understanding': st.session_state.learning_style.get('sequential_global', 'Sequential')
            }
            
            recommendations = get_study_recommendations(profile)
            
            # Create style summary using the profile values
            style_summary = f"{profile['processing']} | {profile['perception']} | {profile['input']} | {profile['understanding']}"
           
            st.markdown(f"""
            <div class="success-message">
                <h4>🎯 Your Learning Style: {style_summary}</h4>
                <p>Ready to explore courses tailored to your learning preferences!</p>
            </div>
            """, unsafe_allow_html=True)
           
            if st.button("📚 View Course Dashboard", key="view_courses"):
                st.session_state.current_page = 'courses'
                st.rerun()
        else:
            st.warning("Complete the assessment above to get personalized recommendations!")
   
    st.markdown('</div>', unsafe_allow_html=True)
    
# Main logic - determines which page to show
if __name__ == "__main__":
    if st.session_state.current_page == 'home':
        display_home_page()
        
    elif st.session_state.current_page == 'profile':
        display_complete_profile()
    elif st.session_state.current_page == 'assessment':
        display_assessment()
    elif st.session_state.current_page == 'courses':
        display_courses()
    elif st.session_state.current_page == 'quiz':
        display_quiz()  # This was missing!
    else:
        # Fallback in case of invalid page state
        st.error("Invalid page state. Redirecting to home.")
        st.session_state.current_page = 'home'
        st.rerun()
