"""
Utility functions for the Healthcare Appointment Agent
"""

from datetime import datetime, timedelta
import re


def format_date(date_str: str) -> str:
    """Format date string to readable format"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")


def get_next_days(num_days: int = 7) -> list:
    """Get list of next N days in YYYY-MM-DD format"""
    dates = []
    today = datetime.now()
    for i in range(num_days):
        date = today + timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates


def validate_time(time_str: str) -> bool:
    """Validate time format (HH:MM AM/PM)"""
    pattern = r'^(0?[1-9]|1[0-2]):[0-5][0-9]\s*(AM|PM)$'
    return bool(re.match(pattern, time_str.strip(), re.IGNORECASE))


def normalize_time(time_str: str) -> str:
    """Normalize time to consistent format (HH:MM AM/PM)"""
    time_str = time_str.strip().upper()
    
    # Add AM/PM if missing
    if 'AM' not in time_str and 'PM' not in time_str:
        time_str += ' AM'
    
    # Ensure consistent spacing
    time_str = re.sub(r'\s+', ' ', time_str)
    
    return time_str


def is_emergency(message: str) -> bool:
    """Check if message indicates emergency"""
    emergency_keywords = [
        'emergency', 'urgent', 'critical', 'heart attack', 'stroke',
        'bleeding', 'unconscious', 'not breathing', 'chest pain severe',
        'severe pain', 'accident', 'injured badly'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in emergency_keywords)


def get_emergency_response() -> str:
    """Get emergency response message"""
    return """⚠️ **EMERGENCY ALERT** ⚠️

If you are experiencing a medical emergency, please:
- Call emergency services immediately (911 in the US, 112 in EU)
- Go to the nearest emergency room
- Do not wait for an appointment

This chatbot is for non-emergency appointment scheduling only.
If this is a life-threatening situation, please seek immediate medical attention.
"""


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_appointment_details(appointment: dict) -> str:
    """Format appointment details for display"""
    details = f"""
**Appointment Details:**
- **Appointment ID:** {appointment.get('appointment_id', 'N/A')}
- **Patient:** {appointment.get('patient_name', 'N/A')}
- **Doctor:** {appointment.get('doctor_name', 'N/A')}
- **Department:** {appointment.get('department_name', 'N/A')}
- **Date:** {format_date(appointment.get('date', 'N/A'))}
- **Time:** {appointment.get('time', 'N/A')}
- **Status:** {appointment.get('status', 'N/A')}
"""
    return details