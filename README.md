# ImReq API - Backend Setup Guide

ระบบวิเคราะห์และปรับปรุง Software Requirements ตามมาตรฐาน ISO/IEC/IEEE 29148 (FastAPI + PostgreSQL)

## 🚀 Quick Start

### Prerequisites
- Python 3.11 (see `runtime.txt`)
- Docker + Docker Compose (for PostgreSQL)
- An API key for either **OpenAI** or **Gemini** (whichever `LLM_PROVIDER` you choose)

---

## 📦 Installation Steps

### 1. Go to the backend folder
```bash
cd backend-imreq
```

### 2. Create & activate a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL with Docker Compose
```bash
docker-compose up -d
```

This starts two containers (see `docker-compose.yml`):
- **`rag-postgres`** — Postgres (pgvector image) on port `5433`, database `ragdb`. `init.sql` runs automatically the first time the container starts and creates all tables (`users`, `projects`, `origin_requirements`, `analyzed_requirements`, `suggested_requirements`, `selected_requirements`).
- **`rag-pgadmin`** — pgAdmin UI on http://localhost:5050 (login: `admin@admin.com` / `admin`) for browsing the DB if you want a GUI.

Check status / logs:
```bash
docker-compose ps
docker-compose logs -f db
```

Verify tables were created:
```bash
docker exec -it rag-postgres psql -U postgres -d ragdb -c "\dt"
```

### 5. Configure environment variables
```bash
# Windows (PowerShell):
copy .env.example .env
# macOS/Linux:
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/ragdb
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# LLM Provider: "openai" (default) or "gemini"
LLM_PROVIDER=openai

# OpenAI (used when LLM_PROVIDER=openai)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Gemini (used when LLM_PROVIDER=gemini)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash

# Suggestion quality control
MIN_SIMILARITY=0.5
MAX_RETRIES=3
```

Notes:
- `DATABASE_URL` must match the Docker Compose credentials (`postgres`/`postgres`, port `5433`, db `ragdb`) unless you change `docker-compose.yml`.
- `CORS_ORIGINS` should include the frontend's dev URL (`http://localhost:5173` for Vite) and/or its deployed URL.
- You only need an API key for the provider you set in `LLM_PROVIDER`.
- Get an OpenAI key at https://platform.openai.com/api-keys, a Gemini key at https://ai.google.dev/.

### 6. Run the server
```bash
python run.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify installation
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

---

## 📁 Project Structure
```
backend-imreq/
├── main.py                 # FastAPI app, CORS, router registration
├── database.py             # SQLAlchemy engine/session
├── models.py                # ORM models
├── schemas.py                # Pydantic schemas
├── embedding.py
├── init.sql                 # DB schema (auto-runs via docker-compose)
├── docker-compose.yml        # Postgres (pgvector) + pgAdmin
├── requirements.txt
├── run.py                    # Dev entrypoint (uvicorn)
├── routers/
│   ├── auth.py                # /api/auth
│   ├── analyze.py              # /api/analyze-parallel
│   ├── suggestion.py            # /api/suggestions
│   ├── export.py                # /api/export
│   └── model_test.py             # /api/model-test
├── services/
│   ├── auth.py                  # password hashing / JWT
│   ├── llm_provider.py           # OpenAI/Gemini switch
│   ├── gemini_service.py
│   └── similarity_utils.py
└── tests/
```

---

## 📊 Database Schema

Defined in `init.sql`, all tables use UUID primary keys with `pgcrypto`:

| Table | Purpose |
|---|---|
| `users` | Auth accounts (email/username/hashed password) |
| `projects` | Projects, owned by a `user_id`, with optional `requirement_template` / `reference_files` |
| `origin_requirements` | Requirements uploaded by users |
| `analyzed_requirements` | ISO 29148 evaluation results (`score`, `characteristics`, `evaluation`) |
| `suggested_requirements` | AI-generated improved requirements (supports splitting via `is_split`/`split_requirements`) |
| `selected_requirements` | User's final chosen requirements |

All child tables reference `projects` (and `projects` references `users`) with `ON DELETE CASCADE`.

---

## 📝 Key Endpoints

| Endpoint prefix | Router | Description |
|---|---|---|
| `/api/auth` | `auth.py` | Register / login (JWT) |
| `/api/projects` | `main.py` | CRUD for projects & origin requirements |
| `/api/analyze-parallel` | `analyze.py` | Run ISO 29148 analysis on requirements |
| `/api/suggestions` | `suggestion.py` | Generate & fetch AI suggestions |
| `/api/export` | `export.py` | Export results/comparison as CSV |
| `/api/model-test` | `model_test.py` | Ad-hoc LLM/model testing |
| `/docs` | — | Swagger UI |

---

## 🛠️ Troubleshooting

### Database connection error
```bash
docker-compose ps
docker-compose logs db
docker-compose restart db
```

### Reset the database (drops all data)
```bash
docker-compose down -v
docker-compose up -d   # init.sql re-runs on fresh volume
```

### Port already in use
```bash
uvicorn main:app --reload --port 8001

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Module not found
```bash
# Make sure venv is activated, then:
pip install -r requirements.txt
```

### LLM/API key error
Check that `LLM_PROVIDER` in `.env` matches the key you filled in (`OPENAI_API_KEY` or `GEMINI_API_KEY`).

---

## 🧪 Running Tests
```bash
pytest
```
(config in `pytest.ini`; coverage output goes to `htmlcov/`)

---

**Runtime**: Python 3.11.9 (see `runtime.txt`) · Deployable to Vercel (see `.vercelignore`)
