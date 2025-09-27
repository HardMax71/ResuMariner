import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getJob, getJobResult, type JobResponse, type JobResult } from "../lib/api";

// Simple utility to make any value renderable
const renderValue = (value: any): string => {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (typeof value === "object") {
    // Handle common nested structures
    if (value.city || value.country) return [value.city, value.country].filter(Boolean).join(", ");
    if (value.name) return value.name;
    if (value.title) return value.title;
    if (value.value) return value.value;
    // For arrays, join them
    if (Array.isArray(value)) return value.map(renderValue).join(", ");
    // Otherwise stringify
    return JSON.stringify(value);
  }
  return String(value);
};

export default function JobStatus() {
  const { jobId = "" } = useParams();
  const [job, setJob] = useState<JobResponse | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["personal", "skills"]));
  const timer = useRef<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const j = await getJob(jobId);
        if (cancelled) return;
        setJob(j);
        if (j.status === "completed") {
          const r = await getJobResult(jobId);
          if (!cancelled) setResult(r);
          return; // stop polling
        }
        if (j.status === "failed") return; // stop polling
        timer.current = window.setTimeout(poll, 2000);
      } catch (e: any) {
        if (!cancelled) setError(String(e.message || e));
      }
    };
    poll();
    return () => { cancelled = true; if (timer.current) window.clearTimeout(timer.current); };
  }, [jobId]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <span className="status-icon pending">⏳</span>;
      case "processing":
        return <span className="spinner" style={{ width: "24px", height: "24px" }}></span>;
      case "completed":
        return <span className="status-icon success">✓</span>;
      case "failed":
        return <span className="status-icon error">✗</span>;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "var(--gray-600)";
      case "processing": return "var(--blue-600)";
      case "completed": return "var(--success)";
      case "failed": return "var(--danger)";
      default: return "var(--gray-600)";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (created: string, updated: string) => {
    const duration = new Date(updated).getTime() - new Date(created).getTime();
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    }
    return `${seconds}s`;
  };

  const renderResumeSection = (title: string, key: string, data: any) => {
    if (!data || (Array.isArray(data) && data.length === 0)) return null;
    if (typeof data === "object" && !Array.isArray(data) && Object.keys(data).length === 0) return null;

    const isExpanded = expandedSections.has(key);

    return (
      <div className="card" style={{ marginBottom: "var(--space-2)" }}>
        <div
          className="flex justify-between items-center"
          style={{ cursor: "pointer", userSelect: "none" }}
          onClick={() => toggleSection(key)}
        >
          <h3 className="title" style={{ marginBottom: 0 }}>{title}</h3>
          <svg
            className={`chevron ${isExpanded ? "expanded" : ""}`}
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M7 10l5 5 5-5" />
          </svg>
        </div>

        {isExpanded && (
          <div style={{ marginTop: "var(--space-2)" }}>
            {key === "personal" && typeof data === "object" && (
              <div className="grid grid-2 gap-2">
                {Object.entries(data).map(([field, value]) => (
                  <div key={field}>
                    <span className="small muted">{field.replace(/_/g, " ").toUpperCase()}</span>
                    <p className="small" style={{ marginTop: "4px" }}>
                      {renderValue(value)}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {key === "skills" && Array.isArray(data) && (
              <div className="chips">
                {data.map((skill: any, idx: number) => (
                  <span key={idx} className="chip">{renderValue(skill)}</span>
                ))}
              </div>
            )}

            {key === "experience" && Array.isArray(data) && (
              <div className="flex flex-col gap-2">
                {data.map((exp: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "var(--space-2)",
                      background: "var(--gray-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--blue-600)"
                    }}
                  >
                    <div className="flex justify-between">
                      <div>
                        <strong>{renderValue(exp.position || exp.role)}</strong>
                        {exp.company && <span className="muted"> at {renderValue(exp.company)}</span>}
                      </div>
                      {(exp.start_date || exp.duration) && (
                        <span className="small muted">
                          {exp.start_date ? `${renderValue(exp.start_date)} - ${renderValue(exp.end_date) || "Present"}` : renderValue(exp.duration)}
                        </span>
                      )}
                    </div>
                    {exp.description && (
                      <p className="small muted" style={{ marginTop: "var(--space-1)" }}>
                        {renderValue(exp.description)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}

            {key === "education" && Array.isArray(data) && (
              <div className="flex flex-col gap-2">
                {data.map((edu: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "var(--space-2)",
                      background: "var(--gray-50)",
                      borderRadius: "var(--radius-sm)"
                    }}
                  >
                    <strong>{renderValue(edu.degree || edu.qualification)}</strong>
                    {edu.field && <span className="muted"> in {renderValue(edu.field)}</span>}
                    {edu.institution && <div className="small muted">{renderValue(edu.institution)}</div>}
                    {edu.year && <div className="small muted">{renderValue(edu.year)}</div>}
                  </div>
                ))}
              </div>
            )}

            {/* Default rendering for other types */}
            {!["personal", "skills", "experience", "education"].includes(key) && (
              <pre className="json-view" style={{ fontSize: "var(--text-sm)" }}>
                {JSON.stringify(data, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="container">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 style={{ marginBottom: "var(--space-1)" }}>Job Details</h1>
          <code className="small" style={{
            background: "var(--gray-100)",
            padding: "var(--space-1)",
            borderRadius: "var(--radius-sm)",
            fontFamily: "monospace"
          }}>
            {jobId}
          </code>
        </div>
        <Link to="/upload" className="btn ghost">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Upload Another
        </Link>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error mb-3">
          <strong>Error loading job:</strong> {error}
        </div>
      )}

      {/* Loading State */}
      {!job && !error && (
        <div className="card" style={{ textAlign: "center", padding: "var(--space-6)" }}>
          <div className="spinner" style={{ width: "48px", height: "48px", margin: "0 auto var(--space-3)" }}></div>
          <p className="muted">Loading job details...</p>
        </div>
      )}

      {/* Job Status Card */}
      {job && (
        <div className="card mb-3" style={{
          borderLeft: `4px solid ${getStatusColor(job.status)}`,
          background: job.status === "processing" ? "var(--blue-50)" : "var(--white)"
        }}>
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              {getStatusIcon(job.status)}
              <div>
                <h2 className="title" style={{ marginBottom: "var(--space-1)" }}>
                  {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </h2>
                <div className="flex flex-col gap-1">
                  <span className="small muted">
                    Created: {formatDate(job.created_at)}
                  </span>
                  {job.updated_at !== job.created_at && (
                    <span className="small muted">
                      Updated: {formatDate(job.updated_at)}
                    </span>
                  )}
                  {(job.status === "completed" || job.status === "failed") && (
                    <span className="small muted">
                      Duration: {formatDuration(job.created_at, job.updated_at)}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {job.status === "completed" && (
              <span className="badge badge-success">COMPLETE</span>
            )}
            {job.status === "failed" && (
              <span className="badge badge-danger">FAILED</span>
            )}
            {job.status === "processing" && (
              <span className="badge badge-primary">IN PROGRESS</span>
            )}
            {job.status === "pending" && (
              <span className="badge">QUEUED</span>
            )}
          </div>

          {/* Error Message */}
          {job.error && (
            <div className="error" style={{ marginTop: "var(--space-3)" }}>
              <strong>Error:</strong> {job.error}
            </div>
          )}

          {/* Processing Animation */}
          {job.status === "processing" && (
            <div style={{ marginTop: "var(--space-3)" }}>
              <div className="flex justify-between mb-1">
                <span className="small muted">Processing your CV...</span>
                <span className="small muted">Please wait</span>
              </div>
              <div style={{
                height: "8px",
                background: "var(--gray-200)",
                borderRadius: "var(--radius-full)",
                overflow: "hidden"
              }}>
                <div className="progress-bar" style={{
                  height: "100%",
                  width: "30%",
                  background: "var(--blue-600)",
                  borderRadius: "var(--radius-full)",
                  animation: "progress 2s ease-in-out infinite"
                }}></div>
              </div>
            </div>
          )}

          {/* Result URL */}
          {job.result_url && (
            <div style={{ marginTop: "var(--space-3)" }}>
              <span className="small muted">Result available at: </span>
              <a href={job.result_url} className="small" style={{ color: "var(--blue-600)" }}>
                {job.result_url}
              </a>
            </div>
          )}
        </div>
      )}

      {/* Results Display */}
      {result && (
        <>
          {/* Resume Data */}
          {result.resume && (
            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h2>Extracted Resume Data</h2>
                <button
                  className="btn ghost"
                  onClick={() => setShowRawJson(!showRawJson)}
                  style={{ padding: "var(--space-1) var(--space-2)", fontSize: "var(--text-sm)" }}
                >
                  {showRawJson ? "Hide" : "Show"} Raw JSON
                </button>
              </div>

              {showRawJson ? (
                <div className="card">
                  <pre className="json-view">{JSON.stringify(result.resume, null, 2)}</pre>
                </div>
              ) : (
                <>
                  {renderResumeSection("Personal Information", "personal", (() => {
                    // Extract personal info from nested structure
                    const r = result.resume;
                    const personal: any = {};

                    // Try different paths for personal info
                    if (r.personal_info) {
                      personal.name = r.personal_info.name;
                      if (r.personal_info.contact) {
                        personal.email = r.personal_info.contact.email;
                        personal.phone = r.personal_info.contact.phone;
                        personal.linkedin = r.personal_info.contact.linkedin;
                        personal.github = r.personal_info.contact.github;
                        personal.website = r.personal_info.contact.website;
                      }
                      if (r.personal_info.demographics?.current_location) {
                        personal.location = r.personal_info.demographics.current_location;
                      }
                    } else {
                      // Fallback to flat structure
                      personal.name = r.name;
                      personal.email = r.email;
                      personal.phone = r.phone;
                      personal.location = r.location;
                      personal.linkedin = r.linkedin;
                      personal.github = r.github;
                      personal.website = r.website;
                    }

                    return Object.fromEntries(
                      Object.entries(personal).filter(([_, v]) => v !== null && v !== undefined)
                    );
                  })())}
                  {renderResumeSection("Skills", "skills", result.resume.skills)}
                  {renderResumeSection("Experience", "experience", result.resume.employment_history || result.resume.experience || result.resume.work_experience)}
                  {renderResumeSection("Education", "education", result.resume.education)}
                  {renderResumeSection("Languages", "languages", result.resume.languages)}
                  {renderResumeSection("Certifications", "certifications", result.resume.certifications)}
                  {renderResumeSection("Projects", "projects", result.resume.projects)}
                </>
              )}
            </div>
          )}

          {/* Review Data */}
          {result.review && (
            <div className="mb-4">
              <h2 className="mb-3">AI Review</h2>
              <div className="card" style={{
                borderLeft: "4px solid var(--blue-600)",
                background: "var(--blue-50)"
              }}>
                <div className="flex items-start gap-2">
                  <span style={{ fontSize: "24px" }}>🤖</span>
                  <div style={{ flex: 1 }}>
                    {typeof result.review === "string" ? (
                      <p>{result.review}</p>
                    ) : (
                      <pre className="json-view" style={{ background: "var(--white)" }}>
                        {JSON.stringify(result.review, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Metadata */}
          {result.metadata && Object.keys(result.metadata).length > 0 && (
            <details>
              <summary className="flex items-center gap-2" style={{
                cursor: "pointer",
                userSelect: "none",
                padding: "var(--space-2) 0",
                listStyle: "none"
              }}>
                <svg
                  className="chevron"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M7 10l5 5 5-5" />
                </svg>
                <span className="title" style={{ marginBottom: 0 }}>Processing Metadata</span>
              </summary>
              <div className="card" style={{ marginTop: "var(--space-2)" }}>
                <pre className="json-view" style={{ fontSize: "var(--text-sm)" }}>
                  {JSON.stringify(result.metadata, null, 2)}
                </pre>
              </div>
            </details>
          )}
        </>
      )}
    </div>
  );
}