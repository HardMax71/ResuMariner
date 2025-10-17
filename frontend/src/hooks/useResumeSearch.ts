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

type UnifiedSearchParams =
  | ({ type: "semantic" } & SemanticSearchParams)
  | ({ type: "structured" } & StructuredSearchParams)
  | ({ type: "hybrid" } & HybridSearchParams);

export function useSearch() {
  return useMutation({
    mutationFn: (params: UnifiedSearchParams) => {
      if (params.type === "semantic") {
        const { type, ...rest } = params;
        return searchSemantic(rest);
      } else if (params.type === "structured") {
        const { type, ...rest } = params;
        return searchStructured(rest);
      } else {
        const { type, ...rest } = params;
        return searchHybrid(rest);
      }
    },
  });
}
