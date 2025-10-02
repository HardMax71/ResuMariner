import { useQuery } from '@tanstack/react-query';
import { getJobStatus, getJobResult } from '../services/resumeService';

export function useJobStatus(jobId: string | null) {
  return useQuery({
    queryKey: ['job', 'status', jobId],
    queryFn: () => getJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'processing' || data?.status === 'queued') {
        return 2000;
      }
      return false;
    },
    staleTime: 1000,
  });
}

export function useJobResult(jobId: string | null) {
  return useQuery({
    queryKey: ['job', 'result', jobId],
    queryFn: () => getJobResult(jobId!),
    enabled: !!jobId,
    staleTime: Infinity,
  });
}
