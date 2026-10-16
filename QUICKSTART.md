# Verityn - Quick Start Guide

Get Verityn running in under 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- Windows PowerShell

## Quick Start

### 1. Backend Setup (2 minutes)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

✅ Backend running at: http://localhost:8000

### 2. Frontend Setup (2 minutes)

Open a **new PowerShell window**:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:5173

### 3. Verify Everything Works

#### Test Backend API
```powershell
curl -UseBasicParsing http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "app_name": "Verityn",
  "status": "healthy",
  "version": "0.1.0"
}
```

#### View API Documentation

Open in browser: http://localhost:8000/docs

#### View Frontend Application

Open in browser: http://localhost:5173

You should see the Verityn dashboard with:
- "Research. Verify. Qualify." tagline
- Backend connection status (green)
- Feature cards for future functionality

## Run Tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

Expected: All 4 tests pass ✅

## Common Issues

### Backend won't start
- Make sure virtual environment is activated
- Check Python version: `python --version` (need 3.10+)
- Verify dependencies installed: `pip list`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -r node_modules; npm install`

### Tests fail
- Make sure you're in the backend directory
- Virtual environment must be activated
- Try reinstalling dependencies

### Port already in use
- Backend (8000): Change port with `uvicorn app.main:app --port 8001`
- Frontend (5173): Vite will automatically use the next available port

## What's Next?

- Read [README.md](README.md) for comprehensive documentation
- Review [docs/architecture.md](docs/architecture.md) for system design
- See [PHASE1_COMPLETION_REPORT.md](PHASE1_COMPLETION_REPORT.md) for implementation details

## Development Workflow

### Making Backend Changes

1. Edit files in `backend/app/`
2. Server auto-reloads (if using `--reload` flag)
3. Run tests: `pytest`
4. Check API docs: http://localhost:8000/docs

### Making Frontend Changes

1. Edit files in `frontend/src/`
2. Browser auto-refreshes
3. Build for production: `npm run build`

## Environment Variables (Optional)

### Backend
Copy `backend/.env.example` to `backend/.env` and customize if needed.

### Frontend
Copy `frontend/.env.example` to `frontend/.env.local` if you need to change the API URL.

---

**Ready to build!** 🚀

For detailed documentation, see [README.md](README.md)
