# ImReq API - Complete Setup Guide

## 💻 Installation

### Step 1: Clone/Download Project

```bash
# If using git
git clone <repository-url>
cd imreq-api

# Or just download and extract the files
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run installer and follow instructions
- Default port: 5432

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database

```bash
# Access PostgreSQL
# Windows/Linux:
sudo -u postgres psql
# macOS:
psql postgres

# Create database and user
CREATE DATABASE imreq_db;
CREATE USER imreq_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE imreq_db TO imreq_user;

# Exit
\q
```

### Step 3: Verify Connection

```bash
# Test connection
psql -h localhost -U imreq_user -d imreq_db

# Should connect successfully, then exit:
\q
```

---

## ⚙️ Configuration

### Step 1: Create `.env` File

Create a file named `.env` in the project root:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql://imreq_user:your_secure_password@localhost:5432/imreq_db

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Step 2: Create `database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://imreq_user:password@localhost:5432/imreq_db"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 3: Get Gemini API Key

1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create new project or select existing
4. Generate API key
5. Copy and paste into `.env` file

---

## 📁 Project Structure

```
imreq-api/
├── main.py                      # Main FastAPI application
├── database.py                  # Database configuration
├── models.py                    # SQLAlchemy models
├── schemas.py                   # Pydantic schemas
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── routers/
│   ├── __init__.py
│   ├── analyze.py              # Analysis endpoints
│   ├── suggestions.py          # Suggestion endpoints
│   └── export.py               # Export endpoints
├── services/
│   ├── __init__.py
│   ├── gemini_service.py       # Gemini AI service
│   └── suggestion_service.py   # Suggestion service
└── README.md                    # This file
```

### Create Required Directories

```bash
mkdir routers services
touch routers/__init__.py services/__init__.py
```

---

## 🏃 Running the Application

### Step 1: Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Load Environment Variables

```bash
# Windows (Command Prompt)
set GEMINI_API_KEY=your_key_here
set DATABASE_URL=postgresql://imreq_user:password@localhost:5432/imreq_db

# Windows (PowerShell)
$env:GEMINI_API_KEY="your_key_here"
$env:DATABASE_URL="postgresql://imreq_user:password@localhost:5432/imreq_db"

# macOS/Linux
export GEMINI_API_KEY=your_key_here
export DATABASE_URL=postgresql://imreq_user:password@localhost:5432/imreq_db
```

Or use python-dotenv:
```bash
pip install python-dotenv
```

Add to main.py:
```python
from dotenv import load_dotenv
load_dotenv()  # Add at the top
```

### Step 3: Run Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Verify Installation

Open browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

You should see:
```json
{
  "message": "Welcome to ImReq API with PostgreSQL - Now with Suggestions & Export!"
}
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Quick Start Flow

```bash
# 1. Create Project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Project",
    "description": "Project description"
  }'

# Response: {"id": "project-uuid"}

# 2. Upload Requirements (CSV)
curl -X POST http://localhost:8000/api/projects/{project_id}/originrequirements \
  -F "file=@requirements.csv" \
  -F 'mapping={"req_id":"ID","module":"Module","requirement":"Requirement"}'

# 3. Analyze Requirements
curl -X POST http://localhost:8000/api/analyze-parallel/projects/{project_id}/requirements

# 4. Generate Suggestions
curl -X POST http://localhost:8000/api/suggestions/projects/{project_id}/generate

# 5. Export Results
curl -o report.csv http://localhost:8000/api/export/projects/{project_id}/comparison/csv
```

### Main Endpoints

#### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project

#### Requirements
- `GET /api/projects/{id}/originrequirements` - Get origin requirements
- `POST /api/projects/{id}/originrequirements` - Upload requirements (CSV)

#### Analysis
- `POST /api/analyze-parallel/projects/{id}/requirements` - Analyze all requirements
- `POST /api/analyze-parallel/projects/{id}/requirements/{req_id}` - Analyze single requirement
- `WS /api/analyze-parallel/projects/{id}/requirements/ws` - Real-time analysis

#### Suggestions
- `POST /api/suggestions/projects/{id}/generate` - Generate suggestions
- `GET /api/suggestions/projects/{id}` - Get all suggestions
- `GET /api/suggestions/projects/{id}/requirements/{req_id}` - Get single suggestion
- `WS /api/suggestions/projects/{id}/generate/ws` - Real-time suggestion generation

#### Export
- `GET /api/export/projects/{id}/origin-requirements/csv` - Export origin requirements
- `GET /api/export/projects/{id}/analyzed-requirements/csv` - Export analysis results
- `GET /api/export/projects/{id}/suggested-requirements/csv` - Export suggestions
- `GET /api/export/projects/{id}/comparison/csv` - Export full comparison ⭐

---

## 🔄 Workflow

### Complete Workflow Example

```
1. Create Project
   ↓
2. Upload Requirements (CSV)
   ↓
3. Analyze Requirements
   - Checks 9 ISO criteria
   - Scores each requirement
   - Identifies failed criteria
   ↓
4. Generate Suggestions
   - Only for requirements with score < 9/9
   - Provides improved versions
   - Explains what was fixed
   ↓
5. Export Results
   - Download comparison report
   - Review suggestions
   - Implement improvements
