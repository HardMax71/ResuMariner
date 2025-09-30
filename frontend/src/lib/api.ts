export type JobStatus = "pending" | "processing" | "completed" | "failed";

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  result_url?: string | null;
  error?: string | null;
}

export interface JobResult {
  resume: Record<string, any>;
  review: Record<string, any> | null;
  metadata: Record<string, any>;
}

export interface FilterOption { value: string; count: number }
export interface FilterOptions {
  skills: FilterOption[];
  roles: FilterOption[];
  companies: FilterOption[];
  locations: FilterOption[];
  education_levels: FilterOption[];
  education_statuses: FilterOption[];
}

export interface SearchFilters {
  skills?: string[] | null;
  role?: string | null;
  company?: string | null;
  location?: string | null;
  years_experience?: number | null;
  education_level?: string | null;
  education_status?: string | null;
}

export interface SearchMatch {
  text: string;
  score: number;
  source?: string;
  context?: string | null;
}

export interface JobExperience {
  company: string;
  position: string;
  duration_months?: number | null;
  start?: string | null;  // ISO date string (YYYY-MM-DD)
  end?: string | null;    // ISO date string or null for ongoing
  employment_type?: string | null;
  work_mode?: string | null;
  key_points?: string[] | null;
}

export interface SearchResult {
  resume_id: string;
  name: string;
  email: string;
  score: number;
  matches: SearchMatch[];
  summary?: string | null;
  skills?: string[] | null;
  experiences?: JobExperience[] | null;
  education?: Record<string, any>[] | null;
  years_experience?: number | null;
  location?: Record<string, any> | null;
  desired_role?: string | null;
}

export interface SearchResponse {
  results: SearchResult[];
  query?: string | null;
  search_type: string;
}

const DEFAULT_BASE = "http://localhost:8000"; // Direct backend URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE;

// Export for use in components
export const API_BASE_URL = BASE_URL;

function withBase(path: string) {
  const base = BASE_URL.replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}${p}`;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(withBase(path), options);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `HTTP ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function uploadFile(file: File): Promise<JobResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<JobResponse>("/api/v1/upload/", {
    method: "POST",
    body: form
  });
}

export function getJob(jobId: string) {
  return request<JobResponse>(`/api/v1/jobs/${encodeURIComponent(jobId)}/`);
}

export function getJobResult(jobId: string) {
  return request<JobResult>(`/api/v1/jobs/${encodeURIComponent(jobId)}/result/`);
}

export function getFilters() {
  return request<FilterOptions>("/filters/");
}

export function searchSemantic(body: {
  query: string;
  limit?: number;
  min_score?: number;
  max_matches_per_result?: number;
  filters?: SearchFilters;
}) {
  return request<SearchResponse>("/search/semantic/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}

export function searchStructured(body: {
  query?: string;
  filters?: SearchFilters;
  limit?: number;
}) {
  return request<SearchResponse>("/search/structured/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}

export function searchHybrid(body: {
  query: string;
  filters?: SearchFilters;
  vector_weight?: number;
  graph_weight?: number;
  limit?: number;
  max_matches_per_result?: number;
}) {
  return request<SearchResponse>("/search/hybrid/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
}

export function getHealth() {
  return request<Record<string, any>>("/api/v1/health/");
}

export function cleanupJobs(params: { days?: number; force?: boolean }) {
  return request<Record<string, any>>("/api/v1/jobs/cleanup/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params)
  });
}

