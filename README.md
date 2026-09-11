# 🏥 Healthcare AI Appointment Assistant

An intelligent healthcare appointment booking system with **Retrieval-Augmented Generation (RAG)** powered by **n8n**, **Streamlit**, **Qdrant**, and **Hugging Face**. The assistant answers healthcare questions from approved hospital documents and handles appointment booking through structured tools.

---

## 🏗️ Architecture

```
User (Streamlit UI)
        │
        ▼
Streamlit Frontend (app.py)
        │  POST request
        ▼
n8n Webhook (Chat Trigger)
        │
        ▼
n8n AI Agent (LangChain Agent)
        │
        ├───► RAG Tool (search_knowledge_base) ──► Qdrant Vector Store
        │                                           ▲
        │                                           │
        │                                   Hugging Face Embeddings
        │
        ├───► find_department (Code Tool)
        ├───► find_doctors (Data Table)
        ├───► check_availability (Data Table)
        └───► book_appointment (Data Table)
        │
        ▼
Grounded Response → Streamlit UI
```

### RAG Flow
```
Approved Documents (.txt)
        │
        ▼
Document Loading → Text Chunking → Embeddings → Qdrant Vector Store
        │
        ▼
User Question → Similarity Search → Retrieved Context → Grounded LLM Response
```

---

## ✨ Features

- 🤖 **Agentic AI Workflow** — n8n orchestrates tool calling and decision-making
- 💬 **Natural Language Chat** — Streamlit-based conversational interface
- 🧠 **RAG Knowledge Base** — Answers grounded in approved healthcare documents
- 📅 **Appointment Booking** — Full booking workflow with confirmation
- 🏥 **Department Routing** — Symptom-based department identification
- 👨‍⚕️ **Doctor Search** — Find doctors by department
- 🔎 **Activity Display** — Real-time agent activity and RAG source attribution
- 🚨 **Emergency Detection** — Overrides all flows for urgent symptoms
- 💾 **SQLite Database** — Persistent appointment storage

---

## 📁 Project Structure

