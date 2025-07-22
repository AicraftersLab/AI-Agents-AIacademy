import json
import os
import pickle
import traceback
import streamlit as st
from datetime import datetime

def save_state(key, value):
    """
    Save a value to the session state.
    
    Parameters:
    - key: The key to store the value under
    - value: The value to store
    """
    st.session_state[key] = value
    return True

def load_state(key, default=None):
    """
    Load a value from the session state.
    
    Parameters:
    - key: The key to load
    - default: Default value if the key doesn't exist
    
    Returns:
    - The stored value or the default
    """
    return st.session_state.get(key, default)

def format_time(seconds):
    """
    Format seconds into a readable time string.
    
    Parameters:
    - seconds: Number of seconds
    
    Returns:
    - Formatted string (e.g., "2h 30m" or "45s")
    """
    if seconds is None or seconds == 0:
        return "0s"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_week_range(date):
    """
    Get the start and end dates for the week containing the given date.
    
    Parameters:
    - date: The date to get the week range for
    
    Returns:
    - Tuple of (start_date, end_date)
    """
    start_date = date - timedelta(days=date.weekday())
    end_date = start_date + timedelta(days=6)
    return start_date, end_date

def date_range(start_date, end_date):
    """
    Generate a list of dates between start_date and end_date, inclusive.
    
    Parameters:
    - start_date: Starting date
    - end_date: Ending date
    
    Returns:
    - List of dates
    """
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates
