# Sakhi Health Navigator

An agentic AI system that helps women find the right healthcare specialist near them. Sakhi is a **health navigator, not a diagnostic tool**. It understands symptoms in natural language (English, Hindi, Marathi), routes to the correct care pathway from 22+ specialties, and returns ranked providers with contact info, ratings, and Google Maps directions.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-purple)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss)

## How It Works

1. **Patient describes symptoms** in their own words, in any language
2. **Intake agent** extracts structured medical context via LLM
3. **Safety layer** checks for crisis red flags (domestic violence, self-harm, substance abuse)
4. **Routing agent** maps symptoms to the correct specialty from 22+ care pathways
5. **Research agent** finds real providers via Composio Google Maps API
6. **Ranking agent** scores providers using deterministic weighted math (not LLM)
7. **Results** are returned with scores, ratings, addresses, phone numbers, and WhatsApp share links

## Architecture

```
Patient Message
      |
  [Intake Agent]  ─── LLM extracts symptoms, location, preferences
      |
  [Safety Check]  ─── Deterministic red-flag rules (rules.yaml)
      |
  [Routing Agent] ─── LLM maps to specialty (gynecology, dermatology, etc.)
      |
  [Research Agent] ── Composio Google Maps → real provider data
      |
  [Ranking Agent]  ── Weighted scoring: 35% specialty + 25% expertise
      |                + 15% insurance + 15% location + 10% availability
  [Response]       ── Formatted results with WhatsApp deep links
```

## Safety Constraints

- **Never diagnoses** diseases or conditions
- **Never prescribes** medication
- **Never fabricates** provider names, credentials, availability, or insurance
- Uses "may be appropriate" instead of diagnosis claims
- Uses "highest-ranked based on selected criteria" instead of "best doctor"
- Crisis detection triggers emergency helpline numbers (Women Helpline, Police, Ambulance)

## Tech Stack

**Backend:** Python 3.11+, FastAPI, LangGraph, LangChain-Groq, MongoDB Atlas, Composio, Pydantic

**Frontend:** React 19, Vite 8, Tailwind CSS 4, Framer Motion, Lucide React, React Router v7

**AI/ML:** Groq LLM (via LangChain), Sentence Transformers (embeddings), LangGraph (agent orchestration)

## Project Structure

```
├── backend/
│   └── app/
│       ├── agents/           # Intake, routing, research, ranking agents
│       ├── api/routes.py     # FastAPI chat endpoint with language detection
│       ├── db/               # MongoDB models, engine, embeddings, seed data
│       ├── domain/           # Scoring engine, taxonomy, scoring_weights.yaml
│       ├── graph/            # LangGraph pipeline (builder.py, state.py)
│       ├── llm/              # LLM client + prompts (intake, routing, followup, provider_qa)
│       ├── safety/           # Red-flag detection, crisis rules (rules.yaml)
│       ├── main.py           # FastAPI app entry
│       └── schemas.py        # Pydantic request/response models
├── frontend/
│   └── src/
│       ├── components/       # ChatWindow, ProviderCard, ProviderModal, CrisisBanner,
│       │                     # Logo, LanguageToggle, LocationDetector
│       ├── pages/            # Landing (hero + phone mockup), ChatApp (chat + provider panel)
│       ├── api.js            # Backend fetch wrapper
│       └── index.css         # Tailwind + custom styles
├── tests/                    # pytest suite (agents, scoring, safety, taxonomy, db)
├── pyproject.toml            # Python deps (uv)
└── .env.example              # Environment variable template
```

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+
- MongoDB (local or Atlas)
- Groq API key
- Composio API key (for Google Maps provider search)

### 1. Clone and install backend

```bash
git clone https://github.com/YOUR_USERNAME/sakhi-health-navigator.git
cd sakhi-health-navigator

# Install Python dependencies
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your actual keys:

```
GROQ_API_KEY=your_groq_api_key
LLM_MODEL=openai/gpt-oss-120b
COMPOSIO_API_KEY=your_composio_key
MONGO_URI=mongodb://localhost:27017
MONGO_DB=sakhi
```

### 3. Install frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Run

**Backend** (from project root):
```bash
uv run uvicorn backend.app.main:app --reload --port 8000
```

**Frontend** (from project root):
```bash
npm --prefix frontend run dev
```

Open http://localhost:3000 in your browser.

### 5. Run tests

```bash
uv run pytest
```

## Features

- **Multilingual support:** English, Hindi, Marathi with auto-detection (Devanagari script counting + Marathi marker words)
- **22+ care pathways:** Gynecology, dermatology, psychiatry, orthopedics, cardiology, and more
- **Deterministic ranking:** Weighted scoring with configurable weights (scoring_weights.yaml)
- **Real provider data:** Live Google Maps results via Composio API
- **WhatsApp sharing:** One-tap share provider details with GPS coordinates
- **Crisis detection:** Automatic emergency helpline display for domestic violence, self-harm, substance abuse
- **Responsive UI:** Production-quality design with phone mockup hero, animated score bars, mobile bottom sheet
- **Session management:** OrderedDict cache (max 200 sessions) for conversation continuity

## API

### POST /api/chat

```json
{
  "conversation": "Patient: I have been having irregular periods\nSakhi: ...",
  "session_id": "optional-existing-session-id"
}
```

**Response:**
```json
{
  "reply": "I found specialists near you...",
  "session_id": "uuid",
  "ranked_providers": [...],
  "needs_more_info": false,
  "crisis": false,
  "whatsapp_link": "https://wa.me/?text=..."
}
```
