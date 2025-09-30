import { useEffect, useState } from "react";
import { getHealth, API_BASE_URL } from "../lib/api";
import { Activity, RefreshCw, Code2, Zap, Database, Clock, BarChart3 } from "lucide-react";

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL || "http://grafana.localhost:8081";

interface HealthData {
  status: string;
  service: string;
  queue: {
    stream_length: number;
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
    <div className="page-wrapper">
      {/* Decorative Elements */}
      <div className="decorative-blur decorative-blur-health-top" />
      <div className="decorative-blur decorative-blur-health-bottom" />

      <div className="page-container">
        {/* Header */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "var(--space-8)"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "var(--space-3)"
          }}>
            <div style={{
              padding: "12px",
              background: "linear-gradient(135deg, rgba(67, 56, 202, 0.15) 0%, rgba(67, 56, 202, 0.05) 100%)",
              borderRadius: "var(--radius-sm)",
              border: "1px solid rgba(67, 56, 202, 0.2)"
            }}>
              <Activity size={28} color="#4338ca" strokeWidth={2.5} />
            </div>
            <h1 style={{ margin: 0 }}>
              System Health
            </h1>
          </div>

          <div style={{ display: "flex", gap: "var(--space-2)" }}>
            <a
              href={GRAFANA_URL}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "10px",
                background: "rgba(255, 255, 255, 0.9)",
                border: "1px solid rgba(245, 158, 11, 0.15)",
                borderRadius: "var(--radius-sm)",
                color: "#f59e0b",
                textDecoration: "none",
                transition: "all 0.2s",
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)"
              }}
              title="Open Grafana Dashboard"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(245, 158, 11, 0.1)";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.9)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <BarChart3 size={18} />
            </a>
            <a
              href={`${API_BASE_URL}/api/v1/health/`}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "10px",
                background: "rgba(255, 255, 255, 0.9)",
                border: "1px solid rgba(67, 56, 202, 0.15)",
                borderRadius: "var(--radius-sm)",
                color: "#4338ca",
                textDecoration: "none",
                transition: "all 0.2s",
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)"
              }}
              title="Open API endpoint"
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(67, 56, 202, 0.1)";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.9)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <Code2 size={18} />
            </a>
            <button
              onClick={fetchHealth}
              disabled={refreshing}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "10px",
                background: refreshing ? "rgba(200, 200, 200, 0.5)" : "rgba(255, 255, 255, 0.9)",
                border: "1px solid rgba(67, 56, 202, 0.15)",
                borderRadius: "var(--radius-sm)",
                color: "#4338ca",
                cursor: refreshing ? "not-allowed" : "pointer",
                transition: "all 0.2s",
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)"
              }}
              title="Refresh"
              onMouseEnter={(e) => {
                if (!refreshing) {
                  e.currentTarget.style.background = "rgba(67, 56, 202, 0.1)";
                  e.currentTarget.style.transform = "translateY(-2px)";
                }
              }}
              onMouseLeave={(e) => {
                if (!refreshing) {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.9)";
                  e.currentTarget.style.transform = "translateY(0)";
                }
              }}
            >
              <RefreshCw size={18} className={refreshing ? "spinning" : ""} />
            </button>
          </div>
        </div>

        {error && (
          <div style={{
            padding: "var(--space-4)",
            background: "rgba(225, 29, 72, 0.1)",
            border: "1px solid rgba(225, 29, 72, 0.3)",
            borderRadius: "var(--radius-sm)",
            color: "#be123c",
            fontSize: "var(--text-base)",
            fontWeight: 600,
            marginBottom: "var(--space-4)"
          }}>
            Failed to fetch health status: {error}
          </div>
        )}

        {!data && !error && (
          <div style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "300px"
          }}>
            <div style={{
              width: "48px",
              height: "48px",
              border: "4px solid rgba(67, 56, 202, 0.2)",
              borderTop: "4px solid #4338ca",
              borderRadius: "50%",
              animation: "spin 1s linear infinite"
            }} />
          </div>
        )}

        {data && (
          <>
            {/* Service Status Card */}
            <div className="glass-card" style={{ marginBottom: "var(--space-3)" }}>
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "var(--space-3)"
              }}>
                <div style={{
                  display: "flex",
                  gap: "var(--space-4)",
                  flexWrap: "wrap",
                  alignItems: "center"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "var(--text-sm)", color: "var(--neutral-600)" }}>Status:</span>
                    <span style={{ fontWeight: 700, fontSize: "var(--text-base)", color: "var(--neutral-900)" }}>
                      {isHealthy ? "Healthy" : "Degraded"}
                    </span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <Clock size={16} color="var(--neutral-600)" />
                    <span style={{ fontSize: "var(--text-sm)", color: "var(--neutral-600)" }}>Last Checked:</span>
                    <span style={{ fontWeight: 600, fontSize: "var(--text-base)", color: "var(--neutral-900)" }}>
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                  <span style={{ fontSize: "var(--text-sm)", color: "var(--neutral-600)", fontFamily: "var(--font-mono)" }}>
                    {data.service}
                  </span>
                  <div style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    background: isHealthy ? "#22c55e" : "#ef4444",
                    boxShadow: isHealthy ? "0 0 12px rgba(34, 197, 94, 0.5)" : "0 0 12px rgba(239, 68, 68, 0.5)"
                  }} />
                  <span style={{
                    padding: "6px 12px",
                    background: isHealthy ? "rgba(34, 197, 94, 0.15)" : "rgba(239, 68, 68, 0.15)",
                    border: isHealthy ? "1px solid rgba(34, 197, 94, 0.3)" : "1px solid rgba(239, 68, 68, 0.3)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "var(--text-sm)",
                    fontWeight: 700,
                    color: isHealthy ? "#15803d" : "#b91c1c",
                    letterSpacing: "0.025em"
                  }}>
                    {data.status.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            {/* Compact Metrics Grid */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(6, 1fr)",
              gap: "var(--space-2)",
              marginBottom: "var(--space-4)"
            }}>
              {[
                { label: "Queue", value: data.queue.stream_length, color: "#4338ca", bgColor: "rgba(67, 56, 202, 0.1)", icon: <Database size={18} strokeWidth={2.5} /> },
                { label: "Active", value: data.queue.active_jobs, color: "#22c55e", bgColor: "rgba(34, 197, 94, 0.1)", icon: <Zap size={18} strokeWidth={2.5} /> },
                { label: "Retries", value: data.queue.scheduled_retries, color: "#f59e0b", bgColor: "rgba(245, 158, 11, 0.1)", icon: <RefreshCw size={18} strokeWidth={2.5} /> },
                { label: "Cleanup", value: data.queue.cleanup_queue_length, color: "#8b5cf6", bgColor: "rgba(139, 92, 246, 0.1)", icon: <Activity size={18} strokeWidth={2.5} /> },
                { label: "Memory", value: formatBytes(data.queue.redis_memory_usage), color: "#06b6d4", bgColor: "rgba(6, 182, 212, 0.1)", icon: <Database size={18} strokeWidth={2.5} /> },
                { label: "Total", value: data.queue.stream_length + data.queue.active_jobs, color: "#ec4899", bgColor: "rgba(236, 72, 153, 0.1)", icon: <Activity size={18} strokeWidth={2.5} /> }
              ].map((metric, idx) => (
                <div key={idx} className="glass-card" style={{
                  borderTop: `3px solid ${metric.color}`,
                  padding: "var(--space-3)",
                  transition: "all 0.2s",
                  cursor: "default",
                  background: `linear-gradient(135deg, ${metric.bgColor} 0%, rgba(255, 255, 255, 0.95) 100%)`
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = "0 6px 20px rgba(0, 0, 0, 0.1)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 4px 16px rgba(0, 0, 0, 0.06)";
                }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-2)" }}>
                    <div style={{ color: metric.color, display: "flex" }}>{metric.icon}</div>
                    <div style={{ fontSize: "11px", color: "var(--neutral-600)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                      {metric.label}
                    </div>
                  </div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: metric.color, lineHeight: 1, fontFamily: "var(--font-display)" }}>
                    {metric.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Processing Configuration */}
            <div className="glass-card">
              <h3 style={{
                fontSize: "14px",
                fontWeight: 700,
                color: "var(--neutral-900)",
                marginBottom: "var(--space-3)",
                textTransform: "uppercase",
                letterSpacing: "0.5px"
              }}>
                Processing Configuration
              </h3>
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "var(--space-4)"
              }}>
                {/* LLM Providers */}
                <div>
                  <h4 style={{
                    fontSize: "13px",
                    fontWeight: 600,
                    color: "var(--neutral-700)",
                    marginBottom: "var(--space-2)",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px"
                  }}>
                    <Zap size={16} color="#4338ca" />
                    LLM Providers
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                    <div style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "var(--space-2)",
                      background: "rgba(67, 56, 202, 0.03)",
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid rgba(67, 56, 202, 0.1)"
                    }}>
                      <span style={{ fontSize: "12px", color: "var(--neutral-600)", fontWeight: 500 }}>
                        Text
                      </span>
                      <div style={{ display: "flex", gap: "4px" }}>
                        <span style={{
                          padding: "2px 6px",
                          background: "rgba(67, 56, 202, 0.15)",
                          border: "1px solid rgba(67, 56, 202, 0.25)",
                          borderRadius: "var(--radius-sm)",
                          fontSize: "11px",
                          fontWeight: 600,
                          color: "#4338ca",
                          fontFamily: "var(--font-mono)"
                        }}>
                          {data.processing_config.text_llm_provider}
                        </span>
                        <span style={{
                          padding: "2px 6px",
                          background: "rgba(67, 56, 202, 0.1)",
                          border: "1px solid rgba(67, 56, 202, 0.2)",
                          borderRadius: "var(--radius-sm)",
                          fontSize: "11px",
                          fontWeight: 600,
                          color: "#4338ca",
                          fontFamily: "var(--font-mono)"
                        }}>
                          {data.processing_config.text_llm_model}
                        </span>
                      </div>
                    </div>

                    <div style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "var(--space-2)",
                      background: "rgba(67, 56, 202, 0.03)",
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid rgba(67, 56, 202, 0.1)"
                    }}>
                      <span style={{ fontSize: "12px", color: "var(--neutral-600)", fontWeight: 500 }}>
                        OCR
                      </span>
                      <div style={{ display: "flex", gap: "4px" }}>
                        <span style={{
                          padding: "2px 6px",
                          background: "rgba(67, 56, 202, 0.15)",
                          border: "1px solid rgba(67, 56, 202, 0.25)",
                          borderRadius: "var(--radius-sm)",
                          fontSize: "11px",
                          fontWeight: 600,
                          color: "#4338ca",
                          fontFamily: "var(--font-mono)"
                        }}>
                          {data.processing_config.ocr_llm_provider}
                        </span>
                        <span style={{
                          padding: "2px 6px",
                          background: "rgba(67, 56, 202, 0.1)",
                          border: "1px solid rgba(67, 56, 202, 0.2)",
                          borderRadius: "var(--radius-sm)",
                          fontSize: "11px",
                          fontWeight: 600,
                          color: "#4338ca",
                          fontFamily: "var(--font-mono)"
                        }}>
                          {data.processing_config.ocr_llm_model}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div>
                  <h4 style={{
                    fontSize: "13px",
                    fontWeight: 600,
                    color: "var(--neutral-700)",
                    marginBottom: "var(--space-2)",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px"
                  }}>
                    <Activity size={16} color="#22c55e" />
                    Features
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                    <div style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "var(--space-2)",
                      background: "rgba(34, 197, 94, 0.03)",
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid rgba(34, 197, 94, 0.1)"
                    }}>
                      <span style={{ fontSize: "12px", color: "var(--neutral-600)", fontWeight: 500 }}>
                        Review
                      </span>
                      <span style={{
                        padding: "3px 8px",
                        background: data.processing_config.generate_review ? "rgba(34, 197, 94, 0.15)" : "rgba(245, 158, 11, 0.15)",
                        border: data.processing_config.generate_review ? "1px solid rgba(34, 197, 94, 0.3)" : "1px solid rgba(245, 158, 11, 0.3)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "10px",
                        fontWeight: 700,
                        color: data.processing_config.generate_review ? "#15803d" : "#b45309",
                        letterSpacing: "0.025em"
                      }}>
                        {data.processing_config.generate_review ? "ON" : "OFF"}
                      </span>
                    </div>

                    <div style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "var(--space-2)",
                      background: "rgba(34, 197, 94, 0.03)",
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid rgba(34, 197, 94, 0.1)"
                    }}>
                      <span style={{ fontSize: "12px", color: "var(--neutral-600)", fontWeight: 500 }}>
                        Store DB
                      </span>
                      <span style={{
                        padding: "3px 8px",
                        background: data.processing_config.store_in_db ? "rgba(34, 197, 94, 0.15)" : "rgba(245, 158, 11, 0.15)",
                        border: data.processing_config.store_in_db ? "1px solid rgba(34, 197, 94, 0.3)" : "1px solid rgba(245, 158, 11, 0.3)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: "10px",
                        fontWeight: 700,
                        color: data.processing_config.store_in_db ? "#15803d" : "#b45309",
                        letterSpacing: "0.025em"
                      }}>
                        {data.processing_config.store_in_db ? "ON" : "OFF"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
