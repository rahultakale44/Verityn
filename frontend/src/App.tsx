import { useState, useEffect } from 'react';
import { apiClient, type Company, type CompanyCreate, type CompanyUpdate, type ResearchRun, type SourceEvidence } from './api/client';
import { CompanyList } from './components/CompanyList';
import { CompanyForm } from './components/CompanyForm';
import { CompanyDetail } from './components/CompanyDetail';
import { ResearchPanel, ResearchHistory, ResearchSources } from './components/ResearchPanel';

type View = 'list' | 'create' | 'edit' | 'detail' | 'research';

function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<View>('list');
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  
  // Research state
  const [isResearching, setIsResearching] = useState(false);
  const [showResearchHistory, setShowResearchHistory] = useState(false);
  const [showResearchSources, setShowResearchSources] = useState(false);
  const [researchRuns, setResearchRuns] = useState<ResearchRun[]>([]);
  const [selectedResearchRun, setSelectedResearchRun] = useState<ResearchRun | null>(null);
  const [researchSources, setResearchSources] = useState<SourceEvidence[]>([]);

  useEffect(() => {
    checkBackendHealth();
    loadCompanies();
  }, []);

  // Auto-dismiss success message after 5 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const checkBackendHealth = async () => {
    try {
      await apiClient.checkHealth();
      setBackendStatus('connected');
    } catch (error) {
      setBackendStatus('disconnected');
    }
  };

  const loadCompanies = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.listCompanies(100, 0);
      setCompanies(response.items);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCompany = async (data: CompanyCreate) => {
    try {
      await apiClient.createCompany(data);
      setSuccess('Company created successfully');
      setCurrentView('list');
      await loadCompanies();
    } catch (err) {
      throw err; // Let the form handle the error display
    }
  };

  const handleUpdateCompany = async (data: CompanyUpdate) => {
    if (!selectedCompany) return;
    try {
      await apiClient.updateCompany(selectedCompany.id, data);
      setSuccess('Company updated successfully');
      setCurrentView('list');
      setSelectedCompany(null);
      await loadCompanies();
    } catch (err) {
      throw err; // Let the form handle the error display
    }
  };

  const handleDeleteCompany = async (company: Company) => {
    try {
      await apiClient.deleteCompany(company.id);
      setSuccess('Company deleted successfully');
      await loadCompanies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete company');
    }
  };

  const handleViewCompany = (company: Company) => {
    setSelectedCompany(company);
    setCurrentView('detail');
  };

  const handleEditFromDetail = () => {
    setCurrentView('edit');
  };

  const handleStartResearch = async (company: Company) => {
    setIsResearching(true);
    setError(null);
    try {
      const run = await apiClient.startResearch(company.id);
      
      if (run.status === 'completed') {
        setSuccess(`Research completed! Found ${run.sources_saved} sources.`);
      } else if (run.status === 'partial') {
        setSuccess(`Research partially completed. Found ${run.sources_saved} sources with some errors.`);
      } else if (run.status === 'failed') {
        setError(run.error_summary || 'Research failed to collect sources');
      }
      
      // Refresh selected company if viewing detail
      if (currentView === 'research' && selectedCompany?.id === company.id) {
        // Could reload research history here
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start research');
    } finally {
      setIsResearching(false);
    }
  };

  const handleViewResearchHistory = async (company: Company) => {
    setSelectedCompany(company);
    setError(null);
    try {
      const response = await apiClient.listResearch(company.id);
      setResearchRuns(response.items);
      setShowResearchHistory(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load research history');
    }
  };

  const handleViewResearchSources = async (run: ResearchRun) => {
    if (!selectedCompany) return;
    setError(null);
    try {
      const response = await apiClient.listResearchSources(selectedCompany.id, run.id);
      setResearchSources(response.items);
      setSelectedResearchRun(run);
      setShowResearchHistory(false);
      setShowResearchSources(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sources');
    }
  };

  const handleResearchCompany = (company: Company) => {
    setSelectedCompany(company);
    setCurrentView('research');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-primary-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Verityn</h1>
              <p className="text-primary-200 mt-1">Research. Verify. Qualify.</p>
            </div>
            <div className="flex items-center space-x-2">
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  backendStatus === 'connected'
                    ? 'bg-green-100 text-green-800'
                    : backendStatus === 'disconnected'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full mr-2 ${
                    backendStatus === 'connected'
                      ? 'bg-green-500'
                      : backendStatus === 'disconnected'
                      ? 'bg-red-500'
                      : 'bg-yellow-500'
                  }`}
                ></span>
                {backendStatus === 'connected'
                  ? 'Connected'
                  : backendStatus === 'disconnected'
                  ? 'Disconnected'
                  : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Message */}
        {success && (
          <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-green-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">{success}</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="inline-flex text-red-400 hover:text-red-500"
                >
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Company Management Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Company Management</h2>
              <p className="text-gray-600 mt-1">
                Manage your B2B lead companies
                {total > 0 && <span className="ml-2">({total} total)</span>}
              </p>
            </div>
            {currentView === 'list' && (
              <div className="flex space-x-3">
                <button
                  onClick={loadCompanies}
                  disabled={loading}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {loading ? 'Refreshing...' : 'Refresh'}
                </button>
                <button
                  onClick={() => setCurrentView('create')}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Add Company
                </button>
              </div>
            )}
          </div>

          {/* View: Company List */}
          {currentView === 'list' && (
            <>
              {loading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <p className="mt-2 text-gray-600">Loading companies...</p>
                </div>
              ) : (
                <CompanyList
                  companies={companies}
                  onEdit={(company) => {
                    setSelectedCompany(company);
                    setCurrentView('edit');
                  }}
                  onDelete={handleDeleteCompany}
                  onView={handleViewCompany}
                  onResearch={handleResearchCompany}
                />
              )}
            </>
          )}

          {/* View: Create Company */}
          {currentView === 'create' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Company</h3>
              <CompanyForm
                mode="create"
                onSubmit={handleCreateCompany}
                onCancel={() => setCurrentView('list')}
              />
            </div>
          )}

          {/* View: Edit Company */}
          {currentView === 'edit' && selectedCompany && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Company</h3>
              <CompanyForm
                mode="edit"
                company={selectedCompany}
                onSubmit={handleUpdateCompany}
                onCancel={() => {
                  setCurrentView('list');
                  setSelectedCompany(null);
                }}
              />
            </div>
          )}

          {/* View: Research Company */}
          {currentView === 'research' && selectedCompany && (
            <div>
              <button
                onClick={() => setCurrentView('list')}
                className="mb-4 text-primary-600 hover:text-primary-800 flex items-center"
              >
                <svg
                  className="h-4 w-4 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                Back to Companies
              </button>
              
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Research: {selectedCompany.company_name}
              </h3>
              
              <ResearchPanel
                company={selectedCompany}
                onStartResearch={handleStartResearch}
                onViewHistory={handleViewResearchHistory}
                isResearching={isResearching}
              />
            </div>
          )}
        </div>

        {/* Phase Info */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Phase 3</strong> - Public company research and evidence collection is now available.
                AI-powered qualification features will be added in future phases.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Company Detail Modal */}
      {currentView === 'detail' && selectedCompany && (
        <CompanyDetail
          company={selectedCompany}
          onClose={() => {
            setCurrentView('list');
            setSelectedCompany(null);
          }}
          onEdit={handleEditFromDetail}
        />
      )}

      {/* Research History Modal */}
      {showResearchHistory && selectedCompany && (
        <ResearchHistory
          company={selectedCompany}
          researchRuns={researchRuns}
          onViewSources={handleViewResearchSources}
          onClose={() => setShowResearchHistory(false)}
        />
      )}

      {/* Research Sources Modal */}
      {showResearchSources && selectedCompany && selectedResearchRun && (
        <ResearchSources
          company={selectedCompany}
          run={selectedResearchRun}
          sources={researchSources}
          onClose={() => {
            setShowResearchSources(false);
            setShowResearchHistory(true);
          }}
        />
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600">
            <p className="text-sm">Verityn v0.3.0 - Phase 3 Development Version</p>
            <p className="text-xs mt-1 text-gray-500">
              Company management and public research active. AI qualification features in development.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
