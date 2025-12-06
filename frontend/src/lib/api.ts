export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Single error interface for entire app - all thrown errors conform to this
export interface AppError {
  message: string;
  statusCode?: number;
  response?: unknown;
}

// Helper to convert any caught error to AppError shape
function toAppError(error: unknown, defaultMessage: string): AppError {
  const e = error as Partial<AppError>;
  return {
    message: e?.message ?? defaultMessage,
    statusCode: e?.statusCode,
    response: e?.response
  };
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
  } catch (error) {
    clearTimeout(timeoutId);
    // All fetch errors become AppError with no statusCode (network-level failure)
    throw toAppError(error, 'Network error - please check your connection');
  }
}

// Helper to create API error response
async function createApiError(response: Response): Promise<AppError> {
  const body = await response.json().catch(() => ({})) as { detail?: string; message?: string };
  return {
    message: body.detail ?? body.message ?? `HTTP ${response.status}: ${response.statusText}`,
    statusCode: response.status,
    response: body
  };
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
    throw await createApiError(response);
  }

  return response.json();
}

export async function apiPost<T>(
  endpoint: string,
  body?: unknown,
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
    throw await createApiError(response);
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
    throw await createApiError(response);
  }

  return response.json();
}

export type ResumeStatus = "pending" | "processing" | "completed" | "failed";

// Resume data types (matching backend domain/resume.py)
export interface Location {
  city?: string;
  state?: string;
  country?: string;
}

export interface ContactLinks {
  telegram?: string;
  linkedin?: string;
  github?: string;
  other_links?: Record<string, string>;
}

export interface Contact {
  email: string;
  phone?: string;
  links?: ContactLinks;
}

export interface WorkAuthorization {
  citizenship?: string;
  work_permit?: boolean;
  visa_sponsorship_required?: boolean;
}

export interface Demographics {
  current_location?: Location;
  work_authorization?: WorkAuthorization;
}

export interface PersonalInfo {
  name: string;
  resume_lang: string;
  contact: Contact;
  demographics?: Demographics;
}

export interface Skill {
  name: string;
}

export interface KeyPoint {
  text: string;
}

export interface CompanyInfo {
  name: string;
  url?: string;
}

export interface EmploymentDuration {
  start: string;
  end?: string;
  duration_months: number;
}

export interface EmploymentHistoryItem {
  position: string;
  employment_type?: string;
  work_mode?: string;
  company?: CompanyInfo;
  duration: EmploymentDuration;
  location?: Location;
  key_points: KeyPoint[];
  skills: Skill[];
}

export interface Project {
  title: string;
  url?: string;
  description?: string;
  skills: Skill[];
  key_points: KeyPoint[];
}

export interface InstitutionInfo {
  name: string;
}

export interface Coursework {
  text: string;
}

export interface EducationExtra {
  text: string;
}

export interface EducationItem {
  qualification?: string;
  field: string;
  institution: InstitutionInfo;
  location?: Location;
  start?: string;
  end?: string;
  year?: number;
  status: string;
  gpa?: string | number;
  coursework: Coursework[];
  extras: EducationExtra[];
}

export interface Course {
  name: string;
  organization: string;
  year?: number;
  course_url?: string;
  certificate_url?: string;
}

export interface Certification {
  name: string;
  issue_org?: string;
  issue_year?: number;
  certificate_link?: string;
}

export interface Language {
  name: string;
}

export interface LanguageProficiency {
  language: Language;
  self_assessed: string;
  cefr: string;
  // Legacy/alternative data shapes
  name?: string;
  level?: string;
}

export interface Award {
  name: string;
  award_type: string;
  organization: string;
  year?: number;
  position?: string;
  description?: string;
  url?: string;
  // Legacy/alternative data shapes
  title?: string;
  issuer?: string;
  date?: string;
}

export interface ScientificContribution {
  title: string;
  publication_type: string;
  year?: number;
  venue?: string;
  doi?: string;
  url?: string;
  description?: string;
}

export interface Preferences {
  role: string;
  employment_types: string[];
  work_modes: string[];
  salary?: string;
}

export interface ProfessionalProfile {
  summary?: string;
  preferences?: Preferences;
}

export interface Resume {
  uid: string;
  personal_info: PersonalInfo;
  professional_profile?: ProfessionalProfile;
  skills: Skill[];
  employment_history: EmploymentHistoryItem[];
  projects: Project[];
  education: EducationItem[];
  courses: Course[];
  certifications: Certification[];
  language_proficiency: LanguageProficiency[];
  awards: Award[];
  scientific_contributions: ScientificContribution[];
}

// Review feedback types
export interface ReviewFeedback {
  must?: string[];
  should?: string[];
  advise?: string[];
}

export interface ReviewData {
  overall_score?: number;
  summary?: string;
  [section: string]: number | string | ReviewFeedback | undefined;
}

export interface ResumeMetadata {
  processing_time?: number;
  [key: string]: unknown;
}

export interface ResumeResponse {
  uid: string;
  status: ResumeStatus;
  created_at: string;
  updated_at: string;
  data?: {
    resume: Resume;
    review: ReviewData | null;
    metadata: ResumeMetadata;
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
