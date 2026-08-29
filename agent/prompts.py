"""
System prompts and templates for the Healthcare Appointment Agent
"""

SYSTEM_PROMPT = """You are a healthcare appointment support agent. Your job is to help users find and book appointments with doctors.

You have access to the following tools:
1. find_department - Determine the appropriate department based on user symptoms
2. find_doctors - Find doctors in a specific department
3. check_availability - Check available appointment slots for a doctor
4. book_appointment - Book an appointment with a doctor

IMPORTANT RULES:
1. Do NOT diagnose medical conditions or prescribe medicines
2. Do NOT invent doctor availability - always use tools to get real information
3. Ask for missing information before booking (patient name, doctor, date, time)
4. Before booking, ensure the user has explicitly selected a doctor and time slot
5. After booking, provide clear confirmation with all details
6. If the user describes an emergency, advise them to seek immediate medical attention

BEHAVIOR GUIDELINES:
- Be helpful, professional, and empathetic
- Use tools to get real data from the database
- Present options clearly to users
- Confirm details before booking
- Provide clear next steps

When a user describes symptoms, use find_department to suggest an appropriate department.
When showing doctors, include their names and specializations.
When checking availability, show all available time slots.
When booking, verify the slot is still available before confirming.
"""


def get_tool_selection_prompt(user_message: str, state: dict) -> str:
    """Generate prompt for tool selection"""
    return f"""Based on the user's message and current state, determine which tool to use next.

User Message: {user_message}

Current State:
- Patient Name: {state.get('patient_name', 'Not provided')}
- Identified Department: {state.get('identified_department', 'None')}
- Selected Doctor: {state.get('selected_doctor', 'None')}
- Selected Date: {state.get('selected_date', 'None')}
- Selected Time: {state.get('selected_time', 'None')}
- Current Step: {state.get('current_step', 'start')}
- Appointment Status: {state.get('appointment_status', 'None')}

Available Tools:
1. find_department(user_request) - Use when you need to identify the right department based on symptoms
2. find_doctors(department_id) - Use when you need to find doctors in a department
3. check_availability(doctor_id, date) - Use when you need to check available slots
4. book_appointment(patient_name, doctor_id, date, time) - Use when user confirms booking
5. None - Use when you need to ask for more information or provide a response

Respond with the tool name and required parameters in JSON format:
{{
    "tool": "tool_name or None",
    "reasoning": "why you chose this tool",
    "parameters": {{}} or null
}}
"""


def get_response_generation_prompt(user_message: str, tool_result: dict, state: dict) -> str:
    """Generate prompt for creating user-facing response"""
    
    if tool_result and tool_result.get("success"):
        if "department_name" in tool_result:
            return f"""The user said: "{user_message}"

I found the department: {tool_result['department_name']}
Reasoning: {tool_result.get('reasoning', '')}

Generate a helpful response that:
1. Acknowledges the user's request
2. Mentions the identified department
3. Asks if they'd like to see available doctors in that department
4. Be friendly and professional
"""
        
        elif "doctors" in tool_result:
            doctors_list = "\n".join([f"- {d['name']} ({d['specialization']})" for d in tool_result['doctors']])
            return f"""The user said: "{user_message}"

I found {tool_result['count']} doctors in the department:
{doctors_list}

Generate a helpful response that:
1. Shows the available doctors
2. Asks the user to select a doctor
3. Asks for their preferred date
4. Be clear and organized
"""
        
        elif "available_slots" in tool_result:
            slots_list = "\n".join([f"- {s['time']}" for s in tool_result['available_slots']])
            return f"""The user said: "{user_message}"

I found {tool_result['count']} available slots for {tool_result['doctor_name']} on {tool_result['date']}:
{slots_list}

Generate a helpful response that:
1. Shows the available time slots
2. Asks the user to select a time
3. Confirm the doctor and date
4. Be clear and organized
"""
        
        elif "appointment_id" in tool_result:
            return f"""The user said: "{user_message}"

Appointment successfully booked!
Details:
- Appointment ID: {tool_result['appointment_id']}
- Patient: {tool_result['patient_name']}
- Doctor: {tool_result['doctor_name']}
- Department: {tool_result['department_name']}
- Date: {tool_result['date']}
- Time: {tool_result['time']}
- Status: {tool_result['status']}

Generate a confirmation message that:
1. Congratulates the user
2. Shows all appointment details
3. Provides any next steps or reminders
4. Be celebratory and clear
"""
    
    # Error case or no tool result
    return f"""The user said: "{user_message}"

Tool result: {tool_result}

Generate a helpful response that addresses the user's request or error appropriately.
"""


def get_activity_description(step: str, tool_name: str = None, result: dict = None) -> str:
    """Get human-readable activity description for UI"""
    
    activities = {
        "start": "🎯 Understanding user request",
        "department_found": f"✓ Identified department: {result.get('department_name') if result else 'Processing'}",
        "doctors_found": f"✓ Found {result.get('count', 0)} doctors" if result else "✓ Searching for doctors",
        "slots_found": f"✓ Found {result.get('count', 0)} available slots" if result else "✓ Checking availability",
        "awaiting_selection": "⏳ Waiting for user to select a time slot",
        "booking_confirmed": f"✓ Appointment confirmed (ID: {result.get('appointment_id')})" if result else "✓ Booking appointment"
    }
    
    if tool_name:
        tool_activities = {
            "find_department": "🔍 Identifying appropriate department",
            "find_doctors": "🔍 Searching for doctors",
            "check_availability": "🔍 Checking appointment availability",
            "book_appointment": "📅 Booking appointment"
        }
        return tool_activities.get(tool_name, "🔄 Processing")
    
    return activities.get(step, "🔄 Processing")