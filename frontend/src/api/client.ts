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
}

export const apiClient = new ApiClient(API_BASE_URL);
