import type { Company } from '../api/client';

interface CompanyDetailProps {
  company: Company;
  onClose: () => void;
  onEdit: () => void;
}

export function CompanyDetail({ company, onClose, onEdit }: CompanyDetailProps) {
  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Company Details</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <div className="px-6 py-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-500">Company Name</h4>
            <p className="mt-1 text-base text-gray-900">{company.company_name}</p>
          </div>

          {company.website && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Website</h4>
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-1 text-base text-primary-600 hover:text-primary-800"
              >
                {company.website}
              </a>
            </div>
          )}

          {company.industry && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Industry</h4>
              <p className="mt-1 text-base text-gray-900">{company.industry}</p>
            </div>
          )}

          {company.description && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Description</h4>
              <p className="mt-1 text-base text-gray-900">{company.description}</p>
            </div>
          )}

          {(company.headquarters_country || company.headquarters_region) && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Headquarters</h4>
              <p className="mt-1 text-base text-gray-900">
                {company.headquarters_region && `${company.headquarters_region}, `}
                {company.headquarters_country}
              </p>
            </div>
          )}

          {company.employee_count !== undefined && company.employee_count !== null && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Employee Count</h4>
              <p className="mt-1 text-base text-gray-900">
                {company.employee_count.toLocaleString()}
              </p>
            </div>
          )}

          <div className="pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Created</h4>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(company.created_at).toLocaleString()}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Last Updated</h4>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(company.updated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Close
          </button>
          <button
            onClick={onEdit}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Edit Company
          </button>
        </div>
      </div>
    </div>
  );
}
