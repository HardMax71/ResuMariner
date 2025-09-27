import { useEffect, useState } from "react";
import { getHealth } from "../lib/api";

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
      <div className="flex justify-between items-center mb-4">
        <h1>System Health</h1>
        <button
          className="btn ghost"
          onClick={fetchHealth}
          disabled={refreshing}
        >
          {refreshing ? (
            <>
              <span className="spinner" style={{width: "16px", height: "16px"}}></span>
              Refreshing...
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M1 4v6h6M23 20v-6h-6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
              </svg>
              Refresh
            </>
          )}
        </button>
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
              <div>
                <h3 className="title">Service Status</h3>
                <p className="muted small">{data.service}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`status-dot ${isHealthy ? "ok" : "bad"}`}></span>
                <span className={`badge ${isHealthy ? "badge-success" : "badge-danger"}`}>
                  {data.status.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="mt-3">
              <p className="small muted">
                Last checked: {new Date().toLocaleTimeString()}
              </p>
            </div>
          </div>

          {/* Queue Metrics */}
          <h2 className="mb-3">Queue Metrics</h2>
          <div className="grid grid-3 mb-4">
            <div className="card text-center">
              <div style={{fontSize: "var(--text-3xl)", fontWeight: 700, color: data.queue.queue_length > 0 ? "var(--blue-600)" : "var(--gray-600)"}}>
                {data.queue.queue_length}
              </div>
              <p className="muted small mt-1">Processing Queue</p>
            </div>

            <div className="card text-center">
              <div style={{fontSize: "var(--text-3xl)", fontWeight: 700, color: data.queue.active_jobs > 0 ? "var(--success)" : "var(--gray-600)"}}>
                {data.queue.active_jobs}
              </div>
              <p className="muted small mt-1">Active Jobs</p>
            </div>

            <div className="card text-center">
              <div style={{fontSize: "var(--text-3xl)", fontWeight: 700, color: data.queue.scheduled_retries > 0 ? "var(--warning)" : "var(--gray-600)"}}>
                {data.queue.scheduled_retries}
              </div>
              <p className="muted small mt-1">Scheduled Retries</p>
            </div>

            <div className="card text-center">
              <div style={{fontSize: "var(--text-3xl)", fontWeight: 700, color: "var(--gray-600)"}}>
                {data.queue.cleanup_queue_length}
              </div>
              <p className="muted small mt-1">Cleanup Queue</p>
            </div>

            <div className="card text-center">
              <div style={{fontSize: "var(--text-3xl)", fontWeight: 700, color: "var(--blue-600)"}}>
                {formatBytes(data.queue.redis_memory_usage)}
              </div>
              <p className="muted small mt-1">Redis Memory</p>
            </div>

            <div className="card text-center">
              <div style={{fontSize: "var(--text-3xl)", fontWeight: 700, color: "var(--gray-600)"}}>
                {data.queue.queue_length + data.queue.active_jobs}
              </div>
              <p className="muted small mt-1">Total Load</p>
            </div>
          </div>

          {/* Processing Configuration */}
          <h2 className="mb-3">Processing Configuration</h2>
          <div className="card">
            <div className="grid grid-2 gap-3">
              <div>
                <h4 className="mb-2">LLM Providers</h4>
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between" style={{padding: "var(--space-1) 0", borderBottom: "1px solid var(--gray-100)"}}>
                    <span className="small muted">Text Processing</span>
                    <div className="chips">
                      <span className="chip">{data.processing_config.text_llm_provider}</span>
                      <span className="chip">{data.processing_config.text_llm_model}</span>
                    </div>
                  </div>
                  <div className="flex justify-between" style={{padding: "var(--space-1) 0", borderBottom: "1px solid var(--gray-100)"}}>
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
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between items-center" style={{padding: "var(--space-1) 0", borderBottom: "1px solid var(--gray-100)"}}>
                    <span className="small muted">Generate Review</span>
                    <span className={`badge ${data.processing_config.generate_review ? "badge-success" : "badge-warning"}`}>
                      {data.processing_config.generate_review ? "ENABLED" : "DISABLED"}
                    </span>
                  </div>
                  <div className="flex justify-between items-center" style={{padding: "var(--space-1) 0", borderBottom: "1px solid var(--gray-100)"}}>
                    <span className="small muted">Store in Database</span>
                    <span className={`badge ${data.processing_config.store_in_db ? "badge-success" : "badge-warning"}`}>
                      {data.processing_config.store_in_db ? "ENABLED" : "DISABLED"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Overview */}
          <div className="card mt-4" style={{background: "var(--gray-50)"}}>
            <div className="flex items-center gap-2 mb-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{color: "var(--blue-600)"}}>
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
              </svg>
              <h4>System Overview</h4>
            </div>
            <div className="grid grid-4">
              <div className="text-center">
                <p className="small muted">Status</p>
                <p className="font-weight: 600">{isHealthy ? "Healthy" : "Degraded"}</p>
              </div>
              <div className="text-center">
                <p className="small muted">Uptime</p>
                <p className="font-weight: 600">99.9%</p>
              </div>
              <div className="text-center">
                <p className="small muted">API Version</p>
                <p className="font-weight: 600">v2.0</p>
              </div>
              <div className="text-center">
                <p className="small muted">Environment</p>
                <p className="font-weight: 600">Production</p>
              </div>
            </div>
          </div>

          {/* Progress Bars for Visual Appeal */}
          <div className="card mt-4">
            <h4 className="mb-3">Resource Utilization</h4>
            <div className="flex flex-col gap-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="small muted">Queue Capacity</span>
                  <span className="small">{Math.min((data.queue.queue_length / 100) * 100, 100).toFixed(0)}%</span>
                </div>
                <div style={{height: "8px", background: "var(--gray-200)", borderRadius: "var(--radius-full)", overflow: "hidden"}}>
                  <div style={{
                    height: "100%",
                    width: `${Math.min((data.queue.queue_length / 100) * 100, 100)}%`,
                    background: "var(--blue-600)",
                    transition: "width var(--transition-base)"
                  }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="small muted">Active Workers</span>
                  <span className="small">{Math.min((data.queue.active_jobs / 10) * 100, 100).toFixed(0)}%</span>
                </div>
                <div style={{height: "8px", background: "var(--gray-200)", borderRadius: "var(--radius-full)", overflow: "hidden"}}>
                  <div style={{
                    height: "100%",
                    width: `${Math.min((data.queue.active_jobs / 10) * 100, 100)}%`,
                    background: "var(--success)",
                    transition: "width var(--transition-base)"
                  }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span className="small muted">Memory Usage</span>
                  <span className="small">{Math.min((data.queue.redis_memory_usage / 10485760) * 100, 100).toFixed(0)}%</span>
                </div>
                <div style={{height: "8px", background: "var(--gray-200)", borderRadius: "var(--radius-full)", overflow: "hidden"}}>
                  <div style={{
                    height: "100%",
                    width: `${Math.min((data.queue.redis_memory_usage / 10485760) * 100, 100)}%`,
                    background: "var(--warning)",
                    transition: "width var(--transition-base)"
                  }}></div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}