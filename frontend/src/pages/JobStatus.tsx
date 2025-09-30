import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getJob, getJobResult, API_BASE_URL, type JobResponse, type JobResult } from "../lib/api";
import { Copy, Check, Hash } from "lucide-react";

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

// Unified badge styling system with gradient color scheme
const getBadgeStyle = (text: string, category?: string) => {
  const t = text.toLowerCase();

  // Education status - gradient: ongoing (blue) → completed (green)
  if (category === "education_status") {
    if (t.includes("ongoing") || t.includes("current")) {
      return { bg: "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)", color: "#1e40af", border: "#3b82f6" };
    }
    if (t.includes("completed") || t.includes("graduated")) {
      return { bg: "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)", color: "#065f46", border: "#10b981" };
    }
  }

  // Employment type - gradient based on commitment level
  if (category === "employment_type") {
    if (t.includes("full-time") || t.includes("full time") || t.includes("fulltime")) {
      return { bg: "linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%)", color: "#5b21b6", border: "#8b5cf6" };
    }
    if (t.includes("part-time") || t.includes("part time") || t.includes("parttime")) {
      return { bg: "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)", color: "#92400e", border: "#f59e0b" };
    }
    if (t.includes("contract") || t.includes("freelance") || t.includes("consultant")) {
      return { bg: "linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)", color: "#3730a3", border: "#6366f1" };
    }
    if (t.includes("intern") || t.includes("internship")) {
      return { bg: "linear-gradient(135deg, #fed7aa 0%, #fdba74 100%)", color: "#9a3412", border: "#f97316" };
    }
  }

  // Work mode - gradient based on flexibility
  if (category === "work_mode") {
    if (t.includes("remote")) {
      return { bg: "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)", color: "#065f46", border: "#10b981" };
    }
    if (t.includes("hybrid")) {
      return { bg: "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)", color: "#1e3a8a", border: "#3b82f6" };
    }
    if (t.includes("on-site") || t.includes("onsite") || t.includes("office")) {
      return { bg: "linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%)", color: "#831843", border: "#ec4899" };
    }
  }

  // Default gradient - neutral purple
  return { bg: "linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)", color: "#374151", border: "#9ca3af" };
};

// Type definition for resume section configuration
interface ResumeSection {
  title: string;       // Display title for the section
  key: string;         // Unique key for React and expanded state
  paths: string[];     // Array of possible property paths to check in order
  alwaysShow?: boolean; // Whether to show section even when empty (shows "No data available")
}

/**
 * Configuration for resume sections - easily extensible and reorderable
 *
 * To add a new section:
 * 1. Add an object with title, key, and paths array
 * 2. Set alwaysShow to true if you want to show "No data" when empty
 *
 * To reorder sections:
 * - Simply move the objects around in this array
 *
 * The paths array contains fallback property names to check in order
 */
const RESUME_SECTIONS: ResumeSection[] = [
  {
    title: "Experience",
    key: "experience",
    paths: ["employment_history", "experience", "work_experience"],
    alwaysShow: false // Only show if data exists
  },
  {
    title: "Education",
    key: "education",
    paths: ["education"],
    alwaysShow: false
  },
  {
    title: "Projects",
    key: "projects",
    paths: ["projects"],
    alwaysShow: false
  },
  {
    title: "Languages",
    key: "languages",
    paths: ["language_proficiency", "languages"],
    alwaysShow: false
  },
  {
    title: "Certifications",
    key: "certifications",
    paths: ["certifications", "certificates"],
    alwaysShow: false
  },
  {
    title: "Awards",
    key: "awards",
    paths: ["awards", "achievements"],
    alwaysShow: false
  },
  {
    title: "Publications",
    key: "publications",
    paths: ["scientific_contributions", "publications"],
    alwaysShow: false
  },
  {
    title: "Courses",
    key: "courses",
    paths: ["courses", "training"],
    alwaysShow: false
  }
];

