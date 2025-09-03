 # 🧭 Nomad AI — Personal AI Travel Planner (Portfolio Project)

Nomad AI is a personal project showcasing an end‑to‑end AI travel planner. It turns a short natural‑language prompt into a personalized, day‑by‑day itinerary with suggested places, activities, and visuals. Built to demonstrate practical LLM orchestration, retrieval, and a clean developer experience.

---

## ✨ Highlights
- **Conversational planning**: Chat your preferences, constraints, and trip style.
- **Itinerary generation**: Day‑wise plans with maps/POIs and time budgeting.
- **Retrieval‑augmented suggestions**: Curated places and activities using embeddings.
- **Multimodal output**: Optional image generation to visualize the trip.
- **Local‑first demo**: Simple environment variables and a single command to run.

---

## 🧰 Tech Stack
- **Frontend**: Next.js, Tailwind CSS
- **Backend**: FastAPI (Python)
- **AI/IR**: OpenAI/Anthropic LLMs, Sentence Transformers + FAISS
- **Data**: PostgreSQL (optional), local JSON/CSV seeds for demo

---

## 🗺️ How It Works (Short)
1. You describe your trip in natural language (e.g., “5‑day budget trip to Japan with food markets”).
2. The backend extracts constraints and user intent, enriches with contextual signals (season, budget, distance windows).
3. A retrieval step surfaces relevant POIs/activities via vector search.
4. The itinerary builder arranges days, balances categories, adds timing and travel estimates.
5. The UI displays a clean, editable plan; you can refine via follow‑ups.

---

## 🚀 Quick Start (Local Demo)

### Prerequisites
- Python 3.9+
- Node.js 18+
- An LLM API key (e.g., OpenAI) stored in `.env`

### 1) Install dependencies
```bash
# from repository root
npm install
pip install -r requirements.txt
```

### 2) Configure environment
```bash
cp .env.example .env
# then edit .env and add your API key(s)
```

### 3) Run the app
```bash
npm run dev
```

That spins up the frontend and backend for a local demo.

---

## 🧪 Example Prompts
- “Plan a romantic 4‑day trip to Paris under $1,000 with a focus on art and coffee.”
- “I have 3 days in Seoul in November. Include street food and fall views.”
- “7‑day family‑friendly Italy trip with minimal walking and gelato stops.”

---

## 🔍 Selected Implementation Notes
- **LLM Orchestration**: Tools/steps modeled as small, testable functions; retries and guards for determinism.
- **RAG**: Sentence‑Transformers embeddings with FAISS for fast local retrieval.
- **Itinerary Balancer**: Simple heuristics to spread categories, cap travel time, and avoid duplicates.
- **Extensibility**: Swap LLM providers or add new data sources without changing the planner core.

---

## 📦 Project Structure (high level)
```
NomadAI/
  ├─ nomadai-frontend/        # Next.js UI
  └─ nomadai-backend/         # FastAPI services and agents
```

---

## 🛠️ Future Improvements
- Calendar export and offline PDF
- Lightweight preferences profile with cold‑start questions
- Map view with clustering and travel‑time overlays
- Basic cost estimation and daily budget guardrails

---

## 👋 About This Project
This is a personal learning/build project to practice real‑world AI product patterns: LLM prompting, retrieval, simple scheduling, and a pragmatic full‑stack setup. Feedback welcome!

— Built by Omkar

