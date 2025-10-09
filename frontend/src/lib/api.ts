export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

interface RequestOptions extends RequestInit {
  timeout?: number;
}

async function fetchWithTimeout(
  url: string,
  options: RequestOptions = {}
): Promise<Response> {
  const { timeout = 30000, ...fetchOptions } = options;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new NetworkError('Request timeout');
    }

    if (error instanceof TypeError) {
      throw new NetworkError('Network error - please check your connection');
    }

    throw error;
  }
}

export async function apiGet<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || error.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      error
    );
  }

  return response.json();
}

export async function apiPost<T>(
  endpoint: string,
  body?: any,
  options?: RequestOptions
): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || error.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      error
    );
  }

  return response.json();
}

export async function apiUpload<T>(
  endpoint: string,
  formData: FormData,
  options?: RequestOptions
): Promise<T> {
  const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || error.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      error
    );
  }

  return response.json();
}

export type ResumeStatus = "pending" | "processing" | "completed" | "failed";

export interface ResumeResponse {
  uid: string;
  status: ResumeStatus;
  created_at: string;
  updated_at: string;
  data?: {
    resume: Record<string, any>;
    review: Record<string, any> | null;
    metadata: Record<string, any>;
  };
  error?: string | null;
}

export interface FilterOption { value: string; count: number }

export interface LanguageOption {
  language: string;
  available_levels: string[];
  resume_count: number;
}

export interface CountryOption {
  country: string;
  cities: string[];
  resume_count: number;
}

export interface EducationLevelOption {
  level: string;
  statuses: string[];
  resume_count: number;
}

export interface FilterOptions {
  skills: FilterOption[];
  roles: FilterOption[];
  companies: FilterOption[];
  countries: CountryOption[];
  education_levels: EducationLevelOption[];
  languages: LanguageOption[];
}

export interface LanguageRequirement {
  language: string;
  min_cefr: string;
}

export interface LocationRequirement {
  country: string;
  cities?: string[] | null;
}

export interface EducationRequirement {
  level: string;
  statuses?: string[] | null;
}

export interface SearchFilters {
  skills?: string[] | null;
  role?: string | null;
  company?: string | null;
  locations?: LocationRequirement[] | null;
  years_experience?: number | null;
  education?: EducationRequirement[] | null;
  languages?: LanguageRequirement[] | null;
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
  start?: string | null;
  end?: string | null;
  employment_type?: string | null;
  work_mode?: string | null;
  key_points?: string[] | null;
}

export interface SearchResult {
  uid: string;
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
  languages?: Array<{language: string; cefr: string; self_assessed: string}> | null;
}

export interface SearchResponse {
  results: SearchResult[];
  query?: string | null;
  search_type: string;
}
