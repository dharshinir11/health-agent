# 🏥 Healthcare AI Appointment Assistant

An intelligent, agentic AI-powered appointment booking system built with Python and Streamlit. This project demonstrates a genuine **Agentic AI workflow** where the agent reasons, decides, calls tools, and completes multi-step tasks autonomously.

## 🎯 What Makes This Agentic?

Unlike simple chatbots that just generate text, this application implements a **true agentic loop**:

```
User Input → Agent Reasoning → Tool Selection → Tool Execution → 
Result Processing → Next Decision → Tool Call → ... → Final Response
```

The agent:
- ✅ **Reasons** about the user's request
- ✅ **Decides** which tool to use based on current state
- ✅ **Calls** appropriate tools (find_department, find_doctors, check_availability, book_appointment)
- ✅ **Inspects** tool results
- ✅ **Decides** next action based on results
- ✅ **Completes** multi-step appointment booking tasks

## 🏗️ Architecture

```
healthcare-agent/
├── app.py                      # Streamlit UI
├── agent/
│   ├── __init__.py
│   ├── agent.py               # Main agent with agentic loop
│   ├── state.py               # Conversation state management
│   └── prompts.py             # System prompts and templates
├── tools/
│   ├── __init__.py
│   ├── department_tool.py     # Find appropriate department
│   ├── doctor_tool.py         # Find doctors in department
│   ├── availability_tool.py   # Check appointment slots
│   └── appointment_tool.py    # Book appointment
├── database/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # Database connection
│   └── seed.py                # Seed initial data
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Utility functions
├── .env.example               # Environment variables template
├── .gitignore
└── requirements.txt
```

## ✨ Features

