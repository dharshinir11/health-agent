import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.agent import HealthcareAgent
from utils.helpers import format_date, is_emergency, get_emergency_response

# Page configuration
st.set_page_config(
    page_title="🏥 Healthcare AI Appointment Assistant",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .agent-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .activity-box {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = HealthcareAgent()
    st.session_state.conversation_history = []
    st.session_state.patient_name = ""

# Title
st.markdown('<p class="main-header">🏥 Healthcare AI Appointment Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your intelligent appointment support assistant</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Patient name input
    patient_name = st.text_input("Patient Name", value=st.session_state.patient_name, key="patient_name_input")
    st.session_state.patient_name = patient_name
    
    st.markdown("---")
    
    # Agent activity section
    st.header("🔎 Agent Activity")
    activity_container = st.container()
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Reset Conversation", type="secondary"):
        st.session_state.agent.reset()
        st.session_state.conversation_history = []
        st.rerun()

# Main chat interface
st.header("💬 Chat")

# Display conversation history
chat_container = st.container()

with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message agent-message"><strong>Agent:</strong> {message["content"]}</div>', unsafe_allow_html=True)

# Display current agent activity
with activity_container:
    current_activity = st.session_state.agent._get_current_activity()
    st.markdown(f'<div class="activity-box"><strong>Current Activity:</strong><br>{current_activity}</div>', unsafe_allow_html=True)

# User input
st.markdown("---")
user_input = st.text_input("Type your message here...", key="user_input", placeholder="e.g., I have fever and headache and want to see a doctor tomorrow")

# Send button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    send_button = st.button("Send", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("Clear", use_container_width=True)

if clear_button:
    st.session_state.conversation_history = []
    st.session_state.agent.reset()
    st.rerun()

if send_button and user_input:
    # Check for emergency
    if is_emergency(user_input):
        emergency_response = get_emergency_response()
        st.session_state.conversation_history.append({"role": "assistant", "content": emergency_response})
        st.rerun()
    
    # Process message through agent
    result = st.session_state.agent.process_message(user_input)
    
    # Add to conversation history
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    st.session_state.conversation_history.append({"role": "assistant", "content": result["response"]})
    
    # Clear input and rerun
    st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2024 Healthcare AI Appointment Assistant | Built with Streamlit")