import { useHealth } from "../hooks/useHealth";
import { API_BASE_URL } from "../lib/api";
import { Activity, RefreshCw, Code2, Zap, Database, Clock, BarChart3 } from "lucide-react";
import {
  PageWrapper,
  PageContainer,
  FlexRow,
  FlexColumn,
  GlassCard
} from "../components/styled";
import {
  Grid,
  MetricCard,
  MetricLabel,
  MetricValue,
  StatusBadge,
  ConfigGrid,
  ConfigRow,
  ConfigLabel,
  ConfigTag,
  ToggleBadge,
  SectionTitle,
  SubsectionTitle
} from "../components/styled/Card";
import { IconButton } from "../components/styled/Button";
import PageHeader from "../components/PageHeader";

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL || "http://grafana.localhost:8081";

export default function Health() {
  const { data, error, isLoading, refetch } = useHealth();

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const isHealthy = data?.status === "ok";

  return (
    <PageWrapper>
      <div className="decorative-blur decorative-blur-health-top" />
      <div className="decorative-blur decorative-blur-health-bottom" />

      <PageContainer>
        <PageHeader
          icon={<Activity size={24} style={{ color: "white" }} strokeWidth={2.5} />}
          title="System Health"
          actions={
            <FlexRow gap="var(--space-2)">
              <IconButton as="a" href={GRAFANA_URL} target="_blank" rel="noopener noreferrer" title="Open Grafana Dashboard">
                <BarChart3 size={18} />
              </IconButton>
              <IconButton as="a" href={`${API_BASE_URL}/api/v1/health/`} target="_blank" rel="noopener noreferrer" title="Open API endpoint">
                <Code2 size={18} />
              </IconButton>
              <IconButton onClick={() => refetch()} disabled={isLoading} title="Refresh">
                <RefreshCw size={18} className={isLoading ? "spinning" : ""} />
              </IconButton>
            </FlexRow>
          }
        />

        {error && (
          <div className="error mb-4">
            Failed to fetch health status: {error.message || 'Unknown error'}
          </div>
        )}

        {!data && !error && (
          <FlexRow justify="center" style={{ height: "300px" }}>
            <div className="spinner" style={{ width: "48px", height: "48px" }} />
          </FlexRow>
        )}

        {data && (
          <>
            <GlassCard style={{ marginBottom: "var(--space-3)" }}>
              <FlexRow justify="space-between" style={{ flexWrap: "wrap", gap: "var(--space-3)" }}>
                <FlexRow gap="var(--space-4)" style={{ flexWrap: "wrap" }}>
                  <FlexRow gap="8px">
                    <span className="small muted">Status:</span>
                    <span style={{ fontWeight: 700 }}>{isHealthy ? "Healthy" : "Degraded"}</span>
                  </FlexRow>
                  <FlexRow gap="8px">
                    <Clock size={16} color="var(--neutral-600)" />
                    <span className="small muted">Last Checked:</span>
                    <span style={{ fontWeight: 600 }}>{new Date().toLocaleTimeString()}</span>
                  </FlexRow>
                </FlexRow>
                <FlexRow gap="var(--space-3)">
                  <span className="small muted" style={{ fontFamily: "var(--font-mono)" }}>{data.service}</span>
                  <div style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    background: isHealthy ? "#22c55e" : "#ef4444",
                    boxShadow: isHealthy ? "0 0 12px rgba(34, 197, 94, 0.5)" : "0 0 12px rgba(239, 68, 68, 0.5)"
                  }} />
                  <StatusBadge variant={isHealthy ? 'success' : 'error'}>
                    {data.status.toUpperCase()}
                  </StatusBadge>
                </FlexRow>
              </FlexRow>
            </GlassCard>

            <Grid columns={6} style={{ marginBottom: "var(--space-4)" }}>
              {[
                { label: "Queue", value: data.queue.stream_length, color: "#4338ca", bgColor: "rgba(67, 56, 202, 0.1)", Icon: Database },
                { label: "Active", value: data.queue.active_jobs, color: "#22c55e", bgColor: "rgba(34, 197, 94, 0.1)", Icon: Zap },
                { label: "Retries", value: data.queue.scheduled_retries, color: "#f59e0b", bgColor: "rgba(245, 158, 11, 0.1)", Icon: RefreshCw },
                { label: "Cleanup", value: data.queue.cleanup_queue_length, color: "#8b5cf6", bgColor: "rgba(139, 92, 246, 0.1)", Icon: Activity },
                { label: "Memory", value: formatBytes(data.queue.redis_memory_usage), color: "#06b6d4", bgColor: "rgba(6, 182, 212, 0.1)", Icon: Database },
                { label: "Total", value: data.queue.stream_length + data.queue.active_jobs, color: "#ec4899", bgColor: "rgba(236, 72, 153, 0.1)", Icon: Activity }
              ].map((metric) => (
                <MetricCard key={metric.label} color={metric.color} bgColor={metric.bgColor}>
                  <FlexRow gap="var(--space-2)" style={{ marginBottom: "var(--space-2)" }}>
                    <metric.Icon size={18} strokeWidth={2.5} color={metric.color} />
                    <MetricLabel>{metric.label}</MetricLabel>
                  </FlexRow>
                  <MetricValue color={metric.color}>{metric.value}</MetricValue>
                </MetricCard>
              ))}
            </Grid>

            <GlassCard>
              <SectionTitle>Processing Configuration</SectionTitle>
              <ConfigGrid>
                <div>
                  <SubsectionTitle>
                    <Zap size={16} color="#4338ca" />
                    LLM Providers
                  </SubsectionTitle>
                  <FlexColumn gap="var(--space-2)">
                    <ConfigRow>
                      <ConfigLabel>Text</ConfigLabel>
                      <FlexRow gap="4px">
                        <ConfigTag emphasis>{data.processing_config.text_llm_provider}</ConfigTag>
                        <ConfigTag>{data.processing_config.text_llm_model}</ConfigTag>
                      </FlexRow>
                    </ConfigRow>

                    <ConfigRow>
                      <ConfigLabel>OCR</ConfigLabel>
                      <FlexRow gap="4px">
                        <ConfigTag emphasis>{data.processing_config.ocr_llm_provider}</ConfigTag>
                        <ConfigTag>{data.processing_config.ocr_llm_model}</ConfigTag>
                      </FlexRow>
                    </ConfigRow>
                  </FlexColumn>
                </div>

                <div>
                  <SubsectionTitle>
                    <Activity size={16} color="#22c55e" />
                    Features
                  </SubsectionTitle>
                  <FlexColumn gap="var(--space-2)">
                    <ConfigRow bgColor="rgba(34, 197, 94, 0.03)" borderColor="rgba(34, 197, 94, 0.1)">
                      <ConfigLabel>Review</ConfigLabel>
                      <ToggleBadge isOn={data.processing_config.generate_review}>
                        {data.processing_config.generate_review ? "ON" : "OFF"}
                      </ToggleBadge>
                    </ConfigRow>

                    <ConfigRow bgColor="rgba(34, 197, 94, 0.03)" borderColor="rgba(34, 197, 94, 0.1)">
                      <ConfigLabel>Store DB</ConfigLabel>
                      <ToggleBadge isOn={data.processing_config.store_in_db}>
                        {data.processing_config.store_in_db ? "ON" : "OFF"}
                      </ToggleBadge>
                    </ConfigRow>
                  </FlexColumn>
                </div>
              </ConfigGrid>
            </GlassCard>
          </>
        )}
      </PageContainer>
    </PageWrapper>
  );
}
