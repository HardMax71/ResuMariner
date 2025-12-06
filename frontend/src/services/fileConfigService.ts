import { v1ConfigFileTypesRetrieve } from '../api/client';

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
  const { data, error } = await v1ConfigFileTypesRetrieve();
  if (error) throw new Error(String(error));
  return data as FileConfigResponse;
}
