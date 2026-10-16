# Verityn

**Evidence-Driven B2B Lead Intelligence Platform**

## Overview

Verityn helps B2B technology consulting companies research potential customer companies, evaluate them against configurable Ideal Customer Profiles (ICP), explain qualification scores using supporting evidence, and produce a prioritized shortlist for human review.

### Current Status: Phase 2 - Company Data Management

This is the Phase 2 implementation, which includes:
- ✅ FastAPI backend with health check endpoint
- ✅ MongoDB Atlas-compatible configuration with indexes
- ✅ **Full CRUD API for company records**
- ✅ **Company data validation and duplicate detection**
- ✅ **React + TypeScript UI for company management**
- ✅ Project structure and development environment
- ✅ Comprehensive tests (31 tests, all passing)

**Phase 2 New Features:**
- ✅ Create, read, update, and delete company records
- ✅ List companies with pagination
- ✅ Duplicate detection (normalized company name and website)
- ✅ Input validation (required fields, URL format, employee count)
- ✅ Professional UI with company list, forms, and detail view
- ✅ Error handling and user feedback

**Not yet implemented:**
- ❌ AI-powered lead research (planned for Phase 3+)
- ❌ LangGraph agent workflows (planned for Phase 3+)
- ❌ Gemini API integration (planned for Phase 3+)
- ❌ Web research and data collection (planned for Phase 3+)
- ❌ ICP qualification scoring (planned for Phase 4+)
- ❌ Evidence tracking and review (planned for Phase 5+)

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

Expected result: **31 tests passing**

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
  "version": "0.2.0"
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
APP_VERSION=0.2.0
DEBUG=false

# MongoDB Configuration - REQUIRED for Phase 2 functionality
MONGODB_URI=mongodb://localhost:27017
# For MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=verityn
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

## Future Phases

- **Phase 3:** LangGraph agent framework and Gemini API integration
- **Phase 4:** Web research and data collection pipeline
- **Phase 5:** ICP configuration and qualification scoring
- **Phase 6:** Evidence tracking and review interface
- **Phase 7:** Production deployment and monitoring

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
