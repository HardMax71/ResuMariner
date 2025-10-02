import { useQuery, useMutation } from '@tanstack/react-query';
import {
  searchSemantic,
  searchStructured,
  searchHybrid,
  getFilterOptions,
  type SemanticSearchParams,
  type StructuredSearchParams,
  type HybridSearchParams,
} from '../services/resumeService';

export function useFilterOptions() {
  return useQuery({
    queryKey: ['filters'],
    queryFn: getFilterOptions,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSemanticSearch() {
  return useMutation({
    mutationFn: (params: SemanticSearchParams) => searchSemantic(params),
    onError: (error) => {
      console.error('Semantic search failed:', error);
    },
  });
}

export function useStructuredSearch() {
  return useMutation({
    mutationFn: (params: StructuredSearchParams) => searchStructured(params),
    onError: (error) => {
      console.error('Structured search failed:', error);
    },
  });
}

export function useHybridSearch() {
  return useMutation({
    mutationFn: (params: HybridSearchParams) => searchHybrid(params),
    onError: (error) => {
      console.error('Hybrid search failed:', error);
    },
  });
}
