import { useState, useEffect } from 'react';
import { apiClient, type Company, type CompanyCreate, type CompanyUpdate, type ResearchRun, type SourceEvidence } from '../api/client';
import { CompanyList } from './CompanyList';
import { CompanyForm } from './CompanyForm';
import { CompanyDetail } from './CompanyDetail';
import { ResearchPanel, ResearchHistory, ResearchSources } from './ResearchPanel';

interface CompanyWorkspaceProps {
  onError: (error: string) => void;
  onSuccess: (message: string) => void;
}

type CompanyView = 'list' | 'create' | 'edit' | 'detail' | 'research';

export function CompanyWorkspace({ onError, onSuccess }: CompanyWorkspaceProps) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [currentView, setCurrentView] = useState<CompanyView>('list');
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  
  // Research state
  const [isResearching, setIsResearching] = useState(false);
  const [showResearchHistory, setShowResearchHistory] = useState(false);
  const [showResearchSources, setShowResearchSources] = useState(false);
  const [researchRuns, setResearchRuns] = useState<ResearchRun[]>([]);
  const [selectedResearchRun, setSelectedResearchRun] = useState<ResearchRun | null>(null);
  const [researchSources, setResearchSources] = useState<SourceEvidence[]>([]);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const response = await apiClient.listCompanies(100, 0);
      setCompanies(response.items);
      setTotal(response.total);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCompany = async (data: CompanyCreate) => {
    try {
      await apiClient.createCompany(data);
      onSuccess('Company created successfully');
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
      onSuccess('Company updated successfully');
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
      onSuccess('Company deleted successfully');
      await loadCompanies();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to delete company');
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
    try {
      const run = await apiClient.startResearch(company.id);
      
      if (run.status === 'completed') {
        onSuccess(`Research completed! Found ${run.sources_saved} sources.`);
      } else if (run.status === 'partial') {
        onSuccess(`Research partially completed. Found ${run.sources_saved} sources with some errors.`);
      } else if (run.status === 'failed') {
        onError(run.error_summary || 'Research failed to collect sources');
      }
      
      // Refresh selected company if viewing research
      if (currentView === 'research' && selectedCompany?.id === company.id) {
        // Could reload research history here
      }
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to start research');
    } finally {
      setIsResearching(false);
    }
  };

  const handleViewResearchHistory = async (company: Company) => {
    setSelectedCompany(company);
    try {
      const response = await apiClient.listResearch(company.id);
      setResearchRuns(response.items);
      setShowResearchHistory(true);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load research history');
    }
  };

  const handleViewResearchSources = async (run: ResearchRun) => {
    if (!selectedCompany) return;
    try {
      const response = await apiClient.listResearchSources(selectedCompany.id, run.id);
      setResearchSources(response.items);
      setSelectedResearchRun(run);
      setShowResearchHistory(false);
      setShowResearchSources(true);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load sources');
    }
  };

  const handleResearchCompany = (company: Company) => {
    setSelectedCompany(company);
    setCurrentView('research');
  };

  return (
    <div>
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Company Workspace</h2>
            <p className="text-gray-600 mt-1">
              Manage your B2B lead companies and conduct research
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
    </div>
  );
}
