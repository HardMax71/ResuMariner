import {
  API_BASE_URL,
  v1ResumesRetrieve2,
  v1SearchSemanticCreate,
  v1SearchStructuredCreate,
  v1SearchHybridCreate,
  v1FiltersRetrieve,
  type ResumeResponse,
  type SearchResponse,
  type FilterOptions,
  type VectorSearchQuerySchema,
  type GraphSearchQuerySchema,
  type HybridSearchQuerySchema,
} from '../api/client';

export async function uploadResume(file: File): Promise<ResumeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/v1/resumes/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as { detail?: string; message?: string };
    throw new Error(body.detail ?? body.message ?? `HTTP ${response.status}`);
  }

  return response.json();
}

export async function getResumeStatus(uid: string): Promise<ResumeResponse> {
  const { data, error } = await v1ResumesRetrieve2({ path: { uid } });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}

export async function searchSemantic(params: VectorSearchQuerySchema): Promise<SearchResponse> {
  const { data, error } = await v1SearchSemanticCreate({ body: params });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}

export async function searchStructured(params: GraphSearchQuerySchema): Promise<SearchResponse> {
  const { data, error } = await v1SearchStructuredCreate({ body: params });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}

export async function searchHybrid(params: HybridSearchQuerySchema): Promise<SearchResponse> {
  const { data, error } = await v1SearchHybridCreate({ body: params });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}

export async function getFilterOptions(): Promise<FilterOptions> {
  const { data, error } = await v1FiltersRetrieve();
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}