```
healthcare-agent/
├── app.py                          # Streamlit UI (connects to n8n webhook)
├── agent/                          # Local agent utilities (reference)
│   ├── agent.py
│   ├── state.py
│   └── prompts.py
├── tools/                          # Local tool utilities (reference)
│   ├── department_tool.py
│   ├── doctor_tool.py
│   ├── availability_tool.py
│   └── appointment_tool.py
├── database/                       # SQLite database layer (reference)
│   ├── models.py
│   ├── database.py
│   └── seed.py
├── utils/                          # Emergency detection, formatting
│   └── helpers.py
├── health-agent/                   # n8n-based project
│   ├── app.py                      # Streamlit UI → n8n webhook
│   ├── n8n/
│   │   ├── Healthcare AI Appointment Assistant(1).json   # Main workflow (RAG + booking)
│   │   └── RAG Document Ingestion Workflow.json          # Ingestion workflow
│   ├── rag/
│   │   ├── __init__.py
│   │   └── documents/                # Approved knowledge base
│   │       ├── hospital_info.txt
│   │       ├── departments.txt
│   │       ├── appointment_policy.txt
│   │       ├── preparation_guidelines.txt
│   │       ├── emergency_guidelines.txt
│   │       └── healthcare_faqs.txt
│   ├── utils/
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 What is RAG?

**Retrieval-Augmented Generation (RAG)** combines a retrieval system with a generative AI model. Instead of relying only on the LLM's pre-trained knowledge, RAG:

1. **Retrieves** relevant information from a curated knowledge base (vector database)
2. **Augments** the LLM prompt with the retrieved context
3. **Generates** a response grounded in the retrieved evidence

This ensures answers are accurate, up-to-date, and verifiable.

---

## 🤔 Why RAG in This Project?

- **Accuracy** — Answers come from approved hospital documents, not hallucinated text
- **Auditability** — Every answer cites its source document
- **Maintainability** — Update `rag/documents/*.txt` and re-run ingestion
- **Safety** — Medical information is constrained to vetted content
- **Local & Free** — Uses free Hugging Face embeddings and local Qdrant

---

## 🔄 RAG vs. Appointment Tools

| RAG (`search_knowledge_base`) | Appointment Tools |
|---|---|
| Hospital timings | `find_department` |
| Department descriptions | `find_doctors` |
| Doctor specializations | `check_availability` |
| Preparation guidelines | `book_appointment` |
| Appointment policies | |
| Cancellation policy | |
| Healthcare FAQs | |
| Emergency guidance | |

The AI Agent decides which tool to use based on user intent. Combined requests use both.

---

## 🚀 Installation

### 1. Prerequisites

- Python 3.8+
- Docker (for n8n and Qdrant)
- Google API key (for Gemini chat model)
- Hugging Face API key (free from https://huggingface.co)

### 2. Clone the Repository

```bash
git clone https://github.com/dharshinir11/health-agent.git
cd health-agent
```

### 3. Start Qdrant (Vector Database)

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 4. Start n8n (Backend)

```bash
docker run -d --name n8n \
  -p 5678:5678 \
  --link qdrant \
  -e N8N_HOST=localhost \
  -e N8N_PORT=5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

### 5. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
GOOGLE_API_KEY=your_google_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
N8N_WEBHOOK_URL=http://localhost:5678/webhook/chat/7a6d9ab6-6394-48d8-a7ee-501db63d1c13
QDRANT_URL=http://localhost:6333
```

---

## ⚙️ n8n Workflow Setup

### 1. Import Workflows

1. Open `http://localhost:5678` in your browser
2. Go to **Workflows → Import**
3. Import:
   - `health-agent/n8n/Healthcare AI Appointment Assistant(1).json`
   - `health-agent/n8n/RAG Document Ingestion Workflow.json`

### 2. Set Up Credentials

In n8n, configure:

- **Google Gemini API** — for the chat model
- **Hugging Face API** — for embeddings
- **Qdrant** — server: `http://host.docker.internal:6333`

### 3. Activate the Main Workflow

Toggle the **Active** switch on the main workflow.

### 4. Run RAG Ingestion

1. Open **"RAG Document Ingestion Workflow"**
2. Click **Execute Workflow**
3. This loads all `.txt` files from `health-agent/rag/documents/` into Qdrant

---

## 🎮 Running the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📖 How to Use

### Example: Informational Question

**User:** "What should I bring to my appointment?"

**Agent:** Uses `search_knowledge_base` → retrieves from `preparation_guidelines.txt` → responds with grounded answer and source.

### Example: Appointment Booking

**User:** "Find a General Medicine doctor tomorrow."

**Agent:** Uses appointment tools only:
1. `find_department` → General Medicine
2. `find_doctors` → list of doctors
3. `check_availability` → available slots
4. Asks for confirmation before `book_appointment`

### Example: Combined Request

**User:** "Tell me what documents I need and find a doctor tomorrow."

**Agent:** Uses **both** RAG and appointment tools.

### Example: Emergency

**User:** "I have severe chest pain."

**Agent:** Emergency detection triggers immediately — provides emergency guidance and advises calling 911.

---

## 🧪 Test Cases

| # | Query | Expected Behavior |
|---|-------|------------------|
| 1 | "What should I bring to my appointment?" | Uses RAG |
| 2 | "What is the cancellation policy?" | Uses RAG |
| 3 | "What does Dermatology treat?" | Uses RAG |
| 4 | "Find a General Medicine doctor tomorrow." | Uses appointment tools |
| 5 | "Tell me what documents I need and find a doctor tomorrow." | Uses both |
| 6 | "What is the insurance claim process?" | Says information unavailable |
| 7 | "I have severe chest pain." | Emergency guidance |

---

## 🛡️ Healthcare Safety Limitations

- **No Medical Diagnosis** — The agent never diagnoses conditions or prescribes medicines
- **No Fabricated Information** — RAG only returns content from approved documents
- **Emergency First** — Emergency keywords override all other flows
- **Confirmation Before Booking** — Appointments require explicit user confirmation
- **Source Attribution** — RAG responses cite the source document
- **Educational Use Only** — Not for real medical decisions

---

## 🔧 Agent Tools

### RAG Tool
- **`search_knowledge_base(query)`** — Searches approved healthcare documents via Qdrant vector similarity

### Appointment Tools
- **`find_department(symptoms)`** — Routes to correct department
- **`find_doctors(department)`** — Lists available doctors
- **`check_availability(doctorName)`** — Shows available time slots
- **`book_appointment(patientName, symptoms, department, doctorName, slotTime, preferredDate)`** — Confirms booking

---

## 📄 Adding New Knowledge Documents

1. Create a new `.txt` file in `health-agent/rag/documents/`
2. Add clear, structured content with headings
3. Re-run the ingestion workflow in n8n
4. The document is now searchable

Documents are split into **500-character chunks** with **50-character overlap**, tagged with metadata (source filename, document type, chunk index).

---

## 🔄 Running Everything (Quick Start)

```bash
# Terminal 1: Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# Terminal 2: Start n8n
docker run -d --name n8n -p 5678:5678 --link qdrant \
  -e N8N_HOST=localhost -e N8N_PORT=5678 \
  -v n8n_data:/home/node/.n8n n8nio/n8n

# Terminal 3: Install and run
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

---

## 🛑 Stopping Services

```bash
docker stop n8n qdrant
```

## 🔄 Restarting Services

```bash
docker start n8n qdrant
streamlit run app.py
```

---

## 📝 License

For educational purposes. Not for real medical use.

**Author:** Built as a demonstration of Agentic AI + RAG for healthcare appointment scheduling.
