import { Link } from "react-router-dom";
import { PageWrapper, PageContainer } from "../components/styled";
import PageHeader from "../components/PageHeader";
import PlantUMLDiagram from "../components/PlantUMLDiagram";
import { POLICY_LAST_UPDATED } from "../constants";

export default function DataPolicy() {
  return (
    <PageWrapper>
      <PageContainer>
        <PageHeader title="Data Policy" />

        <div className="glass-card" style={{ marginBottom: "var(--space-4)" }}>
          <div style={{ maxWidth: "800px", lineHeight: 1.7, fontSize: "var(--text-base)" }}>
            <p style={{ color: "var(--neutral-600)", marginBottom: "var(--space-4)" }}>
              <strong>Last Updated:</strong> {POLICY_LAST_UPDATED}
            </p>

            <div style={{
              background: "rgba(129, 140, 248, 0.1)",
              border: "1px solid rgba(129, 140, 248, 0.3)",
              borderRadius: "var(--radius-sm)",
              padding: "var(--space-3)",
              marginBottom: "var(--space-5)"
            }}>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                <strong>Technical deep dive:</strong> This page explains the technical architecture - what databases, where data goes, how processing works.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                For privacy policy, GDPR rights, data deletion, and contact info, see the <Link to="/privacy" style={{ color: "var(--indigo-400)", textDecoration: "underline" }}>Privacy Policy</Link>.
              </p>
            </div>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                1. How Your Data Gets Processed
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-3)" }}>
                <strong>Neo4j (graph database):</strong> Stores structured resume data as nodes and relationships. When a resume is parsed, it creates a ResumeNode connected to PersonalInfoNode, EmploymentHistoryItemNode, EducationItemNode, etc. Relationships like "WORKED_AT", "HAS_SKILL", "LOCATED_AT" make it easy to query for patterns like "everyone who worked at Google and knows Python."
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-3)" }}>
                <strong>Qdrant (vector database):</strong> Stores 768-dimensional vector embeddings for semantic search. Resume text gets chunked and embedded using an OpenAI-compatible embeddings API (text-embedding-3-small or similar). Each vector includes metadata (uid, text chunk, section type). This enables concept-based search - "backend development" will match "server-side programming" even without exact keywords.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-3)" }}>
                <strong>Local file storage:</strong> Original PDFs saved to <code>uploads/</code> directory with UUID-based filenames like <code>123e4567-e89b-12d3-a456-426614174000.pdf</code>. Alternatively configurable to use S3-compatible storage. Files are kept for downloading originals and re-processing if needed.
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                <strong>Redis:</strong> Job queue and status tracking. Stores temporary job metadata (uid, status, file path, timestamps) during async processing. Job records persist after completion for status checks but aren't used for long-term data storage.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                2. Processing Pipeline
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-4)" }}>
                When you upload a resume, it goes through a multi-stage pipeline: file validation and storage, text extraction with PyMuPDF, email extraction and duplicate checking, AI-powered parsing to structured data, storage in Neo4j graph database, vector embedding generation, and storage in Qdrant. The whole process is asynchronous with Redis tracking job status. Typically takes 10-30 seconds end-to-end.
              </p>

              <PlantUMLDiagram
                src="/diagrams/processing-pipeline.puml"
                alt="Resume Processing Pipeline Sequence Diagram"
                caption="Resume processing flow"
              />
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                3. External AI APIs
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                <strong>LLM for parsing:</strong> Extracted resume text sent to external LLM API for structure extraction. Configurable via <code>TEXT_LLM_PROVIDER</code> setting (openai, anthropic, or any Pydantic AI-compatible provider). This demo uses OpenAI GPT-4 by default.
              </p>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-2)" }}>
                <strong>Embeddings API:</strong> Resume text chunks sent to OpenAI-compatible embeddings endpoint for vector generation. Configurable via <code>TEXT_LLM_BASE_URL</code> and <code>EMBEDDING_MODEL</code> settings. Default model: text-embedding-3-small (768 dimensions).
              </p>
              <p style={{ color: "var(--neutral-700)" }}>
                <strong>Data retention:</strong> Both services see your resume text temporarily. OpenAI (default provider) retains API data for ~30 days by default for abuse monitoring. Enterprise accounts can enable zero data retention (ZDR). This demo instance uses standard API tier without ZDR. If you self-host with your own API keys, you can configure ZDR through your provider account.
              </p>
            </section>

            <section style={{ marginBottom: "var(--space-6)" }}>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                4. Deletion Flow
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-4)" }}>
                When you delete a resume via <code>DELETE /api/v1/resumes/&#123;uid&#125;</code>, the system executes cascading deletion across all storage layers: Neo4j (ResumeNode and all connected nodes with relationships), Qdrant (all vectors matching uid filter), file storage (PDF from local uploads or S3), Redis (job record), and cache (invalidated RAG results). Deletion is permanent and immediate.
              </p>

              <PlantUMLDiagram
                src="/diagrams/deletion-flow.puml"
                alt="Resume Deletion Flow Sequence Diagram"
                caption="Deletion flow"
              />
            </section>

            <section>
              <h2 style={{
                fontSize: "var(--text-2xl)",
                fontWeight: 700,
                marginBottom: "var(--space-3)",
                color: "var(--neutral-900)"
              }}>
                5. Infrastructure
              </h2>
              <p style={{ color: "var(--neutral-700)", marginBottom: "var(--space-4)" }}>
                Self-hosted on EU server via Docker Compose. Traefik reverse proxy routes traffic to frontend (React/Vite SPA) and backend (Django API with Uvicorn). Databases (Neo4j, Qdrant, Redis) isolated on internal network, accessible only from backend and workers. Two async workers handle processing and cleanup jobs. Prometheus scrapes metrics from exporters and backend; Grafana visualizes them. All external traffic uses HTTPS. This is a demo environment, not production-grade infrastructure.
              </p>

              <PlantUMLDiagram
                src="/diagrams/infrastructure.puml"
                alt="Infrastructure Component Diagram"
                caption="System architecture"
              />
            </section>
          </div>
        </div>
      </PageContainer>
    </PageWrapper>
  );
}
