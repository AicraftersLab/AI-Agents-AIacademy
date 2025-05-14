import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

from utils import save_state, load_state

def log_user_activity(user_id, activity_type, content_id, duration, timestamp=None):
    """
    Log a user activity in the system.
    
    Parameters:
    - user_id: Identifier for the user
    - activity_type: Type of activity (e.g., quiz_attempt, video_watch, page_view)
    - content_id: Identifier for the content being interacted with
    - duration: Duration of the activity in seconds
    - timestamp: When the activity occurred (defaults to now)
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Load existing activity data
    activity_data = load_state('activity_data', default=[])
    
    # Create new activity record
    new_activity = {
        'user_id': user_id,
        'activity_type': activity_type,
        'content_id': content_id,
        'duration': duration,
        'timestamp': timestamp
    }
    
    # Add to activity data
    activity_data.append(new_activity)
    
    # Save updated activity data
    save_state('activity_data', activity_data)
    
    return True

def get_user_activities(user_id, start_date=None, end_date=None):
    """
    Get all activities for a specific user within a date range.
    
    Parameters:
    - user_id: Identifier for the user
    - start_date: Starting date for filtering activities
    - end_date: Ending date for filtering activities
    
    Returns:
    - DataFrame with user activities
    """
    # Load activity data
    activity_data = load_state('activity_data', default=[])
    
    # Convert to DataFrame
    if not activity_data:
        return pd.DataFrame(columns=['user_id', 'activity_type', 'content_id', 'duration', 'timestamp'])
    
    df = pd.DataFrame(activity_data)
    
    # Filter by user_id
    user_df = df[df['user_id'] == user_id].copy()
    
    # Filter by date range if provided
    if start_date:
        user_df = user_df[user_df['timestamp'] >= start_date]
    
    if end_date:
        user_df = user_df[user_df['timestamp'] <= end_date]
    
    return user_df

def get_user_sessions(user_id, start_date=None, end_date=None, session_timeout=30):
    """
    Group user activities into sessions based on time gaps.
    
    Parameters:
    - user_id: Identifier for the user
    - start_date: Starting date for filtering activities
    - end_date: Ending date for filtering activities
    - session_timeout: Minutes of inactivity to consider a new session
    
    Returns:
    - DataFrame with session data
    """
    # Get user activities
    activities = get_user_activities(user_id, start_date, end_date)
    
    if activities.empty:
        return pd.DataFrame(columns=['user_id', 'session_id', 'start_time', 'end_time', 'duration', 'activity_count'])
    
    # Sort by timestamp
    activities = activities.sort_values('timestamp')
    
    # Convert session_timeout to timedelta
    timeout = timedelta(minutes=session_timeout)
    
    # Initialize session tracking
    session_id = 0
    session_start = activities.iloc[0]['timestamp']
    last_time = session_start
    sessions = []
    activity_count = 1
    
    # Group activities into sessions
    for i in range(1, len(activities)):
        current_time = activities.iloc[i]['timestamp']
        
        # Check if this activity is part of the current session
        if current_time - last_time > timeout:
            # Save the completed session
            session_duration = (last_time - session_start).total_seconds()
            sessions.append({
                'user_id': user_id,
                'session_id': session_id,
                'start_time': session_start,
                'end_time': last_time,
                'duration': session_duration,
                'activity_count': activity_count
            })
            
            # Start a new session
            session_id += 1
            session_start = current_time
            activity_count = 1
        else:
            # Continue the current session
            activity_count += 1
        
        last_time = current_time
    
    # Add the last session
    session_duration = (last_time - session_start).total_seconds()
    sessions.append({
        'user_id': user_id,
        'session_id': session_id,
        'start_time': session_start,
        'end_time': last_time,
        'duration': session_duration,
        'activity_count': activity_count
    })
    
    return pd.DataFrame(sessions)

def get_all_user_activities(start_date=None, end_date=None):
    """
    Get activities for all users within a date range.
    
    Parameters:
    - start_date: Starting date for filtering activities
    - end_date: Ending date for filtering activities
    
    Returns:
    - DataFrame with all user activities
    """
    # Load activity data
    activity_data = load_state('activity_data', default=[])
    
    # Convert to DataFrame
    if not activity_data:
        return pd.DataFrame(columns=['user_id', 'activity_type', 'content_id', 'duration', 'timestamp'])
    
    df = pd.DataFrame(activity_data)
    
    # Filter by date range if provided
    if start_date:
        df = df[df['timestamp'] >= start_date]
    
    if end_date:
        df = df[df['timestamp'] <= end_date]
    
    return df

def get_daily_engagement(start_date, end_date):
    """
    Calculate daily average engagement scores for all users.
    
    Parameters:
    - start_date: Starting date for the analysis
    - end_date: Ending date for the analysis
    
    Returns:
    - DataFrame with daily engagement scores
    """
    from engagement_model import calculate_engagement_score
    
    # Get all user activities
    activities = get_all_user_activities(start_date, end_date)
    
    if activities.empty:
        # Return empty dataframe with date and engagement_score columns
        date_range = pd.date_range(start=start_date, end=end_date)
        return pd.DataFrame({
            'date': date_range,
            'engagement_score': [0] * len(date_range)
        })
    
    # Get unique dates in the data
    activities['date'] = activities['timestamp'].dt.date
    dates = sorted(activities['date'].unique())
    
    # Calculate daily engagement scores
    daily_scores = []
    for date in dates:
        # Get unique users active on this date
        users_on_date = activities[activities['date'] == date]['user_id'].unique()
        
        # Calculate engagement score for each user on this date
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        
        user_scores = []
        for user_id in users_on_date:
            score = calculate_engagement_score(user_id, day_start, day_end)
            user_scores.append(score)
        
        # Calculate average engagement score for the day
        avg_score = np.mean(user_scores) if user_scores else 0
        
        daily_scores.append({
            'date': date,
            'engagement_score': avg_score,
            'active_users': len(users_on_date)
        })
    
    return pd.DataFrame(daily_scores)
