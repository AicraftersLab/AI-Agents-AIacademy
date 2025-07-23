# Agent AI :Agent Social Learning Collaboratif
Agent Social Learning Collaboratif is an interactive web application designed to foster collaborative learning through social challenges, gamification, and community engagement. The platform enables users to participate in, create, and complete collaborative challenges, track their progress, and interact with a vibrant learning community. By leveraging personalized learner profiles and intelligent team formation, the system aims to enhance both individual and group learning experiences.

# Project Objectives
-  Promote Social Learning: Encourage users to learn through collaboration, discussion, and shared challenges.
-  Personalized Experience: Analyze user profiles to recommend suitable challenges and optimal team pairings.
-  Community Building: Provide a space for users to interact, comment, and support each other.
-  Scalability: Design a modular and extensible system that can accommodate new features and a growing user base.

# System Overview
The application is built using Streamlit for the frontend, providing an intuitive and interactive user interface. The backend logic manages challenge creation and participation, team formation, and feedback collection. The system uses session state to persist user and challenge data during interactions. Key features include:
- Profile Analysis: Generate learner profiles based on learning styles, personality types, and skills.
- Team Formation: Intelligent pairing and role assignment for optimal collaboration.
- Challenge Management: Create, join, and submit solutions for collaborative challenges.
- Community Features: Discussion forums.
  
# Technologies Used
Python 3
- Streamlit – Rapid web application framework for data apps.
- Google Gemini AI – AI-powered challenge generation and personalized feedback.
- Pandas – Data manipulation and analysis.
- Plotly – Interactive data visualization.
- NumPy – Numerical operations.
- Requests – HTTP requests for external data.
- Dataclasses & Enums – For structured data modeling.
- Other Libraries: hashlib, random, datetime, etc
# Configurer l’API Gemini
Crée un fichier .env à la racine du projet :
GEMINI_API_KEY=cle_api_ici




graph TD
    A[User] -->|Interacts with| B[User Interface: Streamlit Web App]
    
    %% User Interface
    B -->|Displays| C[Dashboard]
    B -->|Enables| D[Challenge Creation & Submission]
    B -->|Manages| E[Team Management]
    B -->|Hosts| F[Community Forum]
    B -->|Visualizes| G[Plotly Visualizations]
    
    %% Core System
    B -->|Processes| H[Core System]
    H -->|Analyzes| I[Profile Analysis]
    H -->|Forms| J[Team Formation]
    H -->|Manages| K[Challenge Management]
    H -->|Collects| L[Feedback Collection]
    H -->|Stores| M[Session State]
    
    %% Data Processing
    I -->|Uses| N[Pandas & NumPy]
    J -->|Uses| N
    K -->|Uses| N
    L -->|Uses| N
    
    %% External Services
    H -->|Integrates| O[Google Gemini AI]
    O -->|Generates| P[AI Challenges]
    O -->|Provides| Q[Personalized Feedback]
    H -->|Fetches| R[Requests: HTTP Client]
    
    %% Configuration & Data
    H -->|Reads| S[.env File: GEMINI_API_KEY]
    M -->|Persists| T[User Profiles]
    M -->|Persists| U[Challenge Data]
    M -->|Persists| V[Team Data]
    
    %% Flow Annotations
    A -->|Access| B
    B -->|Sends Data| H
    H -->|Processes & Returns| B
    O -->|API Calls| H




