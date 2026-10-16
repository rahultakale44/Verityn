import { useState, useEffect } from 'react';
import { apiClient, type Company, type ICP, type Qualification, type CriterionEvaluation } from '../api/client';

interface QualificationWorkflowProps {
  onError: (error: string) => void;
  onSuccess: (message: string) => void;
}

type WorkflowView = 'new' | 'history' | 'detail';

export function QualificationWorkflow({ onError, onSuccess }: QualificationWorkflowProps) {
  const [view, setView] = useState<WorkflowView>('new');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [icps, setICPs] = useState<ICP[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [selectedICP, setSelectedICP] = useState<ICP | null>(null);
  const [qualifications, setQualifications] = useState<Qualification[]>([]);
  const [selectedQualification, setSelectedQualification] = useState<Qualification | null>(null);
  const [loading, setLoading] = useState(false);
  const [qualifying, setQualifying] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [companiesResp, icpsResp] = await Promise.all([
        apiClient.listCompanies(100, 0),
        apiClient.listICPs(100, 0),
      ]);
      setCompanies(companiesResp.items);
      setICPs(icpsResp.items);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleQualify = async () => {
    if (!selectedCompany || !selectedICP) return;

    setQualifying(true);
    try {
      const result = await apiClient.qualifyCompany(selectedCompany.id, selectedICP.id);
      onSuccess(`Qualification completed: ${result.outcome}`);
      setSelectedQualification(result);
      setView('detail');
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to qualify company');
    } finally {
      setQualifying(false);
    }
  };

  const loadCompanyHistory = async (company: Company) => {
    setLoading(true);
    try {
      const response = await apiClient.listQualifications(company.id, 50, 0);
      setQualifications(response.items);
      setSelectedCompany(company);
      setView('history');
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load qualification history');
    } finally {
      setLoading(false);
    }
  };

  const viewQualificationDetail = async (qual: Qualification) => {
    setSelectedQualification(qual);
    setView('detail');
  };

  if (loading && companies.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Lead Qualification</h2>
            <p className="text-gray-600 mt-1">
              Qualify companies against ideal customer profiles using evidence-based scoring
            </p>
          </div>
          {view !== 'new' && (
            <button
              onClick={() => {
                setView('new');
                setSelectedQualification(null);
              }}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
            >
              New Qualification
            </button>
          )}
        </div>

        {view === 'new' && (
          <NewQualificationForm
            companies={companies}
            icps={icps}
            selectedCompany={selectedCompany}
            selectedICP={selectedICP}
            onCompanySelect={setSelectedCompany}
            onICPSelect={setSelectedICP}
            onQualify={handleQualify}
            onViewHistory={loadCompanyHistory}
            qualifying={qualifying}
          />
        )}

        {view === 'history' && selectedCompany && (
          <QualificationHistory
            company={selectedCompany}
            qualifications={qualifications}
            onBack={() => setView('new')}
            onViewDetail={viewQualificationDetail}
            loading={loading}
          />
        )}

        {view === 'detail' && selectedQualification && (
          <QualificationDetail
            qualification={selectedQualification}
            company={selectedCompany}
            onBack={() => {
              if (qualifications.length > 0) {
                setView('history');
              } else {
                setView('new');
              }
            }}
          />
        )}
      </div>
    </div>
  );
}

// New Qualification Form Component
interface NewQualificationFormProps {
  companies: Company[];
  icps: ICP[];
  selectedCompany: Company | null;
  selectedICP: ICP | null;
  onCompanySelect: (company: Company) => void;
  onICPSelect: (icp: ICP) => void;
  onQualify: () => void;
  onViewHistory: (company: Company) => void;
  qualifying: boolean;
}

function NewQualificationForm({
  companies,
  icps,
  selectedCompany,
  selectedICP,
  onCompanySelect,
  onICPSelect,
  onQualify,
  onViewHistory,
  qualifying,
}: NewQualificationFormProps) {
  if (companies.length === 0 || icps.length === 0) {
    return (
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
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Prerequisites Required</h3>
        <p className="mt-1 text-sm text-gray-500">
          {companies.length === 0 && 'You need to add at least one company. '}
          {icps.length === 0 && 'You need to create at least one ICP. '}
        </p>
      </div>
    );
  }

  const canQualify = selectedCompany && selectedICP;

  return (
    <div className="space-y-6">
      {/* Info Banner */}
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
              <strong>Evidence-Based Qualification:</strong> Select a company and ICP to run a deterministic
              qualification based on available company data and research evidence. Scores are calculated
              using transparent rules, not AI inference.
            </p>
          </div>
        </div>
      </div>

      {/* Company Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Company <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map((company) => (
            <button
              key={company.id}
              onClick={() => onCompanySelect(company)}
              className={`text-left p-4 border-2 rounded-lg transition-colors ${
                selectedCompany?.id === company.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <p className="font-medium text-gray-900">{company.company_name}</p>
              {company.industry && (
                <p className="text-sm text-gray-500 mt-1">{company.industry}</p>
              )}
              {company.headquarters_country && (
                <p className="text-xs text-gray-400 mt-1">{company.headquarters_country}</p>
              )}
            </button>
          ))}
        </div>
        {selectedCompany && (
          <button
            onClick={() => onViewHistory(selectedCompany)}
            className="mt-2 text-sm text-primary-600 hover:text-primary-800"
          >
            View qualification history for {selectedCompany.company_name}
          </button>
        )}
      </div>

      {/* ICP Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select ICP <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {icps.map((icp) => (
            <button
              key={icp.id}
              onClick={() => onICPSelect(icp)}
              className={`text-left p-4 border-2 rounded-lg transition-colors ${
                selectedICP?.id === icp.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <p className="font-medium text-gray-900">{icp.name}</p>
              {icp.description && (
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">{icp.description}</p>
              )}
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                <span>Qualified: {icp.qualification_threshold}%</span>
                <span>Partial: {icp.partial_qualification_threshold}%</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Qualify Button */}
      <div className="flex justify-end">
        <button
          onClick={onQualify}
          disabled={!canQualify || qualifying}
          className="px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {qualifying ? (
            <span className="flex items-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Qualifying...
            </span>
          ) : (
            'Run Qualification'
          )}
        </button>
      </div>
    </div>
  );
}

