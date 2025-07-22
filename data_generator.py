import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
import json

from utils import save_state, load_state

def generate_user_id():
    """Generate a random user ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_content_id():
    """Generate a random content ID"""
    prefix = random.choice(['VID', 'QZ', 'TXT', 'INF', 'ASM'])
    return f"{prefix}-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def generate_timestamp(start_date, end_date):
    """Generate a random timestamp between start and end dates"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    
    # Add random hour
    random_hour = random.randint(8, 22)  # Assuming most learning happens between 8 AM and 10 PM
    random_date = random_date.replace(hour=random_hour, minute=random.randint(0, 59))
    
    return random_date

def generate_activity_type():
    """Generate a random activity type"""
    activity_types = [
        'video_watch', 
        'quiz_attempt', 
        'reading', 
        'exercise_completion', 
        'discussion_participation',
        'notes_creation',
        'review_session'
    ]
    
    weights = [0.3, 0.25, 0.2, 0.1, 0.05, 0.05, 0.05]  # More common activities have higher weights
    return random.choices(activity_types, weights=weights)[0]

def generate_duration(activity_type):
    """Generate a plausible duration for the activity type in seconds"""
    duration_ranges = {
        'video_watch': (120, 1200),  # 2-20 minutes
        'quiz_attempt': (60, 900),   # 1-15 minutes
        'reading': (300, 1800),      # 5-30 minutes
        'exercise_completion': (300, 1200),  # 5-20 minutes
        'discussion_participation': (60, 600),  # 1-10 minutes
        'notes_creation': (60, 900),  # 1-15 minutes
        'review_session': (300, 1800)  # 5-30 minutes
    }
    
    min_duration, max_duration = duration_ranges.get(activity_type, (60, 600))
    return random.randint(min_duration, max_duration)

def generate_user_pattern(user_id, start_date, end_date, engagement_level='medium'):
    """
    Generate activity data for a single user with a consistent pattern.
    
    Parameters:
    - user_id: User identifier
    - start_date: Starting date for data generation
    - end_date: Ending date for data generation
    - engagement_level: 'high', 'medium', or 'low'
    
    Returns:
    - List of activity dictionaries
    """
    activities = []
    
    # Parameters based on engagement level
    if engagement_level == 'high':
        sessions_per_week = random.randint(5, 7)
        activities_per_session = random.randint(4, 8)
        consistency = 0.9  # Probability of maintaining the pattern
    elif engagement_level == 'medium':
        sessions_per_week = random.randint(2, 4)
        activities_per_session = random.randint(2, 5)
        consistency = 0.7
    else:  # low
        sessions_per_week = random.randint(0, 2)
        activities_per_session = random.randint(1, 3)
        consistency = 0.5
    
    # Preferred days (for consistent pattern)
    days_of_week = list(range(7))  # 0 = Monday, 6 = Sunday
    preferred_days = random.sample(days_of_week, min(sessions_per_week, 7))
    
    # Preferred hours (for consistent pattern)
    if random.random() < 0.7:  # 70% chance of having a preferred time of day
        if random.random() < 0.4:
            preferred_hours = list(range(7, 12))  # Morning person
        elif random.random() < 0.7:
            preferred_hours = list(range(12, 18))  # Afternoon person
        else:
            preferred_hours = list(range(18, 23))  # Evening person
    else:
        preferred_hours = list(range(7, 23))  # No strong preference
    
    # Generate activities
    current_date = start_date
    while current_date <= end_date:
        # Check if this is a preferred day
        if current_date.weekday() in preferred_days:
            # Check consistency
            if random.random() <= consistency:
                # Generate a session for this day
                session_hour = random.choice(preferred_hours)
                session_time = current_date.replace(hour=session_hour, minute=random.randint(0, 59))
                
                # Generate activities for this session
                for _ in range(activities_per_session):
                    activity_type = generate_activity_type()
                    duration = generate_duration(activity_type)
                    content_id = generate_content_id()
                    
                    activity = {
                        'user_id': user_id,
                        'activity_type': activity_type,
                        'content_id': content_id,
                        'duration': duration,
                        'timestamp': session_time
                    }
                    
                    activities.append(activity)
                    
                    # Increment time for next activity in the session
                    session_time += timedelta(seconds=duration + random.randint(0, 300))  # Add some gap between activities
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return activities

def initialize_demo_data():
    """Initialize demo data for the application"""
    # Check if data already exists
    if load_state('activity_data') is not None:
        return  # Data already initialized
    
    # Set date range for data generation
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # Generate 60 days of data
    
    # Generate users with different engagement levels
    users = [
        # High engagement users
        {'id': 'USER01', 'level': 'high'},
        {'id': 'USER02', 'level': 'high'},
        {'id': 'USER03', 'level': 'high'},
        
        # Medium engagement users
        {'id': 'USER04', 'level': 'medium'},
        {'id': 'USER05', 'level': 'medium'},
        {'id': 'USER06', 'level': 'medium'},
        {'id': 'USER07', 'level': 'medium'},
        
        # Low engagement users
        {'id': 'USER08', 'level': 'low'},
        {'id': 'USER09', 'level': 'low'},
        {'id': 'USER10', 'level': 'low'}
    ]
    
    # Generate activities for each user
    all_activities = []
    for user in users:
        user_activities = generate_user_pattern(
            user_id=user['id'],
            start_date=start_date,
            end_date=end_date,
            engagement_level=user['level']
        )
        all_activities.extend(user_activities)
    
    # Save the generated data
    save_state('activity_data', all_activities)
    
    return True

def get_user_data():
    """Get all user activity data as a DataFrame"""
    activity_data = load_state('activity_data', default=[])
    
    if not activity_data:
        return pd.DataFrame(columns=['user_id', 'activity_type', 'content_id', 'duration', 'timestamp'])
    
    return pd.DataFrame(activity_data)
