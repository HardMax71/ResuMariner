import { useEffect, useState } from "react";
import { getHealth, API_BASE_URL } from "../lib/api";

interface HealthData {
  status: string;
  service: string;
  queue: {
    queue_length: number;
    cleanup_queue_length: number;
    scheduled_retries: number;
    active_jobs: number;
    redis_memory_usage: number;
  };
  processing_config: {
    text_llm_provider: string;
    text_llm_model: string;
    ocr_llm_provider: string;
    ocr_llm_model: string;
    generate_review: boolean;
    store_in_db: boolean;
  };
}

export default function Health() {
  const [data, setData] = useState<HealthData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHealth = async () => {
    setRefreshing(true);
    try {
      const result = await getHealth();
      setData(result as HealthData);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const isHealthy = data?.status === "ok";

  return (
    <div className="container">
      <div className="flex justify-between align-center mb-4">
        <h1 style={{ marginBottom: 0 }}>System Health</h1>
        <div className="flex gap-2">
          <a
            href={`${API_BASE_URL}/api/v1/health/`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn ghost"
            style={{ padding: "var(--space-2)" }}
            title="Open API endpoint"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
          </a>
          <button
            className="btn ghost"
            onClick={fetchHealth}
            disabled={refreshing}
            style={{ padding: "var(--space-2)" }}
            title="Refresh"
          >
            {refreshing ? (
              <span className="spinner" style={{width: "16px", height: "16px"}}></span>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M1 4v6h6M23 20v-6h-6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="error mb-3">
          Failed to fetch health status: {error}
        </div>
      )}

      {!data && !error && (
        <div className="flex justify-center items-center" style={{height: "200px"}}>
          <div className="spinner"></div>
        </div>
      )}

      {data && (
        <>
          {/* Service Status Card */}
          <div className="card mb-3">
            <div className="flex justify-between items-center">
              <div style={{
                display: "flex",
                gap: "var(--space-3)",
                flexWrap: "wrap",
                alignItems: "center"
              }}>
                <div className="flex items-center gap-1">
                  <span className="small muted">Status:</span>
                  <span style={{ fontWeight: 600 }}>{isHealthy ? "Healthy" : "Degraded"}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="small muted">Last Checked:</span>
                  <span style={{ fontWeight: 600 }}>{new Date().toLocaleTimeString()}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="muted small">{data.service}</span>
                <span className={`status-dot ${isHealthy ? "ok" : "bad"}`}></span>
                <span className={`badge ${isHealthy ? "badge-success" : "badge-danger"}`}>
                  {data.status.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Metrics with Resource Utilization */}
          <div className="grid grid-3 mb-4">
            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center">
                <span className="small muted">Processing Queue</span>
                <span style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: data.queue.queue_length > 0 ? "var(--blue-600)" : "var(--gray-600)" }}>
                  {data.queue.queue_length}
                </span>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center">
                <span className="small muted">Active Jobs</span>
                <span style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: data.queue.active_jobs > 0 ? "var(--success)" : "var(--gray-600)" }}>
                  {data.queue.active_jobs}
                </span>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center">
                <span className="small muted">Scheduled Retries</span>
                <span style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: data.queue.scheduled_retries > 0 ? "var(--warning)" : "var(--gray-600)" }}>
                  {data.queue.scheduled_retries}
                </span>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center">
                <span className="small muted">Cleanup Queue</span>
                <span style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: "var(--gray-600)" }}>
                  {data.queue.cleanup_queue_length}
                </span>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center">
                <span className="small muted">Redis Memory</span>
                <span style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: "var(--blue-600)" }}>
                  {formatBytes(data.queue.redis_memory_usage)}
                </span>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center">
                <span className="small muted">Total Load</span>
                <span style={{ fontSize: "var(--text-xl)", fontWeight: 700, color: "var(--gray-600)" }}>
                  {data.queue.queue_length + data.queue.active_jobs}
                </span>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center mb-1">
                <span className="small muted">Queue Capacity</span>
                <span style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--blue-600)" }}>
                  {Math.min((data.queue.queue_length / 100) * 100, 100).toFixed(0)}%
                </span>
              </div>
              <div style={{height: "6px", background: "var(--gray-200)", borderRadius: "var(--radius-full)", overflow: "hidden"}}>
                <div style={{
                  height: "100%",
                  width: `${Math.min((data.queue.queue_length / 100) * 100, 100)}%`,
                  background: "var(--blue-600)",
                  transition: "width var(--transition-base)"
                }}></div>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center mb-1">
                <span className="small muted">Active Workers</span>
                <span style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--success)" }}>
                  {Math.min((data.queue.active_jobs / 10) * 100, 100).toFixed(0)}%
                </span>
              </div>
              <div style={{height: "6px", background: "var(--gray-200)", borderRadius: "var(--radius-full)", overflow: "hidden"}}>
                <div style={{
                  height: "100%",
                  width: `${Math.min((data.queue.active_jobs / 10) * 100, 100)}%`,
                  background: "var(--success)",
                  transition: "width var(--transition-base)"
                }}></div>
              </div>
            </div>

            <div className="card" style={{ padding: "var(--space-2)" }}>
              <div className="flex justify-between align-center mb-1">
                <span className="small muted">Memory Usage</span>
                <span style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--warning)" }}>
                  {Math.min((data.queue.redis_memory_usage / 10485760) * 100, 100).toFixed(0)}%
                </span>
              </div>
              <div style={{height: "6px", background: "var(--gray-200)", borderRadius: "var(--radius-full)", overflow: "hidden"}}>
                <div style={{
                  height: "100%",
                  width: `${Math.min((data.queue.redis_memory_usage / 10485760) * 100, 100)}%`,
                  background: "var(--warning)",
                  transition: "width var(--transition-base)"
                }}></div>
              </div>
            </div>
          </div>

          {/* Processing Configuration */}
          <h2 className="mb-3">Processing Configuration</h2>
          <div className="card">
            <div className="grid grid-2 gap-3">
              <div>
                <h4 className="mb-2">LLM Providers</h4>
                <div className="flex flex-col">
                  <div className="flex justify-between align-center" style={{padding: "var(--space-2) 0", borderBottom: "1px solid var(--gray-100)", height: "48px"}}>
                    <span className="small muted">Text Processing</span>
                    <div className="chips">
                      <span className="chip">{data.processing_config.text_llm_provider}</span>
                      <span className="chip">{data.processing_config.text_llm_model}</span>
                    </div>
                  </div>
                  <div className="flex justify-between align-center" style={{padding: "var(--space-2) 0", borderBottom: "1px solid var(--gray-100)", height: "48px"}}>
                    <span className="small muted">OCR Processing</span>
                    <div className="chips">
                      <span className="chip">{data.processing_config.ocr_llm_provider}</span>
                      <span className="chip">{data.processing_config.ocr_llm_model}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="mb-2">Features</h4>
                <div className="flex flex-col">
                  <div className="flex justify-between align-center" style={{padding: "var(--space-2) 0", borderBottom: "1px solid var(--gray-100)", height: "48px"}}>
                    <span className="small muted">Generate Review</span>
                    <span className={`badge ${data.processing_config.generate_review ? "badge-success" : "badge-warning"}`}>
                      {data.processing_config.generate_review ? "ENABLED" : "DISABLED"}
                    </span>
                  </div>
                  <div className="flex justify-between align-center" style={{padding: "var(--space-2) 0", borderBottom: "1px solid var(--gray-100)", height: "48px"}}>
                    <span className="small muted">Store in Database</span>
                    <span className={`badge ${data.processing_config.store_in_db ? "badge-success" : "badge-warning"}`}>
                      {data.processing_config.store_in_db ? "ENABLED" : "DISABLED"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </>
      )}
    </div>
  );
}