import { useState, useEffect } from 'react';
import { apiClient, type MainView } from '../api/client';

interface DashboardProps {
  onNavigate: (view: MainView) => void;
}

interface DashboardMetrics {
  totalCompanies: number;
  totalICPs: number;
  recentResearchCount: number;
  recentQualificationsCount: number;
  loading: boolean;
  error: string | null;
}

export function Dashboard({ onNavigate }: DashboardProps) {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalCompanies: 0,
    totalICPs: 0,
    recentResearchCount: 0,
    recentQualificationsCount: 0,
    loading: true,
    error: null,
  });

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    setMetrics(prev => ({ ...prev, loading: true, error: null }));
    try {
      // Load companies count
      const companiesResponse = await apiClient.listCompanies(1, 0);
      const totalCompanies = companiesResponse.total;

      // Load ICPs count
      const icpsResponse = await apiClient.listICPs(1, 0);
      const totalICPs = icpsResponse.total;

      setMetrics({
        totalCompanies,
        totalICPs,
        recentResearchCount: 0, // Not supported by current API
        recentQualificationsCount: 0, // Not supported by current API
        loading: false,
        error: null,
      });
    } catch (err) {
      setMetrics(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to load metrics',
      }));
    }
  };

  if (metrics.loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (metrics.error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4">
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
            <p className="text-sm text-red-700">{metrics.error}</p>
          </div>
        </div>
      </div>
    );
  }

  const metricCards = [
    {
      title: 'Companies',
      value: metrics.totalCompanies,
      description: 'Total companies tracked',
      icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
      action: () => onNavigate('companies'),
      color: 'blue',
    },
    {
      title: 'ICPs',
      value: metrics.totalICPs,
      description: 'Active ideal customer profiles',
      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
      action: () => onNavigate('icps'),
      color: 'purple',
    },
  ];

  return (
    <div>
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to Verityn
        </h2>
        <p className="text-gray-600">
          Your evidence-driven B2B lead intelligence platform. Manage companies, configure ideal customer profiles,
          conduct research, and qualify leads with transparent, explainable scoring.
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mb-6">
        {metricCards.map((card) => (
          <button
            key={card.title}
            onClick={card.action}
            className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow text-left border-l-4 ${
              card.color === 'blue'
                ? 'border-blue-500'
                : card.color === 'green'
                ? 'border-green-500'
                : card.color === 'purple'
                ? 'border-purple-500'
                : 'border-yellow-500'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                <p className="text-sm text-gray-500 mt-1">{card.description}</p>
              </div>
              <div
                className={`p-3 rounded-full ${
                  card.color === 'blue'
                    ? 'bg-blue-100'
                    : card.color === 'green'
                    ? 'bg-green-100'
                    : card.color === 'purple'
                    ? 'bg-purple-100'
                    : 'bg-yellow-100'
                }`}
              >
                <svg
                  className={`h-8 w-8 ${
                    card.color === 'blue'
                      ? 'text-blue-600'
                      : card.color === 'green'
                      ? 'text-green-600'
                      : card.color === 'purple'
                      ? 'text-purple-600'
                      : 'text-yellow-600'
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d={card.icon}
                  />
                </svg>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => onNavigate('companies')}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <svg
              className="h-6 w-6 text-primary-600 mr-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            <div className="text-left">
              <p className="font-medium text-gray-900">Add Company</p>
              <p className="text-sm text-gray-500">Create a new company record</p>
            </div>
          </button>

          <button
            onClick={() => onNavigate('icps')}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <svg
              className="h-6 w-6 text-primary-600 mr-3"
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
            <div className="text-left">
              <p className="font-medium text-gray-900">Create ICP</p>
              <p className="text-sm text-gray-500">Define ideal customer profile</p>
            </div>
          </button>

          <button
            onClick={() => onNavigate('qualifications')}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <svg
              className="h-6 w-6 text-primary-600 mr-3"
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
            <div className="text-left">
              <p className="font-medium text-gray-900">Qualify Lead</p>
              <p className="text-sm text-gray-500">Run qualification against ICP</p>
            </div>
          </button>

          <button
            onClick={loadMetrics}
            className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <svg
              className="h-6 w-6 text-primary-600 mr-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            <div className="text-left">
              <p className="font-medium text-gray-900">Refresh Dashboard</p>
              <p className="text-sm text-gray-500">Reload current metrics</p>
            </div>
          </button>
        </div>
      </div>

      {/* Phase Info */}
      <div className="mt-6 bg-blue-50 border-l-4 border-blue-400 p-4">
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
              <strong>Phase 5</strong> - End-to-end lead intelligence dashboard active.
              Company management, research, ICP configuration, and evidence-based qualification are fully operational.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
