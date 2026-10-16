# Verityn - Quick Start Guide (Phase 6)

Get Verityn Phase 6 running and view your first qualified leads in under 10 minutes!

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed  
- **MongoDB** (Atlas or local) - **Required**
- **Tavily API Key** - **Required for research** (get free key at [tavily.com](https://tavily.com))
- Windows PowerShell

## Quick Start

### Step 1: MongoDB Setup (2 minutes)

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

### Step 2: Get Tavily API Key (1 minute)

1. Go to [https://tavily.com](https://tavily.com)
2. Sign up for free account
3. Copy your API key from dashboard

### Step 3: Backend Setup (2 minutes)

```powershell
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Configure environment
# Copy .env.example to .env
cp .env.example .env

# Edit .env and set:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
# OR for local: MONGODB_URI=mongodb://localhost:27017
# MONGODB_DATABASE=verityn
# TAVILY_API_KEY=your_tavily_api_key_here

# Start the server
uvicorn app.main:app --reload
```

✅ Backend running at: http://localhost:8000  
✅ API Docs: http://localhost:8000/docs

### Step 4: Frontend Setup (2 minutes)

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

### Step 5: Create Your First Qualified Lead (5 minutes)

#### 5.1 Add a Company
1. Open http://localhost:5173
2. Check green "Connected" status in header
3. Click **"Companies"** tab
4. Click **"Add Company"**
5. Fill in:
   - Company name: `Acme Software Inc.`
   - Website: `https://acme-software.example.com`
   - Industry: `Software`
   - Country: `United States`
   - Region: `California`
   - Employees: `500`
6. Click **"Create Company"**

#### 5.2 Run Research
1. Find your company in the list
2. Click **"Research"** button
3. Click **"Start New Research"**
4. Wait ~10-30 seconds (watch status: pending → running → completed)
5. View research sources with URLs and snippets

#### 5.3 Create an ICP
1. Click **"ICPs"** tab
2. Click **"Create ICP"**
3. Fill in:
   - Name: `Mid-Market Software Companies`
   - Description: `Software companies with 100-1000 employees`
   - Industries: `Software, SaaS, Technology`
   - Countries: `United States, Canada`
   - Min Employees: `100`
   - Max Employees: `1000`
   - Qualification Threshold: `70`
   - Partial Threshold: `50`
   - Min Evidence Coverage: `60`
4. Click **"Create ICP"**

#### 5.4 Qualify the Company
1. Click **"Qualifications"** tab
2. Select your company
3. Select your ICP
4. Click **"Run Qualification"**
5. View results:
   - Outcome badge (qualified/partially/not qualified)
   - Score and evidence coverage
   - Criterion evaluations with evidence links

#### 5.5 View in Lead Intelligence
1. Click **"Leads"** tab
2. Select your ICP from dropdown
3. See your company in ranked leads table with:
   - Qualification outcome
   - Score and coverage
   - Qualification date
   - Research availability

✅ **You now have an end-to-end qualified lead!**

## Phase 6 Features

### 🎯 Lead Intelligence (NEW)
- **ICP Selector:** Choose which ICP to rank against
- **Lead Table:** View all qualified companies with scores
- **Sorting:** Click columns to sort by score, coverage, date, outcome
- **Filtering:** 
  - Company name search
  - Outcome filter (qualified, partial, not qualified, insufficient data)
  - Score range (min-max)
  - Evidence coverage threshold
  - Employee count range
  - Research availability
- **Pagination:** Browse results 25 at a time
- **Saved Views:** Save filter configurations for reuse

### 💾 Saved Views (NEW)
- **Save Current View:** Store your filter configuration
- **Load Saved View:** Reapply filters to current data
- **Manage Views:** View and delete saved configurations
- **Real-Time:** Views always show current data (no stale results)

### 🏢 Companies (Phase 1-2)
- Create, view, edit, delete companies
- Duplicate detection (name and website)
- Full data validation

### 🔬 Research (Phase 2-3)
- Tavily-powered web research
- Source evidence collection
- Research run history
- Status tracking (pending, running, completed, partial, failed)

### 📋 ICPs (Phase 3-4)
- Create ideal customer profiles
- Configure criteria: industry, country, employees, keywords
- Set thresholds: qualification, partial, evidence coverage
- Manage criteria weights

### ✅ Qualifications (Phase 4)
- Deterministic qualification engine
- Evidence-based scoring
- Criterion evaluations with explanations
- Historical qualification tracking
- ICP snapshots for reproducibility

### 📊 Dashboard (Phase 5)
- Real-time metrics
- Quick actions
- Navigation hub

## Test Phase 6 Features

### Test Filtering
1. Go to **Leads** tab
2. Click **"Show Filters"**
3. Set **Min Score**: 50
4. Select **Outcomes**: qualified, partially_qualified
5. Click **"Apply Filters"**
6. See filtered results

### Test Sorting
1. Click **"Score"** column header → sort descending
2. Click again → sort ascending
3. Try other columns: Coverage, Qualified, Outcome

### Test Saved Views
1. Configure some filters
2. Click **"Save Current View"**
3. Enter name: "High Quality Leads"
4. Enter description: "Qualified with score > 70"
5. Click **"Save View"**
6. Reset filters with **"Reset Filters"**
7. Select saved view from **"Load Saved View..."** dropdown
8. Filters reapply automatically

### Test with Multiple Companies
1. Add 5-10 companies in different industries
2. Run research on each
3. Create 2-3 different ICPs
4. Qualify all companies against all ICPs
5. View leads tab → see full ranking
6. Compare different ICPs using ICP selector

## Run Tests

### Backend Tests (All 118 should pass)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

Expected: **118 passed in ~1.8s** ✅

### Frontend Build
```powershell
cd frontend
npm run build
```

Expected: **✓ built in ~961ms, 321 KB bundle** ✅

## API Documentation

Interactive docs with try-it-out: **http://localhost:8000/docs**

Key endpoints:
- `GET /api/v1/leads?icp_id={id}` - Search leads with filters
- `POST /api/v1/saved-views` - Create saved view
- `GET /api/v1/saved-views` - List saved views
- All previous endpoints from Phases 1-5

## Common Issues

### "Database connection not available"
- Check MongoDB is running (local) or connection string is correct (Atlas)
- Verify `MONGODB_URI` in `backend/.env`
- Check firewall/network settings for Atlas

### "Tavily API key not configured"
- Add `TAVILY_API_KEY` to `backend/.env`
- Get free key at [tavily.com](https://tavily.com)
- Research won't work without valid API key

### "No ICPs Available" in Leads tab
- Create at least one ICP first (ICPs tab)
- ICPs are required to view leads
- Each lead is ranked against a specific ICP

### "No Leads Found"
- Ensure you have qualified at least one company (Qualifications tab)
- Check filters aren't too restrictive
- Try "Reset Filters" button

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check backend terminal for errors
- Verify `VITE_API_URL` in `frontend/.env.local` (default: http://localhost:8000)

### Research fails with timeout
- Check internet connection
- Verify Tavily API key is valid
- Some domains may block web scraping
- Try different companies

## Development Workflow

### Daily Development
1. Start backend: `cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Access app: http://localhost:5173
4. Make changes → auto-reload

### Testing Workflow
1. Make code changes
2. Run backend tests: `cd backend && pytest -v`
3. Build frontend: `cd frontend && npm run build`
4. Verify: 118 backend tests pass, frontend builds successfully

### Adding Test Data
Create realistic test companies to try different scenarios:
- **Tech Startup:** 50 employees, Software industry, US
- **Enterprise:** 10,000 employees, Technology, Multiple countries
- **Consulting Firm:** 500 employees, Professional Services, UK
- **SaaS Company:** 200 employees, SaaS, Canada

Then create ICPs targeting different segments:
- **SMB Tech:** 10-500 employees, Software/SaaS
- **Enterprise:** 5000+ employees, Technology
- **Mid-Market:** 500-5000 employees, Multiple industries

## Architecture Overview

```
User Flow:
1. Add Companies → 2. Run Research → 3. Create ICPs → 
4. Qualify Companies → 5. View Ranked Leads → 6. Save Views

Components:
- Companies: CRUD + validation + deduplication
- Research: Tavily integration + source storage
- ICPs: Criteria configuration + validation
- Qualifications: Deterministic scoring + evidence tracking
- Leads: Ranking + filtering + saved views
- Dashboard: Metrics + navigation
```

## What's Next?

### Explore More Features
- Try different ICP configurations
- Experiment with filter combinations
- Create multiple saved views for different use cases
- Compare how companies rank against different ICPs

### Optional Enhancements (Not Yet Implemented)
- Industry/country dropdown filters in UI
- Lead detail modal (click row to view)
- Dashboard lead metrics
- CSV export
- Batch qualification

### Read Documentation
- [README.md](README.md) - Full project documentation
- [PHASE6_COMPLETION_REPORT.md](PHASE6_COMPLETION_REPORT.md) - Phase 6 technical details
- [PHASE6_FRONTEND_COMPLETION_REPORT.md](PHASE6_FRONTEND_COMPLETION_REPORT.md) - Frontend implementation
- [docs/architecture.md](docs/architecture.md) - System architecture

---

## Quick Command Reference

### Backend
```powershell
# Start server
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Run tests
pytest -v

# Run specific test file
pytest tests/test_ranking_engine.py -v
```

### Frontend
```powershell
# Start dev server
cd frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Full System
```powershell
# Terminal 1: Backend
cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Access: http://localhost:5173
```

---

**🎉 Congratulations! You now have a complete B2B lead intelligence platform running!**

- ✅ 118 backend tests passing
- ✅ Full UI implementation (321 KB bundle)
- ✅ End-to-end workflow: Companies → Research → ICPs → Qualifications → Leads
- ✅ Advanced filtering and saved views
- ✅ Deterministic, evidence-based ranking

**Ready for production deployment!** 🚀

For detailed technical documentation, see [README.md](README.md)  
For Phase 6 implementation details, see [PHASE6_COMPLETION_REPORT.md](PHASE6_COMPLETION_REPORT.md)
