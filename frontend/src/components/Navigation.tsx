import type { Dispatch, SetStateAction } from 'react';

export type MainView = 'dashboard' | 'companies' | 'icps' | 'qualifications';

interface NavigationProps {
  currentView: MainView;
  onNavigate: Dispatch<SetStateAction<MainView>>;
  backendStatus: 'checking' | 'connected' | 'disconnected';
}

export function Navigation({ currentView, onNavigate, backendStatus }: NavigationProps) {
  const navItems: { id: MainView; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { id: 'companies', label: 'Companies', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
    { id: 'icps', label: 'ICPs', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
    { id: 'qualifications', label: 'Qualifications', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  ];

  return (
    <header className="bg-primary-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-4">
          <div>
            <h1 className="text-3xl font-bold">Verityn</h1>
            <p className="text-primary-200 text-sm mt-1">Evidence-Driven B2B Lead Intelligence</p>
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
        
        <nav className="flex space-x-1 pb-2">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex items-center px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
                currentView === item.id
                  ? 'bg-white text-primary-800'
                  : 'text-primary-100 hover:bg-primary-700 hover:text-white'
              }`}
            >
              <svg
                className="h-5 w-5 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={item.icon}
                />
              </svg>
              {item.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}
