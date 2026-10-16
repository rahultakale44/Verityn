import { useState, useEffect } from 'react';
import { apiClient, type ICP, type ICPCreate, type ICPUpdate } from '../api/client';

interface ICPManagementProps {
  onError: (error: string) => void;
  onSuccess: (message: string) => void;
}

type ICPView = 'list' | 'create' | 'edit' | 'detail';

export function ICPManagement({ onError, onSuccess }: ICPManagementProps) {
  const [icps, setICPs] = useState<ICP[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentView, setCurrentView] = useState<ICPView>('list');
  const [selectedICP, setSelectedICP] = useState<ICP | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [icpToDelete, setICPToDelete] = useState<ICP | null>(null);

  useEffect(() => {
    loadICPs();
  }, []);

  const loadICPs = async () => {
    setLoading(true);
    try {
      const response = await apiClient.listICPs(100, 0);
      setICPs(response.items);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load ICPs');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data: ICPCreate) => {
    try {
      await apiClient.createICP(data);
      onSuccess('ICP created successfully');
      setCurrentView('list');
      await loadICPs();
    } catch (err) {
      throw err;
    }
  };

  const handleUpdate = async (data: ICPUpdate) => {
    if (!selectedICP) return;
    try {
      await apiClient.updateICP(selectedICP.id, data);
      onSuccess('ICP updated successfully');
      setCurrentView('list');
      setSelectedICP(null);
      await loadICPs();
    } catch (err) {
      throw err;
    }
  };

  const handleDeleteClick = (icp: ICP) => {
    setICPToDelete(icp);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!icpToDelete) return;
    try {
      await apiClient.deleteICP(icpToDelete.id);
      onSuccess('ICP deleted successfully');
      setShowDeleteConfirm(false);
      setICPToDelete(null);
      await loadICPs();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to delete ICP');
      setShowDeleteConfirm(false);
      setICPToDelete(null);
    }
  };

  return (
    <div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">ICP Management</h2>
            <p className="text-gray-600 mt-1">
              Manage ideal customer profiles for lead qualification
              {icps.length > 0 && <span className="ml-2">({icps.length} total)</span>}
            </p>
          </div>
          {currentView === 'list' && (
            <div className="flex space-x-3">
              <button
                onClick={loadICPs}
                disabled={loading}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
              <button
                onClick={() => setCurrentView('create')}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Create ICP
              </button>
            </div>
          )}
        </div>

        {currentView === 'list' && (
          <>
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <p className="mt-2 text-gray-600">Loading ICPs...</p>
              </div>
            ) : icps.length === 0 ? (
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
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No ICPs</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by creating an ideal customer profile.
                </p>
                <div className="mt-6">
                  <button
                    onClick={() => setCurrentView('create')}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Create ICP
                  </button>
                </div>
              </div>
            ) : (
              <ICPList
                icps={icps}
                onView={(icp) => {
                  setSelectedICP(icp);
                  setCurrentView('detail');
                }}
                onEdit={(icp) => {
                  setSelectedICP(icp);
                  setCurrentView('edit');
                }}
                onDelete={handleDeleteClick}
              />
            )}
          </>
        )}

        {currentView === 'create' && (
          <div>
            <button
              onClick={() => setCurrentView('list')}
              className="mb-4 text-primary-600 hover:text-primary-800 flex items-center"
            >
              <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to ICPs
            </button>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New ICP</h3>
            <ICPForm
              mode="create"
              onSubmit={handleCreate}
              onCancel={() => setCurrentView('list')}
            />
          </div>
        )}

        {currentView === 'edit' && selectedICP && (
          <div>
            <button
              onClick={() => {
                setCurrentView('list');
                setSelectedICP(null);
              }}
              className="mb-4 text-primary-600 hover:text-primary-800 flex items-center"
            >
              <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to ICPs
            </button>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Edit ICP</h3>
            <ICPForm
              mode="edit"
              icp={selectedICP}
              onSubmit={handleUpdate}
              onCancel={() => {
                setCurrentView('list');
                setSelectedICP(null);
              }}
            />
          </div>
        )}

        {currentView === 'detail' && selectedICP && (
          <ICPDetail
            icp={selectedICP}
            onClose={() => {
              setCurrentView('list');
              setSelectedICP(null);
            }}
            onEdit={() => setCurrentView('edit')}
            onDelete={() => handleDeleteClick(selectedICP)}
          />
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && icpToDelete && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Confirm Deletion</h3>
            <p className="text-sm text-gray-500 mb-6">
              Are you sure you want to delete the ICP "{icpToDelete.name}"? This action cannot be undone.
              Historical qualification results will be preserved with an ICP snapshot.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setICPToDelete(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ICP List Component
interface ICPListProps {
  icps: ICP[];
  onView: (icp: ICP) => void;
  onEdit: (icp: ICP) => void;
  onDelete: (icp: ICP) => void;
}

function ICPList({ icps, onView, onEdit, onDelete }: ICPListProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Criteria
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Thresholds
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {icps.map((icp) => {
            const criteriaCount = [
              icp.industries?.length,
              icp.headquarters_countries?.length,
              icp.minimum_employee_count !== undefined || icp.maximum_employee_count !== undefined,
              icp.required_keywords?.length,
              icp.excluded_keywords?.length,
            ].filter(Boolean).length;

            return (
              <tr key={icp.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <button
                    onClick={() => onView(icp)}
                    className="text-primary-600 hover:text-primary-900 font-medium text-left"
                  >
                    {icp.name}
                  </button>
                  {icp.description && (
                    <p className="text-sm text-gray-500 mt-1">{icp.description}</p>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {criteriaCount} criteria configured
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  Qualified: {icp.qualification_threshold}%<br />
                  Partial: {icp.partial_qualification_threshold}%
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {new Date(icp.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                  <button
                    onClick={() => onView(icp)}
                    className="text-primary-600 hover:text-primary-900"
                  >
                    View
                  </button>
                  <button
                    onClick={() => onEdit(icp)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(icp)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ICP Form Component - will be in next file due to length
interface ICPFormProps {
  mode: 'create' | 'edit';
  icp?: ICP;
  onSubmit: (data: ICPCreate) => Promise<void>;
  onCancel: () => void;
}

function ICPForm({ mode, icp, onSubmit, onCancel }: ICPFormProps) {
  const [formData, setFormData] = useState({
    name: icp?.name || '',
    description: icp?.description || '',
    industries: icp?.industries?.join(', ') || '',
    headquarters_countries: icp?.headquarters_countries?.join(', ') || '',
    minimum_employee_count: icp?.minimum_employee_count?.toString() || '',
    maximum_employee_count: icp?.maximum_employee_count?.toString() || '',
    required_keywords: icp?.required_keywords?.join(', ') || '',
    excluded_keywords: icp?.excluded_keywords?.join(', ') || '',
    qualification_threshold: icp?.qualification_threshold?.toString() || '70',
    partial_qualification_threshold: icp?.partial_qualification_threshold?.toString() || '50',
    minimum_evidence_coverage: icp?.minimum_evidence_coverage?.toString() || '60',
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const data: ICPCreate = {
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        industries: formData.industries
          ? formData.industries.split(',').map(s => s.trim()).filter(Boolean)
          : undefined,
        headquarters_countries: formData.headquarters_countries
          ? formData.headquarters_countries.split(',').map(s => s.trim()).filter(Boolean)
          : undefined,
        minimum_employee_count: formData.minimum_employee_count
          ? parseInt(formData.minimum_employee_count)
          : undefined,
        maximum_employee_count: formData.maximum_employee_count
          ? parseInt(formData.maximum_employee_count)
          : undefined,
        required_keywords: formData.required_keywords
          ? formData.required_keywords.split(',').map(s => s.trim()).filter(Boolean)
          : undefined,
        excluded_keywords: formData.excluded_keywords
          ? formData.excluded_keywords.split(',').map(s => s.trim()).filter(Boolean)
          : undefined,
        qualification_threshold: parseFloat(formData.qualification_threshold),
        partial_qualification_threshold: parseFloat(formData.partial_qualification_threshold),
        minimum_evidence_coverage: parseFloat(formData.minimum_evidence_coverage),
      };

      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save ICP');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          ICP Name *
        </label>
        <input
          type="text"
          id="name"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          rows={3}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="industries" className="block text-sm font-medium text-gray-700">
            Industries (comma-separated)
          </label>
          <input
            type="text"
            id="industries"
            value={formData.industries}
            onChange={(e) => setFormData({ ...formData, industries: e.target.value })}
            placeholder="Software, Technology, SaaS"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="headquarters_countries" className="block text-sm font-medium text-gray-700">
            Headquarters Countries (comma-separated)
          </label>
          <input
            type="text"
            id="headquarters_countries"
            value={formData.headquarters_countries}
            onChange={(e) => setFormData({ ...formData, headquarters_countries: e.target.value })}
            placeholder="United States, Canada"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="minimum_employee_count" className="block text-sm font-medium text-gray-700">
            Minimum Employee Count
          </label>
          <input
            type="number"
            id="minimum_employee_count"
            min="0"
            value={formData.minimum_employee_count}
            onChange={(e) => setFormData({ ...formData, minimum_employee_count: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="maximum_employee_count" className="block text-sm font-medium text-gray-700">
            Maximum Employee Count
          </label>
          <input
            type="number"
            id="maximum_employee_count"
            min="0"
            value={formData.maximum_employee_count}
            onChange={(e) => setFormData({ ...formData, maximum_employee_count: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="required_keywords" className="block text-sm font-medium text-gray-700">
            Required Keywords (comma-separated)
          </label>
          <input
            type="text"
            id="required_keywords"
            value={formData.required_keywords}
            onChange={(e) => setFormData({ ...formData, required_keywords: e.target.value })}
            placeholder="enterprise, B2B, cloud"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="excluded_keywords" className="block text-sm font-medium text-gray-700">
            Excluded Keywords (comma-separated)
          </label>
          <input
            type="text"
            id="excluded_keywords"
            value={formData.excluded_keywords}
            onChange={(e) => setFormData({ ...formData, excluded_keywords: e.target.value })}
            placeholder="consumer, B2C"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label htmlFor="qualification_threshold" className="block text-sm font-medium text-gray-700">
            Qualification Threshold (%)
          </label>
          <input
            type="number"
            id="qualification_threshold"
            required
            min="0"
            max="100"
            step="0.1"
            value={formData.qualification_threshold}
            onChange={(e) => setFormData({ ...formData, qualification_threshold: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="partial_qualification_threshold" className="block text-sm font-medium text-gray-700">
            Partial Threshold (%)
          </label>
          <input
            type="number"
            id="partial_qualification_threshold"
            required
            min="0"
            max="100"
            step="0.1"
            value={formData.partial_qualification_threshold}
            onChange={(e) => setFormData({ ...formData, partial_qualification_threshold: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>

        <div>
          <label htmlFor="minimum_evidence_coverage" className="block text-sm font-medium text-gray-700">
            Min Evidence Coverage (%)
          </label>
          <input
            type="number"
            id="minimum_evidence_coverage"
            required
            min="0"
            max="100"
            step="0.1"
            value={formData.minimum_evidence_coverage}
            onChange={(e) => setFormData({ ...formData, minimum_evidence_coverage: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          {submitting ? 'Saving...' : mode === 'create' ? 'Create ICP' : 'Update ICP'}
        </button>
      </div>
    </form>
  );
}

// ICP Detail Component
interface ICPDetailProps {
  icp: ICP;
  onClose: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

function ICPDetail({ icp, onClose, onEdit, onDelete }: ICPDetailProps) {
  return (
    <div>
      <button
        onClick={onClose}
        className="mb-4 text-primary-600 hover:text-primary-800 flex items-center"
      >
        <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to ICPs
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{icp.name}</h3>
          {icp.description && (
            <p className="text-gray-600 mt-2">{icp.description}</p>
          )}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={onEdit}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Edit
          </button>
          <button
            onClick={onDelete}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Criteria Section */}
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Qualification Criteria</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {icp.industries && icp.industries.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700">Industries</p>
                <p className="mt-1 text-sm text-gray-900">{icp.industries.join(', ')}</p>
              </div>
            )}
            {icp.headquarters_countries && icp.headquarters_countries.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700">Headquarters Countries</p>
                <p className="mt-1 text-sm text-gray-900">{icp.headquarters_countries.join(', ')}</p>
              </div>
            )}
            {(icp.minimum_employee_count !== undefined || icp.maximum_employee_count !== undefined) && (
              <div>
                <p className="text-sm font-medium text-gray-700">Employee Count Range</p>
                <p className="mt-1 text-sm text-gray-900">
                  {icp.minimum_employee_count || 0} - {icp.maximum_employee_count || '∞'}
                </p>
              </div>
            )}
            {icp.required_keywords && icp.required_keywords.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700">Required Keywords</p>
                <p className="mt-1 text-sm text-gray-900">{icp.required_keywords.join(', ')}</p>
              </div>
            )}
            {icp.excluded_keywords && icp.excluded_keywords.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700">Excluded Keywords (Disqualifying)</p>
                <p className="mt-1 text-sm text-red-600">{icp.excluded_keywords.join(', ')}</p>
              </div>
            )}
          </div>
        </div>

        {/* Thresholds Section */}
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Qualification Thresholds</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-700">Qualification Threshold</p>
              <p className="mt-1 text-2xl font-bold text-green-600">{icp.qualification_threshold}%</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Partial Qualification Threshold</p>
              <p className="mt-1 text-2xl font-bold text-yellow-600">{icp.partial_qualification_threshold}%</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Minimum Evidence Coverage</p>
              <p className="mt-1 text-2xl font-bold text-blue-600">{icp.minimum_evidence_coverage}%</p>
            </div>
          </div>
        </div>

        {/* Metadata Section */}
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Metadata</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-700">Created</p>
              <p className="mt-1 text-sm text-gray-900">{new Date(icp.created_at).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Last Updated</p>
              <p className="mt-1 text-sm text-gray-900">{new Date(icp.updated_at).toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
