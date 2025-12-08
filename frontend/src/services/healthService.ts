import { v1HealthRetrieve } from '../api/client';
import type { HealthResponse, QueueMetrics, ProcessingConfig } from '../api/client';

export type { HealthResponse, QueueMetrics, ProcessingConfig };

export async function getHealth(): Promise<HealthResponse> {
  const { data, error } = await v1HealthRetrieve();
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}
