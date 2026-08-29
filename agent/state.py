"""
Agent State Management
Maintains conversation state and appointment context
"""

class AgentState:
    """Maintains the state of the healthcare appointment agent"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset state to initial values"""
        self.patient_name = None
        self.user_request = None
        self.identified_department = None
        self.department_id = None
        self.selected_doctor = None
        self.doctor_id = None
        self.selected_date = None
        self.selected_time = None
        self.available_slots = []
        self.appointment_status = None
        self.conversation_history = []
        self.current_step = "start"  # start, department_found, doctors_found, slots_found, awaiting_selection, booking_confirmed
        self.last_tool_result = None
    
    def update(self, key, value):
        """Update a state variable"""
        if hasattr(self, key):
            setattr(self, key, value)
            return True
        return False
    
    def get(self, key, default=None):
        """Get a state variable"""
        return getattr(self, key, default)
    
    def to_dict(self):
        """Convert state to dictionary"""
        return {
            "patient_name": self.patient_name,
            "user_request": self.user_request,
            "identified_department": self.identified_department,
            "department_id": self.department_id,
            "selected_doctor": self.selected_doctor,
            "doctor_id": self.doctor_id,
            "selected_date": self.selected_date,
            "selected_time": self.selected_time,
            "available_slots": self.available_slots,
            "appointment_status": self.appointment_status,
            "current_step": self.current_step
        }
    
    def add_to_history(self, role, content):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp()
        })
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")