# 🏋️ FitCoach

**FitCoach** is an AI-powered fitness coaching platform that generates personalized workout programs, tracks training progress, and provides a conversational fitness coach with long-term memory.

Built as a full-stack AI application using **FastAPI**, **Vue 3**, **Supabase**, **LangChain**, **OpenAI**, and **ChromaDB**.

---

## ✨ Features

### 🤖 AI Workout Generation

- Personalized workout programs based on:
  - fitness goal
  - experience level
  - available equipment
  - injuries & limitations
- Retrieval-Augmented Generation (RAG) using a curated exercise database
- Automatic validation of generated programs
- Balanced weekly volume and duplicate exercise prevention

---

### 💬 AI Fitness Coach

- Persistent conversational coach
- Long-term memory of user preferences
- Workout history awareness
- Personalized fitness advice
- Context-aware conversations across sessions

---

### 📈 Progress Tracking

- Workout logging
- Exercise history
- Weekly activity dashboard
- Program persistence
- User profiles

---

### 🔐 Authentication

- Secure authentication with Supabase Auth
- Protected routes
- User-specific data isolation
- Persistent sessions

---

## 🛠 Tech Stack

### Frontend

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router
- Tailwind CSS

### Backend

- FastAPI
- Python
- Pydantic

### AI

- OpenAI GPT-5
- LangChain
- ChromaDB
- OpenAI Embeddings (`text-embedding-3-small`)

### Database

- Supabase
- PostgreSQL

### Deployment

- Frontend → Vercel
- Backend → Railway

---

# 🏗 Architecture

```text
               Vue 3 Frontend
                      │
                      ▼
               FastAPI Backend
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
 Supabase Auth   OpenAI GPT      Chroma Vector DB
      │               │                │
      └───────────────┼────────────────┘
                      ▼
                Exercise Library
```

---

# 🧠 AI Workflow

```
User Profile
      │
      ▼
Training Assessment
      │
      ▼
Exercise Retrieval (Chroma)
      │
      ▼
GPT Program Generation
      │
      ▼
Program Validation
      │
      ▼
Workout Plan
```

---

# 🚀 Getting Started

## Clone the repository

```bash
git clone https://github.com/dahlia276/fitcoach.git

cd fitcoach
```

---

## Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env`

```env
SUPABASE_URL=

SUPABASE_KEY=

OPENAI_API_KEY=
```

Run the API

```bash
uvicorn main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Create a `.env`

```env
VITE_API_URL=http://localhost:8000

VITE_SUPABASE_URL=

VITE_SUPABASE_ANON_KEY=
```

---

# 🌍 Live Demo

Frontend

> https://fitcoach-nine-beryl.vercel.app

Backend

> Railway

---

# 📂 Project Structure

```
fitcoach
│
├── backend
│   ├── app
│   │   ├── ai
│   │   ├── auth
│   │   ├── models
│   │   ├── services
│   │   └── scripts
│   │
│   └── main.py
│
├── frontend
│   ├── src
│   │   ├── views
│   │   ├── stores
│   │   ├── router
│   │   ├── api
│   │   └── components
│   │
│   └── ...
│
└── README.md
```

---

# 🔍 AI Design

FitCoach combines several AI techniques:

- Retrieval-Augmented Generation (RAG)
- Structured LLM outputs
- Prompt engineering
- Deterministic program validation
- Conversational memory
- Tool calling (fitness coach)

Instead of allowing the LLM to freely invent workouts, FitCoach retrieves exercises from a curated vector database before generating a structured training plan.

---

# 🧪 Future Improvements

- Nutrition planning
- Progressive overload recommendations
- Calendar integration
- Apple Health / Google Fit sync
- Wearables integration
- Exercise video demonstrations
- Multi-agent coaching system
