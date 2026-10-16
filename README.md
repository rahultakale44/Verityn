# Verityn

**Evidence-Driven B2B Lead Intelligence Platform**

## Overview

Verityn helps B2B technology consulting companies research potential customer companies, evaluate them against configurable Ideal Customer Profiles (ICP), explain qualification scores using supporting evidence, and produce a prioritized shortlist for human review.

### Current Status: Phase 6 - Lead Intelligence & Ranking ✅

This is the Phase 6 implementation, which includes a complete, production-ready lead intelligence platform with:

**Phase 1-2 Features:**
- ✅ FastAPI backend with comprehensive API
- ✅ MongoDB with proper indexes and connection handling
- ✅ Full CRUD operations for company records
- ✅ Company data validation and duplicate detection

**Phase 3 Features:**
- ✅ Tavily-powered web research integration
- ✅ Research run tracking and history
- ✅ Source evidence collection and storage
- ✅ Research status management (pending, running, completed, partial, failed)

**Phase 4 Features:**
- ✅ ICP (Ideal Customer Profile) configuration and management
- ✅ Deterministic qualification engine with 5 criteria types
- ✅ Evidence-based scoring with transparency
- ✅ ICP snapshots for historical reproducibility
- ✅ Qualification outcomes: qualified, partially_qualified, not_qualified, insufficient_data

**Phase 5 Features:**
- ✅ **Dashboard View:** Real-time metrics from API, quick actions, welcome section
- ✅ **Company Workspace:** Unified interface for all company operations and research
- ✅ **ICP Management UI:** Full CRUD interface for ICP configuration
- ✅ **Qualification Workflow:** Select company + ICP, run qualification, view detailed results
- ✅ **Qualification History:** View past qualifications with full criterion evaluations
- ✅ **Evidence Display:** Clickable source URLs, snippets, and detailed explanations
- ✅ **Tab Navigation:** Intuitive flow between Dashboard, Companies, ICPs, and Qualifications
- ✅ **Responsive Design:** Professional UI using Tailwind CSS conventions

**Phase 6 Features (NEW):**
- ✅ **Lead Intelligence UI:** Complete 733-line component for lead viewing and management
- ✅ **Deterministic Ranking:** Rank leads by score, coverage, timestamp, or outcome
- ✅ **Advanced Filtering:** Filter by outcome, score range, coverage, employees, name, research status
- ✅ **Saved Views:** Create, load, and manage custom filter configurations
- ✅ **Smart Sorting:** Click column headers to sort with visual indicators
- ✅ **Pagination:** Browse large result sets with smart page numbering
- ✅ **Aggregation Pipeline:** Efficient MongoDB queries with indexes
- ✅ **Real-Time Data:** Saved views reapply to current data (no stale results)

**Test Coverage:**
- ✅ 118 backend tests (all passing in 1.83s)
- ✅ Frontend production build successful (961ms, 321 KB bundle)
- ✅ Full API coverage across all endpoints
- ✅ 13 new ranking engine tests

**Not yet implemented:**
- ❌ Industry/country filter dropdowns in UI (backend supports)
- ❌ Lead detail modal (full qualification view)
- ❌ Dashboard lead metrics (global counts)
- ❌ Export functionality (CSV/PDF)
- ❌ Batch qualification operations
- ❌ Multi-user authentication and permissions

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
│   │   ├── main.py                      # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py            # Health check endpoint
│   │   │       └── companies.py         # Company CRUD endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py                # Configuration management
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py               # MongoDB connection
│   │   │   └── companies.py             # Company data access layer
│   │   └── models/
│   │       ├── __init__.py
│   │       └── company.py               # Company data models
│   ├── tests/
│   │   ├── test_health.py               # Health endpoint tests
│   │   ├── test_mongodb.py              # Database tests
│   │   └── test_companies.py            # Company API tests
│   ├── requirements.txt                 # Python dependencies
│   └── .env.example                    # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── App.tsx                      # Main application component
│   │   ├── main.tsx                     # Application entry point
│   │   ├── index.css                    # Global styles with Tailwind
│   │   ├── api/
│   │   │   └── client.ts                # Typed API client
│   │   └── components/
│   │       ├── CompanyList.tsx          # Company list component
│   │       ├── CompanyForm.tsx          # Company create/edit form
│   │       └── CompanyDetail.tsx        # Company detail modal
│   ├── public/                          # Static assets
│   ├── package.json                     # Node dependencies
│   ├── vite.config.ts                   # Vite configuration
│   ├── tailwind.config.js               # Tailwind CSS configuration
│   ├── postcss.config.js                # PostCSS configuration
│   └── .env.example                    # Environment variable template
├── docs/
│   └── architecture.md                  # Architecture documentation
├── .gitignore
└── README.md
```

## Prerequisites

- **Python:** 3.11+ (currently using 3.10.0)
- **Node.js:** 18+ (currently using 24.13.1)
- **npm:** Latest version
- **MongoDB:** Atlas account or local instance (required for Phase 2 company features)

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
   Edit `.env` to set your MongoDB connection string:
   ```
   MONGODB_URI=mongodb://localhost:27017
   # Or for MongoDB Atlas:
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DATABASE=verityn
   ```

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
   The default `VITE_API_URL=http://localhost:8000` should work for local development.

4. **Start the development server:**
   ```powershell
   npm run dev
   ```

   The application will be available at: `http://localhost:5173`

