import { useQuery } from '@tanstack/react-query';
import { getResumeStatus } from '../services/resumeService';

export function useResumeStatus(uid: string | null) {
  return useQuery({
    queryKey: ['resume', 'status', uid],
    queryFn: () => getResumeStatus(uid!),
    enabled: !!uid,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 2000;
      }
      return false;
    },
    staleTime: 1000,
  });
}
