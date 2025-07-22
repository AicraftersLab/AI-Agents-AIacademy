import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

from user_tracking import log_user_activity, get_user_sessions, get_daily_engagement
from engagement_model import predict_engagement_risk, get_engagement_metrics, calculate_engagement_score
from motivation_engine import generate_motivation_message, get_recommendation
from data_generator import initialize_demo_data, get_user_data
from utils import save_state, load_state, format_time

# Page configuration
st.set_page_config(
    page_title="Adaptive Learning - Motivation & Engagement Agent",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.selected_user = None
    st.session_state.start_date = datetime.now() - timedelta(days=30)
    st.session_state.end_date = datetime.now()
    st.session_state.show_recommendations = False
    st.session_state.show_message = False
    st.session_state.current_tab = "dashboard"
    # Initialize demo data
    initialize_demo_data()

# Main layout
st.title("📚 Adaptive Learning - Motivation & Engagement Agent")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    
    # Navigation tabs
    tab_options = ["Dashboard", "User Analysis", "Intervention System", "Settings"]
    selected_tab = st.radio("Select Section:", tab_options)
    st.session_state.current_tab = selected_tab.lower()
    
    st.markdown("---")
    
    # User selection
    users_data = get_user_data()
    user_list = users_data['user_id'].unique().tolist()
    selected_user = st.selectbox("Select User:", user_list)
    st.session_state.selected_user = selected_user
    
    # Date range selection
    st.subheader("Date Range")
    start_date = st.date_input("Start Date", value=st.session_state.start_date)
    end_date = st.date_input("End Date", value=st.session_state.end_date)
    
    if start_date and end_date:
        st.session_state.start_date = datetime.combine(start_date, datetime.min.time())
        st.session_state.end_date = datetime.combine(end_date, datetime.min.time())
    
    # Log this session
    log_user_activity(
        user_id="admin",
        activity_type="dashboard_view",
        content_id="dashboard",
        duration=0,
        timestamp=datetime.now()
    )

# Main content area
if st.session_state.current_tab == "dashboard":
    # Dashboard overview tab
    st.header("📊 Engagement Dashboard")
    
    # Key metrics in a row
    col1, col2, col3, col4 = st.columns(4)
    
    # Get engagement metrics for all users
    metrics = get_engagement_metrics(start_date=st.session_state.start_date, end_date=st.session_state.end_date)
    
    with col1:
        st.metric(
            label="Average Engagement Score", 
            value=f"{metrics['avg_engagement_score']:.1f}%",
            delta=f"{metrics['engagement_trend']:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Active Users", 
            value=metrics['active_users'],
            delta=metrics['active_users_trend']
        )
    
    with col3:
        st.metric(
            label="Avg. Session Duration", 
            value=format_time(metrics['avg_session_duration']),
            delta=f"{metrics['duration_trend']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Users at Risk", 
            value=metrics['users_at_risk'],
            delta=metrics['at_risk_trend'] * -1,  # Inverse delta for risk (negative is good)
            delta_color="inverse"
        )
    
    # Engagement trend chart
    st.subheader("Engagement Trends")
    daily_engagement = get_daily_engagement(st.session_state.start_date, st.session_state.end_date)
    
    fig = px.line(
        daily_engagement, 
        x='date', 
        y='engagement_score', 
        title='Daily Average Engagement Score',
        labels={'date': 'Date', 'engagement_score': 'Engagement Score (%)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Two columns for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        # User activity distribution
        st.subheader("Activity Distribution")
        activity_data = users_data.groupby('activity_type').size().reset_index(name='count')
        
        fig = px.pie(
            activity_data, 
            values='count', 
            names='activity_type', 
            title='User Activity Distribution',
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Engagement risk categories
        st.subheader("Engagement Risk Categories")
        
        # Get risk categories for all users
        users_data['risk_score'] = users_data.apply(
            lambda x: predict_engagement_risk(x['user_id']), axis=1
        )
        
        risk_categories = {
            'High Risk (>70%)': len(users_data[users_data['risk_score'] > 70]),
            'Medium Risk (40-70%)': len(users_data[(users_data['risk_score'] > 40) & (users_data['risk_score'] <= 70)]),
            'Low Risk (<40%)': len(users_data[users_data['risk_score'] <= 40])
        }
        
        risk_df = pd.DataFrame({
            'Category': list(risk_categories.keys()),
            'Count': list(risk_categories.values())
        })
        
        fig = px.bar(
            risk_df, 
            x='Category', 
            y='Count', 
            title='Users by Risk Category',
            color='Category',
            color_discrete_map={
                'High Risk (>70%)': 'red',
                'Medium Risk (40-70%)': 'orange',
                'Low Risk (<40%)': 'green'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.current_tab == "user analysis":
    # User Analysis Tab
    st.header(f"👤 User Analysis: User {st.session_state.selected_user}")
    
    # Get user-specific data
    user_data = users_data[users_data['user_id'] == st.session_state.selected_user]
    
    if len(user_data) > 0:
        # Calculate key metrics for the selected user
        engagement_score = calculate_engagement_score(st.session_state.selected_user)
        risk_score = predict_engagement_risk(st.session_state.selected_user)
        user_sessions = get_user_sessions(st.session_state.selected_user)
        avg_session_duration = user_sessions['duration'].mean() if len(user_sessions) > 0 else 0
        
        # User metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Engagement Score", 
                value=f"{engagement_score:.1f}%"
            )
        
        with col2:
            # Format risk with color
            risk_level = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"
            st.metric(
                label="Disengagement Risk", 
                value=f"{risk_score:.1f}% ({risk_level})",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Avg. Session Duration", 
                value=format_time(avg_session_duration)
            )
        
        # Activity timeline
        st.subheader("Activity Timeline")
        activity_df = user_data.sort_values('timestamp')
        
        if len(activity_df) > 0:
            fig = px.scatter(
                activity_df,
                x='timestamp',
                y='duration',
                color='activity_type',
                size='duration',
                hover_data=['content_id'],
                title='User Activity Timeline',
                labels={'timestamp': 'Date', 'duration': 'Duration (seconds)', 'activity_type': 'Activity Type'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activity data available for the selected date range.")
        
        # Two columns for additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Activity type breakdown
            st.subheader("Activity Distribution")
            activity_counts = user_data['activity_type'].value_counts().reset_index()
            activity_counts.columns = ['Activity Type', 'Count']
            
            fig = px.pie(
                activity_counts, 
                values='Count', 
                names='Activity Type', 
                title='Activity Type Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Daily engagement pattern
            st.subheader("Daily Engagement Pattern")
            user_data['date'] = user_data['timestamp'].dt.date
            daily_data = user_data.groupby('date')['duration'].sum().reset_index()
            
            fig = px.bar(
                daily_data,
                x='date',
                y='duration',
                title='Daily Time Spent (seconds)',
                labels={'date': 'Date', 'duration': 'Total Duration (seconds)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Engagement prediction and recommendations
        st.subheader("Engagement Analysis")
        
        if risk_score > 60:
            st.warning(f"⚠️ This user has a high disengagement risk score of {risk_score:.1f}%. Intervention is recommended.")
        elif risk_score > 30:
            st.info(f"ℹ️ This user has a moderate disengagement risk score of {risk_score:.1f}%. Monitoring is advised.")
        else:
            st.success(f"✅ This user has a low disengagement risk score of {risk_score:.1f}%. They are well engaged.")
        
        if st.button("Generate Recommendations"):
            recommendations = get_recommendation(st.session_state.selected_user)
            
            st.subheader("Personalized Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}. {rec['title']}**")
                st.markdown(f"_{rec['description']}_")
                st.markdown(f"Impact: {rec['impact']}")
                st.markdown("---")
    else:
        st.info("No data available for the selected user in the specified date range.")

elif st.session_state.current_tab == "intervention system":
    # Intervention System Tab
    st.header("🔔 Motivation & Intervention System")
    
    # Get at-risk users
    users_data['risk_score'] = users_data.apply(
        lambda x: predict_engagement_risk(x['user_id']), axis=1
    )
    
    # Get unique users with their risk scores
    at_risk_users = users_data[['user_id', 'risk_score']].drop_duplicates()
    at_risk_users = at_risk_users.sort_values('risk_score', ascending=False)
    
    # Filter for medium to high risk (above 40%)
    at_risk_users = at_risk_users[at_risk_users['risk_score'] > 40]
    
    if len(at_risk_users) > 0:
        st.subheader("Users Requiring Intervention")
        
        # Create a dataframe for display
        display_df = at_risk_users.copy()
        display_df.columns = ['User ID', 'Risk Score (%)']
        display_df['Risk Level'] = display_df['Risk Score (%)'].apply(
            lambda x: "High" if x > 70 else "Medium"
        )
        
        # Add color formatting based on risk level
        def highlight_risk(row):
            if row['Risk Level'] == 'High':
                return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
            else:
                return ['background-color: rgba(255, 165, 0, 0.2)'] * len(row)
        
        # Display the table with styling
        st.dataframe(display_df.style.apply(highlight_risk, axis=1))
        
        # Intervention generator
        st.subheader("Generate Personalized Intervention")
        
        intervention_user = st.selectbox(
            "Select user for intervention:",
            options=at_risk_users['user_id'].tolist(),
            index=0 if st.session_state.selected_user in at_risk_users['user_id'].tolist() else 0
        )
        
        selected_risk = at_risk_users[at_risk_users['user_id'] == intervention_user]['risk_score'].values[0]
        
        # Show the risk level prominently
        risk_level = "High" if selected_risk > 70 else "Medium"
        st.markdown(f"**Risk Level:** {risk_level} ({selected_risk:.1f}%)")
        
        # Generate recommendations and motivational messages
        if st.button("Generate Intervention"):
            with st.spinner("Analyzing user data and generating personalized intervention..."):
                time.sleep(1)  # Simulate processing time
                
                # Get recommendations
                recommendations = get_recommendation(intervention_user)
                
                # Get motivational message
                message = generate_motivation_message(intervention_user)
                
                # Display the intervention
                st.subheader("Personalized Intervention Plan")
                
                # Display motivational message
                st.markdown("### 📧 Motivational Message")
                message_col1, message_col2 = st.columns([3, 1])
                
                with message_col1:
                    st.markdown(f"""
                    **Subject:** {message['subject']}
                    
                    {message['content']}
                    
                    Best regards,  
                    The Learning Assistant
                    """)
                
                with message_col2:
                    if st.button("Send Message"):
                        st.success("Message sent successfully!")
                
                # Display recommendations
                st.markdown("### 🎯 Recommended Interventions")
                for i, rec in enumerate(recommendations, 1):
                    with st.expander(f"{i}. {rec['title']}"):
                        st.markdown(f"**Description:** {rec['description']}")
                        st.markdown(f"**Expected Impact:** {rec['impact']}")
                        st.markdown(f"**Implementation:** {rec['implementation']}")
                
                # Log the intervention
                log_user_activity(
                    user_id="admin",
                    activity_type="generate_intervention",
                    content_id=f"intervention_{intervention_user}",
                    duration=0,
                    timestamp=datetime.now()
                )
    else:
        st.success("🎉 Great news! No users currently require intervention.")

elif st.session_state.current_tab == "settings":
    # Settings Tab
    st.header("⚙️ System Settings")
    
    # System parameters section
    st.subheader("Engagement Tracking Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        engagement_threshold = st.slider(
            "Engagement Score Threshold (%)", 
            min_value=0, 
            max_value=100, 
            value=40,
            help="Minimum engagement score before a user is considered at risk"
        )
        
        session_timeout = st.slider(
            "Session Timeout (minutes)", 
            min_value=1, 
            max_value=60, 
            value=30,
            help="Time of inactivity before a user session is considered ended"
        )
    
    with col2:
        intervention_frequency = st.slider(
            "Intervention Frequency (days)", 
            min_value=1, 
            max_value=14, 
            value=3,
            help="Minimum days between interventions for the same user"
        )
        
        data_retention = st.slider(
            "Data Retention Period (days)", 
            min_value=30, 
            max_value=365, 
            value=90,
            help="How long to keep user activity data"
        )
    
    # Data and model settings
    st.subheader("Model & Data Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        model_retrain = st.selectbox(
            "Model Retraining Frequency",
            options=["Daily", "Weekly", "Monthly", "Quarterly"],
            index=1
        )
        
        prediction_window = st.slider(
            "Prediction Window (days)", 
            min_value=1, 
            max_value=30, 
            value=7,
            help="How far ahead to predict disengagement risk"
        )
    
    with col2:
        feature_importance = st.checkbox(
            "Show Feature Importance in Reports", 
            value=True
        )
        
        anomaly_detection = st.checkbox(
            "Enable Anomaly Detection", 
            value=True,
            help="Detect unusual patterns in user behavior"
        )
    
    # Save settings button
    if st.button("Save Settings"):
        # Here we would normally save these settings to a configuration file or database
        # For demo purposes, we'll use session state
        settings = {
            'engagement_threshold': engagement_threshold,
            'session_timeout': session_timeout,
            'intervention_frequency': intervention_frequency,
            'data_retention': data_retention,
            'model_retrain': model_retrain,
            'prediction_window': prediction_window,
            'feature_importance': feature_importance,
            'anomaly_detection': anomaly_detection
        }
        
        save_state('settings', settings)
        st.success("Settings saved successfully!")
        
        # Log the settings change
        log_user_activity(
            user_id="admin",
            activity_type="update_settings",
            content_id="system_settings",
            duration=0,
            timestamp=datetime.now()
        )
    
    # Advanced section
    with st.expander("Advanced Settings"):
        st.subheader("Model Parameters")
        
        algorithm = st.selectbox(
            "Prediction Algorithm",
            options=["Random Forest", "Gradient Boosting", "Logistic Regression", "Neural Network"],
            index=0
        )
        
        feature_selection = st.multiselect(
            "Features to Use",
            options=[
                "Session Duration", 
                "Activity Frequency", 
                "Content Diversity", 
                "Time of Day Patterns",
                "Day of Week Patterns",
                "Response Time",
                "Achievement Rate",
                "Social Interactions"
            ],
            default=[
                "Session Duration", 
                "Activity Frequency", 
                "Content Diversity", 
                "Time of Day Patterns"
            ]
        )
        
        st.subheader("Notification Settings")
        
        notify_risk_threshold = st.slider(
            "Risk Threshold for Notifications (%)", 
            min_value=0, 
            max_value=100, 
            value=70,
            help="Send notifications for users above this risk threshold"
        )
        
        notification_channels = st.multiselect(
            "Notification Channels",
            options=["Email", "In-App", "SMS", "Push Notification"],
            default=["Email", "In-App"]
        )

# Footer
st.markdown("---")
st.markdown("📚 **Adaptive Learning Motivation & Engagement Agent** | Developed for educational purposes")