## MongoDB Setup

### Option 1: MongoDB Atlas (Recommended)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Create a database user with read/write permissions
4. Whitelist your IP address (or use 0.0.0.0/0 for development)
5. Get your connection string and update `MONGODB_URI` in `.env`

### Option 2: Local MongoDB

1. Download and install MongoDB Community Edition
2. Start MongoDB service
3. Use `MONGODB_URI=mongodb://localhost:27017` in `.env`

## Running Tests

### Backend Tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

Run with verbose output:
```powershell
pytest -v
```

Run specific test file:
```powershell
pytest tests/test_companies.py -v
```

Expected result: **118 tests passing** (Company: 27, Health: 3, ICP: 14, MongoDB: 1, Qualification Engine: 27, Qualifications: 10, Ranking Engine: 13, Research: 23)

### Frontend Build Verification

```powershell
cd frontend
npm run build
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
  "version": "0.6.0"
}
```

### Company Management Endpoints

#### Create Company

**Endpoint:** `POST /api/v1/companies`

**Request Body:**
```json
{
  "company_name": "Acme Corporation",
  "website": "https://acme.com",
  "industry": "Technology",
  "description": "A leading technology company",
  "headquarters_country": "United States",
  "headquarters_region": "California",
  "employee_count": 5000
}
```

**Response (201 Created):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "company_name": "Acme Corporation",
  "website": "https://acme.com",
  "industry": "Technology",
  "description": "A leading technology company",
  "headquarters_country": "United States",
  "headquarters_region": "California",
  "employee_count": 5000,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Validation:**
- `company_name`: Required, 1-200 characters, trimmed
- `website`: Optional, must be valid HTTP/HTTPS URL
- `industry`: Optional, max 100 characters
- `description`: Optional, max 2000 characters
- `headquarters_country`: Optional, max 100 characters
- `headquarters_region`: Optional, max 100 characters
- `employee_count`: Optional, must be non-negative integer

**Duplicate Detection:**
- Returns 409 if a company with the same normalized name exists
- Returns 409 if a company with the same normalized website exists
- Normalization: case-insensitive, whitespace collapsed

#### List Companies

**Endpoint:** `GET /api/v1/companies?limit=50&offset=0`

**Query Parameters:**
- `limit`: Number of records to return (1-100, default 50)
- `offset`: Number of records to skip (default 0)

**Response:**
```json
{
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "company_name": "Acme Corporation",
      "website": "https://acme.com",
      "industry": "Technology",
      "description": "A leading technology company",
      "headquarters_country": "United States",
      "headquarters_region": "California",
      "employee_count": 5000,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

Companies are sorted by creation date, newest first.

#### Get Company

**Endpoint:** `GET /api/v1/companies/{company_id}`

**Response:** Single company object (same format as create response)

**Errors:**
- 404: Company not found
- 422: Invalid ObjectId format

#### Update Company

**Endpoint:** `PATCH /api/v1/companies/{company_id}`

**Request Body (all fields optional):**
```json
{
  "company_name": "Updated Name",
  "employee_count": 6000
}
```

**Response:** Updated company object

**Notes:**
- Only provided fields are updated
- `updated_at` is automatically set
- Cannot update `id`, `created_at`
- Duplicate detection applies

**Errors:**
- 404: Company not found
- 409: Update would create duplicate
- 422: Validation error or invalid ID

#### Delete Company

**Endpoint:** `DELETE /api/v1/companies/{company_id}`

**Response:** 204 No Content (on success)

**Errors:**
- 404: Company not found
- 422: Invalid ObjectId format

### Interactive API Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Environment Variables

### Backend (.env)

```env
APP_NAME=Verityn
APP_VERSION=0.6.0
DEBUG=false

# MongoDB Configuration - REQUIRED
MONGODB_URI=mongodb://localhost:27017
# For MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=verityn

# Tavily API Configuration - REQUIRED for research features
TAVILY_API_KEY=your_tavily_api_key_here
TAVILY_MAX_RESULTS=5
TAVILY_SEARCH_TIMEOUT=10
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
```

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
   .\venv\Scripts\Activate.ps1
   pytest -v
   ```

4. **Access the Application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## MongoDB Indexes

The application automatically creates the following indexes on startup:

1. **Unique index on `normalized_name`** - Prevents duplicate company names
2. **Unique sparse index on `normalized_website`** - Prevents duplicate websites
3. **Index on `created_at` (descending)** - Optimizes list queries

## Project Principles

- **Factual Reliability:** Evidence-based decisions only
- **Traceable Evidence:** Complete source attribution
- **Explainable Scoring:** Clear reasoning for all decisions
- **Input Validation:** Strict validation and security
- **Maintainable Code:** Clean, typed, well-documented code

## Future Enhancements

### Short Term
- Industry/country filter dropdowns in UI
- Lead detail modal (full qualification view)
- Dashboard lead metrics (global counts)
- Page size selector (25, 50, 100)
- CSV export functionality

### Medium Term
- Batch qualification operations
- Multi-user authentication
- Saved view sharing
- Advanced filter logic (OR, NOT operators)
- Lead activity timeline

### Long Term
- Real-time updates (WebSocket)
- CRM integration (Salesforce, HubSpot)
- Lead scoring trends over time
- ICP performance comparison
- Automated lead nurturing workflows

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
