import { apiGet } from '../lib/api';

export interface FileTypeConfig {
  media_type: string;
  category: string;
  max_size_mb: number;
  parser: string;
}

export interface FileConfigResponse {
  [extension: string]: FileTypeConfig;
}

export async function getFileConfig(): Promise<FileConfigResponse> {
  return apiGet<FileConfigResponse>('/api/v1/config/file-types/');
}
