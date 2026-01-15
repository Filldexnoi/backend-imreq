# ImReq API - Quick Setup Guide

ระบบวิเคราะห์และปรับปรุง Software Requirements ตามมาตรฐาน ISO/IEC/IEEE 29148

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.10+
- Docker (for PostgreSQL database)
- Gemini API Key ([Get here](https://ai.google.dev/))

---

## 📦 Installation Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd imreq-api
```

### 2. Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**If `requirements.txt` doesn't exist, install manually:**
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-multipart google-generativeai python-dotenv
```

### 4. Setup Database with Docker

**Install Docker:**
- Download from: https://www.docker.com/get-started

**Option 1: Using docker-compose (Recommended)**
```bash
# Start database (will auto-run init.sql on first start)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

**Schema is created automatically!** The `init.sql` file will run when the database starts for the first time.

**Option 2: Using docker run + manual schema**
```bash
# Start database
docker run -d \
  --name imreq-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=imreq \
  -p 5433:5432 \
  postgres:14

# Wait a few seconds for database to start, then run schema
docker exec -i imreq-postgres psql -U postgres -d imreq < init.sql
```

**Verify database is running:**
```bash
docker ps
# Should see imreq-postgres container running
```

**Verify tables are created:**
```bash
# Connect to database
docker exec -it imreq-postgres psql -U postgres -d imreq

# List tables
\dt

# Should see: projects, origin_requirements, analyzed_requirements, 
#             suggested_requirements, selected_requirements

# Exit
\q
```

### 5. Configure Environment Variables

**Copy `.env.example` to `.env`:**
```bash
# Windows (Command Prompt):
copy .env.example .env

# Windows (PowerShell) / macOS / Linux:
cp .env.example .env
```

**Edit `.env` file and add your Gemini API key:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5433/imreq
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

**Get Gemini API Key:**
1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Copy and paste into `.env` file

### 6. Run Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify Installation
Open browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

Should see:
```json
{
  "message": "Welcome to ImReq API with PostgreSQL - Now with Suggestions & Export!"
}
```

---

## 📁 Required Project Structure

Make sure you have these files/folders:
```
imreq-api/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── init.sql                # Database schema (auto-runs with docker-compose)
├── docker-compose.yml      # Docker configuration
├── .env.example            # Environment template
├── .env                    # Your config (create from .env.example)
├── requirements.txt        # Python dependencies
├── routers/
│   ├── __init__.py
│   ├── analyze.py
│   ├── suggestions.py
│   └── export.py
└── services/
    ├── __init__.py
    ├── gemini_service.py
    └── suggestion_service.py
```

**Create missing directories:**
```bash
mkdir -p routers services
touch routers/__init__.py services/__init__.py
```

---

## 📊 Database Schema

The database consists of 5 main tables (defined in `init.sql`):

### 1. **projects**
Stores project information
- `id` (UUID, Primary Key)
- `title` (VARCHAR) - Project name
- `description` (TEXT) - Project description
- `created_at`, `updated_at` (TIMESTAMP)

### 2. **origin_requirements**
Original requirements uploaded by users
- `id` (UUID, Primary Key)
- `req_id` (VARCHAR) - Requirement identifier
- `project_id` (UUID) → References projects
- `module` (VARCHAR) - Module/category name
- `requirement` (TEXT) - Requirement text
- Indexed on: `req_id`, `project_id`

### 3. **analyzed_requirements**
Analysis results from ISO 29148 evaluation
- `id` (UUID, Primary Key)
- `req_id` (VARCHAR)
- `project_id` (UUID) → References projects
- `module` (VARCHAR)
- `score` (VARCHAR) - e.g., "7/9"
- `characteristics` (JSONB) - Array of passed criteria
- `requirement` (TEXT)
- `evaluation` (JSONB) - Failed criteria with reasons
- Indexed on: `req_id`, `project_id`

### 4. **suggested_requirements**
AI-generated improvement suggestions
- `id` (UUID, Primary Key)
- `req_id` (VARCHAR)
- `project_id` (UUID) → References projects
- `module` (VARCHAR)
- `original_requirement` (TEXT)
- `suggested_requirement` (TEXT) - Improved version
- `original_score` (VARCHAR)
- `improvements` (JSONB) - What was fixed per criterion
- Indexed on: `req_id`, `project_id`

### 5. **selected_requirements**
User-selected final requirements
- `id` (UUID, Primary Key)
- `req_id` (VARCHAR)
- `project_id` (UUID) → References projects
- `module` (VARCHAR)
- `requirement` (TEXT)
- Indexed on: `req_id`, `project_id`

**Schema Features:**
- ✅ All tables use UUID primary keys
- ✅ Foreign keys with `ON DELETE CASCADE`
- ✅ Indexes for fast lookups
- ✅ `pgcrypto` extension for UUID generation
- ✅ JSONB for flexible data storage

---

## 🎯 Basic Usage Flow

```bash
# 1. Create Project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"My Project","description":"Test"}'

# Response: {"id":"<project-id>"}

# 2. Upload Requirements CSV
curl -X POST http://localhost:8000/api/projects/<project-id>/originrequirements \
  -F "file=@requirements.csv" \
  -F 'mapping={"req_id":"ID","module":"Module","requirement":"Requirement"}'

# 3. Analyze Requirements
curl -X POST http://localhost:8000/api/analyze-parallel/projects/<project-id>/requirements

# 4. Generate Suggestions
curl -X POST http://localhost:8000/api/suggestions/projects/<project-id>/generate

# 5. Export Results
curl -o report.csv \
  http://localhost:8000/api/export/projects/<project-id>/comparison/csv
```

---

## 🛠️ Troubleshooting

### Database Connection Error

**Using docker-compose:**
```bash
# Check status
docker-compose ps

# Start database
docker-compose up -d

# View logs
docker-compose logs postgres

# Restart
docker-compose restart postgres

# Stop and remove (data will be preserved in volume)
docker-compose down

# Stop and remove including data
docker-compose down -v
```

**Using docker run:**
```bash
# Check if Docker container is running
docker ps

# If not running, start it
docker start imreq-postgres

# Check container logs
docker logs imreq-postgres

# Restart container if needed
docker restart imreq-postgres
```

### Stop/Remove Database Container

**Using docker-compose:**
```bash
# Stop (data preserved)
docker-compose stop

# Stop and remove (data preserved in volume)
docker-compose down

# Stop, remove, and delete all data
docker-compose down -v

# Recreate fresh database (schema will auto-run)
docker-compose down -v
docker-compose up -d
```

**Using docker run:**
```bash
# Stop container
docker stop imreq-postgres

# Remove container (data will be lost)
docker rm imreq-postgres

# Remove and recreate fresh database
docker rm -f imreq-postgres
docker run -d \
  --name imreq-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=imreq \
  -p 5433:5432 \
  postgres:14

# Run schema
docker exec -i imreq-postgres psql -U postgres -d imreq < init.sql
```

### Manually Run Schema (if needed)

If tables are not created or you need to reset:

```bash
# Run init.sql
docker exec -i imreq-postgres psql -U postgres -d imreq < init.sql

# Or connect and paste SQL manually
docker exec -it imreq-postgres psql -U postgres -d imreq
# Then paste contents of init.sql
```

### Port Already in Use
```bash
# Use different port
uvicorn main:app --reload --port 8001

# Or kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Module Not Found
```bash
# Make sure venv is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Error
```bash
# Check .env file exists and has correct key
cat .env

# Or set directly in terminal
export GEMINI_API_KEY=your_actual_key
```

---

## 📊 CSV Format for Upload

**requirements.csv example:**
```csv
req_id,module,requirement
REQ-001,Authentication,ระบบต้องสามารถ login ได้
REQ-002,Payment,ระบบต้องรองรับการชำระเงิน
REQ-003,Reporting,ระบบต้องสร้างรายงาน
```

---

## 🔑 Get Gemini API Key

1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create/select Google Cloud project
4. Generate API key
5. Copy to `.env` file

---

## 📝 Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects` | GET | List projects |
| `/api/projects` | POST | Create project |
| `/api/projects/{project_id}/originrequirements` | POST | Create Origin Requirement |
| `/api/projects/{project_id}/originrequirements` | GET | Get Origin Requirement |
| `/api/analyze-parallel/projects/{project_id}/requirements` | POST | Create Analyze Requirement |
| `/api/analyze-parallel/projects/{project_id}/requirements` | GET | Get Analyze Requirement |
| `/api/suggestions/projects/{project_id}/requirements` | POST | Create Suggest Requirement |
| `/api/suggestions/projects/{project_id}/requirements` | GET | GET Suggest Requirement |
| `/api/export/projects/{project_id}/selectedrequirements/csv` | GET | Export Selected Requirement |
| `/docs` | GET | API Documentation |

---

## 🎉 Quick Start Summary

```bash
# 1. Clone repository
git clone <repository-url>
cd imreq-api

# 2. Setup Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Start PostgreSQL with Docker Compose
docker-compose up -d
# Schema (init.sql) runs automatically on first start!

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run server
uvicorn main:app --reload

# 6. Done! Open browser
# http://localhost:8000/docs
```

**Alternative (without docker-compose):**
```bash
# Step 3 alternative:
docker run -d \
  --name imreq-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=imreq \
  -p 5433:5432 \
  postgres:14

# Run schema manually
docker exec -i imreq-postgres psql -U postgres -d imreq < init.sql
```

Server running at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

---

## 💡 Quick Commands Reference

```bash
# Database (Docker Compose) - Recommended
docker-compose up -d            # Start database
docker-compose down             # Stop database (keep data)
docker-compose down -v          # Stop and delete data
docker-compose ps               # Check status
docker-compose logs postgres    # View logs

# Database (Docker)
docker ps                       # Check if database is running
docker start imreq-postgres     # Start database
docker stop imreq-postgres      # Stop database
docker logs imreq-postgres      # View database logs

# Python Environment
source venv/bin/activate        # Activate venv (macOS/Linux)
venv\Scripts\activate           # Activate venv (Windows)

# Run server
uvicorn main:app --reload                              # Development
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4  # Production

# Database access (optional)
docker exec -it imreq-postgres psql -U postgres -d imreq

# View API docs
open http://localhost:8000/docs  # macOS
start http://localhost:8000/docs # Windows
```

---

**Version**: 1.0.0  
**Status**: Ready to Use ✅