```

### CSV Format for Upload

**requirements.csv:**
```csv
req_id,module,requirement
REQ-001,Authentication,ระบบต้องสามารถ login ได้
REQ-002,Payment,ระบบต้องรองรับการชำระเงิน
REQ-003,Reporting,ระบบต้องสร้างรายงาน
```

**Column Mapping:**
```json
{
  "req_id": "req_id",
  "module": "module",
  "requirement": "requirement"
}
```

---

## 🎯 ISO 29148 - 9 Quality Criteria

The system evaluates requirements against these criteria:

1. **Appropriate** - ระดับความละเอียดเหมาะสม
2. **Complete** - ครบถ้วนสมบูรณ์
3. **Conforming** - ตรงตามมาตรฐาน
4. **Correct** - ถูกต้องแม่นยำ
5. **Feasible** - ทำได้จริง
6. **Necessary** - จำเป็นต้องมี
7. **Singular** - ระบุสิ่งเดียว
8. **Unambiguous** - ไม่คลุมเครือ
9. **Verifiable** - วัดผลได้

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check if PostgreSQL is running
# Windows:
services.msc  # Look for PostgreSQL

# macOS:
brew services list

# Linux:
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql  # Linux
brew services start postgresql@14  # macOS
```

#### 2. Gemini API Error

**Error:**
```
ValueError: GEMINI_API_KEY not found in environment variables
```

**Solution:**
```bash
# Set environment variable
export GEMINI_API_KEY=your_key_here

# Or add to .env file
echo "GEMINI_API_KEY=your_key_here" >> .env
```

#### 3. Module Import Error

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Then install dependencies
pip install -r requirements.txt
```

#### 4. Port Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Use different port
uvicorn main:app --port 8001

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

#### 5. CSV Upload Error

**Error:**
```
KeyError: 'req_id' ใน CSV
```

**Solution:**
- Check CSV column names match your mapping
- Ensure no extra spaces in column names
- Verify CSV encoding (should be UTF-8)

```python
# Correct mapping
{
  "req_id": "ID",        # Your CSV column name
  "module": "Module",    # Your CSV column name
  "requirement": "Desc"  # Your CSV column name
}
```

#### 6. CORS Error (Frontend)

**Error:**
```
Access to fetch blocked by CORS policy
```

**Solution:**
Add your frontend URL to CORS origins in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://your-frontend-url.com"  # Add your URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Performance Tips

### 1. Adjust Parallel Workers

```python
# In gemini_service.py or suggestion_service.py
gemini_service = GeminiService(max_workers=10)  # Default
gemini_service = GeminiService(max_workers=20)  # Faster, more API calls
gemini_service = GeminiService(max_workers=5)   # Slower, fewer API calls
```

### 2. Database Connection Pool

```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Default: 5
    max_overflow=20,       # Default: 10
    pool_pre_ping=True     # Verify connections
)
```

### 3. Production Deployment

```bash
# Use multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🔒 Security Considerations

### 1. Environment Variables

**Never commit `.env` to git:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 2. Database Security

```sql
-- Use strong passwords
-- Limit user privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO imreq_user;

-- Don't grant SUPERUSER or CREATE DATABASE unless needed
```

### 3. API Rate Limiting

Consider adding rate limiting for production:
```bash
pip install slowapi

# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
```

---

## 📈 Monitoring & Logging

### Enable Detailed Logging

```python
# Add to main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('imreq.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor API Usage

```bash
# Check logs
tail -f imreq.log

# Monitor Gemini API usage
# Go to: https://makersuite.google.com/app/apikey
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/

# Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Test project"}'

# List projects
curl http://localhost:8000/api/projects
```

### Testing with Postman

1. Import API from: http://localhost:8000/openapi.json
2. Create environment with `base_url` = http://localhost:8000
3. Test each endpoint

---

## 📝 Example Usage Scenarios

### Scenario 1: New Project Setup

```bash
# 1. Create project
PROJECT_ID=$(curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"Mobile App","description":"Requirements for mobile app"}' \
  | jq -r '.id')

# 2. Upload requirements
curl -X POST http://localhost:8000/api/projects/$PROJECT_ID/originrequirements \
  -F "file=@requirements.csv" \
  -F 'mapping={"req_id":"ID","module":"Module","requirement":"Requirement"}'

# 3. Analyze
curl -X POST http://localhost:8000/api/analyze-parallel/projects/$PROJECT_ID/requirements

# 4. Generate suggestions
curl -X POST http://localhost:8000/api/suggestions/projects/$PROJECT_ID/generate

# 5. Export report
curl -o final_report.csv \
  http://localhost:8000/api/export/projects/$PROJECT_ID/comparison/csv

echo "Report saved to final_report.csv"
```

### Scenario 2: Re-analyze After Updates

```bash
# Re-analyze all requirements
curl -X POST http://localhost:8000/api/analyze-parallel/projects/$PROJECT_ID/requirements

# Re-generate suggestions
curl -X POST http://localhost:8000/api/suggestions/projects/$PROJECT_ID/generate
```

---

## 🆘 Getting Help

### Resources

- **API Documentation**: http://localhost:8000/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Gemini AI Docs**: https://ai.google.dev/docs

### Common Commands Cheat Sheet

```bash
# Start server
uvicorn main:app --reload

# Check database
psql -U imreq_user -d imreq_db

# View logs
tail -f imreq.log

# Check Python packages
pip list

# Test API
curl http://localhost:8000/

# Export requirements
curl -o output.csv http://localhost:8000/api/export/projects/{id}/comparison/csv
```

---

## 📜 License & Credits

**Developed with:**
- FastAPI - Web framework
- SQLAlchemy - Database ORM
- PostgreSQL - Database
- Google Gemini AI - AI analysis
- ISO/IEC/IEEE 29148 - Quality standard

---

## 🎉 Quick Start Summary

```bash
# 1. Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary google-generativeai

# 2. Setup database
createdb imreq_db

# 3. Create .env file
echo "GEMINI_API_KEY=your_key" > .env
echo "DATABASE_URL=postgresql://user:pass@localhost/imreq_db" >> .env

# 4. Run server
uvicorn main:app --reload

# 5. Open browser
# http://localhost:8000/docs

# 6. Start using!
```

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Status**: Production Ready ✅
