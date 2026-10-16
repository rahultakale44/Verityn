# Phase 6 Implementation Plan

## Repository Analysis Summary

### Existing Schema & Data Models
- **Company**: Has `industry`, `headquarters_country`, `employee_count`, timestamps
- **ICP**: Complete configuration with criteria weights, thresholds
- **Qualification**: Has `score`, `evidence_coverage`, `outcome`, `qualified_at`, `company_id`, `icp_id`
- **MongoDB Collections**: companies, icps, qualifications, research_runs, source_evidence

### Existing Indexes
- Qualifications: `(company_id, qualified_at desc)`, `icp_id`, `outcome`
- Companies: `normalized_name unique`, `normalized_website unique sparse`, `created_at desc`

### Available Filter Fields
From existing schemas:
- Company: name, industry, headquarters_country, employee_count, website
- Qualification: score (Optional[float]), evidence_coverage (Optional[float]), outcome, qualified_at
- ICP: id for selection

### Gaps Identified
1. **No global qualification listing** - current API only lists by company_id
2. **No ranking/sorting service** - need to implement deterministic ranking
3. **No filter API** - need company + qualification filtering
4. **No saved views storage** - need new collection + CRUD

---

## Implementation Plan

### 1. Backend: Ranking Engine Service
**File**: `backend/app/services/ranking_engine.py` (NEW)

**Purpose**: Deterministic lead ranking using latest qualification per company+ICP

**Functions**:
- `get_latest_qualification_per_company(icp_id, company_ids)` → dict[company_id, qualification]
- `rank_leads(qualifications, sort_by, sort_direction)` → sorted list
- Stable tie-breaking: qualified_at DESC, then company_id ASC

**Sort Options**:
- score (default DESC)
- evidence_coverage (default DESC)
- qualified_at (default DESC) 
- outcome (custom order: qualified > partially_qualified > not_qualified > insufficient_data)

**Edge Cases**:
- Handle None scores (insufficient_data)
- Companies with no qualification excluded by default
- Never invent scores

### 2. Backend: Lead Data Access Layer
**File**: `backend/app/db/leads.py` (NEW)

**Purpose**: Query leads with filters, pagination, ranking

**Functions**:
- `get_ranked_leads(filters, sort_by, sort_direction, limit, offset)` → (leads, total)
- Uses aggregation pipeline for efficiency
- Joins latest qualification per company+ICP

**Filters**:
- `icp_id` (required)
- `outcome` (optional list)
- `min_score`, `max_score` (optional)
- `min_evidence_coverage` (optional)
- `industries` (optional list, from company)
- `countries` (optional list, from company)
- `min_employees`, `max_employees` (optional)
- `company_name_search` (optional, case-insensitive partial match)
- `has_research` (optional bool - check if source_evidence exists)

### 3. Backend: Saved Views Data Models
**File**: `backend/app/models/saved_view.py` (NEW)

**Models**:
- `SavedViewFilters` - validated filter configuration
- `SavedViewCreate` - name, description, filters
- `SavedViewUpdate` - optional fields
- `SavedViewResponse` - full saved view with timestamps

**Validation**:
- Name required, max 200 chars
- Description optional, max 1000 chars
- Filters validated against allowed fields
- icp_id required in filters

### 4. Backend: Saved Views Data Access
**File**: `backend/app/db/saved_views.py` (NEW)

**Functions**:
- `create_saved_view(user_id, name, description, filters)` → SavedViewResponse
- `list_saved_views(user_id, limit, offset)` → (views, total)
- `get_saved_view(view_id, user_id)` → SavedViewResponse
- `update_saved_view(view_id, user_id, data)` → SavedViewResponse
- `delete_saved_view(view_id, user_id)` → None

**Note**: user_id placeholder for future auth, use default for now

**Indexes**:
- `created_at DESC`
- Consider `name` for uniqueness per user

### 5. Backend: API Routes - Leads
**File**: `backend/app/api/routes/leads.py` (NEW)

**Endpoints**:
- `GET /api/v1/leads?icp_id={id}&outcome=qualified&min_score=70&...`
  - Query params for all filters
  - Returns: `LeadListResponse` with ranked leads
  - Includes: company data + latest qualification + pagination

**Response Schema**: `LeadResponse` combines company + qualification

### 6. Backend: API Routes - Saved Views
**File**: `backend/app/api/routes/saved_views.py` (NEW)

**Endpoints**:
- `POST /api/v1/saved-views` - Create saved view
- `GET /api/v1/saved-views` - List saved views
- `GET /api/v1/saved-views/{id}` - Get saved view
- `PATCH /api/v1/saved-views/{id}` - Update saved view
- `DELETE /api/v1/saved-views/{id}` - Delete saved view

