# Verityn

**Evidence-Driven B2B Lead Intelligence Platform**

## Overview

Verityn helps B2B technology consulting companies research potential customer companies, evaluate them against configurable Ideal Customer Profiles (ICP), explain qualification scores using supporting evidence, and produce a prioritized shortlist for human review.

### Current Status: Phase 1 - Foundation Only

This is the Phase 1 implementation, which includes:
- ✅ FastAPI backend with health check endpoint
- ✅ MongoDB Atlas-compatible configuration
- ✅ React + TypeScript + Vite frontend with Tailwind CSS
- ✅ Project structure and development environment
- ✅ Basic tests and documentation

**Not yet implemented:**
- ❌ AI-powered lead research (planned for Phase 2+)
- ❌ LangGraph agent workflows (planned for Phase 2+)
- ❌ Gemini API integration (planned for Phase 2+)
- ❌ Web research and data collection (planned for Phase 2+)
- ❌ ICP qualification scoring (planned for Phase 2+)
- ❌ Evidence tracking and review (planned for Phase 2+)

## Technology Stack

### Backend
- **Language:** Python 3.11+ (currently using 3.10.0)
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **Database:** MongoDB (PyMongo 4.6.0)
- **Configuration:** Pydantic Settings 2.1.0
- **Testing:** Pytest 7.4.3

### Frontend
- **Framework:** React 19.2.8
- **Language:** TypeScript 6.0.2
- **Build Tool:** Vite 8.3.0
- **Styling:** Tailwind CSS 3.x
- **Package Manager:** npm

## Repository Structure

```
verityn/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── health.py    # Health check endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py        # Configuration management
│   │   └── db/
│   │       ├── __init__.py
│   │       └── mongodb.py       # MongoDB connection
│   ├── tests/
│   │   ├── test_health.py       # Health endpoint tests
│   │   └── test_mongodb.py      # Database tests
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── main.tsx            # Application entry point
│   │   └── index.css           # Global styles with Tailwind
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   ├── postcss.config.js       # PostCSS configuration
│   └── .env.example           # Environment variable template
├── docs/
│   └── architecture.md         # Architecture documentation
├── .gitignore
└── README.md
```

## Prerequisites

- **Python:** 3.11+ (currently using 3.10.0)
- **Node.js:** 18+ (currently using 24.13.1)
- **npm:** Latest version
- **MongoDB:** Atlas account or local instance (optional for Phase 1)

## Setup Instructions (Windows PowerShell)

### Backend Setup

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   ```powershell
   cp .env.example .env
   ```
   Edit `.env` if you need to customize MongoDB connection settings.

6. **Start the backend server:**
   ```powershell
   python -m app.main
   ```
   
   Or with reload for development:
   ```powershell
   uvicorn app.main:app --reload
   ```

   The API will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```powershell
   cd frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Configure environment variables (optional):**
   ```powershell
   cp .env.example .env.local
   ```

4. **Start the development server:**
   ```powershell
   npm run dev
   ```

   The application will be available at: `http://localhost:5173`

## Running Tests

### Backend Tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest
```

Run with verbose output:
```powershell
pytest -v
```

Run with coverage:
```powershell
pytest --cov=app
```

### Frontend Build Verification

```powershell
cd frontend
npm run build
```

## Environment Variables

### Backend (.env)

```env
APP_NAME=Verityn
APP_VERSION=0.1.0
DEBUG=false

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=verityn
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
```

## API Documentation

### Health Check Endpoint

**Endpoint:** `GET /api/v1/health`

**Description:** Returns application health status, name, and version. Does not check external dependencies.

**Response:**
```json
{
  "app_name": "Verityn",
  "status": "healthy",
  "version": "0.1.0"
}
```

**Example:**
```powershell
curl http://localhost:8000/api/v1/health
```

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development Workflow

1. **Start Backend:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload
   ```

2. **Start Frontend (in a new terminal):**
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Run Tests:**
   ```powershell
   cd backend
   pytest
   ```

## MongoDB Configuration

MongoDB is configured but not required for Phase 1. The application will:
- Initialize a MongoDB client on startup (with lazy connection)
- Handle connection failures gracefully
- Not crash if MongoDB is unavailable
- Report application health independently of database status

To use MongoDB:
1. Set up a MongoDB Atlas cluster or local MongoDB instance
2. Update `MONGODB_URI` in backend/.env
3. The connection will be established automatically

## Project Principles

- **Factual Reliability:** Evidence-based decisions only
- **Traceable Evidence:** Complete source attribution
- **Explainable Scoring:** Clear reasoning for all decisions
- **Input Validation:** Strict validation and security
- **Maintainable Code:** Clean, typed, well-documented code

## Future Phases

- **Phase 2:** LangGraph agent framework and Gemini API integration
- **Phase 3:** Web research and data collection pipeline
- **Phase 4:** ICP configuration and qualification scoring
- **Phase 5:** Evidence tracking and review interface
- **Phase 6:** Production deployment and monitoring

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
