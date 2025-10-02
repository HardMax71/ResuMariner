import { apiGet } from '../lib/api';

export interface QueueMetrics {
  stream_length: number;
  cleanup_queue_length: number;
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
  return apiGet<HealthData>('/api/v1/health/');
}
