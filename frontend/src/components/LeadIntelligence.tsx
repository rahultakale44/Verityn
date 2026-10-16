import { useState, useEffect } from 'react';
import {
  apiClient,
  type ICP,
  type LeadResponse,
  type LeadFilters,
  type SavedView,
  type SavedViewCreate,
  type SortField,
  type SortDirection,
} from '../api/client';

interface LeadIntelligenceProps {
  onError: (error: string) => void;
  onSuccess: (message: string) => void;
}

export function LeadIntelligence({ onError, onSuccess }: LeadIntelligenceProps) {
  // Core state
  const [icps, setICPs] = useState<ICP[]>([]);
  const [leads, setLeads] = useState<LeadResponse[]>([]);
  const [savedViews, setSavedViews] = useState<SavedView[]>([]);
  const [selectedICP, setSelectedICP] = useState<ICP | null>(null);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(25);
  
  // Filters
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<Omit<LeadFilters, 'icp_id'>>({
    outcomes: [],
    min_score: undefined,
    max_score: undefined,
    min_evidence_coverage: undefined,
    industries: [],
    countries: [],
    min_employees: undefined,
    max_employees: undefined,
    company_name_search: '',
    has_research: undefined,
    sort_by: 'score',
    sort_direction: 'desc',
  });
  
  // Saved Views
  const [showSavedViewModal, setShowSavedViewModal] = useState(false);
  const [savedViewName, setSavedViewName] = useState('');
  const [savedViewDescription, setSavedViewDescription] = useState('');
  const [savingView, setSavingView] = useState(false);

  // Load ICPs and saved views on mount
  useEffect(() => {
    loadICPs();
    loadSavedViews();
  }, []);

  // Load leads when ICP or filters change
  useEffect(() => {
    if (selectedICP) {
      loadLeads();
    }
  }, [selectedICP, filters, currentPage]);

  const loadICPs = async () => {
    try {
      const response = await apiClient.listICPs(100, 0);
      setICPs(response.items);
      if (response.items.length > 0 && !selectedICP) {
        setSelectedICP(response.items[0]);
      }
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load ICPs');
    }
  };

  const loadSavedViews = async () => {
    try {
      const response = await apiClient.listSavedViews(100, 0);
      setSavedViews(response.items);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load saved views');
    }
  };

  const loadLeads = async () => {
    if (!selectedICP) return;
    
    setLoading(true);
    try {
      const fullFilters: LeadFilters = {
        icp_id: selectedICP.id,
        ...filters,
      };
      
      const offset = (currentPage - 1) * pageSize;
      const response = await apiClient.searchLeads(fullFilters, pageSize, offset);
      
      setLeads(response.items);
      setTotal(response.total);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

  const handleICPChange = (icp: ICP) => {
    setSelectedICP(icp);
    setCurrentPage(1);
  };

  const handleFilterChange = (newFilters: Partial<typeof filters>) => {
    setFilters({ ...filters, ...newFilters });
    setCurrentPage(1);
  };

  const handleSortChange = (field: SortField) => {
    const newDirection: SortDirection =
      filters.sort_by === field && filters.sort_direction === 'desc' ? 'asc' : 'desc';
    handleFilterChange({ sort_by: field, sort_direction: newDirection });
  };

  const handleResetFilters = () => {
    setFilters({
      outcomes: [],
      min_score: undefined,
      max_score: undefined,
      min_evidence_coverage: undefined,
      industries: [],
      countries: [],
      min_employees: undefined,
      max_employees: undefined,
      company_name_search: '',
      has_research: undefined,
      sort_by: 'score',
      sort_direction: 'desc',
    });
    setCurrentPage(1);
  };

  const handleSaveView = async () => {
    if (!selectedICP || !savedViewName.trim()) return;

    setSavingView(true);
    try {
      const viewData: SavedViewCreate = {
        name: savedViewName.trim(),
        description: savedViewDescription.trim() || undefined,
        filters: {
          icp_id: selectedICP.id,
          ...filters,
        },
      };

      await apiClient.createSavedView(viewData);
      onSuccess('Saved view created successfully');
      setShowSavedViewModal(false);
      setSavedViewName('');
      setSavedViewDescription('');
      await loadSavedViews();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to save view');
    } finally {
      setSavingView(false);
    }
  };

  const handleLoadSavedView = async (view: SavedView) => {
    // Find the ICP from saved view
    const icp = icps.find(i => i.id === view.filters.icp_id);
    if (icp) {
      setSelectedICP(icp);
    }
    
    // Apply filters
    const { icp_id, ...viewFilters } = view.filters;
    setFilters(viewFilters);
    setCurrentPage(1);
    onSuccess(`Loaded saved view: ${view.name}`);
  };

  const handleDeleteSavedView = async (viewId: string) => {
    if (!window.confirm('Are you sure you want to delete this saved view?')) return;

    try {
      await apiClient.deleteSavedView(viewId);
      onSuccess('Saved view deleted');
      await loadSavedViews();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to delete saved view');
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  if (icps.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No ICPs Available</h3>
        <p className="mt-1 text-sm text-gray-500">
          Create an ICP first to start viewing qualified leads.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="bg-white rounded-lg shadow-md p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Lead Intelligence</h2>
            <p className="text-gray-600 mt-1">
              View and rank qualified leads based on evidence-driven scoring
            </p>
          </div>
          <button
            onClick={loadLeads}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {/* ICP Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select ICP
          </label>
          <div className="flex items-center space-x-4">
            <select
              value={selectedICP?.id || ''}
              onChange={(e) => {
                const icp = icps.find(i => i.id === e.target.value);
                if (icp) handleICPChange(icp);
              }}
              className="block w-full md:w-96 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {icps.map(icp => (
                <option key={icp.id} value={icp.id}>
                  {icp.name}
                </option>
              ))}
            </select>
            
            {selectedICP && (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>Thresholds:</span>
                <span className="text-green-600 font-medium">
                  Qualified ≥{selectedICP.qualification_threshold}%
                </span>
                <span className="text-yellow-600 font-medium">
                  Partial ≥{selectedICP.partial_qualification_threshold}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Saved Views and Filters Row */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
            
            {((filters.outcomes?.length ?? 0) > 0 ||
              filters.min_score !== undefined ||
              filters.max_score !== undefined ||
              filters.min_evidence_coverage !== undefined ||
              (filters.industries?.length ?? 0) > 0 ||
              (filters.countries?.length ?? 0) > 0 ||
              filters.min_employees !== undefined ||
              filters.max_employees !== undefined ||
              filters.company_name_search ||
              filters.has_research !== undefined) && (
              <button
                onClick={handleResetFilters}
                className="text-sm text-primary-600 hover:text-primary-800"
              >
                Reset Filters
              </button>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {savedViews.length > 0 && (
              <div className="relative">
                <select
                  onChange={(e) => {
                    const view = savedViews.find(v => v.id === e.target.value);
                    if (view) handleLoadSavedView(view);
                  }}
                  defaultValue=""
                  className="block rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                >
                  <option value="">Load Saved View...</option>
                  {savedViews.map(view => (
                    <option key={view.id} value={view.id}>
                      {view.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <button
              onClick={() => setShowSavedViewModal(true)}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
            >
              Save Current View
            </button>
          </div>
        </div>

        {/* Collapsible Filters */}
        {showFilters && (
          <FilterPanel
            filters={filters}
            onFilterChange={handleFilterChange}
          />
        )}

        {/* Results Count */}
        <div className="mb-4 text-sm text-gray-600">
          {loading ? 'Loading...' : `${total} lead${total !== 1 ? 's' : ''} found`}
        </div>

        {/* Leads Table */}
        {loading && leads.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading leads...</p>
          </div>
        ) : leads.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Leads Found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No companies match the current filters. Try adjusting your criteria.
            </p>
          </div>
        ) : (
          <>
            <LeadsTable
              leads={leads}
              sortBy={filters.sort_by || 'score'}
              sortDirection={filters.sort_direction || 'desc'}
              onSortChange={handleSortChange}
            />

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            )}
          </>
        )}
      </div>

      {/* Saved Views Management */}
      {savedViews.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Saved Views</h3>
          <SavedViewsList
            savedViews={savedViews}
            onLoad={handleLoadSavedView}
            onDelete={handleDeleteSavedView}
          />
        </div>
      )}

      {/* Save View Modal */}
      {showSavedViewModal && (
        <SaveViewModal
          viewName={savedViewName}
          viewDescription={savedViewDescription}
          onNameChange={setSavedViewName}
          onDescriptionChange={setSavedViewDescription}
          onSave={handleSaveView}
          onCancel={() => {
            setShowSavedViewModal(false);
            setSavedViewName('');
            setSavedViewDescription('');
          }}
          saving={savingView}
        />
      )}
    </div>
  );
}

// Filter Panel Component
interface FilterPanelProps {
  filters: Omit<LeadFilters, 'icp_id'>;
  onFilterChange: (filters: Partial<Omit<LeadFilters, 'icp_id'>>) => void;
}

function FilterPanel({ filters, onFilterChange }: FilterPanelProps) {
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleApply = () => {
    onFilterChange(localFilters);
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Company Name Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company Name
          </label>
          <input
            type="text"
            value={localFilters.company_name_search || ''}
            onChange={(e) =>
              setLocalFilters({ ...localFilters, company_name_search: e.target.value })
            }
            placeholder="Search by name..."
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
          />
        </div>

        {/* Outcomes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Outcomes
          </label>
          <select
            multiple
            value={localFilters.outcomes || []}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, option => option.value);
              setLocalFilters({ ...localFilters, outcomes: selected });
            }}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            size={4}
          >
            <option value="qualified">Qualified</option>
            <option value="partially_qualified">Partially Qualified</option>
            <option value="not_qualified">Not Qualified</option>
            <option value="insufficient_data">Insufficient Data</option>
          </select>
        </div>

        {/* Score Range */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Score Range</label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={localFilters.min_score ?? ''}
              onChange={(e) =>
                setLocalFilters({
                  ...localFilters,
                  min_score: e.target.value ? parseFloat(e.target.value) : undefined,
                })
              }
              placeholder="Min"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            />
            <span className="text-gray-500">to</span>
            <input
              type="number"
              min="0"
              max="100"
              step="1"
              value={localFilters.max_score ?? ''}
              onChange={(e) =>
                setLocalFilters({
                  ...localFilters,
                  max_score: e.target.value ? parseFloat(e.target.value) : undefined,
                })
              }
              placeholder="Max"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            />
          </div>
        </div>

        {/* Evidence Coverage */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Evidence Coverage (%)
          </label>
          <input
            type="number"
            min="0"
            max="100"
            step="1"
            value={localFilters.min_evidence_coverage ?? ''}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                min_evidence_coverage: e.target.value ? parseFloat(e.target.value) : undefined,
              })
            }
            placeholder="e.g., 60"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
          />
        </div>

        {/* Employee Range */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Employee Count</label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              min="0"
              value={localFilters.min_employees ?? ''}
              onChange={(e) =>
                setLocalFilters({
                  ...localFilters,
                  min_employees: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              placeholder="Min"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            />
            <span className="text-gray-500">to</span>
            <input
              type="number"
              min="0"
              value={localFilters.max_employees ?? ''}
              onChange={(e) =>
                setLocalFilters({
                  ...localFilters,
                  max_employees: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              placeholder="Max"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            />
          </div>
        </div>

        {/* Has Research */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Research Availability
          </label>
          <select
            value={
              localFilters.has_research === undefined
                ? ''
                : localFilters.has_research
                ? 'true'
                : 'false'
            }
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                has_research:
                  e.target.value === '' ? undefined : e.target.value === 'true',
              })
            }
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
          >
            <option value="">Any</option>
            <option value="true">Has Research</option>
            <option value="false">No Research</option>
          </select>
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          onClick={handleApply}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          Apply Filters
        </button>
      </div>
    </div>
  );
}

// Leads Table Component
interface LeadsTableProps {
  leads: LeadResponse[];
  sortBy: SortField;
  sortDirection: SortDirection;
  onSortChange: (field: SortField) => void;
}

function LeadsTable({ leads, sortBy, sortDirection, onSortChange }: LeadsTableProps) {
  const getOutcomeBadge = (outcome: LeadResponse['outcome']) => {
    const styles = {
      qualified: 'bg-green-100 text-green-800',
      partially_qualified: 'bg-yellow-100 text-yellow-800',
      not_qualified: 'bg-red-100 text-red-800',
      insufficient_data: 'bg-gray-100 text-gray-800',
    };
    return styles[outcome];
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortBy !== field) {
      return (
        <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    return sortDirection === 'asc' ? (
      <svg className="h-4 w-4 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="h-4 w-4 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Company
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Industry
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Location
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Employees
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button
                onClick={() => onSortChange('outcome')}
                className="flex items-center space-x-1 hover:text-gray-700"
              >
                <span>Outcome</span>
                <SortIcon field="outcome" />
              </button>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button
                onClick={() => onSortChange('score')}
                className="flex items-center space-x-1 hover:text-gray-700"
              >
                <span>Score</span>
                <SortIcon field="score" />
              </button>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button
                onClick={() => onSortChange('evidence_coverage')}
                className="flex items-center space-x-1 hover:text-gray-700"
              >
                <span>Coverage</span>
                <SortIcon field="evidence_coverage" />
              </button>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <button
                onClick={() => onSortChange('qualified_at')}
                className="flex items-center space-x-1 hover:text-gray-700"
              >
                <span>Qualified</span>
                <SortIcon field="qualified_at" />
              </button>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Research
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {leads.map((lead) => (
            <tr key={`${lead.company_id}-${lead.qualification_id}`} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex flex-col">
                  <div className="text-sm font-medium text-gray-900">{lead.company_name}</div>
                  {lead.website && (
                    <a
                      href={lead.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary-600 hover:text-primary-800"
                    >
                      {lead.website}
                    </a>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">{lead.industry || '—'}</td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {lead.headquarters_country ? (
                  <div>
                    {lead.headquarters_region && `${lead.headquarters_region}, `}
                    {lead.headquarters_country}
                  </div>
                ) : (
                  '—'
                )}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {lead.employee_count !== undefined && lead.employee_count !== null
                  ? lead.employee_count.toLocaleString()
                  : '—'}
              </td>
              <td className="px-6 py-4">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getOutcomeBadge(
                    lead.outcome
                  )}`}
                >
                  {lead.outcome.replace(/_/g, ' ')}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                {lead.score !== undefined && lead.score !== null
                  ? `${lead.score.toFixed(1)}%`
                  : '—'}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">
                {lead.evidence_coverage !== undefined && lead.evidence_coverage !== null
                  ? `${lead.evidence_coverage.toFixed(1)}%`
                  : '—'}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {new Date(lead.qualified_at).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 text-sm">
                {lead.has_research ? (
                  <span className="text-green-600">✓</span>
                ) : (
                  <span className="text-gray-400">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Pagination Component
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const pages: (number | string)[] = [];
  
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i);
    }
  } else {
    if (currentPage <= 3) {
      pages.push(1, 2, 3, 4, '...', totalPages);
    } else if (currentPage >= totalPages - 2) {
      pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
    } else {
      pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
    }
  }

  return (
    <div className="flex items-center justify-between mt-6">
      <div className="text-sm text-gray-700">
        Page {currentPage} of {totalPages}
      </div>
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        {pages.map((page, index) =>
          page === '...' ? (
            <span key={`ellipsis-${index}`} className="px-3 py-1 text-gray-500">
              ...
            </span>
          ) : (
            <button
              key={page}
              onClick={() => onPageChange(page as number)}
              className={`px-3 py-1 border rounded-md text-sm font-medium ${
                currentPage === page
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
              }`}
            >
              {page}
            </button>
          )
        )}
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
}

// Saved Views List Component
interface SavedViewsListProps {
  savedViews: SavedView[];
  onLoad: (view: SavedView) => void;
  onDelete: (viewId: string) => void;
}

function SavedViewsList({ savedViews, onLoad, onDelete }: SavedViewsListProps) {
  return (
    <div className="space-y-2">
      {savedViews.map((view) => (
        <div
          key={view.id}
          className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-gray-300"
        >
          <div className="flex-1">
            <button
              onClick={() => onLoad(view)}
              className="text-left hover:text-primary-600"
            >
              <p className="font-medium text-gray-900">{view.name}</p>
              {view.description && (
                <p className="text-sm text-gray-500 mt-1">{view.description}</p>
              )}
              <p className="text-xs text-gray-400 mt-1">
                Created {new Date(view.created_at).toLocaleDateString()}
              </p>
            </button>
          </div>
          <button
            onClick={() => onDelete(view.id)}
            className="ml-4 text-red-600 hover:text-red-800"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}

// Save View Modal Component
interface SaveViewModalProps {
  viewName: string;
  viewDescription: string;
  onNameChange: (name: string) => void;
  onDescriptionChange: (description: string) => void;
  onSave: () => void;
  onCancel: () => void;
  saving: boolean;
}

function SaveViewModal({
  viewName,
  viewDescription,
  onNameChange,
  onDescriptionChange,
  onSave,
  onCancel,
  saving,
}: SaveViewModalProps) {
  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Save Current View</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              View Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={viewName}
              onChange={(e) => onNameChange(e.target.value)}
              placeholder="e.g., High-Quality SaaS Leads"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
              autoFocus
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (optional)
            </label>
            <textarea
              value={viewDescription}
              onChange={(e) => onDescriptionChange(e.target.value)}
              placeholder="Describe this saved view..."
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onCancel}
            disabled={saving}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            disabled={!viewName.trim() || saving}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save View'}
          </button>
        </div>
      </div>
    </div>
  );
}
