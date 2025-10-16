import { apiGet, apiPost, apiUpload, SearchFilters, SearchResult, FilterOptions } from '../lib/api';

export interface UploadResult {
  uid: string;
  status: string;
}

export interface ResumeStatusResult {
  uid: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  completed_at?: string;
  result?: any;
  error?: string;
}

export async function uploadResume(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);

  return apiUpload<UploadResult>('/api/v1/resumes/', formData);
}

export async function getResumeStatus(uid: string): Promise<ResumeStatusResult> {
  return apiGet<ResumeStatusResult>(`/api/v1/resumes/${uid}/`);
}

export async function searchResumes(filters: SearchFilters): Promise<SearchResult[]> {
  return apiPost<SearchResult[]>('/api/v1/resumes/search', filters);
}

export interface SearchResponse {
  results: SearchResult[];
  search_type: string;
  execution_time?: number;
}

export interface SemanticSearchParams {
  query: string;
  limit?: number;
  min_score?: number;
  max_matches_per_result?: number;
  filters?: SearchFilters;
}

export interface StructuredSearchParams {
  query: string;
  filters: SearchFilters;
  limit?: number;
}

export interface HybridSearchParams {
  query: string;
  filters?: SearchFilters;
  limit?: number;
  max_matches_per_result?: number;
}

export async function searchSemantic(params: SemanticSearchParams): Promise<SearchResponse> {
  return apiPost<SearchResponse>('/search/semantic/', params);
}

export async function searchStructured(params: StructuredSearchParams): Promise<SearchResponse> {
  return apiPost<SearchResponse>('/search/structured/', params);
}

export async function searchHybrid(params: HybridSearchParams): Promise<SearchResponse> {
  return apiPost<SearchResponse>('/search/hybrid/', params);
}

export async function getFilterOptions(): Promise<FilterOptions> {
  return apiGet<FilterOptions>('/filters/');
}
