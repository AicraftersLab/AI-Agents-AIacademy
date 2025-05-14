import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

from user_tracking import get_user_activities, get_user_sessions
from engagement_model import calculate_engagement_score, predict_engagement_risk
from utils import save_state, load_state

def analyze_user_behavior(user_id, start_date=None, end_date=None):
    """
    Analyze user behavior to identify patterns, strengths, and areas for improvement.
    
    Parameters:
    - user_id: Identifier for the user
    - start_date: Starting date for the analysis
    - end_date: Ending date for the analysis
    
    Returns:
    - Dictionary with behavior analysis results
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)
    
    if end_date is None:
        end_date = datetime.now()
    
    # Get user activities and sessions
    activities = get_user_activities(user_id, start_date, end_date)
    sessions = get_user_sessions(user_id, start_date, end_date)
    
    # Initialize analysis results
    analysis = {
        'strengths': [],
        'weaknesses': [],
        'patterns': [],
        'preferences': {
            'favorite_content_types': [],
            'preferred_time': None,
            'longest_sessions': []
        }
    }
    
    # Default analysis for no data
    if activities.empty:
        analysis['weaknesses'].append("No recent activity detected.")
        return analysis
    
    # Analyze activity patterns
    
    # 1. Frequency of activities
    active_days = activities['timestamp'].dt.date.nunique()
    total_days = (end_date - start_date).days or 1  # Avoid division by zero
    activity_frequency = active_days / total_days
    
    if activity_frequency > 0.7:
        analysis['strengths'].append("Consistent activity across most days")
    elif activity_frequency > 0.4:
        analysis['patterns'].append("Moderate activity consistency")
    else:
        analysis['weaknesses'].append("Inconsistent learning activity")
    
    # 2. Favorite content types
    if 'activity_type' in activities.columns:
        activity_counts = activities['activity_type'].value_counts()
        if not activity_counts.empty:
            top_activities = activity_counts.nlargest(3)
            analysis['preferences']['favorite_content_types'] = top_activities.index.tolist()
            
            if top_activities.iloc[0] > activities.shape[0] * 0.6:
                analysis['patterns'].append(f"Strong preference for {top_activities.index[0]} activities")
    
    # 3. Time of day patterns
    if 'timestamp' in activities.columns:
        activities['hour'] = activities['timestamp'].dt.hour
        hour_counts = activities['hour'].value_counts()
        
        if not hour_counts.empty:
            peak_hour = hour_counts.idxmax()
            morning_hours = activities[activities['hour'].between(5, 11)].shape[0]
            afternoon_hours = activities[activities['hour'].between(12, 17)].shape[0]
            evening_hours = activities[activities['hour'].between(18, 23)].shape[0]
            night_hours = activities[activities['hour'].between(0, 4)].shape[0]
            
            max_period_count = max(morning_hours, afternoon_hours, evening_hours, night_hours)
            
            if morning_hours == max_period_count:
                analysis['preferences']['preferred_time'] = "morning"
            elif afternoon_hours == max_period_count:
                analysis['preferences']['preferred_time'] = "afternoon"
            elif evening_hours == max_period_count:
                analysis['preferences']['preferred_time'] = "evening"
            else:
                analysis['preferences']['preferred_time'] = "night"
            
            if hour_counts.iloc[0] > activities.shape[0] * 0.4:
                analysis['patterns'].append(f"Tends to study at specific hours (peak at {peak_hour}:00)")
    
    # 4. Session length analysis
    if not sessions.empty:
        avg_session_duration = sessions['duration'].mean()
        max_session_duration = sessions['duration'].max()
        
        # Get content from longest sessions
        if 'content_id' in activities.columns:
            longest_session = sessions.loc[sessions['duration'].idxmax()]
            session_start = longest_session['start_time']
            session_end = longest_session['end_time']
            
            session_activities = activities[
                (activities['timestamp'] >= session_start) & 
                (activities['timestamp'] <= session_end)
            ]
            
            if not session_activities.empty:
                content_in_longest = session_activities['content_id'].value_counts().nlargest(3)
                analysis['preferences']['longest_sessions'] = content_in_longest.index.tolist()
        
        if avg_session_duration > 1800:  # 30 minutes
            analysis['strengths'].append("Good concentration with long study sessions")
        elif avg_session_duration < 300:  # 5 minutes
            analysis['weaknesses'].append("Short attention span with brief sessions")
    
    # 5. Progress patterns
    # This would typically connect to a learning progress system
    # For now, we'll use activity frequency as a proxy
    
    recent_week = activities[activities['timestamp'] >= (end_date - timedelta(days=7))]
    previous_week = activities[
        (activities['timestamp'] >= (end_date - timedelta(days=14))) &
        (activities['timestamp'] < (end_date - timedelta(days=7)))
    ]
    
    if not recent_week.empty and not previous_week.empty:
        recent_count = len(recent_week)
        previous_count = len(previous_week)
        
        if recent_count > previous_count * 1.2:
            analysis['strengths'].append("Increasing engagement trend")
        elif previous_count > recent_count * 1.2:
            analysis['weaknesses'].append("Decreasing engagement trend")
    
    return analysis

def generate_motivation_message(user_id):
    """
    Generate a personalized motivation message for a user.
    
    Parameters:
    - user_id: Identifier for the user
    
    Returns:
    - Dictionary with message subject and content
    """
    # Analyze user behavior
    behavior = analyze_user_behavior(user_id)
    engagement_score = calculate_engagement_score(user_id)
    risk_score = predict_engagement_risk(user_id)
    
    # Message templates based on engagement level
    templates = {
        'high_engagement': [
            {
                'subject': "Keep up the great work!",
                'content': "You've been doing exceptionally well with your learning journey. Your consistency and dedication are truly impressive. Remember that continuous learning leads to mastery. What topic would you like to explore next?"
            },
            {
                'subject': "You're on fire! 🔥",
                'content': "Your recent learning performance has been outstanding! Your dedication is paying off, and we've noticed your consistent progress. Keep challenging yourself with new concepts to maintain this momentum."
            }
        ],
        'medium_engagement': [
            {
                'subject': "Building good momentum",
                'content': "You're making steady progress in your learning journey. With a bit more consistency, you could really accelerate your growth. Try setting a regular schedule to make learning a daily habit."
            },
            {
                'subject': "You're making progress!",
                'content': "We've noticed your engagement in the learning platform. You're on the right track! Consider exploring more diverse topics or spending just 10 more minutes per session to maximize your learning potential."
            }
        ],
        'low_engagement': [
            {
                'subject': "Let's get back on track",
                'content': "We've missed seeing you regularly in the learning platform. Learning is most effective when it's consistent. Even just 15 minutes a day can make a big difference. What topics would interest you most right now?"
            },
            {
                'subject': "Ready to continue your learning journey?",
                'content': "It's been a while since you've engaged deeply with the learning material. Everyone faces challenges sometimes. Let's start with something interesting and manageable to rebuild momentum. What would you like to revisit?"
            }
        ]
    }
    
    # Select message template based on engagement score
    if engagement_score > 70:
        template_list = templates['high_engagement']
        engagement_level = "high_engagement"
    elif engagement_score > 40:
        template_list = templates['medium_engagement']
        engagement_level = "medium_engagement"
    else:
        template_list = templates['low_engagement']
        engagement_level = "low_engagement"
    
    # Randomly select a template
    template = random.choice(template_list)
    message = {
        'subject': template['subject'],
        'content': template['content']
    }
    
    # Personalize message based on behavior analysis
    personalized_content = message['content']
    
    # Add strength-based encouragement
    if behavior['strengths'] and engagement_level != 'low_engagement':
        strength = random.choice(behavior['strengths'])
        personalized_content += f"\n\nOne thing that stands out is your {strength.lower()}. This is a valuable skill that will help you succeed."
    
    # Add suggestions based on weaknesses
    if behavior['weaknesses']:
        weakness = random.choice(behavior['weaknesses'])
        
        suggestions = {
            "Inconsistent learning activity": "Setting aside just 15 minutes at the same time each day can help build a consistent learning habit.",
            "Short attention span with brief sessions": "Try the Pomodoro technique: 25 minutes of focused learning followed by a 5-minute break.",
            "Decreasing engagement trend": "Mixing up your learning with different types of content might help rekindle your interest.",
            "No recent activity detected.": "Starting with a quick 10-minute session can help rebuild momentum. How about trying that today?"
        }
        
        for key in suggestions:
            if key.lower() in weakness.lower():
                personalized_content += f"\n\nA small suggestion: {suggestions[key]}"
                break
        else:
            personalized_content += f"\n\nA small suggestion: Consider focusing on improving your {weakness.lower()}."
    
    # Add time-based customization
    if behavior['preferences']['preferred_time']:
        preferred_time = behavior['preferences']['preferred_time']
        
        time_messages = {
            "morning": "I've noticed you often learn in the morning. That's a great habit as many studies show our minds are freshest early in the day!",
            "afternoon": "You seem to prefer afternoon learning sessions, which can be a great way to overcome the mid-day slump.",
            "evening": "Evening learning seems to work well for you. It's a great way to review and consolidate the day's experiences.",
            "night": "You often study at night. While this works for many, consider trying some shorter sessions earlier in the day if possible for variety."
        }
        
        personalized_content += f"\n\n{time_messages[preferred_time]}"
    
    # Add favorite content acknowledgment if available
    if behavior['preferences']['favorite_content_types']:
        favorite = behavior['preferences']['favorite_content_types'][0]
        personalized_content += f"\n\nYour interest in {favorite} activities shows your learning preferences. We'll keep that in mind for future recommendations."
    
    # Finalize message
    message['content'] = personalized_content
    
    return message

def get_recommendation(user_id):
    """
    Generate personalized learning recommendations for a user.
    
    Parameters:
    - user_id: Identifier for the user
    
    Returns:
    - List of recommendation dictionaries
    """
    # Analyze user behavior and engagement
    behavior = analyze_user_behavior(user_id)
    engagement_score = calculate_engagement_score(user_id)
    risk_score = predict_engagement_risk(user_id)
    
    # Base recommendations by engagement level
    base_recommendations = {
        'high_engagement': [
            {
                'title': "Challenge Yourself",
                'description': "You're performing well. Try more challenging content to maintain engagement.",
                'impact': "Prevents plateauing and maintains long-term interest",
                'implementation': "Suggest advanced content or projects that build on existing skills"
            },
            {
                'title': "Accountability Partner",
                'description': "Connect with another high-performing learner to maintain accountability.",
                'impact': "Creates positive social pressure and shared learning opportunities",
                'implementation': "Set up an optional buddy system with regular check-ins"
            },
            {
                'title': "Content Diversification",
                'description': "Explore new related topics to broaden knowledge base.",
                'impact': "Builds cognitive connections and prevents monotony",
                'implementation': "Suggest complementary topics that connect to current interests"
            }
        ],
        'medium_engagement': [
            {
                'title': "Goal Setting Intervention",
                'description': "Guide the user to set specific, achievable short-term goals.",
                'impact': "Provides clear direction and sense of accomplishment",
                'implementation': "Introduce a simple goal-setting template with weekly check-ins"
            },
            {
                'title': "Streak Incentive",
                'description': "Implement a streak counter to encourage consistent engagement.",
                'impact': "Builds habit formation through visible progress tracking",
                'implementation': "Show streak counter prominently and celebrate milestones"
            },
            {
                'title': "Micro-Learning Moments",
                'description': "Introduce 5-minute learning opportunities for busy days.",
                'impact': "Maintains connection even during time constraints",
                'implementation': "Create quick-consumption content specifically designed for brief sessions"
            }
        ],
        'low_engagement': [
            {
                'title': "Re-engagement Campaign",
                'description': "Send a personalized message highlighting past achievements.",
                'impact': "Reminds user of previous success and builds confidence",
                'implementation': "Send personalized email/notification citing specific past accomplishments"
            },
            {
                'title': "Interest Assessment",
                'description': "Ask about current interests to realign content recommendations.",
                'impact': "Addresses potential mismatch between content and interests",
                'implementation': "Short survey with immediate content recommendations based on responses"
            },
            {
                'title': "Decrease Difficulty",
                'description': "Temporarily reduce content difficulty to rebuild confidence.",
                'impact': "Creates quick wins to rebuild motivation and self-efficacy",
                'implementation': "Offer simpler content that guarantees success with gradual difficulty increase"
            }
        ]
    }
    
    # Determine engagement level
    if engagement_score > 70:
        level = 'high_engagement'
    elif engagement_score > 40:
        level = 'medium_engagement'
    else:
        level = 'low_engagement'
    
    # Start with base recommendations for this engagement level
    recommendations = base_recommendations[level].copy()
    
    # Personalize based on behavior analysis
    
    # 1. Address specific weaknesses
    if behavior['weaknesses']:
        for weakness in behavior['weaknesses']:
            if "inconsistent" in weakness.lower():
                recommendations.append({
                    'title': "Scheduled Learning Sessions",
                    'description': "Set up regular, calendar-blocked learning times.",
                    'impact': "Creates structure and habit formation",
                    'implementation': "Suggest optimal times based on past engagement patterns and send reminders"
                })
            elif "short attention" in weakness.lower():
                recommendations.append({
                    'title': "Focus Building Exercise",
                    'description': "Gradually increase session duration with focused activities.",
                    'impact': "Trains sustained attention over time",
                    'implementation': "Start with engaging 10-minute sessions, increasing by 5 minutes each week"
                })
            elif "decreasing" in weakness.lower():
                recommendations.append({
                    'title': "Content Refresh",
                    'description': "Introduce new, high-interest content types.",
                    'impact': "Reignites curiosity and renews interest",
                    'implementation': "Present completely different learning formats or topics connected to existing interests"
                })
    
    # 2. Leverage user preferences
    if behavior['preferences']['preferred_time']:
        preferred_time = behavior['preferences']['preferred_time']
        
        recommendations.append({
            'title': f"Optimize {preferred_time.capitalize()} Learning",
            'description': f"Schedule activities during the user's preferred {preferred_time} time slot.",
            'impact': "Works with natural rhythm and existing habits",
            'implementation': f"Send reminders and highlight new content during {preferred_time} hours"
        })
    
    # 3. Adapt to risk level
    if risk_score > 70:  # High risk of disengagement
        recommendations.append({
            'title': "Immediate Re-engagement",
            'description': "Direct outreach with personalized content suggestions.",
            'impact': "Provides immediate intervention before complete disengagement",
            'implementation': "Personal message from instructor/system with specific next steps and encouragement"
        })
        
        # Increase recommendation priority
        for rec in recommendations:
            if "Re-engagement" in rec['title']:
                recommendations.remove(rec)
                recommendations.insert(0, rec)
                break
    
    # Limit to 3 most relevant recommendations
    if len(recommendations) > 3:
        recommendations = recommendations[:3]
    
    return recommendations
