import { useQuery } from '@tanstack/react-query';
import { getFileConfig, FileConfigResponse } from '../services/fileConfigService';

export function useFileConfig() {
  return useQuery<FileConfigResponse>({
    queryKey: ['fileConfig'],
    queryFn: getFileConfig,
    staleTime: 24 * 60 * 60 * 1000,
    gcTime: 24 * 60 * 60 * 1000,
  });
}
