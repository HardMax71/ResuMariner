import { v1ConfigFileTypesRetrieve, type FileConfigResponse, type FileTypeConfig } from '../api/client';

export type { FileConfigResponse, FileTypeConfig };

export async function getFileConfig(): Promise<FileConfigResponse> {
  const { data, error } = await v1ConfigFileTypesRetrieve();
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}
