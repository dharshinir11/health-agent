"""
Healthcare Appointment Agent
Implements the agentic loop with tool calling
"""

import re
from .state import AgentState
from .prompts import get_activity_description
from tools import find_department, find_doctors, check_availability, book_appointment


class HealthcareAgent:
    """Healthcare appointment agent with tool-calling capabilities"""
    
    def __init__(self):
        self.state = AgentState()
    
    def reset(self):
        """Reset agent state"""
        self.state.reset()
    
    def process_message(self, user_message: str) -> dict:
        """
        Process user message through agentic loop
        
        Args:
            user_message: User's input message
            
        Returns:
            dict with response and agent activity
        """
        # Add user message to history
        self.state.add_to_history("user", user_message)
        
        # Extract patient name if mentioned
        self._extract_patient_name(user_message)
        
        # Agentic loop: decide and act
        response = self._agentic_loop(user_message)
        
        # Add agent response to history
        self.state.add_to_history("assistant", response)
        
        return {
            "response": response,
            "state": self.state.to_dict(),
            "activity": self._get_current_activity()
        }
    
    def _extract_patient_name(self, message: str):
        """Extract patient name from message if mentioned"""
        # Pattern: "my name is X" or "I'm X" or "I am X"
        patterns = [
            r"my name is ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
            r"I'm ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
            r"I am ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
            r"name is ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                self.state.patient_name = match.group(1)
                break
    
    def _agentic_loop(self, user_message: str) -> str:
        """
        Main agentic loop: reason → decide → act → respond
        
        Args:
            user_message: User's input message
            
        Returns:
            Agent's response string
        """
        message_lower = user_message.lower()
        
        # Step 1: Determine what to do based on current state and message
        
        # If we're awaiting a selection (time slot)
        if self.state.current_step == "awaiting_selection":
            return self._handle_time_selection(user_message)
        
        # If appointment is already confirmed
        if self.state.current_step == "booking_confirmed":
            return "Your appointment has already been confirmed. Is there anything else I can help you with?"
        
        # Check if user wants to book (has department, doctor, and is providing time)
        if self.state.department_id and self.state.doctor_id and self._is_time_mention(message_lower):
            return self._handle_booking_request(user_message)
        
        # Check if user is selecting a doctor
        if self.state.department_id and not self.state.doctor_id and self._is_doctor_selection(message_lower):
            return self._handle_doctor_selection(user_message)
        
        # Check if user is providing a date
        if self.state.department_id and self.state.doctor_id and not self.state.selected_date and self._is_date_mention(message_lower):
            return self._handle_date_selection(user_message)
        
        # If no department identified yet, find department
        if not self.state.department_id:
            return self._find_department_step(user_message)
        
        # If department found but no doctors shown yet
        if self.state.department_id and not self.state.doctor_id:
            return self._find_doctors_step()
        
        # If doctors found but no date selected
        if self.state.department_id and self.state.doctor_id and not self.state.selected_date:
            return self._request_date_selection()
        
        # If date selected but no slots checked
        if self.state.department_id and self.state.doctor_id and self.state.selected_date and not self.state.available_slots:
            return self._check_availability_step()
        
        # Default: ask what they need
        return "I can help you book an appointment. Please tell me about your symptoms or which department you'd like to visit."
    
    def _is_time_mention(self, message: str) -> bool:
        """Check if message mentions a time"""
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm)?',
            r'\d{1,2}\s*(am|pm)',
            r'morning|afternoon|evening'
        ]
        return any(re.search(pattern, message, re.IGNORECASE) for pattern in time_patterns)
    
    def _is_doctor_selection(self, message: str) -> bool:
        """Check if message is selecting a doctor"""
        return 'dr.' in message.lower() or 'doctor' in message.lower()
    
    def _is_date_mention(self, message: str) -> bool:
        """Check if message mentions a date"""
        date_patterns = [
            r'tomorrow',
            r'day after tomorrow',
            r'\d{1,2}/\d{1,2}',
            r'\d{1,2}-\d{1,2}',
            r'monday|tuesday|wednesday|thursday|friday|saturday|sunday'
        ]
        return any(re.search(pattern, message, re.IGNORECASE) for pattern in date_patterns)
    
    def _find_department_step(self, user_message: str) -> str:
        """Step 1: Find appropriate department"""
        self.state.current_step = "department_found"
        
        # Call tool
        result = find_department(user_message)
        self.state.last_tool_result = result
        
        if result["success"]:
            self.state.identified_department = result["department_name"]
            self.state.department_id = result["department_id"]
            
            response = f"I understand you're looking for a doctor. Based on your symptoms, **{result['department_name']}** seems like the right department.\n\n"
            response += f"{result.get('reasoning', '')}\n\n"
            response += "Would you like me to show you the available doctors in this department?"
            
            return response
        else:
            return "I'm sorry, I couldn't determine the right department. Could you please tell me more about your symptoms?"
    
    def _find_doctors_step(self) -> str:
        """Step 2: Find doctors in the department"""
        self.state.current_step = "doctors_found"
        
        # Call tool
        result = find_doctors(self.state.department_id)
        self.state.last_tool_result = result
        
        if result["success"]:
            response = f"Here are the available doctors in **{self.state.identified_department}**:\n\n"
            
            for idx, doctor in enumerate(result["doctors"], 1):
                response += f"{idx}. **{doctor['name']}**\n"
                response += f"   {doctor['specialization']}\n\n"
            
            response += "Please select a doctor (you can say the doctor's name) and let me know your preferred date."
            
            return response
        else:
            return f"I'm sorry, but there are no doctors available in {self.state.identified_department} at the moment."
    
    def _handle_doctor_selection(self, user_message: str) -> str:
        """Handle doctor selection from user"""
        # Find which doctor was mentioned
        result = find_doctors(self.state.department_id)
        
        if not result["success"]:
            return "I'm having trouble finding doctors. Please try again."
        
        selected_doctor = None
        for doctor in result["doctors"]:
            if doctor["name"].lower() in user_message.lower():
                selected_doctor = doctor
                break
        
        if not selected_doctor:
            # If no exact match, ask them to be more specific
            response = "I couldn't identify which doctor you selected. Please choose from the list:\n\n"
            for doctor in result["doctors"]:
                response += f"- {doctor['name']}\n"
            return response
        
        self.state.selected_doctor = selected_doctor["name"]
        self.state.doctor_id = selected_doctor["id"]
        
        return f"Great! You've selected **{selected_doctor['name']}** ({selected_doctor['specialization']}).\n\nNow, please let me know your preferred date (e.g., 'tomorrow', '2025-08-25')."
    
    def _handle_date_selection(self, user_message: str) -> str:
        """Handle date selection and convert to YYYY-MM-DD format"""
        date_str = self._parse_date(user_message)
        
        if not date_str:
            return "I couldn't understand the date. Please provide a date in format like 'tomorrow', '2025-08-25', or 'next Monday'."
        
        self.state.selected_date = date_str
        return self._check_availability_step()
    
    def _parse_date(self, message: str) -> str:
        """Parse date from user message to YYYY-MM-DD format"""
        from datetime import datetime, timedelta
        
        message_lower = message.lower()
        today = datetime.now()
        
        # Handle relative dates
        if 'tomorrow' in message_lower:
            target_date = today + timedelta(days=1)
            return target_date.strftime("%Y-%m-%d")
        
        if 'day after tomorrow' in message_lower:
            target_date = today + timedelta(days=2)
            return target_date.strftime("%Y-%m-%d")
        
        # Handle day names
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for idx, day in enumerate(days):
            if day in message_lower:
                days_ahead = idx - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime("%Y-%m-%d")
        
        # Try to parse YYYY-MM-DD or MM/DD/YYYY
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{2}-\d{2}-\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                date_str = match.group(1)
                try:
                    if '/' in date_str or '-' in date_str[2:3]:
                        # MM/DD/YYYY or MM-DD-YYYY
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y" if '/' in date_str else "%m-%d-%Y")
                    else:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    return date_obj.strftime("%Y-%m-%d")
                except:
                    continue
        
        return None
    
    def _request_date_selection(self) -> str:
        """Request user to select a date"""
        return f"Please let me know your preferred date for the appointment with {self.state.selected_doctor} (e.g., 'tomorrow', '2025-08-25')."
    
    def _check_availability_step(self) -> str:
        """Step 3: Check availability"""
        self.state.current_step = "slots_found"
        
        # Call tool
        result = check_availability(self.state.doctor_id, self.state.selected_date)
        self.state.last_tool_result = result
        
        if result["success"]:
            self.state.available_slots = result["available_slots"]
            
            response = f"Great! I found **{result['count']}** available slots for **{result['doctor_name']}** on **{result['date']}**:\n\n"
            
            for idx, slot in enumerate(result["available_slots"], 1):
                response += f"{idx}. {slot['time']}\n"
            
            response += "\nPlease select a time slot (e.g., '10:00 AM' or 'Book 10 AM')."
            self.state.current_step = "awaiting_selection"
            
            return response
        else:
            response = f"I'm sorry, but there are no available slots for {self.state.selected_doctor} on {self.state.selected_date}.\n\n"
            response += "Would you like to try a different date?"
            self.state.selected_date = None
            return response
    
    def _handle_time_selection(self, user_message: str) -> str:
        """Handle time slot selection"""
        # Extract time from message
        time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM)?|\d{1,2}\s*(?:AM|PM))', user_message, re.IGNORECASE)
        
        if not time_match:
            return "Please select a valid time slot from the list provided (e.g., '10:00 AM')."
        
        selected_time = time_match.group(1).upper()
        
        # Normalize time format
        if 'AM' not in selected_time and 'PM' not in selected_time:
            selected_time += ' AM'
        
        # Check if this time is in available slots
        slot_found = False
        for slot in self.state.available_slots:
            if slot['time'].upper() == selected_time:
                slot_found = True
                break
        
        if not slot_found:
            return f"Sorry, {selected_time} is not available. Please choose from the available slots shown earlier."
        
        self.state.selected_time = selected_time
        
        # Ask for confirmation before booking
        response = f"Perfect! You've selected **{selected_time}** on **{self.state.selected_date}** with **{self.state.selected_doctor}**.\n\n"
        response += "Please confirm:\n"
        response += f"- Patient: {self.state.patient_name or 'Not provided'}\n"
        response += f"- Doctor: {self.state.selected_doctor}\n"
        response += f"- Date: {self.state.selected_date}\n"
        response += f"- Time: {self.state.selected_time}\n\n"
        response += "Should I proceed with booking this appointment? (Say 'yes' or 'confirm' to book)"
        
        return response
    
    def _handle_booking_request(self, user_message: str) -> str:
        """Handle booking confirmation"""
        message_lower = user_message.lower()
        
        # Check if user confirmed
        if any(word in message_lower for word in ['yes', 'confirm', 'book', 'proceed', 'ok', 'sure']):
            return self._book_appointment_step()
        else:
            return "Please confirm by saying 'yes' or 'confirm' if you'd like me to book this appointment."
    
    def _book_appointment_step(self) -> str:
        """Step 4: Book the appointment"""
        self.state.current_step = "booking_confirmed"
        
        # Ensure we have patient name
        patient_name = self.state.patient_name or "Patient"
        
        # Call tool
        result = book_appointment(
            patient_name=patient_name,
            doctor_id=self.state.doctor_id,
            date=self.state.selected_date,
            time=self.state.selected_time
        )
        self.state.last_tool_result = result
        
        if result["success"]:
            self.state.appointment_status = "confirmed"
            
            response = "🎉 **Appointment Successfully Booked!**\n\n"
            response += f"**Appointment ID:** {result['appointment_id']}\n"
            response += f"**Patient:** {result['patient_name']}\n"
            response += f"**Doctor:** {result['doctor_name']}\n"
            response += f"**Department:** {result['department_name']}\n"
            response += f"**Date:** {result['date']}\n"
            response += f"**Time:** {result['time']}\n"
            response += f"**Status:** {result['status']}\n\n"
            response += "Please arrive 10 minutes before your scheduled time. "
            response += "Bring any relevant medical records with you.\n\n"
            response += "Is there anything else I can help you with?"
            
            return response
        else:
            self.state.current_step = "slots_found"
            return f"I'm sorry, but I couldn't book the appointment: {result['error']}. Please try selecting a different time slot."
    
    def _get_current_activity(self) -> str:
        """Get current agent activity for UI display"""
        tool_name = None
        if self.state.last_tool_result:
            # Determine which tool was called based on result keys
            if "department_name" in self.state.last_tool_result:
                tool_name = "find_department"
            elif "doctors" in self.state.last_tool_result:
                tool_name = "find_doctors"
            elif "available_slots" in self.state.last_tool_result:
                tool_name = "check_availability"
            elif "appointment_id" in self.state.last_tool_result:
                tool_name = "book_appointment"
        
        return get_activity_description(self.state.current_step, tool_name, self.state.last_tool_result)