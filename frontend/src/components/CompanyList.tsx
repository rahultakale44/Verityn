import { useState } from 'react';
import type { Company } from '../api/client';

interface CompanyListProps {
  companies: Company[];
  onEdit: (company: Company) => void;
  onDelete: (company: Company) => void;
  onView: (company: Company) => void;
  onResearch: (company: Company) => void;
}

export function CompanyList({ companies, onEdit, onDelete, onView, onResearch }: CompanyListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = (company: Company) => {
    if (window.confirm(`Are you sure you want to delete "${company.company_name}"?`)) {
      setDeletingId(company.id);
      onDelete(company);
    }
  };

  if (companies.length === 0) {
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
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No companies</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by adding a new company.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
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
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {companies.map((company) => (
              <tr key={company.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <div className="text-sm font-medium text-gray-900">
                      {company.company_name}
                    </div>
                    {company.website && (
                      <a
                        href={company.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-600 hover:text-primary-800"
                      >
                        {company.website}
                      </a>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {company.industry || '—'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {company.headquarters_country && (
                    <div>
                      {company.headquarters_region && `${company.headquarters_region}, `}
                      {company.headquarters_country}
                    </div>
                  )}
                  {!company.headquarters_country && '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {company.employee_count !== undefined && company.employee_count !== null
                    ? company.employee_count.toLocaleString()
                    : '—'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onView(company)}
                    className="text-primary-600 hover:text-primary-900 mr-4"
                  >
                    View
                  </button>
                  <button
                    onClick={() => onResearch(company)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Research
                  </button>
                  <button
                    onClick={() => onEdit(company)}
                    className="text-green-600 hover:text-green-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(company)}
                    disabled={deletingId === company.id}
                    className="text-red-600 hover:text-red-900 disabled:opacity-50"
                  >
                    {deletingId === company.id ? 'Deleting...' : 'Delete'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
