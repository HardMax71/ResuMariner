import { useQuery, useMutation } from '@tanstack/react-query';
import {
  searchSemantic,
  searchStructured,
  searchHybrid,
  getFilterOptions,
} from '../services/resumeService';
import type {
  VectorSearchQuerySchema,
  GraphSearchQuerySchema,
  HybridSearchQuerySchema,
} from '../api/client';

export function useFilterOptions() {
  return useQuery({
    queryKey: ['filters'],
    queryFn: getFilterOptions,
    staleTime: 5 * 60 * 1000,
  });
}

type UnifiedSearchParams =
  | ({ type: "semantic" } & VectorSearchQuerySchema)
  | ({ type: "structured" } & GraphSearchQuerySchema)
  | ({ type: "hybrid" } & HybridSearchQuerySchema);

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
