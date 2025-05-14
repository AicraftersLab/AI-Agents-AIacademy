import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

from user_tracking import get_user_activities, get_all_user_activities, get_user_sessions
from utils import save_state, load_state

def calculate_engagement_score(user_id, start_date=None, end_date=None):
    """
    Calculate an engagement score for a user based on their activity patterns.
    
    Parameters:
    - user_id: Identifier for the user
    - start_date: Starting date for the analysis (default: 30 days ago)
    - end_date: Ending date for the analysis (default: now)
    
    Returns:
    - Engagement score (0-100)
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)
    
    if end_date is None:
        end_date = datetime.now()
    
    # Get user activities
    activities = get_user_activities(user_id, start_date, end_date)
    
    if activities.empty:
        return 0  # No activity means no engagement
    
    # Get user sessions
    sessions = get_user_sessions(user_id, start_date, end_date)
    
    # Calculate engagement metrics
    metrics = {}
    
    # 1. Activity frequency (activities per day)
    days_in_period = max(1, (end_date - start_date).days)
    metrics['activity_frequency'] = len(activities) / days_in_period
    
    # 2. Session frequency (sessions per day)
    metrics['session_frequency'] = len(sessions) / days_in_period
    
    # 3. Average session duration (in minutes)
    if not sessions.empty:
        metrics['avg_session_duration'] = sessions['duration'].mean() / 60
    else:
        metrics['avg_session_duration'] = 0
    
    # 4. Content diversity (unique content items)
    metrics['content_diversity'] = activities['content_id'].nunique()
    
    # 5. Activity type diversity (unique activity types)
    metrics['activity_diversity'] = activities['activity_type'].nunique()
    
    # 6. Recency (days since last activity, inversed)
    if not activities.empty:
        last_activity = activities['timestamp'].max()
        days_since = (end_date - last_activity).total_seconds() / (24 * 3600)
        metrics['recency'] = max(0, 1 - (days_since / 30))  # Decay over 30 days
    else:
        metrics['recency'] = 0
    
    # 7. Consistency (standard deviation of time between sessions, inversed)
    if len(sessions) > 1:
        session_gaps = []
        for i in range(1, len(sessions)):
            gap = (sessions.iloc[i]['start_time'] - sessions.iloc[i-1]['end_time']).total_seconds() / 3600
            session_gaps.append(gap)
        
        std_gap = np.std(session_gaps)
        metrics['consistency'] = 1 / (1 + std_gap)  # Inverse relationship with standard deviation
    else:
        metrics['consistency'] = 0
    
    # Calculate weighted engagement score
    weights = {
        'activity_frequency': 0.15,
        'session_frequency': 0.15,
        'avg_session_duration': 0.2,
        'content_diversity': 0.15,
        'activity_diversity': 0.1,
        'recency': 0.15,
        'consistency': 0.1
    }
    
    # Normalize metrics to 0-1 scale based on typical values
    normalizers = {
        'activity_frequency': 10,  # 10 activities per day is excellent
        'session_frequency': 3,    # 3 sessions per day is excellent
        'avg_session_duration': 30, # 30 minutes per session is excellent
        'content_diversity': 10,   # 10 unique content items is excellent
        'activity_diversity': 5,   # 5 different activity types is excellent
        'recency': 1,              # Already normalized
        'consistency': 1           # Already normalized
    }
    
    normalized_metrics = {}
    for key, value in metrics.items():
        normalized_metrics[key] = min(1, value / normalizers[key])
    
    # Calculate weighted score
    score = 0
    for key, weight in weights.items():
        score += normalized_metrics[key] * weight
    
    # Scale to 0-100
    score = score * 100
    
    return score

def predict_engagement_risk(user_id, prediction_window=7):
    """
    Predict the risk of a user disengaging in the next X days.
    
    Parameters:
    - user_id: Identifier for the user
    - prediction_window: Days ahead to predict disengagement
    
    Returns:
    - Risk score (0-100)
    """
    # Get historical engagement data
    now = datetime.now()
    past_30_days = now - timedelta(days=30)
    past_7_days = now - timedelta(days=7)
    
    # Calculate engagement scores for different time periods
    engagement_30d = calculate_engagement_score(user_id, past_30_days, now)
    engagement_7d = calculate_engagement_score(user_id, past_7_days, now)
    
    # Get user activities and sessions
    activities = get_user_activities(user_id, past_30_days, now)
    sessions = get_user_sessions(user_id, past_30_days, now)
    
    # Extract features
    features = {}
    
    # Engagement trends
    features['engagement_30d'] = engagement_30d
    features['engagement_7d'] = engagement_7d
    features['engagement_trend'] = engagement_7d - engagement_30d
    
    # Activity patterns
    if not activities.empty:
        features['total_activities'] = len(activities)
        features['unique_content'] = activities['content_id'].nunique()
        features['unique_activity_types'] = activities['activity_type'].nunique()
        
        # Recent activity
        last_week_activities = activities[activities['timestamp'] >= past_7_days]
        features['recent_activities'] = len(last_week_activities)
        
        # Last activity time
        last_activity = activities['timestamp'].max()
        features['days_since_last_activity'] = (now - last_activity).total_seconds() / (24 * 3600)
        
        # Time distribution
        activities['hour'] = activities['timestamp'].dt.hour
        peak_hours = activities['hour'].value_counts().nlargest(3).index.tolist()
        features['has_regular_schedule'] = len(peak_hours) <= 3 and activities['hour'].value_counts().iloc[0] > len(activities) * 0.3
    else:
        features['total_activities'] = 0
        features['unique_content'] = 0
        features['unique_activity_types'] = 0
        features['recent_activities'] = 0
        features['days_since_last_activity'] = 30  # Maximum value
        features['has_regular_schedule'] = False
    
    # Session patterns
    if not sessions.empty:
        features['total_sessions'] = len(sessions)
        features['avg_session_duration'] = sessions['duration'].mean()
        features['max_session_duration'] = sessions['duration'].max()
        
        # Session gap analysis
        if len(sessions) > 1:
            session_times = sorted(sessions['start_time'].tolist())
            gaps = []
            for i in range(1, len(session_times)):
                gap = (session_times[i] - session_times[i-1]).total_seconds() / 3600  # Hours
                gaps.append(gap)
            
            features['avg_session_gap'] = np.mean(gaps)
            features['max_session_gap'] = np.max(gaps)
            features['std_session_gap'] = np.std(gaps)
        else:
            features['avg_session_gap'] = 168  # 1 week in hours
            features['max_session_gap'] = 168
            features['std_session_gap'] = 0
    else:
        features['total_sessions'] = 0
        features['avg_session_duration'] = 0
        features['max_session_duration'] = 0
        features['avg_session_gap'] = 168  # 1 week in hours
        features['max_session_gap'] = 168
        features['std_session_gap'] = 0
    
    # Calculate risk score based on features
    # This is a simplified model - in a real system, this would use a trained ML model
    
    # Weights for features
    weights = {
        'engagement_30d': -0.2,  # Higher engagement = lower risk
        'engagement_trend': -0.3,  # Positive trend = lower risk
        'recent_activities': -0.15,  # More recent activities = lower risk
        'days_since_last_activity': 0.15,  # More days since activity = higher risk
        'avg_session_gap': 0.1,  # Larger gaps = higher risk
        'has_regular_schedule': -0.1  # Regular schedule = lower risk
    }
    
    # Normalize features
    normalizers = {
        'engagement_30d': 100,  # 0-100 scale
        'engagement_trend': 50,  # -50 to +50 scale
        'recent_activities': 20,  # 0-20 scale
        'days_since_last_activity': 7,  # 0-7 days scale
        'avg_session_gap': 48,  # 0-48 hours scale
        'has_regular_schedule': 1  # Boolean 0-1
    }
    
    # Calculate base risk (0-1 scale)
    base_risk = 0.5  # Start at 50%
    
    for feature, weight in weights.items():
        if feature == 'has_regular_schedule':
            normalized_value = 1 if features[feature] else 0
        else:
            normalized_value = min(1, features[feature] / normalizers[feature])
        
        base_risk += normalized_value * weight
    
    # Clamp risk to 0-1 range
    base_risk = max(0, min(1, base_risk))
    
    # Convert to 0-100 scale
    risk_score = base_risk * 100
    
    return risk_score

def get_engagement_metrics(start_date=None, end_date=None):
    """
    Calculate global engagement metrics for the dashboard.
    
    Parameters:
    - start_date: Starting date for the analysis
    - end_date: Ending date for the analysis
    
    Returns:
    - Dictionary with engagement metrics
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)
    
    if end_date is None:
        end_date = datetime.now()
    
    # Get all user activities
    activities = get_all_user_activities(start_date, end_date)
    
    # Default metrics for empty data
    if activities.empty:
        return {
            'avg_engagement_score': 0,
            'active_users': 0,
            'avg_session_duration': 0,
            'users_at_risk': 0,
            'engagement_trend': 0,
            'active_users_trend': 0,
            'duration_trend': 0,
            'at_risk_trend': 0
        }
    
    # Get unique users
    unique_users = activities['user_id'].unique()
    
    # Calculate metrics
    metrics = {}
    
    # 1. Average engagement score
    user_scores = []
    for user_id in unique_users:
        score = calculate_engagement_score(user_id, start_date, end_date)
        user_scores.append(score)
    
    metrics['avg_engagement_score'] = np.mean(user_scores) if user_scores else 0
    
    # 2. Active users
    metrics['active_users'] = len(unique_users)
    
    # 3. Average session duration
    session_durations = []
    for user_id in unique_users:
        sessions = get_user_sessions(user_id, start_date, end_date)
        if not sessions.empty:
            session_durations.extend(sessions['duration'].tolist())
    
    metrics['avg_session_duration'] = np.mean(session_durations) if session_durations else 0
    
    # 4. Users at risk (risk score > 70)
    users_at_risk = 0
    for user_id in unique_users:
        risk = predict_engagement_risk(user_id)
        if risk > 70:
            users_at_risk += 1
    
    metrics['users_at_risk'] = users_at_risk
    
    # Calculate trends (compare to previous period)
    previous_start = start_date - (end_date - start_date)
    previous_end = start_date
    
    # Get previous period activities
    prev_activities = get_all_user_activities(previous_start, previous_end)
    
    if not prev_activities.empty:
        # Previous period unique users
        prev_unique_users = prev_activities['user_id'].unique()
        
        # 1. Engagement score trend
        prev_user_scores = []
        for user_id in prev_unique_users:
            score = calculate_engagement_score(user_id, previous_start, previous_end)
            prev_user_scores.append(score)
        
        prev_avg_score = np.mean(prev_user_scores) if prev_user_scores else 0
        metrics['engagement_trend'] = metrics['avg_engagement_score'] - prev_avg_score
        
        # 2. Active users trend
        metrics['active_users_trend'] = len(unique_users) - len(prev_unique_users)
        
        # 3. Session duration trend
        prev_session_durations = []
        for user_id in prev_unique_users:
            sessions = get_user_sessions(user_id, previous_start, previous_end)
            if not sessions.empty:
                prev_session_durations.extend(sessions['duration'].tolist())
        
        prev_avg_duration = np.mean(prev_session_durations) if prev_session_durations else 0
        
        if prev_avg_duration > 0:
            metrics['duration_trend'] = ((metrics['avg_session_duration'] - prev_avg_duration) / prev_avg_duration) * 100
        else:
            metrics['duration_trend'] = 0
        
        # 4. At-risk users trend
        prev_users_at_risk = 0
        for user_id in prev_unique_users:
            risk = predict_engagement_risk(user_id)
            if risk > 70:
                prev_users_at_risk += 1
        
        metrics['at_risk_trend'] = users_at_risk - prev_users_at_risk
    else:
        # No previous data
        metrics['engagement_trend'] = 0
        metrics['active_users_trend'] = 0
        metrics['duration_trend'] = 0
        metrics['at_risk_trend'] = 0
    
    return metrics
