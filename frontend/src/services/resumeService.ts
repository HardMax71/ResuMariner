import { apiGet, apiPost, apiUpload, SearchFilters, SearchResult, FilterOptions } from '../lib/api';

export interface UploadResult {
  job_id: string;
  status: string;
}

export interface JobResult {
  id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
  created_at?: string;
  completed_at?: string;
}

export async function uploadResume(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);

  return apiUpload<UploadResult>('/api/v1/upload/', formData);
}

export async function getJobStatus(jobId: string): Promise<JobResult> {
  return apiGet<JobResult>(`/api/v1/jobs/${jobId}/`);
}

export async function getJobResult(jobId: string): Promise<any> {
  return apiGet(`/api/v1/jobs/${jobId}/result/`);
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
  vector_weight?: number;
  graph_weight?: number;
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