// Qualification History Component
interface QualificationHistoryProps {
  company: Company;
  qualifications: Qualification[];
  onBack: () => void;
  onViewDetail: (qual: Qualification) => void;
  loading: boolean;
}

function QualificationHistory({
  company,
  qualifications,
  onBack,
  onViewDetail,
  loading,
}: QualificationHistoryProps) {
  const getOutcomeBadge = (outcome: Qualification['outcome']) => {
    const styles = {
      qualified: 'bg-green-100 text-green-800',
      partially_qualified: 'bg-yellow-100 text-yellow-800',
      not_qualified: 'bg-red-100 text-red-800',
      insufficient_data: 'bg-gray-100 text-gray-800',
    };
    return styles[outcome] || styles.insufficient_data;
  };

  return (
    <div>
      <button
        onClick={onBack}
        className="mb-4 text-primary-600 hover:text-primary-800 flex items-center"
      >
        <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back
      </button>

      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Qualification History: {company.company_name}
      </h3>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-gray-600">Loading history...</p>
        </div>
      ) : qualifications.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No qualification history for this company.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {qualifications.map((qual) => (
            <div
              key={qual.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 cursor-pointer"
              onClick={() => onViewDetail(qual)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getOutcomeBadge(qual.outcome)}`}>
                      {qual.outcome.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(qual.qualified_at).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    {qual.score !== undefined && (
                      <div>
                        <span className="text-gray-500">Score:</span>{' '}
                        <span className="font-medium text-gray-900">{qual.score.toFixed(1)}%</span>
                      </div>
                    )}
                    {qual.evidence_coverage !== undefined && (
                      <div>
                        <span className="text-gray-500">Evidence Coverage:</span>{' '}
                        <span className="font-medium text-gray-900">{qual.evidence_coverage.toFixed(1)}%</span>
                      </div>
                    )}
                    <div>
                      <span className="text-gray-500">ICP:</span>{' '}
                      <span className="font-medium text-gray-900">
                        {qual.icp_snapshot?.name || 'Unknown'}
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mt-2">{qual.outcome_explanation}</p>
                </div>

                <svg
                  className="h-5 w-5 text-gray-400 ml-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Qualification Detail Component
interface QualificationDetailProps {
  qualification: Qualification;
  company: Company | null;
  onBack: () => void;
}

function QualificationDetail({ qualification, company, onBack }: QualificationDetailProps) {
  const getOutcomeBadge = (outcome: Qualification['outcome']) => {
    const styles = {
      qualified: 'bg-green-100 text-green-800 border-green-500',
      partially_qualified: 'bg-yellow-100 text-yellow-800 border-yellow-500',
      not_qualified: 'bg-red-100 text-red-800 border-red-500',
      insufficient_data: 'bg-gray-100 text-gray-800 border-gray-500',
    };
    return styles[outcome] || styles.insufficient_data;
  };

  const getStatusBadge = (status: CriterionEvaluation['status']) => {
    const styles = {
      match: { bg: 'bg-green-100', text: 'text-green-800', icon: '✓' },
      mismatch: { bg: 'bg-red-100', text: 'text-red-800', icon: '✗' },
      insufficient_evidence: { bg: 'bg-gray-100', text: 'text-gray-600', icon: '?' },
      not_applicable: { bg: 'bg-blue-100', text: 'text-blue-800', icon: '—' },
    };
    return styles[status] || styles.insufficient_evidence;
  };

  return (
    <div>
      <button
        onClick={onBack}
        className="mb-4 text-primary-600 hover:text-primary-800 flex items-center"
      >
        <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back
      </button>

      {/* Header */}
      <div className={`border-l-4 p-6 rounded-lg mb-6 ${getOutcomeBadge(qualification.outcome)}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-gray-900">
              {qualification.outcome.replace(/_/g, ' ').toUpperCase()}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {company?.company_name || 'Company'} vs. {qualification.icp_snapshot?.name || 'ICP'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Qualified on {new Date(qualification.qualified_at).toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          {qualification.score !== undefined && (
            <div className="bg-white bg-opacity-50 rounded p-3">
              <p className="text-sm text-gray-700">Qualification Score</p>
              <p className="text-3xl font-bold text-gray-900">{qualification.score.toFixed(1)}%</p>
            </div>
          )}
          {qualification.evidence_coverage !== undefined && (
            <div className="bg-white bg-opacity-50 rounded p-3">
              <p className="text-sm text-gray-700">Evidence Coverage</p>
              <p className="text-3xl font-bold text-gray-900">{qualification.evidence_coverage.toFixed(1)}%</p>
            </div>
          )}
        </div>

        <p className="mt-4 text-sm text-gray-700">{qualification.outcome_explanation}</p>
        
        {qualification.limitations && (
          <div className="mt-4 bg-yellow-50 border-l-4 border-yellow-400 p-3">
            <p className="text-sm text-yellow-700">
              <strong>Limitations:</strong> {qualification.limitations}
            </p>
          </div>
        )}
      </div>

      {/* Criteria Evaluations */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Criterion Evaluations</h4>
        
        {qualification.criteria_evaluations.map((criterion, index) => {
          const statusStyle = getStatusBadge(criterion.status);
          return (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full ${statusStyle.bg} ${statusStyle.text} font-bold`}>
                    {statusStyle.icon}
                  </span>
                  <div>
                    <h5 className="font-medium text-gray-900">{criterion.criterion_name}</h5>
                    <p className="text-sm text-gray-500">Weight: {criterion.weight}%</p>
                  </div>
                </div>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyle.bg} ${statusStyle.text}`}>
                  {criterion.status.replace(/_/g, ' ')}
                </span>
              </div>

              <p className="text-sm text-gray-700 mb-2">{criterion.explanation}</p>

              {criterion.observed_value !== undefined && (
                <div className="text-sm text-gray-600 mb-1">
                  <strong>Observed:</strong> {JSON.stringify(criterion.observed_value)}
                </div>
              )}

              {criterion.expected_value !== undefined && (
                <div className="text-sm text-gray-600 mb-1">
                  <strong>Expected:</strong> {JSON.stringify(criterion.expected_value)}
                </div>
              )}

              {criterion.reason_insufficient && (
                <div className="text-sm text-gray-500 mb-2">
                  <strong>Reason Insufficient:</strong> {criterion.reason_insufficient}
                </div>
              )}

              {criterion.evidence_references.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Evidence References ({criterion.evidence_references.length})
                  </p>
                  <div className="space-y-2">
                    {criterion.evidence_references.map((evidence, idx) => (
                      <div key={idx} className="bg-gray-50 rounded p-2">
                        <a
                          href={evidence.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary-600 hover:text-primary-800 font-medium flex items-center"
                        >
                          {evidence.title}
                          <svg
                            className="ml-1 h-3 w-3"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                            />
                          </svg>
                        </a>
                        <p className="text-xs text-gray-600 mt-1">{evidence.snippet}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