export default function JobStatus() {
  const { jobId = "" } = useParams();
  const [job, setJob] = useState<JobResponse | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["personal", "skills"]));
  const [copiedButtons, setCopiedButtons] = useState<Set<string>>(new Set());
  const timer = useRef<number | null>(null);

  const handleCopy = (text: string, buttonId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedButtons(prev => new Set(prev).add(buttonId));
    setTimeout(() => {
      setCopiedButtons(prev => {
        const next = new Set(prev);
        next.delete(buttonId);
        return next;
      });
    }, 2000);
  };

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
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "var(--gray-600)" }}>
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        );
      case "processing":
        return <span className="spinner" style={{ width: "24px", height: "24px" }}></span>;
      case "completed":
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ color: "var(--success)" }}>
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        );
      case "failed":
        return (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ color: "var(--danger)" }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        );
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
    const isEmpty = !data ||
                   (Array.isArray(data) && data.length === 0) ||
                   (typeof data === "object" && !Array.isArray(data) && Object.keys(data).length === 0);

    const isExpanded = expandedSections.has(key);

    return (
      <div className="glass-card" style={{ marginBottom: "var(--space-2)" }}>
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
            {isEmpty ? (
              <div style={{
                padding: "var(--space-3)",
                textAlign: "center",
                color: "var(--gray-500)",
                fontSize: "14px"
              }}>
                No data available
              </div>
            ) : (
              <>
            {key === "personal" && typeof data === "object" && (
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
                {/* Avatar */}
                <div style={{
                  width: "48px",
                  height: "48px",
                  borderRadius: "var(--radius-full)",
                  background: "var(--blue-100)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "20px",
                  fontWeight: 600,
                  color: "var(--blue-600)",
                  flexShrink: 0
                }}>
                  {data.name ? data.name.charAt(0).toUpperCase() : "?"}
                </div>

                {/* Info */}
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "6px" }}>
                  <h4 style={{ fontSize: "var(--text-lg)", fontWeight: 600, margin: 0 }}>
                    {renderValue(data.name) || "—"}
                  </h4>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", flexWrap: "wrap" }}>
                    {data.email && (
                      <a href={`mailto:${renderValue(data.email)}`} style={{
                        fontSize: "13px",
                        color: "var(--blue-600)",
                        textDecoration: "none"
                      }}>
                        {renderValue(data.email)}
                      </a>
                    )}
                    {data.phone && (
                      <a href={`tel:${renderValue(data.phone)}`} style={{
                        fontSize: "13px",
                        color: "var(--gray-700)",
                        textDecoration: "none"
                      }}>
                        📞 {renderValue(data.phone)}
                      </a>
                    )}
                    {data.location && (
                      <span style={{ fontSize: "13px", color: "var(--gray-600)" }}>
                        📍 {renderValue(data.location)}
                      </span>
                    )}
                  </div>
                </div>

                {/* Social Links */}
                {(data.linkedin || data.github || data.website) && (
                  <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                    {data.linkedin && (
                      <a href={renderValue(data.linkedin)} target="_blank" rel="noopener noreferrer" title="LinkedIn">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-600)" }}>
                          <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
                        </svg>
                      </a>
                    )}
                    {data.github && (
                      <a href={renderValue(data.github)} target="_blank" rel="noopener noreferrer" title="GitHub">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-600)" }}>
                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                      </a>
                    )}
                    {data.website && (
                      <a href={renderValue(data.website)} target="_blank" rel="noopener noreferrer" title="Website">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "var(--gray-600)" }}>
                          <circle cx="12" cy="12" r="10" />
                          <line x1="2" y1="12" x2="22" y2="12" />
                          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                        </svg>
                      </a>
                    )}
                  </div>
                )}
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
              <div className="flex flex-col gap-3">
                {data.map((exp: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "14px",
                      background: "var(--white)",
                      border: "1px solid var(--gray-200)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--blue-500)"
                    }}
                  >
                    {/* Header row with position and dates */}
                    <div className="flex justify-between items-start" style={{ marginBottom: "8px" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "15px",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--gray-900)"
                        }}>
                          {renderValue(exp.position)}
                        </h4>
                        <div style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          marginTop: "4px"
                        }}>
                          {exp.company && (
                            <a
                              href={exp.company.url || "#"}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                fontSize: "14px",
                                color: exp.company.url ? "var(--blue-600)" : "var(--gray-700)",
                                textDecoration: "none",
                                fontWeight: 500,
                                cursor: exp.company.url ? "pointer" : "default"
                              }}
                              onClick={!exp.company.url ? (e) => e.preventDefault() : undefined}
                            >
                              {renderValue(exp.company.name || exp.company)}
                            </a>
                          )}
                          {exp.employment_type && (
                            <span style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              ...(() => {
                                const style = getBadgeStyle(exp.employment_type, "employment_type");
                                return {
                                  background: style.bg,
                                  color: style.color,
                                  border: `1px solid ${style.border}40`,
                                  padding: "3px 8px",
                                  borderRadius: "12px",
                                  textTransform: "uppercase" as const,
                                  letterSpacing: "0.02em"
                                };
                              })()
                            }}>
                              {exp.employment_type}
                            </span>
                          )}
                          {exp.work_mode && (
                            <span style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              ...(() => {
                                const style = getBadgeStyle(exp.work_mode, "work_mode");
                                return {
                                  background: style.bg,
                                  color: style.color,
                                  border: `1px solid ${style.border}40`,
                                  padding: "3px 8px",
                                  borderRadius: "12px",
                                  textTransform: "uppercase" as const,
                                  letterSpacing: "0.02em"
                                };
                              })()
                            }}>
                              {exp.work_mode}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Duration and location */}
                      <div style={{
                        textAlign: "right",
                        fontSize: "13px",
                        color: "var(--gray-600)"
                      }}>
                        {exp.duration && (
                          <div style={{ fontWeight: 500 }}>
                            {exp.duration.start} – {exp.duration.end || "Present"}
                          </div>
                        )}
                        {exp.location && (
                          <div style={{ fontSize: "12px", marginTop: "2px" }}>
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" style={{
                              marginRight: "4px",
                              verticalAlign: "middle",
                              color: "var(--gray-500)"
                            }}>
                              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                            </svg>
                            {[exp.location.city, exp.location.country].filter(Boolean).join(", ")}
                          </div>
                        )}
                        {exp.duration?.duration_months && (
                          <div style={{
                            fontSize: "11px",
                            color: "var(--gray-500)",
                            marginTop: "2px"
                          }}>
                            {Math.floor(exp.duration.duration_months / 12) > 0 &&
                              `${Math.floor(exp.duration.duration_months / 12)}y `}
                            {exp.duration.duration_months % 12 > 0 &&
                              `${exp.duration.duration_months % 12}mo`}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Key points */}
                    {exp.key_points && exp.key_points.length > 0 && (
                      <ul style={{
                        margin: "10px 0 0 0",
                        paddingLeft: "20px",
                        fontSize: "13px",
                        color: "var(--gray-700)",
                        lineHeight: 1.6
                      }}>
                        {exp.key_points.map((point: any, pidx: number) => (
                          <li key={pidx} style={{ marginBottom: "4px" }}>
                            {renderValue(point.text || point)}
                          </li>
                        ))}
                      </ul>
                    )}

                    {/* Skills */}
                    {exp.skills && exp.skills.length > 0 && (
                      <div style={{
                        marginTop: "10px",
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "6px"
                      }}>
                        {exp.skills.map((skill: any, tidx: number) => (
                          <span
                            key={tidx}
                            style={{
                              fontSize: "11px",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)",
                              color: "#3730a3",
                              border: "1px solid #6366f140",
                              borderRadius: "12px"
                            }}
                          >
                            {renderValue(skill.name || skill)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {key === "projects" && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((proj: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "14px",
                      background: "var(--white)",
                      border: "1px solid var(--gray-200)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--green-600)"
                    }}
                  >
                    {/* Header with title and link */}
                    <div className="flex justify-between items-start" style={{ marginBottom: "8px" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "15px",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--gray-900)"
                        }}>
                          {proj.url ? (
                            <a
                              href={renderValue(proj.url)}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                color: "var(--gray-900)",
                                textDecoration: "none"
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.textDecoration = "underline"}
                              onMouseLeave={(e) => e.currentTarget.style.textDecoration = "none"}
                            >
                              {renderValue(proj.title)}
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{
                                marginLeft: "6px",
                                verticalAlign: "middle",
                                opacity: 0.6
                              }}>
                                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                                <polyline points="15 3 21 3 21 9" />
                                <line x1="10" y1="14" x2="21" y2="3" />
                              </svg>
                            </a>
                          ) : (
                            renderValue(proj.title)
                          )}
                        </h4>
                        {proj.description && (
                          <div style={{
                            fontSize: "13px",
                            color: "var(--gray-600)",
                            marginTop: "4px"
                          }}>
                            {renderValue(proj.description)}
                          </div>
                        )}
                      </div>

                      {/* Platform icon based on URL */}
                      {proj.url && (
                        <a
                          href={renderValue(proj.url)}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "4px",
                            padding: "4px",
                            borderRadius: "var(--radius-sm)",
                            transition: "background 0.2s"
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.background = "var(--gray-100)"}
                          onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                          title={(() => {
                            const url = renderValue(proj.url).toLowerCase();
                            if (url.includes("github")) return "View on GitHub";
                            if (url.includes("gitlab")) return "View on GitLab";
                            if (url.includes("gitea")) return "View on Gitea";
                            if (url.includes("bitbucket")) return "View on Bitbucket";
                            return "View project";
                          })()}
                        >
                          {(() => {
                            const url = renderValue(proj.url).toLowerCase();
                            if (url.includes("github")) {
                              return (
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-600)" }}>
                                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                </svg>
                              );
                            }
                            if (url.includes("gitlab")) {
                              return (
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-600)" }}>
                                  <path d="M22.65 14.39L12 22.13 1.35 14.39a.84.84 0 0 1-.3-.94l1.22-3.78 2.44-7.51A.42.42 0 0 1 4.82 2a.43.43 0 0 1 .58 0 .42.42 0 0 1 .11.18l2.44 7.49h8.1l2.44-7.51A.42.42 0 0 1 18.6 2a.43.43 0 0 1 .58 0 .42.42 0 0 1 .11.18l2.44 7.51L23 13.45a.84.84 0 0 1-.35.94z"/>
                                </svg>
                              );
                            }
                            if (url.includes("gitea")) {
                              return (
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-600)" }}>
                                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5.5 11c-.28 0-.5-.22-.5-.5s-.22-.5-.5-.5-.5.22-.5.5v2c0 .28-.22.5-.5.5s-.5-.22-.5-.5v-2c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.22.5-.5.5zm-11 0c-.28 0-.5-.22-.5-.5S7.72 11 8 11s.5.22.5.5v2c0 .28.22.5.5.5s.5-.22.5-.5v-2c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5.22.5.5.5z"/>
                                </svg>
                              );
                            }
                            if (url.includes("bitbucket")) {
                              return (
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-600)" }}>
                                  <path d="M3.04 2.43a.73.73 0 0 0-.73.86l3.04 17.79c.06.36.34.64.7.7l.06.01 7.62 2.18c.24.07.5-.02.66-.22a.74.74 0 0 0 .15-.26l3.04-20.31a.73.73 0 0 0-.59-.86.73.73 0 0 0-.14-.01zm7.29 13.3H7.66l-.73-4.32h4.66z"/>
                                </svg>
                              );
                            }
                            // Generic code/link icon for other sites
                            return (
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "var(--gray-600)" }}>
                                <polyline points="16 18 22 12 16 6" />
                                <polyline points="8 6 2 12 8 18" />
                              </svg>
                            );
                          })()}
                        </a>
                      )}
                    </div>

                    {/* Key points */}
                    {proj.key_points && proj.key_points.length > 0 && (
                      <ul style={{
                        margin: "10px 0 0 0",
                        paddingLeft: "20px",
                        fontSize: "13px",
                        color: "var(--gray-700)",
                        lineHeight: 1.6
                      }}>
                        {proj.key_points.map((point: any, pidx: number) => (
                          <li key={pidx} style={{ marginBottom: "4px" }}>
                            {renderValue(point.text || point)}
                          </li>
                        ))}
                      </ul>
                    )}

                    {/* Skills */}
                    {proj.skills && proj.skills.length > 0 && (
                      <div style={{
                        marginTop: "10px",
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "6px"
                      }}>
                        {proj.skills.map((skill: any, tidx: number) => (
                          <span
                            key={tidx}
                            style={{
                              fontSize: "11px",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)",
                              color: "#065f46",
                              border: "1px solid #10b98140",
                              borderRadius: "12px"
                            }}
                          >
                            {renderValue(skill.name || skill)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {key === "education" && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((edu: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "12px 14px",
                      background: "var(--white)",
                      border: "1px solid var(--gray-200)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--purple-500)"
                    }}
                  >
                    {/* Header with degree and dates */}
                    <div className="flex justify-between items-center">
                      <div style={{ flex: 1 }}>
                        <div style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          marginBottom: "4px"
                        }}>
                          <h4 style={{
                            fontSize: "var(--text-base)",
                            fontWeight: 600,
                            margin: 0,
                            color: "var(--gray-900)",
                            lineHeight: 1.3
                          }}>
                            {renderValue(edu.qualification || edu.degree)}
                            {edu.field && (
                              <>
                                <span style={{ fontWeight: 400, color: "var(--gray-600)" }}> in </span>
                                <span style={{ fontWeight: 400, color: "var(--gray-800)" }}>{renderValue(edu.field)}</span>
                              </>
                            )}
                          </h4>
                          {edu.status && (
                            <span style={{
                              fontSize: "var(--text-xs)",
                              fontWeight: 600,
                              flexShrink: 0,
                              ...(() => {
                                const style = getBadgeStyle(edu.status, "education_status");
                                return {
                                  background: style.bg,
                                  color: style.color,
                                  border: `1px solid ${style.border}40`,
                                  padding: "3px 8px",
                                  borderRadius: "12px",
                                  textTransform: "uppercase" as const,
                                  letterSpacing: "0.02em"
                                };
                              })()
                            }}>
                              {edu.status}
                            </span>
                          )}
                        </div>
                        <div style={{
                          fontSize: "var(--text-sm)",
                          color: "var(--gray-700)"
                        }}>
                          {edu.institution && renderValue(edu.institution.name || edu.institution)}
                        </div>
                      </div>

                      {/* Dates and location */}
                      <div style={{
                        textAlign: "right",
                        fontSize: "var(--text-sm)",
                        color: "var(--gray-600)",
                        marginLeft: "var(--space-3)",
                        flexShrink: 0
                      }}>
                        {(edu.start || edu.end) && (
                          <div style={{ fontWeight: 500 }}>
                            {edu.start} – {edu.end || "Present"}
                          </div>
                        )}
                        {edu.year && !edu.start && (
                          <div style={{ fontWeight: 500 }}>
                            {renderValue(edu.year)}
                          </div>
                        )}
                        {edu.location && (
                          <div style={{ fontSize: "12px", marginTop: "2px" }}>
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" style={{
                              marginRight: "4px",
                              verticalAlign: "middle",
                              color: "var(--gray-500)"
                            }}>
                              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                            </svg>
                            {[edu.location.city, edu.location.state, edu.location.country].filter(Boolean).join(", ")}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Coursework */}
                    {edu.coursework && edu.coursework.length > 0 && (
                      <div style={{ marginTop: "8px" }}>
                        <div style={{
                          fontSize: "11px",
                          fontWeight: 500,
                          color: "var(--gray-500)",
                          marginBottom: "4px",
                          textTransform: "uppercase",
                          letterSpacing: "0.5px"
                        }}>
                          Coursework
                        </div>
                        <div style={{
                          display: "flex",
                          flexWrap: "wrap",
                          gap: "5px"
                        }}>
                          {edu.coursework.map((course: any, cidx: number) => (
                            <span
                              key={cidx}
                              style={{
                                fontSize: "11px",
                                fontWeight: 500,
                                padding: "3px 8px",
                                background: "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)",
                                color: "#92400e",
                                border: "1px solid #f59e0b40",
                                borderRadius: "12px"
                              }}
                            >
                              {renderValue(course.name || course)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Extras like GPA, honors, etc */}
                    {edu.extras && edu.extras.length > 0 && (
                      <ul style={{
                        margin: "8px 0 0 0",
                        paddingLeft: "18px",
                        fontSize: "12px",
                        color: "var(--gray-600)",
                        lineHeight: 1.5
                      }}>
                        {edu.extras.map((extra: any, eidx: number) => (
                          <li key={eidx} style={{ marginBottom: "2px" }}>
                            {renderValue(extra)}
                          </li>
                        ))}
                      </ul>
                    )}

                    {/* GPA if present */}
                    {edu.gpa && (
                      <div style={{
                        marginTop: "6px",
                        fontSize: "12px",
                        color: "var(--gray-600)"
                      }}>
                        <span style={{ fontWeight: 500 }}>GPA:</span> {renderValue(edu.gpa)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {key === "languages" && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((lang: any, idx: number) => {
                  const langName = lang.language?.name || lang.name || lang;
                  const cefr = lang.cefr;
                  const selfAssessed = lang.self_assessed;
                  const level = lang.level;

                  return (
                    <div
                      key={idx}
                      style={{
                        padding: "12px 14px",
                        background: "var(--white)",
                        border: "1px solid var(--gray-200)",
                        borderRadius: "var(--radius-sm)",
                        borderLeft: "3px solid var(--cyan-600)"
                      }}
                    >
                      <div className="flex justify-between items-center">
                        {/* Language name */}
                        <h4 style={{
                          fontSize: "15px",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--gray-900)"
                        }}>
                          {renderValue(langName)}
                        </h4>

                        {/* Proficiency badges */}
                        <div style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "6px"
                        }}>
                          {selfAssessed && (
                            <span style={{
                              fontSize: "11px",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "var(--gray-100)",
                              color: "var(--gray-700)",
                              border: "1px solid var(--gray-300)",
                              borderRadius: "10px",
                              textTransform: "uppercase",
                              letterSpacing: "0.3px"
                            }}>
                              Self: {selfAssessed}
                            </span>
                          )}
                          {cefr && (
                            <span style={{
                              fontSize: "11px",
                              fontWeight: 600,
                              padding: "3px 8px",
                              background: "#10b981",
                              color: "white",
                              borderRadius: "10px",
                              textTransform: "uppercase",
                              letterSpacing: "0.3px"
                            }}>
                              CEFR: {cefr}
                            </span>
                          )}
                          {!cefr && !selfAssessed && level && (
                            <span style={{
                              fontSize: "11px",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "var(--gray-100)",
                              color: "var(--gray-700)",
                              border: "1px solid var(--gray-300)",
                              borderRadius: "10px"
                            }}>
                              {level}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Default rendering for other types */}
            {!["personal", "skills", "experience", "education", "projects", "languages"].includes(key) && (
              <div style={{ position: "relative" }}>
                <button
                  className="btn ghost"
                  onClick={() => handleCopy(JSON.stringify(data, null, 2), `section-${key}`)}
                  style={{
                    position: "absolute",
                    top: "4px",
                    right: "4px",
                    padding: "4px",
                    fontSize: "11px",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    background: copiedButtons.has(`section-${key}`) ? "var(--green-50)" : "var(--white)",
                    border: `1px solid ${copiedButtons.has(`section-${key}`) ? "var(--green-300)" : "var(--gray-300)"}`,
                    zIndex: 1,
                    transition: "all 0.3s ease",
                    color: copiedButtons.has(`section-${key}`) ? "var(--green-600)" : "inherit"
                  }}
                  title={copiedButtons.has(`section-${key}`) ? "Copied!" : "Copy to clipboard"}
                >
                  {copiedButtons.has(`section-${key}`) ? (
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : (
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                  )}
                </button>
                <pre className="json-view" style={{ fontSize: "var(--text-sm)", paddingTop: "28px" }}>
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            )}
            </>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="page-wrapper">
      <div className="page-container">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 style={{ margin: 0 }}>Job Processing Status</h1>
        <Link to="/upload" className="btn ghost">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: "var(--space-1)" }}>
            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
            <path d="M21 3v5h-5" />
            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
            <path d="M8 16H3v5" />
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
        <div className="glass-card" style={{
          padding: "var(--space-6)",
          textAlign: "center"
        }}>
          <div className="spinner" style={{ width: "48px", height: "48px", margin: "0 auto var(--space-3)" }}></div>
          <p className="muted">Loading job details...</p>
        </div>
      )}

      {/* Job Status Card */}
      {job && (
        <div className="glass-card" style={{
          borderTop: `3px solid ${getStatusColor(job.status)}`,
          marginBottom: "var(--space-3)"
        }}>
          {/* Main Status Row */}
          <div className="flex justify-between items-center" style={{ marginBottom: "var(--space-3)" }}>
            {/* Status Hero */}
            <div className="flex items-center gap-3">
              <div style={{
                width: "48px",
                height: "48px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "var(--radius-full)",
                background: job.status === "completed" ? "rgba(16, 185, 129, 0.1)" :
                           job.status === "processing" ? "rgba(59, 130, 246, 0.1)" :
                           job.status === "failed" ? "rgba(239, 68, 68, 0.1)" : "var(--gray-100)"
              }}>
                {getStatusIcon(job.status)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 style={{
                    color: getStatusColor(job.status),
                    margin: 0
                  }}>
                    {job.status === "completed" ? "Processing Complete" :
                     job.status === "processing" ? "Processing Resume" :
                     job.status === "failed" ? "Processing Failed" : "Queued for Processing"}
                  </h1>
                  <button
                    onClick={() => handleCopy(job.job_id, "job-id")}
                    style={{
                      padding: "4px",
                      background: "transparent",
                      border: "none",
                      borderRadius: "var(--radius-sm)",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      transition: "background var(--transition-fast)",
                      color: "var(--gray-600)"
                    }}
                    title={copiedButtons.has("job-id") ? "Copied!" : `Job ID: ${job.job_id}`}
                    onMouseEnter={(e) => e.currentTarget.style.background = "var(--gray-100)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                  >
                    {copiedButtons.has("job-id") ? (
                      <Check size={14} style={{ color: "var(--success)" }} />
                    ) : (
                      <Hash size={14} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Actions */}
            {job.status === "completed" && (
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    const url = `${window.location.origin}/jobs/${job.job_id}`;
                    handleCopy(url, "copy-link");
                  }}
                  style={{
                    padding: "8px",
                    background: "white",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: "inherit"
                  }}
                  title={copiedButtons.has("copy-link") ? "Copied!" : "Copy link to clipboard"}
                >
                  {copiedButtons.has("copy-link") ? (
                    <Check size={16} style={{ color: "#10b981" }} />
                  ) : (
                    <Copy size={16} style={{ color: "#374151" }} />
                  )}
                </button>
                <a
                  href={`${API_BASE_URL}/api/v1/jobs/${job.job_id}/result/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: "8px",
                    background: "white",
                    border: "1px solid #d1d5db",
                    borderRadius: "6px",
                    cursor: "pointer",
                    textDecoration: "none",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                  }}
                  title="Open API JSON response"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "#374151" }}>
                    <polyline points="16 18 22 12 16 6" />
                    <polyline points="8 6 2 12 8 18" />
                  </svg>
                </a>
                {result?.review && (
                  <Link
                    to={`/jobs/${job.job_id}/review`}
                    style={{
                      padding: "6px 12px",
                      fontSize: "14px",
                      fontWeight: "600",
                      background: "#9333ea",
                      border: "1px solid #9333ea",
                      borderRadius: "6px",
                      color: "#ffffff",
                      textDecoration: "none",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      fontFamily: "inherit"
                    }}
                    title="View AI Resume Review"
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "#7e22ce";
                      e.currentTarget.style.borderColor = "#7e22ce";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "#9333ea";
                      e.currentTarget.style.borderColor = "#9333ea";
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "#ffffff" }}>
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                      <polyline points="10 9 9 9 8 9" />
                    </svg>
                    AI Review
                  </Link>
                )}
            </div>
            )}
          </div>

          {/* Processing Progress */}
          {job.status === "processing" && (
            <div style={{
              padding: "var(--space-2)",
              background: "var(--blue-50)",
              borderRadius: "var(--radius-sm)",
              marginBottom: "var(--space-2)"
            }}>
              <div className="flex justify-between mb-2">
                <span className="small" style={{ fontWeight: 600 }}>Analyzing document content...</span>
                <span className="small muted">Please wait</span>
              </div>
              <div style={{
                height: "6px",
                background: "var(--gray-200)",
                borderRadius: "var(--radius-full)",
                overflow: "hidden"
              }}>
                <div style={{
                  height: "100%",
                  width: "40%",
                  background: "var(--blue-600)",
                  borderRadius: "var(--radius-full)",
                  animation: "progress 2s ease-in-out infinite"
                }}></div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {job.error && (
            <div className="error" style={{ marginTop: 0 }}>
              <strong>Error:</strong> {job.error}
            </div>
          )}

          {/* Timing Information Footer */}
          <div className="flex gap-4" style={{
            paddingTop: "var(--space-2)",
            borderTop: "1px solid var(--gray-100)",
            marginTop: job.status === "processing" ? 0 : "var(--space-2)"
          }}>
            <span className="small muted">
              <strong>Started:</strong> {new Date(job.created_at).toLocaleTimeString()}
            </span>
            {job.updated_at !== job.created_at && (
              <span className="small muted">
                <strong>Updated:</strong> {new Date(job.updated_at).toLocaleTimeString()}
              </span>
            )}
            {(job.status === "completed" || job.status === "failed") && (
              <span className="small muted">
                <strong>Duration:</strong> {formatDuration(job.created_at, job.updated_at)}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <>
          {/* Resume Data */}
          {result.resume && (
            <div className="mb-4">
              <div className="flex justify-between items-center mb-3">
                <h2 style={{ margin: 0 }}>Extracted Resume Data</h2>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    className="btn ghost"
                    onClick={() => setShowRawJson(!showRawJson)}
                    style={{ padding: "var(--space-1) var(--space-2)", fontSize: "var(--text-sm)" }}
                  >
                    {showRawJson ? "Hide" : "Show"} Raw JSON
                  </button>
                  {result.metadata && Object.keys(result.metadata).length > 0 && (
                    <button
                      className="btn ghost"
                      onClick={() => setShowMetadata(!showMetadata)}
                      style={{ padding: "var(--space-1) var(--space-2)", fontSize: "var(--text-sm)" }}
                    >
                      {showMetadata ? "Hide" : "Show"} Metadata
                    </button>
                  )}
                </div>
              </div>

              {showMetadata ? (
                <div className="glass-card" style={{
                  position: "relative",
                  marginBottom: "var(--space-3)"
                }}>
                  <button
                    className="btn ghost"
                    onClick={() => handleCopy(JSON.stringify(result.metadata, null, 2), "metadata-json")}
                    style={{
                      position: "absolute",
                      top: "var(--space-2)",
                      right: "var(--space-2)",
                      padding: "6px",
                      fontSize: "12px",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      background: copiedButtons.has("metadata-json") ? "var(--green-50)" : "var(--white)",
                      border: `1px solid ${copiedButtons.has("metadata-json") ? "var(--green-300)" : "var(--gray-300)"}`,
                      zIndex: 1,
                      transition: "all 0.3s ease",
                      color: copiedButtons.has("metadata-json") ? "var(--green-600)" : "inherit"
                    }}
                    title={copiedButtons.has("metadata-json") ? "Copied!" : "Copy metadata to clipboard"}
                  >
                    {copiedButtons.has("metadata-json") ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    )}
                  </button>
                  <pre className="json-view" style={{ fontSize: "var(--text-sm)", paddingTop: "var(--space-4)" }}>
                    {JSON.stringify(result.metadata, null, 2)}
                  </pre>
                </div>
              ) : null}

              {showRawJson ? (
                <div className="glass-card" style={{ position: "relative" }}>
                  <button
                    className="btn ghost"
                    onClick={() => handleCopy(JSON.stringify(result.resume, null, 2), "main-json")}
                    style={{
                      position: "absolute",
                      top: "var(--space-2)",
                      right: "var(--space-2)",
                      padding: "6px",
                      fontSize: "12px",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      background: copiedButtons.has("main-json") ? "var(--green-50)" : "var(--white)",
                      border: `1px solid ${copiedButtons.has("main-json") ? "var(--green-300)" : "var(--gray-300)"}`,
                      zIndex: 1,
                      transition: "all 0.3s ease",
                      color: copiedButtons.has("main-json") ? "var(--green-600)" : "inherit"
                    }}
                    title={copiedButtons.has("main-json") ? "Copied!" : "Copy JSON to clipboard"}
                  >
                    {copiedButtons.has("main-json") ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                      </svg>
                    )}
                  </button>
                  <pre className="json-view" style={{ paddingTop: "var(--space-4)" }}>{JSON.stringify(result.resume, null, 2)}</pre>
                </div>
              ) : (
                <>

                  {/* Personal and Skills in flexible split */}
                  <div className="personal-skills-grid">
                    {/* Personal Info Card */}
                    <div className="glass-card">
                      {(() => {
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

                        const filteredPersonal = Object.fromEntries(
                          Object.entries(personal).filter(([_, v]) => v !== null && v !== undefined)
                        );

                        const resumeLang = r.personal_info?.resume_lang || r.resume_lang;

                        return (
                          <>
                            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "var(--space-2)" }}>
                              <h3 className="title" style={{ margin: 0, fontSize: "var(--text-sm)", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--gray-600)", fontWeight: 600 }}>Personal Information</h3>
                              {resumeLang && (
                                <span style={{
                                  display: "inline-flex",
                                  alignItems: "center",
                                  gap: "4px",
                                  padding: "2px 8px",
                                  background: "var(--blue-50)",
                                  border: "1px solid var(--blue-200)",
                                  borderRadius: "var(--radius-full)",
                                  fontSize: "10px",
                                  fontWeight: 600,
                                  color: "var(--blue-700)",
                                  textTransform: "uppercase",
                                  letterSpacing: "0.02em"
                                }}>
                                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ flexShrink: 0 }}>
                                    <path d="M4 5h16M4 9h16M4 13h16M4 17h10"/>
                                  </svg>
                                  {renderValue(resumeLang)}
                                </span>
                              )}
                            </div>

                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
                              {/* Name */}
                              <div>
                                <h4 style={{ fontSize: "var(--text-xl)", fontWeight: 700, margin: 0, lineHeight: 1.2, marginBottom: "4px", color: "var(--neutral-900)" }}>
                                  {renderValue(personal.name) || "—"}
                                </h4>
                                {personal.location && (
                                  <span style={{ fontSize: "var(--text-xs)", color: "var(--gray-600)", display: "flex", alignItems: "center", gap: "4px" }}>
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-500)", flexShrink: 0 }}>
                                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                                    </svg>
                                    {renderValue(personal.location)}
                                  </span>
                                )}
                              </div>

                            {/* Contact info in compact layout */}
                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
                              {personal.email && (
                                <a href={`mailto:${renderValue(personal.email)}`} style={{
                                  fontSize: "var(--text-sm)",
                                  color: "var(--blue-600)",
                                  textDecoration: "none",
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "8px",
                                  padding: "6px 8px",
                                  borderRadius: "var(--radius-sm)",
                                  transition: "background 0.2s"
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = "var(--blue-50)"}
                                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0 }}>
                                    <rect x="2" y="4" width="20" height="16" rx="2"/>
                                    <path d="m22,7-10,5L2,7"/>
                                  </svg>
                                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                    {renderValue(personal.email)}
                                  </span>
                                </a>
                              )}

                              {personal.phone && (
                                <a href={`tel:${renderValue(personal.phone)}`} style={{
                                  fontSize: "var(--text-sm)",
                                  color: "var(--blue-600)",
                                  textDecoration: "none",
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "8px",
                                  padding: "6px 8px",
                                  borderRadius: "var(--radius-sm)",
                                  transition: "background 0.2s"
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = "var(--blue-50)"}
                                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0 }}>
                                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                                  </svg>
                                  {renderValue(personal.phone)}
                                </a>
                              )}
                            </div>

                            {/* Social Links */}
                            {(personal.linkedin || personal.github || personal.website) && (
                              <div style={{
                                display: "flex",
                                gap: "8px",
                                paddingTop: "var(--space-2)",
                                borderTop: "1px solid var(--gray-200)"
                              }}>
                                {personal.linkedin && (
                                  <a
                                    href={renderValue(personal.linkedin)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    title="LinkedIn"
                                    style={{
                                      padding: "8px",
                                      background: "var(--gray-100)",
                                      borderRadius: "var(--radius-sm)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      transition: "all 0.2s",
                                      cursor: "pointer"
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = "var(--blue-600)";
                                      e.currentTarget.querySelector('svg')!.style.color = "white";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = "var(--gray-100)";
                                      e.currentTarget.querySelector('svg')!.style.color = "var(--gray-700)";
                                    }}
                                  >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-700)", transition: "color 0.2s" }}>
                                      <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
                                    </svg>
                                  </a>
                                )}
                                {personal.github && (
                                  <a
                                    href={renderValue(personal.github)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    title="GitHub"
                                    style={{
                                      padding: "8px",
                                      background: "var(--gray-100)",
                                      borderRadius: "var(--radius-sm)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      transition: "all 0.2s",
                                      cursor: "pointer"
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = "var(--gray-900)";
                                      e.currentTarget.querySelector('svg')!.style.color = "white";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = "var(--gray-100)";
                                      e.currentTarget.querySelector('svg')!.style.color = "var(--gray-700)";
                                    }}
                                  >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ color: "var(--gray-700)", transition: "color 0.2s" }}>
                                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                    </svg>
                                  </a>
                                )}
                                {personal.website && (
                                  <a
                                    href={renderValue(personal.website)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    title="Website"
                                    style={{
                                      padding: "8px",
                                      background: "var(--gray-100)",
                                      borderRadius: "var(--radius-sm)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      transition: "all 0.2s",
                                      cursor: "pointer"
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = "var(--purple-600)";
                                      e.currentTarget.querySelector('svg')!.style.stroke = "white";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = "var(--gray-100)";
                                      e.currentTarget.querySelector('svg')!.style.stroke = "var(--gray-700)";
                                    }}
                                  >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "var(--gray-700)", transition: "stroke 0.2s" }}>
                                      <circle cx="12" cy="12" r="10" />
                                      <line x1="2" y1="12" x2="22" y2="12" />
                                      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                                    </svg>
                                  </a>
                                )}
                              </div>
                            )}
                          </div>
                          </>
                        );
                      })()}
                    </div>

                    {/* Skills Card */}
                    <div className="glass-card">
                      <h3 className="title" style={{ marginBottom: "var(--space-2)" }}>Skills</h3>
                      <div style={{ position: "relative" }}>
                        <div className="chips" style={{ maxHeight: "150px", overflowY: "auto", paddingBottom: "var(--space-2)" }}>
                          {result.resume.skills && Array.isArray(result.resume.skills) ? (
                            result.resume.skills.map((skill: any, idx: number) => (
                              <span key={idx} className="chip" style={{ fontSize: "var(--text-xs)" }}>
                                {renderValue(skill)}
                              </span>
                            ))
                          ) : (
                            <span className="small muted">No skills data available</span>
                          )}
                        </div>
                        {/* Gradient fade overlay to indicate scrollable content */}
                        <div style={{
                          position: "absolute",
                          bottom: 0,
                          left: 0,
                          right: 0,
                          height: "40px",
                          background: "linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.95))",
                          pointerEvents: "none",
                          borderRadius: "0 0 var(--radius-sm) var(--radius-sm)"
                        }}></div>
                      </div>
                    </div>
                  </div>
                  {/* Dynamically render all configured resume sections */}
                  {RESUME_SECTIONS.map(section => {
                    // Find the first available data path for this section
                    const data = section.paths.reduce((found, path) => {
                      return found || result.resume[path];
                    }, null);

                    // Skip rendering if no data and alwaysShow is false
                    const isEmpty = !data ||
                                   (Array.isArray(data) && data.length === 0) ||
                                   (typeof data === 'object' && Object.keys(data).length === 0);

                    if (isEmpty && !section.alwaysShow) {
                      return null;
                    }

                    // Use React key for proper rendering optimization
                    return (
                      <div key={section.key}>
                        {renderResumeSection(section.title, section.key, data)}
                      </div>
                    );
                  })}
                </>
              )}
            </div>
          )}


        </>
      )}
      </div>
    </div>
  );
}