### 7. Backend: Main App Integration
**File**: `backend/app/main.py` (MODIFY)

**Changes**:
- Import and include leads router
- Import and include saved_views router
- Call ensure_saved_views_indexes() on startup

### 8. Frontend: API Client Types & Methods
**File**: `frontend/src/api/client.ts` (MODIFY)

**Add Types**:
- `LeadFilters`
- `LeadResponse`
- `LeadListResponse`
- `SavedView`, `SavedViewCreate`, `SavedViewUpdate`, `SavedViewListResponse`

**Add Methods**:
- `searchLeads(filters, sortBy, sortDirection, limit, offset)`
- `createSavedView(data)`
- `listSavedViews(limit, offset)`
- `getSavedView(id)`
- `updateSavedView(id, data)`
- `deleteSavedView(id)`

### 9. Frontend: Lead Intelligence Component
**File**: `frontend/src/components/LeadIntelligence.tsx` (NEW)

**Features**:
- ICP selector dropdown
- Filter panel (collapsible):
  - Outcome checkboxes
  - Score range sliders
  - Evidence coverage slider
  - Industry multi-select (from API)
  - Country multi-select (from API)
  - Employee range inputs
  - Company name search
  - Research availability toggle
- Sort controls (column headers or dropdown)
- Results table:
  - Company name (clickable to detail)
  - Industry, Country, Employees
  - Outcome badge
  - Score, Coverage (with N/A handling)
  - Actions: View details, View research, Re-qualify
- Pagination controls
- Empty, loading, error states
- Save current filters as view
- Load saved view dropdown

### 10. Frontend: Saved Views Manager
**File**: `frontend/src/components/SavedViewsManager.tsx` (NEW)

**Features**:
- List saved views
- Create new view (modal with name, description)
- Load view (applies filters to LeadIntelligence)
- Update view (save current filters to existing view)
- Delete view (with confirmation)

### 11. Frontend: Navigation Update
**File**: `frontend/src/App.tsx` (MODIFY)

**Changes**:
- Add "Leads" tab to navigation (between Qualifications and Dashboard)
- Wire up LeadIntelligence component
- Integrate with existing error/success messaging

### 12. Backend: Tests
**Files**:
- `backend/tests/test_ranking_engine.py` (NEW)
- `backend/tests/test_leads.py` (NEW)
- `backend/tests/test_saved_views.py` (NEW)

**Coverage**:
- Ranking determinism and tie-breaking
- Filter combinations
- Pagination edge cases
- Latest qualification selection
- Missing scores handling
- Saved view CRUD and validation

### 13. Documentation
**File**: `PHASE6_COMPLETION_REPORT.md` (NEW)

---

## MongoDB Indexes to Add

### saved_views collection
- `created_at DESC` - for listing
- Consider: `(user_id, name) UNIQUE` - for future multi-user

### Existing collections - no new indexes needed
- qualifications already has `(company_id, qualified_at DESC)` for latest selection
- companies already has fields for filtering

---

## Implementation Order

1. Backend ranking engine service ✓
2. Backend saved view models ✓
3. Backend saved views data access ✓
4. Backend leads data access (uses ranking) ✓
5. Backend API routes (leads, saved views) ✓
6. Backend main app integration ✓
7. Backend tests ✓
8. Frontend API client updates ✓
9. Frontend LeadIntelligence component ✓
10. Frontend navigation integration ✓
11. Frontend build verification ✓
12. Completion report ✓

---

## Key Design Decisions

1. **Latest Qualification**: Use `(company_id, icp_id, qualified_at DESC)` to get latest
2. **No Qualification Handling**: Exclude from results by default, explicit filter to show
3. **Stable Sort**: Primary sort + qualified_at DESC + company_id ASC
4. **Filter Validation**: Backend validates all filter values
5. **Saved Views**: Store filter config, not results (apply to current data)
6. **User ID**: Placeholder field (all users see all views for now)
7. **Research Availability**: Check if any source_evidence records exist for company

---

## Risks & Mitigations

**Risk**: Large qualification dataset slows pagination
**Mitigation**: Use MongoDB aggregation with proper indexes, limit to 100 per page

**Risk**: Missing qualification scores break ranking
**Mitigation**: Handle None explicitly, exclude from score-based ranking

**Risk**: Duplicate company+ICP qualifications
**Mitigation**: Use qualified_at DESC to get latest, stable tie-break

**Risk**: Frontend filter state complexity
**Mitigation**: Centralize filter state, use URL params for shareability (future)

---

## Out of Scope (Not Implementing)

- User authentication/multi-tenancy (placeholder only)
- Filter URL parameters / deep linking
- Export to CSV/PDF
- Batch operations
- Complex collaboration features
- Real-time updates
- Advanced analytics dashboard
