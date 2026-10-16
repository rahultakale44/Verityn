import { useState, useEffect } from 'react';

interface HealthStatus {
  app_name: string;
  status: string;
  version: string;
}

function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [healthData, setHealthData] = useState<HealthStatus | null>(null);

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/health');
      if (response.ok) {
        const data = await response.json();
        setHealthData(data);
        setBackendStatus('connected');
      } else {
        setBackendStatus('disconnected');
      }
    } catch (error) {
      setBackendStatus('disconnected');
    }
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
                  ? 'Backend Connected'
                  : backendStatus === 'disconnected'
                  ? 'Backend Disconnected'
                  : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Evidence-Driven B2B Lead Intelligence
          </h2>
          <p className="text-gray-600 text-lg mb-4">
            Verityn helps B2B technology consulting companies research potential customers,
            evaluate them against configurable Ideal Customer Profiles (ICP), and produce
            prioritized shortlists backed by traceable evidence.
          </p>
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-blue-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
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
                  <strong>Phase 1 Development Version</strong> - Core infrastructure and foundation only.
                  AI-powered research and qualification features will be added in future phases.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Backend Connection Status */}
        {healthData && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">System Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Application</p>
                <p className="text-lg font-semibold text-gray-900">{healthData.app_name}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Status</p>
                <p className="text-lg font-semibold text-green-600 capitalize">
                  {healthData.status}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Version</p>
                <p className="text-lg font-semibold text-gray-900">{healthData.version}</p>
              </div>
            </div>
          </div>
        )}

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Lead Research Card */}
          <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-primary-600">
            <div className="flex items-center mb-4">
              <svg
                className="h-8 w-8 text-primary-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <h3 className="ml-3 text-xl font-semibold text-gray-900">Lead Research</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Automated research on potential B2B customers using reliable public sources.
            </p>
            <div className="bg-gray-100 rounded-lg p-4">
              <p className="text-sm text-gray-600 italic">
                Coming in a later phase
              </p>
            </div>
          </div>

          {/* Qualification Card */}
          <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-primary-600">
            <div className="flex items-center mb-4">
              <svg
                className="h-8 w-8 text-primary-600"
                xmlns="http://www.w3.org/2000/svg"
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
              <h3 className="ml-3 text-xl font-semibold text-gray-900">Qualification</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Score leads against your Ideal Customer Profile with explainable criteria.
            </p>
            <div className="bg-gray-100 rounded-lg p-4">
              <p className="text-sm text-gray-600 italic">
                Coming in a later phase
              </p>
            </div>
          </div>

          {/* Evidence Review Card */}
          <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-primary-600">
            <div className="flex items-center mb-4">
              <svg
                className="h-8 w-8 text-primary-600"
                xmlns="http://www.w3.org/2000/svg"
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
              <h3 className="ml-3 text-xl font-semibold text-gray-900">Evidence Review</h3>
            </div>
            <p className="text-gray-600 mb-4">
              Review supporting evidence and sources for every qualification decision.
            </p>
            <div className="bg-gray-100 rounded-lg p-4">
              <p className="text-sm text-gray-600 italic">
                Coming in a later phase
              </p>
            </div>
          </div>
        </div>

        {/* Key Principles */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Our Principles</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-primary-600 text-white">
                  <svg
                    className="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Factual Reliability</h4>
                <p className="mt-1 text-gray-600">
                  Every data point sourced from verifiable public information
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-primary-600 text-white">
                  <svg
                    className="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Traceable Evidence</h4>
                <p className="mt-1 text-gray-600">
                  Complete source attribution for audit and verification
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-primary-600 text-white">
                  <svg
                    className="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
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
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Explainable Scoring</h4>
                <p className="mt-1 text-gray-600">
                  Clear reasoning behind every qualification decision
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-10 w-10 rounded-md bg-primary-600 text-white">
                  <svg
                    className="h-6 w-6"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Security First</h4>
                <p className="mt-1 text-gray-600">
                  Input validation and secure practices throughout
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-600">
            <p className="text-sm">
              Verityn v0.1.0 - Phase 1 Development Version
            </p>
            <p className="text-xs mt-1 text-gray-500">
              Foundation infrastructure only. AI research and qualification features in development.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
