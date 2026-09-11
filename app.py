import streamlit as st
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import is_emergency, get_emergency_response
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="🏥 Healthcare AI Appointment Assistant",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 0.5rem; }
    .subtitle { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .chat-message { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
    .user-message { background-color: #e3f2fd; border-left: 4px solid #2196f3; }
    .agent-message { background-color: #f3e5f5; border-left: 4px solid #9c27b0; }
    .activity-box { background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 0.5rem; padding: 1rem; margin-top: 1rem; }
    .rag-source { font-size: 0.85rem; color: #8e24aa; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/chat/7a6d9ab6-6394-48d8-a7ee-501db63d1c13")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
    st.session_state.patient_name = ""
    st.session_state.activities = []
    st.session_state.current_activity = ""
    st.session_state.rag_sources = []

st.markdown('<p class="main-header">🏥 Healthcare AI Appointment Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your intelligent appointment support assistant</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    patient_name = st.text_input("Patient Name", value=st.session_state.patient_name, key="patient_name_input")
    st.session_state.patient_name = patient_name
    st.markdown("---")
    st.header("🔎 Agent Activity")
    activity_container = st.container()
    st.markdown("---")
    if st.button("🔄 Reset Conversation", type="secondary"):
        st.session_state.conversation_history = []
        st.session_state.activities = []
        st.session_state.rag_sources = []
        st.session_state.current_activity = ""
        st.rerun()

st.header("💬 Chat")

chat_container = st.container()
with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message agent-message"><strong>Agent:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            if message.get("sources"):
                st.markdown(f'<div class="rag-source">Sources: {", ".join(message["sources"])}</div>', unsafe_allow_html=True)

with activity_container:
    if st.session_state.activities:
        st.markdown("**Activity Log:**")
        for act in st.session_state.activities[-8:]:
            st.markdown(f"- {act}")
    else:
        st.markdown(f'<div class="activity-box"><strong>Current Activity:</strong><br>{st.session_state.current_activity or "Ready"}</div>', unsafe_allow_html=True)

st.markdown("---")
user_input = st.text_input("Type your message here...", key="user_input", placeholder="e.g., What should I bring for my appointment?")

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    send_button = st.button("Send", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("Clear", use_container_width=True)

if clear_button:
    st.session_state.conversation_history = []
    st.session_state.activities = []
    st.session_state.rag_sources = []
    st.session_state.current_activity = ""
    st.rerun()

if send_button and user_input:
    if is_emergency(user_input):
        st.session_state.activities.append("Emergency detected - providing emergency guidance")
        st.session_state.conversation_history.append({"role": "assistant", "content": get_emergency_response()})
        st.session_state.current_activity = "Emergency guidance provided"
        st.rerun()

    st.session_state.activities.append("Understanding user request...")
    st.session_state.current_activity = "Understanding user request..."

    patient_name = st.session_state.patient_name or ""
    full_message = f"[Patient: {patient_name}] {user_input}" if patient_name else user_input

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={"messages": [{"role": "user", "content": full_message}]},
            timeout=60
        )
        if response.status_code == 200:
            r_json = response.json()
            agent_response = r_json.get("reply", r_json.get("output", "I received your message."))
            st.session_state.activities.append("Response received from agent")
        else:
            agent_response = f"Backend error (HTTP {response.status_code}). Please try again."
            st.session_state.activities.append(f"Backend error: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        agent_response = "Cannot connect to n8n backend. Ensure n8n is running and N8N_WEBHOOK_URL is set in .env."
        st.session_state.activities.append("Cannot connect to n8n backend")
    except requests.exceptions.Timeout:
        agent_response = "Request timed out. Please try again."
        st.session_state.activities.append("Request timed out")
    except Exception as e:
        agent_response = "An error occurred. Please try again."
        st.session_state.activities.append(f"Error: {str(e)}")

    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": agent_response,
        "sources": st.session_state.rag_sources
    })
    st.session_state.current_activity = "Ready"
    st.session_state.rag_sources = []
    st.rerun()

st.markdown("---")
st.markdown("© 2024 Healthcare AI Appointment Assistant | Streamlit + n8n")
