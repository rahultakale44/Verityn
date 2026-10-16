# Verityn - Quick Start Guide (Phase 2)

Get Verityn Phase 2 running in under 5 minutes!

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- **MongoDB** (Atlas or local) - **Required for Phase 2 features**
- Windows PowerShell

## Quick Start

### Step 1: MongoDB Setup (Required)

**Option A: MongoDB Atlas (Recommended)**
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create free account
2. Create a cluster (free tier available)
3. Create database user with read/write permissions
4. Add your IP to whitelist (or 0.0.0.0/0 for development)
5. Get connection string

**Option B: Local MongoDB**
1. Install MongoDB Community Edition
2. Start MongoDB service
3. Use connection string: `mongodb://localhost:27017`

### Step 2: Backend Setup (2 minutes)

```powershell
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Configure MongoDB
# Copy .env.example to .env
cp .env.example .env

# Edit .env and set your MongoDB connection:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
# OR
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DATABASE=verityn

# Start the server
uvicorn app.main:app --reload
```

✅ Backend running at: http://localhost:8000  
✅ API Docs: http://localhost:8000/docs

### Step 3: Frontend Setup (2 minutes)

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

### Step 4: Verify Everything Works

1. **Open Frontend:** http://localhost:5173
2. **Check Status:** Green "Connected" badge in header
3. **Add a Company:**
   - Click "Add Company" button
   - Fill in company name (required) and other fields
   - Click "Create Company"
4. **View Company:** Click "View" on the company
5. **Edit Company:** Click "Edit" and update fields
6. **Delete Company:** Click "Delete" and confirm

## What's New in Phase 2?

### Backend Features ✅
- **POST /api/v1/companies** - Create companies
- **GET /api/v1/companies** - List with pagination
- **GET /api/v1/companies/{id}** - Get single company
- **PATCH /api/v1/companies/{id}** - Update company
- **DELETE /api/v1/companies/{id}** - Delete company

### Frontend Features ✅
- Company list table with all records
- Add company form with validation
- View company details modal
- Edit company with pre-filled form
- Delete with confirmation
- Real-time success/error messages
- Backend connection status

### Data Features ✅
- Duplicate detection (name and website)
- Input validation (required fields, formats)
- MongoDB indexes for performance
- Automatic timestamps (created_at, updated_at)

## Test the API Directly

```powershell
# Create a company
curl -X POST http://localhost:8000/api/v1/companies `
  -H "Content-Type: application/json" `
  -d '{"company_name":"Acme Corp","website":"https://acme.com","industry":"Technology","employee_count":5000}'

# List companies
curl http://localhost:8000/api/v1/companies

# Check health
curl http://localhost:8000/api/v1/health
```

## Run Tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

Expected: **31 tests pass** ✅

## Common Issues

### "Database connection not available" error
- Check MongoDB is running (local) or connection string is correct (Atlas)
- Verify MONGODB_URI in backend/.env
- Check firewall/network settings for Atlas

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check backend terminal for errors
- Verify VITE_API_URL in frontend/.env.local (default: http://localhost:8000)

### Duplicate company error
- Company names are compared case-insensitive
- Websites are normalized (trailing slashes removed)
- This is expected behavior to prevent subtle duplicates

### Port already in use
- Backend (8000): Change with `uvicorn app.main:app --port 8001`
- Frontend (5173): Vite will auto-select next available port

## API Documentation

Interactive docs with try-it-out feature: http://localhost:8000/docs

## What's Next?

- Read [README.md](README.md) for full API documentation
- Review [PHASE2_COMPLETION_REPORT.md](PHASE2_COMPLETION_REPORT.md) for technical details
- Check [docs/architecture.md](docs/architecture.md) for system design

## Development Tips

### Backend Development
1. Make changes in `backend/app/`
2. Server auto-reloads with `--reload` flag
3. Run tests: `pytest`
4. View logs in terminal

### Frontend Development
1. Edit files in `frontend/src/`
2. Browser auto-refreshes
3. Check console for errors
4. Build for production: `npm run build`

### Adding Test Data
Use the UI or API to add companies. Example companies:
- Tech startup with 50 employees
- Enterprise software company with 10,000 employees
- Consulting firm with website and description

---

**Ready to manage B2B leads!** 🚀

For detailed documentation, see [README.md](README.md)  
For implementation details, see [PHASE2_COMPLETION_REPORT.md](PHASE2_COMPLETION_REPORT.md)
