import streamlit as st
import sys
import os
import uuid
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import is_emergency, get_emergency_response
from tools.rag_tool import search_knowledge_base, DOCS_DIR
from agent.agent import HealthcareAgent
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="CityCare AI - Healthcare Appointment Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern healthcare UI aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #0f4c81 0%, #1e3c72 100%);
        border-radius: 1rem;
        padding: 1.5rem 2rem;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(15, 76, 129, 0.15);
    }
    
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        color: #e0e7ff;
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }
    
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.25rem 0.7rem;
        border-radius: 9999px;
        background: rgba(255, 255, 255, 0.18);
        color: #ffffff;
        backdrop-filter: blur(4px);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
    }
    
    .chat-bubble {
        padding: 1.1rem 1.3rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
        border: 1px solid #c7d2fe;
        border-left: 5px solid #4f46e5;
    }
    
    .agent-bubble {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0f4c81;
    }
    
    .emergency-bubble {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-left: 5px solid #e11d48;
        color: #9f1239;
    }
    
    .rag-box {
        background-color: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 0.6rem;
        padding: 0.7rem 1rem;
        margin-top: 0.6rem;
        font-size: 0.85rem;
    }
    
    .rag-badge {
        display: inline-block;
        background-color: #ede9fe;
        color: #5b21b6;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        margin-right: 0.4rem;
        margin-top: 0.2rem;
    }
    
    .welcome-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .quick-chip {
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# Default n8n cloud webhook URL
DEFAULT_N8N_URL = "https://mmsampathram.app.n8n.cloud/webhook/healthcare-appointment"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", DEFAULT_N8N_URL)

# Initialize Session State
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session-{str(uuid.uuid4())[:8]}"
if 'patient_name' not in st.session_state:
    st.session_state.patient_name = "Sampath"
if 'patient_email' not in st.session_state:
    st.session_state.patient_email = "sampathram777@gmail.com"
if 'patient_phone' not in st.session_state:
    st.session_state.patient_phone = "+1 555-0199"
if 'date_provided' not in st.session_state:
    st.session_state.date_provided = False
if 'activities' not in st.session_state:
    st.session_state.activities = []
if 'current_activity' not in st.session_state:
    st.session_state.current_activity = "Ready for consultation"
if 'local_agent' not in st.session_state:
    st.session_state.local_agent = HealthcareAgent()



@st.cache_data(ttl=60)
def check_n8n_status(url: str):
    """Test n8n webhook connectivity"""
    try:
        # Check endpoint with HEAD or lightweight test POST
        r = requests.post(url, json={"chatInput": "ping", "sessionId": "health-check"}, timeout=3)
        return r.status_code == 200, "Online (200 OK)"
    except requests.exceptions.Timeout:
        return True, "Online (Slow/Timeout)"
    except Exception as e:
        return False, f"Offline ({str(e)[:25]})"


n8n_online, n8n_msg = check_n8n_status(N8N_WEBHOOK_URL)

# Top Hero Header
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">
        <span>🏥</span> CityCare Healthcare AI Appointment Assistant
    </div>
    <div class="hero-subtitle">
        Intelligent Receptionist • Live n8n Agent Workflow • Local RAG Knowledge Base
    </div>
    <div class="badge-container">
        <span class="status-badge">
            <span class="status-dot"></span>
            {'n8n Cloud Backend: ' + ('Connected' if n8n_online else 'Standby') + ' (' + N8N_WEBHOOK_URL.split('/')[2] + ')'}
        </span>
        <span class="status-badge">
            📚 Local RAG Engine: Active (6 Approved Docs)
        </span>
        <span class="status-badge">
            🛡️ 2-Layer Emergency Screen: Armed
        </span>
        <span class="status-badge">
            🆔 Session: {st.session_state.session_id}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("👤 Patient Profile")
    st.caption("Auto-fills appointment booking, calendar events & email confirmation:")
    p_name = st.text_input("Full Name", value=st.session_state.patient_name, placeholder="e.g. Sampath")
    p_email = st.text_input("Email Address", value=st.session_state.patient_email, placeholder="e.g. sampathram777@gmail.com")
    p_phone = st.text_input("Phone Number", value=st.session_state.patient_phone, placeholder="e.g. +1 555-0199")

    st.session_state.patient_name = p_name
    st.session_state.patient_email = p_email
    st.session_state.patient_phone = p_phone

    st.markdown("---")
    st.header("⚙️ System Architecture")
    st.markdown("""
    **n8n Workflow Nodes:**
    - ⚡ `Emergency Pre-Screen` (Red-flag filter)
    - 🤖 `Healthcare Appointment Agent` (Gemini Flash)
    - 🧠 `Conversation Memory` (12-turn Buffer)
    - 📅 `create_calendar_event` (Google Calendar)
    - 📧 `send_confirmation_email` (Gmail)
    - 🗃️ `save_booking` & `Mock Doctors` (Data Tables)
    """)

    st.markdown("---")
    st.header("📚 Local RAG Documents")
    st.caption("Click to preview approved hospital knowledge base:")
    
    doc_options = [
        ("hospital_info.txt", "Hospital Hours, Contact & Facilities"),
        ("departments.txt", "Medical Specialties & Doctors"),
        ("appointment_policy.txt", "Cancellation & Rescheduling Rules"),
        ("preparation_guidelines.txt", "What to Bring & Fasting Rules"),
        ("emergency_guidelines.txt", "Emergency Red Flags & Hotlines"),
        ("healthcare_faqs.txt", "Insurance, Teleconsultation & Portal FAQs")
    ]
    
    for filename, desc in doc_options:
        with st.expander(f"📄 {filename}"):
            st.caption(desc)
            file_path = os.path.join(DOCS_DIR, filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as df:
                    st.text(df.read()[:400] + "\n...")

    st.markdown("---")
    st.header("🔎 Activity Timeline")
    if st.session_state.activities:
        for act in st.session_state.activities[-6:]:
            st.markdown(f"• {act}")
    else:
        st.info("Agent is standing by.")

    st.markdown("---")
    if st.button("🔄 New Consultation / Reset", type="secondary", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.activities = []
        st.session_state.session_id = f"session-{str(uuid.uuid4())[:8]}"
        st.session_state.patient_name = "Sampath"
        st.session_state.patient_email = "sampathram777@gmail.com"
        st.session_state.date_provided = False
        st.session_state.local_agent.reset()
        st.rerun()

# Main Consultation Area
st.subheader("💬 Chat with Healthcare Assistant")

# Quick Action Chips
st.markdown("**💡 Common Patient Queries & Quick Actions:**")
chip_cols = st.columns(4)
quick_query = None

with chip_cols[0]:
    if st.button("🎒 What should I bring?", use_container_width=True):
        quick_query = "What should I bring for my appointment?"
    if st.button("🕒 Hospital timings?", use_container_width=True):
        quick_query = "What are the hospital operating timings and visiting hours?"

with chip_cols[1]:
    if st.button("📋 Cancellation policy?", use_container_width=True):
        quick_query = "What is the appointment cancellation and rescheduling policy?"
    if st.button("💳 Accept insurance?", use_container_width=True):
        quick_query = "Does CityCare General Hospital accept health insurance plans?"

with chip_cols[2]:
    if st.button("🤒 Book: Fever & Headache", use_container_width=True):
        quick_query = "I have a fever and headache and want to see a doctor."
    if st.button("🧴 Book: Skin Rash", use_container_width=True):
        quick_query = "I have a skin rash and want to book with Dermatology tomorrow."


with chip_cols[3]:
    if st.button("🔄 Reschedule Appointment", use_container_width=True):
        quick_query = "I would like to reschedule my appointment to next Monday."
    if st.button("🚨 Emergency Check", use_container_width=True):
        quick_query = "I have severe chest pain and difficulty breathing."


# Display Conversation History
chat_placeholder = st.container()
with chat_placeholder:
    if not st.session_state.conversation_history:
        st.markdown("""
        <div class="welcome-card">
            <h4>👋 Welcome to CityCare Healthcare Assistant</h4>
            <p>I can help you with:</p>
            <ul>
                <li><strong>Medical Triage:</strong> Describe symptoms to find the appropriate department and specialist.</li>
                <li><strong>Appointment Management:</strong> Book, reschedule, or cancel real appointments with calendar invites and email receipts.</li>
                <li><strong>Approved Hospital Knowledge (RAG):</strong> Ask about timings, what documents to bring, fasting guidelines, or insurance policies.</li>
                <li><strong>Emergency Safeguard:</strong> Immediate triage and escalation if red-flag symptoms are detected.</li>
            </ul>
            <p style="margin-bottom:0; color:#64748b; font-size:0.9rem;">Select a quick prompt above or type your message below to begin.</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.conversation_history:
        role = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])
        snippets = msg.get("snippets", [])
        is_emerg = msg.get("is_emergency", False)

        if role == "user":
            st.markdown(f'<div class="chat-bubble user-bubble"><strong>👤 You:</strong><br>{content}</div>', unsafe_allow_html=True)
        else:
            bubble_class = "emergency-bubble" if is_emerg else "agent-bubble"
            icon = "🚨" if is_emerg else "🏥"
            st.markdown(f'<div class="chat-bubble {bubble_class}"><strong>{icon} Assistant:</strong><br>{content}</div>', unsafe_allow_html=True)
            
            if sources:
                st.markdown('<div class="rag-box">', unsafe_allow_html=True)
                st.markdown("<strong>📚 Grounded via Local Knowledge Base (RAG):</strong>", unsafe_allow_html=True)
                for src in sources:
                    st.markdown(f'<span class="rag-badge">📄 {src}</span>', unsafe_allow_html=True)
                if snippets:
                    with st.expander("🔍 View Retrieved Knowledge Chunks"):
                        for idx, snip in enumerate(snippets, 1):
                            st.caption(f"Chunk {idx} (from {snip.get('source')}):")
                            st.text(snip.get("text", ""))
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# User Input Form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Enter your message or question:",
        placeholder="e.g. What should I bring? Or: I have a persistent cough and fever...",
        key="form_user_input"
    )
    col_submit, col_clear = st.columns([1, 6])
    with col_submit:
        submitted = st.form_submit_button("Send ➔", type="primary", use_container_width=True)

message_to_send = quick_query if quick_query else (user_input if submitted and user_input.strip() else None)

if message_to_send:
    timestamp_str = datetime.now().strftime("%H:%M:%S")
    st.session_state.activities.append(f"[{timestamp_str}] 🎯 User: {message_to_send[:35]}...")

    # Step 1: Emergency Pre-Screening (Dual-Layer: Local + n8n)
    if is_emergency(message_to_send):
        st.session_state.activities.append(f"[{timestamp_str}] 🚨 Emergency Detected: Triggering Emergency Override")
        emergency_msg = get_emergency_response()
        
        st.session_state.conversation_history.append({
            "role": "user",
            "content": message_to_send
        })
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": emergency_msg,
            "sources": ["emergency_guidelines.txt"],
            "is_emergency": True
        })
        st.rerun()

    # Function to distinguish medical/booking queries from static informational queries
    def is_symptom_or_booking_query(text: str) -> bool:
        text_lower = text.lower()
        clinical_keywords = [
            "fever", "headache", "cough", "cold", "pain", "rash", "skin", "ache", "throat",
            "stomach", "vomit", "dizzy", "sick", "ill", "symptom", "symptoms", "doctor",
            "dr.", "dr ", "book", "booking", "slot", "slots", "appointment", "schedule",
            "reschedule", "cancel", "confirm", "consultation", "consult", "tomorrow", "today",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "am", "pm", "general medicine", "cardiology", "dermatology", "orthopedics", "pediatrics"
        ]
        info_guides = [
            "what should i bring", "what to bring", "documents to bring", "hospital timings",
            "operating timings", "visiting hours", "cancellation policy", "rescheduling policy",
            "accept insurance", "insurance policy", "fasting rules"
        ]
        if any(g in text_lower for g in info_guides):
            return False
        return any(k in text_lower for k in clinical_keywords)

    def contains_date_mention(text: str) -> bool:
        """Check if a date, day of week, or relative date reference is present in text."""
        import re
        text_lower = text.lower()
        date_keywords = [
            "today", "tomorrow", "day after tomorrow", "yesterday", "tonight",
            "next week", "this week", "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday", "january", "february", "march", "april",
            "may", "june", "july", "august", "september", "october", "november",
            "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep",
            "oct", "nov", "dec", "2025", "2026", "2027"
        ]
        if re.search(r'\b\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?\b', text_lower):
            return True
        return any(re.search(rf'\b{re.escape(k)}\b', text_lower) for k in date_keywords)

    is_clinical = is_symptom_or_booking_query(message_to_send)

    # Check if a date has been mentioned in this message or prior
    if contains_date_mention(message_to_send):
        st.session_state.date_provided = True

    date_already_given = st.session_state.date_provided
    missing_date = is_clinical and not date_already_given

    rag_sources = []
    rag_snippets = []

    # Step 2: Local RAG Knowledge Search ONLY for hospital informational queries (timings, what to bring, policies)
    if not is_clinical:
        st.session_state.activities.append(f"[{timestamp_str}] 📚 Querying Local RAG Knowledge Base")
        rag_result = search_knowledge_base(message_to_send, top_k=2)
        has_rag_match = rag_result.get("success", False) and rag_result.get("top_score", 0) >= 0.08
        if has_rag_match:
            rag_sources = rag_result.get("sources", [])
            rag_snippets = rag_result.get("chunks", [])

    # Step 3: Format query for n8n - ALWAYS take Patient Name and Email from sidebar for EVERY chat
    cur_patient_name = st.session_state.patient_name.strip() or "Sampath"
    cur_patient_email = st.session_state.patient_email.strip() or "sampathram777@gmail.com"
    profile_tag = f"[Patient Name: {cur_patient_name}, Patient Email: {cur_patient_email}]"

    if is_clinical:
        if missing_date:
            n8n_input = f"{profile_tag} [Notice: No appointment date was given in the chat. Please ask the patient for their preferred date before booking.] {message_to_send}"
        else:
            n8n_input = f"{profile_tag} {message_to_send}"
    else:
        if rag_sources and "answer" in rag_result:
            n8n_input = f"{profile_tag} [RAG Knowledge: {rag_result['answer'][:300]}] {message_to_send}"
        else:
            n8n_input = f"{profile_tag} {message_to_send}"

    # Step 4: Dispatch to n8n Cloud Webhook Backend
    st.session_state.activities.append(f"[{timestamp_str}] 🌐 Dispatching to n8n Agent Backend")
    agent_output = ""
    n8n_success = False

    try:
        payload = {
            "chatInput": n8n_input,
            "sessionId": st.session_state.session_id
        }
        res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=25)
        if res.status_code == 200:
            res_json = res.json()
            agent_output = res_json.get("output", res_json.get("reply", res_json.get("message", "")))
            if agent_output:
                n8n_success = True
                st.session_state.activities.append(f"[{timestamp_str}] ✓ Response received from n8n agent")
    except Exception as e:
        st.session_state.activities.append(f"[{timestamp_str}] ⚠️ n8n request issue: {str(e)[:30]}")
        n8n_success = False

    # Step 5: Fallback to local agent if n8n was not responsive or empty
    if not n8n_success or not agent_output:
        st.session_state.activities.append(f"[{timestamp_str}] 🤖 Running Local Healthcare Agent Fallback")
        st.session_state.local_agent.state.patient_name = cur_patient_name
        local_res = st.session_state.local_agent.process_message(message_to_send)
        agent_output = local_res.get("response", "I received your request.")

        if not rag_sources:
            rag_sources = local_res.get("sources", [])

    # If no date was given in the chat, verify that the assistant asks the user for the date:
    if missing_date and agent_output:
        out_lower = agent_output.lower()
        asked_date = any(w in out_lower for w in ["date", "when", "which day", "what day", "preferred date", "tomorrow"])
        if not asked_date:
            agent_output += "\n\n📅 **Could you please let me know your preferred date for the appointment?** (e.g. tomorrow, next Monday, or a specific date like YYYY-MM-DD)"


    # Record to conversation history
    st.session_state.conversation_history.append({
        "role": "user",
        "content": message_to_send
    })
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": agent_output,
        "sources": rag_sources,
        "snippets": rag_snippets,
        "is_emergency": False
    })
    st.rerun()

st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:2rem;">
    CityCare AI Assistant • Powered by n8n Cloud Workflow + Local TF-IDF RAG • Multi-turn LangChain Memory
</div>
""", unsafe_allow_html=True)
