import { v1HealthRetrieve } from '../api/client';

export interface QueueMetrics {
  stream_length: number;
  queue_length: number;
  scheduled_retries: number;
  active_jobs: number;
  redis_memory_usage: number;
}

export interface ProcessingConfig {
  text_llm_provider: string;
  text_llm_model: string;
  ocr_llm_provider: string;
  ocr_llm_model: string;
  generate_review: boolean;
  store_in_db: boolean;
}

export interface HealthData {
  status: 'ok' | 'degraded' | 'down';
  service: string;
  queue: QueueMetrics;
  processing_config: ProcessingConfig;
}

export async function getHealth(): Promise<HealthData> {
  const { data, error } = await v1HealthRetrieve();
  if (error) throw new Error(String(error));
  return data as HealthData;
}
