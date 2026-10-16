/**
 * API client for Verityn backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Company {
  id: string;
  company_name: string;
  website?: string;
  industry?: string;
  description?: string;
  headquarters_country?: string;
  headquarters_region?: string;
  employee_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  company_name: string;
  website?: string;
  industry?: string;
  description?: string;
  headquarters_country?: string;
  headquarters_region?: string;
  employee_count?: number;
}

export interface CompanyUpdate {
  company_name?: string;
  website?: string;
  industry?: string;
  description?: string;
  headquarters_country?: string;
  headquarters_region?: string;
  employee_count?: number;
}

export interface CompanyListResponse {
  items: Company[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApiError {
  detail: string | { message: string; field?: string };
}

export interface ResearchRun {
  id: string;
  company_id: string;
  status: 'pending' | 'running' | 'completed' | 'partial' | 'failed';
  started_at: string;
  completed_at?: string;
  queries_executed: number;
  sources_found: number;
  sources_saved: number;
  error_summary?: string;
}

export interface ResearchRunListResponse {
  items: ResearchRun[];
  total: number;
  limit: number;
  offset: number;
}

export interface SourceEvidence {
  id: string;
  research_run_id: string;
  company_id: string;
  source_url: string;
  source_domain: string;
  title: string;
  snippet: string;
  published_at?: string;
  retrieved_at: string;
  provider: string;
  content_type?: string;
}

export interface SourceEvidenceListResponse {
  items: SourceEvidence[];
  total: number;
  limit: number;
  offset: number;
}

export interface ICP {
  id: string;
  name: string;
  description?: string;
  industries?: string[];
  headquarters_countries?: string[];
  minimum_employee_count?: number;
  maximum_employee_count?: number;
  required_keywords?: string[];
  excluded_keywords?: string[];
  criteria_weights: Record<string, number>;
  qualification_threshold: number;
  partial_qualification_threshold: number;
  minimum_evidence_coverage: number;
  created_at: string;
  updated_at: string;
}

export interface ICPCreate {
  name: string;
  description?: string;
  industries?: string[];
  headquarters_countries?: string[];
  minimum_employee_count?: number;
  maximum_employee_count?: number;
  required_keywords?: string[];
  excluded_keywords?: string[];
  criteria_weights?: Record<string, number>;
  qualification_threshold?: number;
  partial_qualification_threshold?: number;
  minimum_evidence_coverage?: number;
}

export interface ICPUpdate {
  name?: string;
  description?: string;
  industries?: string[];
  headquarters_countries?: string[];
  minimum_employee_count?: number;
  maximum_employee_count?: number;
  required_keywords?: string[];
  excluded_keywords?: string[];
  criteria_weights?: Record<string, number>;
  qualification_threshold?: number;
  partial_qualification_threshold?: number;
  minimum_evidence_coverage?: number;
}

export interface ICPListResponse {
  items: ICP[];
  total: number;
  limit: number;
  offset: number;
}

export interface EvidenceReference {
  source_id: string;
  source_url: string;
  title: string;
  snippet: string;
}

export interface CriterionEvaluation {
  criterion_id: string;
  criterion_name: string;
  weight: number;
  status: 'match' | 'mismatch' | 'insufficient_evidence' | 'not_applicable';
  explanation: string;
  observed_value?: any;
  expected_value?: any;
  evidence_references: EvidenceReference[];
  reason_insufficient?: string;
}

export interface Qualification {
  id: string;
  company_id: string;
  icp_id: string;
  icp_snapshot: Record<string, any>;
  qualified_at: string;
  score?: number;
  evidence_coverage?: number;
  outcome: 'qualified' | 'partially_qualified' | 'not_qualified' | 'insufficient_data';
  outcome_explanation: string;
  criteria_evaluations: CriterionEvaluation[];
  limitations?: string;
}

export interface QualificationListResponse {
  items: Qualification[];
  total: number;
  limit: number;
  offset: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(
        typeof error.detail === 'string'
          ? error.detail
          : error.detail.message || 'An error occurred'
      );
    }

    // For 204 No Content, return null
    if (response.status === 204) {
      return null as T;
    }

    return response.json();
  }

  // Health check
  async checkHealth(): Promise<{ app_name: string; status: string; version: string }> {
    return this.request('/api/v1/health');
  }

  // Company endpoints
  async createCompany(data: CompanyCreate): Promise<Company> {
    return this.request('/api/v1/companies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listCompanies(limit: number = 50, offset: number = 0): Promise<CompanyListResponse> {
    return this.request(`/api/v1/companies?limit=${limit}&offset=${offset}`);
  }

  async getCompany(id: string): Promise<Company> {
    return this.request(`/api/v1/companies/${id}`);
  }

  async updateCompany(id: string, data: CompanyUpdate): Promise<Company> {
    return this.request(`/api/v1/companies/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteCompany(id: string): Promise<void> {
    return this.request(`/api/v1/companies/${id}`, {
      method: 'DELETE',
    });
  }

  // Research endpoints
  async startResearch(companyId: string): Promise<ResearchRun> {
    return this.request(`/api/v1/companies/${companyId}/research`, {
      method: 'POST',
    });
  }

  async listResearch(companyId: string, limit: number = 50, offset: number = 0): Promise<ResearchRunListResponse> {
    return this.request(`/api/v1/companies/${companyId}/research?limit=${limit}&offset=${offset}`);
  }

  async getResearchRun(companyId: string, researchRunId: string): Promise<ResearchRun> {
    return this.request(`/api/v1/companies/${companyId}/research/${researchRunId}`);
  }

  async listResearchSources(
    companyId: string,
    researchRunId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<SourceEvidenceListResponse> {
    return this.request(
      `/api/v1/companies/${companyId}/research/${researchRunId}/sources?limit=${limit}&offset=${offset}`
    );
  }

  // ICP endpoints
  async createICP(data: ICPCreate): Promise<ICP> {
    return this.request('/api/v1/icps', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listICPs(limit: number = 50, offset: number = 0): Promise<ICPListResponse> {
    return this.request(`/api/v1/icps?limit=${limit}&offset=${offset}`);
  }

  async getICP(id: string): Promise<ICP> {
    return this.request(`/api/v1/icps/${id}`);
  }

  async updateICP(id: string, data: ICPUpdate): Promise<ICP> {
    return this.request(`/api/v1/icps/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteICP(id: string): Promise<void> {
    return this.request(`/api/v1/icps/${id}`, {
      method: 'DELETE',
    });
  }

  // Qualification endpoints
  async qualifyCompany(companyId: string, icpId: string): Promise<Qualification> {
    return this.request(`/api/v1/companies/${companyId}/qualifications`, {
      method: 'POST',
      body: JSON.stringify({ icp_id: icpId }),
    });
  }

  async listQualifications(companyId: string, limit: number = 50, offset: number = 0): Promise<QualificationListResponse> {
    return this.request(`/api/v1/companies/${companyId}/qualifications?limit=${limit}&offset=${offset}`);
  }

  async getQualification(companyId: string, qualificationId: string): Promise<Qualification> {
    return this.request(`/api/v1/companies/${companyId}/qualifications/${qualificationId}`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