- 🤖 **Agentic AI Workflow**: Real tool calling and decision-making
- 💬 **Natural Language Chat**: Chat naturally with the AI agent
- 🏥 **Smart Department Routing**: Automatically identifies the right department based on symptoms
- 👨‍⚕️ **Doctor Search**: Find available doctors in any department
- 📅 **Availability Checking**: Real-time appointment slot checking
- ✅ **Appointment Booking**: Complete booking with confirmation
- 🔎 **Agent Activity Display**: See what the agent is doing in real-time
- 🚨 **Emergency Detection**: Recognizes emergency situations and provides appropriate guidance
- 💾 **SQLite Database**: Persistent storage for all appointments

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Agent**: Python-based agent orchestration with rule-based decision making
- **Database**: SQLite with SQLAlchemy ORM
- **Architecture**: Modular, tool-based agent system

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd healthcare-agent
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for MVP)
```

### 5. Initialize Database

```bash
python database/seed.py
```

This will create the SQLite database and seed it with:
- 5 departments (General Medicine, Dermatology, Cardiology, Orthopedics, Pediatrics)
- 10 doctors across all departments
- Appointment slots for the next 7 days

## 🎮 Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Example Conversation Flow

**User:** "My name is Dharshini. I have fever and headache and want to see a doctor tomorrow."

**Agent:** 
- 🎯 Understanding user request
- ✓ Identified department: General Medicine
- ✓ Found 2 doctors

"I understand you're looking for a doctor. Based on your symptoms, **General Medicine** seems like the right department.

Here are the available doctors in **General Medicine**:

1. **Dr. Ananya Sharma**
   MBBS, MD - General Medicine

2. **Dr. Rahul Verma**
   MBBS, MD - Internal Medicine

Please select a doctor (you can say the doctor's name) and let me know your preferred date."

**User:** "Book Dr. Ananya at 10 AM tomorrow."

**Agent:**
- ✓ Searching for doctors
- ✓ Checking appointment availability
- ✓ Found 5 available slots

"Great! I found **5** available slots for **Dr. Ananya Sharma** on **2025-08-23**:

1. 09:00 AM
2. 10:00 AM
3. 11:00 AM
4. 02:00 PM
5. 03:00 PM

Please select a time slot (e.g., '10:00 AM' or 'Book 10 AM')."

**User:** "10:00 AM"

**Agent:**
- ⏳ Waiting for user to select a time slot

"Perfect! You've selected **10:00 AM** on **2025-08-23** with **Dr. Ananya Sharma**.

Please confirm:
- Patient: Dharshini
- Doctor: Dr. Ananya Sharma
- Date: 2025-08-23
- Time: 10:00 AM

Should I proceed with booking this appointment? (Say 'yes' or 'confirm' to book)"

**User:** "Yes, confirm."

**Agent:**
- ✓ Appointment confirmed (ID: 1)

"🎉 **Appointment Successfully Booked!**

**Appointment ID:** 1
**Patient:** Dharshini
**Doctor:** Dr. Ananya Sharma
**Department:** General Medicine
**Date:** 2025-08-23
**Time:** 10:00 AM
**Status:** confirmed

Please arrive 10 minutes before your scheduled time. Bring any relevant medical records with you.

Is there anything else I can help you with?"

## 🔧 Agent Tools

The agent has access to 4 main tools:

### 1. `find_department(user_request)`
Determines the appropriate department based on user symptoms using keyword matching.

**Example:**
- Input: "I have skin rashes"
- Output: Dermatology

### 2. `find_doctors(department_id)`
Finds all doctors in a specific department.

**Example:**
- Input: department_id=1 (General Medicine)
- Output: List of doctors with names and specializations

### 3. `check_availability(doctor_id, date)`
Checks available appointment slots for a doctor on a specific date.

**Example:**
- Input: doctor_id=1, date="2025-08-23"
- Output: List of available time slots

### 4. `book_appointment(patient_name, doctor_id, date, time)`
Books an appointment and marks the slot as unavailable.

**Example:**
- Input: patient_name="Dharshini", doctor_id=1, date="2025-08-23", time="10:00 AM"
- Output: Appointment confirmation with ID

## 🧠 Agent State Management

The agent maintains conversation state including:
- Patient name
- Identified department
- Selected doctor
- Selected date and time
- Available slots
- Appointment status
- Conversation history

This allows the agent to:
- Remember context across multiple messages
- Make decisions based on previous interactions
- Guide users through multi-step workflows

## 🎨 UI Features

### Main Chat Interface
- Clean, professional chat UI
- Message history with color-coded user/agent messages
- Real-time agent activity display

### Sidebar
- Patient name input
- Agent activity monitor (shows current action)
- Reset conversation button

### Agent Activity Display
Shows high-level actions like:
- 🎯 Understanding user request
- ✓ Identified department: General Medicine
- ✓ Found 2 doctors
- ✓ Found 5 available slots
- ⏳ Waiting for user to select a time slot
- ✓ Appointment confirmed (ID: 1)

## 🛡️ Safety Features

- **No Medical Diagnosis**: Agent never diagnoses conditions or prescribes medicines
- **Emergency Detection**: Recognizes emergency keywords and provides appropriate guidance
- **Data Validation**: Validates all inputs before database operations
- **Error Handling**: Graceful error handling with user-friendly messages
- **Slot Verification**: Verifies slot availability before booking

## 🧪 Testing the Application

### Test Case 1: Basic Appointment Booking

1. Open the application
2. Enter patient name: "Dharshini"
3. Type: "I have fever and headache and want to see a doctor tomorrow"
4. Select a doctor from the list
5. Confirm the date
6. Choose a time slot
7. Confirm booking
8. Verify appointment is stored in database

### Test Case 2: Department-Specific Request

1. Type: "I need a dermatologist for my skin rash"
2. Agent should identify Dermatology department
3. Show dermatologists
4. Continue with booking flow

### Test Case 3: Emergency Detection

1. Type: "I'm having severe chest pain and think it's a heart attack"
2. Agent should display emergency message
3. Advise calling emergency services

## 📊 Database Schema

### Departments
- id, name, description

### Doctors
- id, name, department_id, specialization

### AppointmentSlots
- id, doctor_id, date, time, available

### Appointments
- id, patient_name, doctor_id, date, time, status, created_at

## 🔮 Future Improvements

- [ ] Integrate real LLM (OpenAI/Claude) for better natural language understanding
- [ ] Add user authentication
- [ ] Email/SMS confirmation
- [ ] Appointment rescheduling and cancellation
- [ ] Doctor ratings and reviews
- [ ] Multi-language support
- [ ] Calendar integration
- [ ] Patient medical history
- [ ] Payment integration
- [ ] Admin dashboard

## 🎓 Educational Value

This project is perfect for demonstrating:
- **Agentic AI concepts**: Tool use, reasoning, decision-making
- **State management**: Maintaining context in conversations
- **Database design**: Relational data with SQLAlchemy
- **Modular architecture**: Separation of concerns
- **Error handling**: Robust error management
- **UI/UX design**: Clean, professional interface

## 📝 Presentation Tips

When presenting this project:

1. **Explain the Agentic Loop**: Show how the agent decides which tool to call
2. **Demonstrate Tool Calls**: Show the agent activity panel
3. **Walk Through State**: Explain how state is maintained across messages
4. **Show Database**: Verify appointments are stored in SQLite
5. **Highlight Safety**: Mention emergency detection and no-diagnosis policy
6. **Discuss Architecture**: Explain modular design and separation of concerns

## 🤝 Contributing

This is a beginner-friendly project perfect for learning Agentic AI concepts. Feel free to:
- Add new tools
- Improve the agent's reasoning
- Enhance the UI
- Add more features

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author

Built as a demonstration of Agentic AI principles for healthcare appointment scheduling.

---

**Note**: This is a mock/demo application. Do not use for actual medical appointments or diagnoses.