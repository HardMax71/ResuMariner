import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { useResumeStatus } from "../hooks/useJobStatus";
import { API_BASE_URL } from "../lib/api";
import {
  Copy, Check, Hash, FileText, Network, Database,
  Clock, Loader2, CheckCircle2, XCircle, RefreshCw,
  Mail, Phone, MapPin, Linkedin, Github, Globe, ExternalLink,
  Flag, Shield, FileCheck, Calendar, Code2
} from "lucide-react";
import CollapsibleSection from "../components/CollapsibleSection";
import { PageWrapper, PageContainer } from "../components/styled";
import PageHeader from "../components/PageHeader";
import Tooltip from "../components/Tooltip";

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

const getBadgeStyle = (text: string, category?: string) => {
  const t = text.toLowerCase();

  if (category === "education_status") {
    if (t.includes("ongoing") || t.includes("current")) {
      return { bg: "linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%)", color: "var(--primary-800)", border: "var(--primary-500)" };
    }
    if (t.includes("completed") || t.includes("graduated")) {
      return { bg: "linear-gradient(135deg, var(--accent3-100) 0%, var(--accent3-200) 100%)", color: "var(--accent3-800)", border: "var(--accent3-500)" };
    }
  }

  if (category === "employment_type") {
    if (t.includes("full-time") || t.includes("full time") || t.includes("fulltime")) {
      return { bg: "linear-gradient(135deg, var(--primary-200) 0%, var(--primary-300) 100%)", color: "var(--primary-800)", border: "var(--primary-500)" };
    }
    if (t.includes("part-time") || t.includes("part time") || t.includes("parttime")) {
      return { bg: "linear-gradient(135deg, var(--accent1-100) 0%, var(--accent1-200) 100%)", color: "var(--accent1-800)", border: "var(--accent1-500)" };
    }
    if (t.includes("contract") || t.includes("freelance") || t.includes("consultant")) {
      return { bg: "linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%)", color: "var(--primary-800)", border: "var(--primary-500)" };
    }
    if (t.includes("intern") || t.includes("internship")) {
      return { bg: "linear-gradient(135deg, var(--accent1-200) 0%, var(--accent1-300) 100%)", color: "var(--accent1-800)", border: "var(--accent1-500)" };
    }
  }

  if (category === "work_mode") {
    if (t.includes("remote")) {
      return { bg: "linear-gradient(135deg, var(--accent3-100) 0%, var(--accent3-200) 100%)", color: "var(--accent3-800)", border: "var(--accent3-500)" };
    }
    if (t.includes("hybrid")) {
      return { bg: "linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%)", color: "var(--primary-900)", border: "var(--primary-500)" };
    }
    if (t.includes("on-site") || t.includes("onsite") || t.includes("office")) {
      return { bg: "linear-gradient(135deg, var(--accent2-100) 0%, var(--accent2-200) 100%)", color: "var(--accent2-800)", border: "var(--accent2-500)" };
    }
  }

  return { bg: "linear-gradient(135deg, var(--neutral-100) 0%, var(--neutral-200) 100%)", color: "var(--neutral-700)", border: "var(--neutral-400)" };
};

interface ResumeSection {
  title: string;
  key: string;
  paths: string[];
  alwaysShow?: boolean;
}

const RESUME_SECTIONS: ResumeSection[] = [
  {
    title: "Experience",
    key: "experience",
    paths: ["employment_history", "experience", "work_experience"],
    alwaysShow: false
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
  const { uid = "" } = useParams();
  const [showRawJson, setShowRawJson] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["personal", "skills"]));
  const [copiedButtons, setCopiedButtons] = useState<Set<string>>(new Set());
  const [isSkillsOverflowing, setIsSkillsOverflowing] = useState(false);
  const [isSkillsAtBottom, setIsSkillsAtBottom] = useState(false);
  const skillsContainerRef = useRef<HTMLDivElement>(null);

  const { data: job, error: jobError } = useResumeStatus(uid);

  const result = job?.status === "completed" ? job.result : null;
  const error = jobError;

  useEffect(() => {
    const checkOverflow = () => {
      if (skillsContainerRef.current) {
        const hasOverflow = skillsContainerRef.current.scrollHeight > skillsContainerRef.current.clientHeight;
        setIsSkillsOverflowing(hasOverflow);
      }
    };

    const checkScrollPosition = () => {
      if (skillsContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = skillsContainerRef.current;
        const isAtBottom = scrollTop + clientHeight >= scrollHeight - 5; // 5px threshold
        setIsSkillsAtBottom(isAtBottom);
      }
    };

    checkOverflow();
    checkScrollPosition();

    const container = skillsContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollPosition);
    }

    window.addEventListener('resize', checkOverflow);

    return () => {
      if (container) {
        container.removeEventListener('scroll', checkScrollPosition);
      }
      window.removeEventListener('resize', checkOverflow);
    };
  }, [result]);

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
        return <Clock size={24} strokeWidth={2} style={{ color: "var(--neutral-600)" }} />;
      case "processing":
        return <Loader2 size={24} className="spinner" />;
      case "completed":
        return <CheckCircle2 size={24} strokeWidth={2.5} style={{ color: "var(--success)" }} />;
      case "failed":
        return <XCircle size={24} strokeWidth={2.5} style={{ color: "var(--danger)" }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "var(--neutral-600)";
      case "processing": return "var(--primary-600)";
      case "completed": return "var(--success)";
      case "failed": return "var(--danger)";
      default: return "var(--neutral-600)";
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
      <CollapsibleSection
        title={title}
        isExpanded={isExpanded}
        onToggle={() => toggleSection(key)}
        containerStyle={{ marginBottom: "var(--space-2)" }}
        containerClassName="glass-card"
      >
        <div style={{ marginTop: "var(--space-2)" }}>
          {isEmpty ? (
            <div style={{
              padding: "var(--space-3)",
              textAlign: "center",
              color: "var(--neutral-500)",
              fontSize: "var(--text-sm)"
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
                  background: "var(--primary-100)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "var(--text-xl)",
                  fontWeight: 600,
                  color: "var(--primary-600)",
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
                        fontSize: "var(--text-sm)",
                        color: "var(--primary-600)",
                        textDecoration: "none"
                      }}>
                        {renderValue(data.email)}
                      </a>
                    )}
                    {data.phone && (
                      <a href={`tel:${renderValue(data.phone)}`} style={{
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-700)",
                        textDecoration: "none",
                        display: "flex",
                        alignItems: "center",
                        gap: "4px"
                      }}>
                        <Phone size={13} strokeWidth={2} /> {renderValue(data.phone)}
                      </a>
                    )}
                    {data.location && (
                      <span style={{ fontSize: "var(--text-sm)", color: "var(--neutral-600)", display: "flex", alignItems: "center", gap: "4px" }}>
                        <MapPin size={13} strokeWidth={2} /> {renderValue(data.location)}
                      </span>
                    )}
                  </div>
                </div>

                {/* Social Links */}
                {(data.linkedin || data.github || data.website) && (
                  <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                    {data.linkedin && (
                      <a href={renderValue(data.linkedin)} target="_blank" rel="noopener noreferrer" title="LinkedIn">
                        <Linkedin size={18} style={{ color: "var(--neutral-600)" }} />
                      </a>
                    )}
                    {data.github && (
                      <a href={renderValue(data.github)} target="_blank" rel="noopener noreferrer" title="GitHub">
                        <Github size={18} style={{ color: "var(--neutral-600)" }} />
                      </a>
                    )}
                    {data.website && (
                      <a href={renderValue(data.website)} target="_blank" rel="noopener noreferrer" title="Website">
                        <Globe size={18} strokeWidth={2} style={{ color: "var(--neutral-600)" }} />
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
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--primary-500)"
                    }}
                  >
                    {/* Header row with position and dates */}
                    <div className="flex justify-between items-start" style={{ marginBottom: "8px" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "var(--text-base)",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--neutral-900)"
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
                                fontSize: "var(--text-sm)",
                                color: exp.company.url ? "var(--primary-600)" : "var(--neutral-700)",
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
                              fontSize: "var(--text-xs)",
                              fontWeight: 600,
                              ...(() => {
                                const style = getBadgeStyle(exp.employment_type, "employment_type");
                                return {
                                  background: style.bg,
                                  color: style.color,
                                  border: `1px solid ${style.border}40`,
                                  padding: "3px 8px",
                                  borderRadius: "var(--radius-lg)",
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
                              fontSize: "var(--text-xs)",
                              fontWeight: 600,
                              ...(() => {
                                const style = getBadgeStyle(exp.work_mode, "work_mode");
                                return {
                                  background: style.bg,
                                  color: style.color,
                                  border: `1px solid ${style.border}40`,
                                  padding: "3px 8px",
                                  borderRadius: "var(--radius-lg)",
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
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-600)"
                      }}>
                        {exp.duration && (
                          <div style={{ fontWeight: 500 }}>
                            {exp.duration.start} – {exp.duration.end || "Present"}
                          </div>
                        )}
                        {exp.location && [exp.location.city, exp.location.state, exp.location.country].filter(Boolean).length > 0 && (
                          <div style={{ fontSize: "var(--text-xs)", marginTop: "2px" }}>
                            <MapPin size={10} style={{
                              marginRight: "4px",
                              verticalAlign: "middle",
                              color: "var(--neutral-500)"
                            }} />
                            {[exp.location.city, exp.location.state, exp.location.country].filter(Boolean).join(", ")}
                          </div>
                        )}
                        {exp.duration?.duration_months && (
                          <div style={{
                            fontSize: "var(--text-xs)",
                            color: "var(--neutral-500)",
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
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-700)",
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
                              fontSize: "var(--text-xs)",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%)",
                              color: "var(--primary-800)",
                              border: "1px solid rgba(var(--primary-500-rgb), 0.25)",
                              borderRadius: "var(--radius-lg)"
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
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--accent3-600)"
                    }}
                  >
                    {/* Header with title and link */}
                    <div className="flex justify-between items-start" style={{ marginBottom: "8px" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "var(--text-base)",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--neutral-900)"
                        }}>
                          {proj.url ? (
                            <a
                              href={renderValue(proj.url)}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                color: "var(--neutral-900)",
                                textDecoration: "none"
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.textDecoration = "underline"}
                              onMouseLeave={(e) => e.currentTarget.style.textDecoration = "none"}
                            >
                              {renderValue(proj.title)}
                              <ExternalLink size={12} strokeWidth={2} style={{
                                marginLeft: "6px",
                                verticalAlign: "middle",
                                opacity: 0.6
                              }} />
                            </a>
                          ) : (
                            renderValue(proj.title)
                          )}
                        </h4>
                        {proj.description && (
                          <div style={{
                            fontSize: "var(--text-sm)",
                            color: "var(--neutral-600)",
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
                          onMouseEnter={(e) => e.currentTarget.style.background = "var(--neutral-100)"}
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
                              return <Github size={16} style={{ color: "var(--neutral-600)" }} />;
                            }
                            if (url.includes("gitlab")) {
                              return <Code2 size={16} strokeWidth={2} style={{ color: "var(--neutral-600)" }} />;
                            }
                            if (url.includes("gitea")) {
                              return <Code2 size={16} strokeWidth={2} style={{ color: "var(--neutral-600)" }} />;
                            }
                            if (url.includes("bitbucket")) {
                              return <Code2 size={16} strokeWidth={2} style={{ color: "var(--neutral-600)" }} />;
                            }
                            // Generic code/link icon for other sites
                            return <Code2 size={16} strokeWidth={2} style={{ color: "var(--neutral-600)" }} />;
                          })()}
                        </a>
                      )}
                    </div>

                    {/* Key points */}
                    {proj.key_points && proj.key_points.length > 0 && (
                      <ul style={{
                        margin: "10px 0 0 0",
                        paddingLeft: "20px",
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-700)",
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
                              fontSize: "var(--text-xs)",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "linear-gradient(135deg, var(--accent3-100) 0%, var(--accent3-200) 100%)",
                              color: "var(--accent3-800)",
                              border: "1px solid rgba(var(--accent3-500-rgb), 0.25)",
                              borderRadius: "var(--radius-lg)"
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
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--primary-500)"
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
                            color: "var(--neutral-900)",
                            lineHeight: 1.3
                          }}>
                            {renderValue(edu.qualification)}
                            {edu.field && (
                              <>
                                <span style={{ fontWeight: 400, color: "var(--neutral-600)" }}> in </span>
                                <span style={{ fontWeight: 400, color: "var(--neutral-800)" }}>{renderValue(edu.field)}</span>
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
                                  borderRadius: "var(--radius-lg)",
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
                          color: "var(--neutral-700)"
                        }}>
                          {edu.institution && renderValue(edu.institution.name || edu.institution)}
                        </div>
                      </div>

                      {/* Dates and location */}
                      <div style={{
                        textAlign: "right",
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-600)",
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
                        {edu.location && [edu.location.city, edu.location.state, edu.location.country].filter(Boolean).length > 0 && (
                          <div style={{ fontSize: "var(--text-xs)", marginTop: "2px" }}>
                            <MapPin size={10} style={{
                              marginRight: "4px",
                              verticalAlign: "middle",
                              color: "var(--neutral-500)"
                            }} />
                            {[edu.location.city, edu.location.state, edu.location.country].filter(Boolean).join(", ")}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Coursework */}
                    {edu.coursework && edu.coursework.length > 0 && (
                      <div style={{ marginTop: "8px" }}>
                        <div style={{
                          fontSize: "var(--text-xs)",
                          fontWeight: 500,
                          color: "var(--neutral-500)",
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
                                fontSize: "var(--text-xs)",
                                fontWeight: 500,
                                padding: "3px 8px",
                                background: "linear-gradient(135deg, var(--accent1-100) 0%, var(--accent1-200) 100%)",
                                color: "var(--accent1-800)",
                                border: "1px solid rgba(var(--accent1-500-rgb), 0.25)",
                                borderRadius: "var(--radius-lg)"
                              }}
                            >
                              {renderValue(course.text || course.name || course)}
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
                        fontSize: "var(--text-xs)",
                        color: "var(--neutral-600)",
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
                        fontSize: "var(--text-xs)",
                        color: "var(--neutral-600)"
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
                        background: "var(--neutral-50)",
                        borderRadius: "var(--radius-sm)",
                        borderLeft: "3px solid var(--primary-600)"
                      }}
                    >
                      <div className="flex justify-between items-center">
                        {/* Language name */}
                        <h4 style={{
                          fontSize: "var(--text-base)",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--neutral-900)"
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
                              fontSize: "var(--text-xs)",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "var(--neutral-100)",
                              color: "var(--neutral-700)",
                              borderRadius: "var(--radius-lg)",
                              textTransform: "uppercase",
                              letterSpacing: "0.3px"
                            }}>
                              Self: {selfAssessed}
                            </span>
                          )}
                          {cefr && (
                            <span style={{
                              fontSize: "var(--text-xs)",
                              fontWeight: 600,
                              padding: "3px 8px",
                              background: "var(--accent3-500)",
                              color: "white",
                              borderRadius: "var(--radius-lg)",
                              textTransform: "uppercase",
                              letterSpacing: "0.3px"
                            }}>
                              CEFR: {cefr}
                            </span>
                          )}
                          {!cefr && !selfAssessed && level && (
                            <span style={{
                              fontSize: "var(--text-xs)",
                              fontWeight: 500,
                              padding: "3px 8px",
                              background: "var(--neutral-100)",
                              color: "var(--neutral-700)",
                              borderRadius: "var(--radius-lg)"
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

            {key === "certifications" && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((cert: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "14px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--primary-600)"
                    }}
                  >
                    <div className="flex justify-between items-start" style={{ marginBottom: cert.issue_org ? "6px" : "0" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "var(--text-base)",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--neutral-900)"
                        }}>
                          {cert.certificate_link ? (
                            <a
                              href={renderValue(cert.certificate_link)}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                color: "var(--neutral-900)",
                                textDecoration: "none"
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.textDecoration = "underline"}
                              onMouseLeave={(e) => e.currentTarget.style.textDecoration = "none"}
                            >
                              {renderValue(cert.name)}
                              <ExternalLink size={12} strokeWidth={2} style={{
                                marginLeft: "6px",
                                verticalAlign: "middle",
                                opacity: 0.6
                              }} />
                            </a>
                          ) : (
                            renderValue(cert.name)
                          )}
                        </h4>
                      </div>
                      {cert.issue_year && (
                        <span style={{
                          fontSize: "var(--text-sm)",
                          color: "var(--neutral-600)",
                          fontWeight: 500,
                          marginLeft: "12px",
                          flexShrink: 0
                        }}>
                          {cert.issue_year}
                        </span>
                      )}
                    </div>
                    {cert.issue_org && (
                      <div style={{
                        fontSize: "var(--text-xs)",
                        color: "var(--neutral-600)",
                        fontWeight: 500
                      }}>
                        {renderValue(cert.issue_org)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {key === "awards" && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((award: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "14px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--accent1-600)"
                    }}
                  >
                    <div className="flex justify-between items-start" style={{ marginBottom: (award.issuer || award.organization || award.description) ? "6px" : "0" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "var(--text-base)",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--neutral-900)"
                        }}>
                          {renderValue(award.name || award.title)}
                        </h4>
                      </div>
                      {(award.year || award.date) && (
                        <span style={{
                          fontSize: "var(--text-sm)",
                          color: "var(--neutral-600)",
                          fontWeight: 500,
                          marginLeft: "12px",
                          flexShrink: 0
                        }}>
                          {renderValue(award.year || award.date)}
                        </span>
                      )}
                    </div>
                    {(award.issuer || award.organization) && (
                      <div style={{
                        fontSize: "var(--text-xs)",
                        color: "var(--neutral-600)",
                        fontWeight: 500,
                        marginBottom: award.description ? "6px" : "0"
                      }}>
                        {renderValue(award.issuer || award.organization)}
                      </div>
                    )}
                    {award.description && (
                      <div style={{
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-700)",
                        lineHeight: 1.5
                      }}>
                        {renderValue(award.description)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {(key === "publications" || key === "scientific_contributions") && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((pub: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "14px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--primary-600)"
                    }}
                  >
                    <div className="flex justify-between items-start" style={{ marginBottom: "8px" }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{
                          fontSize: "var(--text-base)",
                          fontWeight: 600,
                          margin: 0,
                          color: "var(--neutral-900)"
                        }}>
                          {pub.url ? (
                            <a
                              href={renderValue(pub.url)}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                color: "var(--neutral-900)",
                                textDecoration: "none"
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.textDecoration = "underline"}
                              onMouseLeave={(e) => e.currentTarget.style.textDecoration = "none"}
                            >
                              {renderValue(pub.title)}
                              <ExternalLink size={12} strokeWidth={2} style={{
                                marginLeft: "6px",
                                verticalAlign: "middle",
                                opacity: 0.6
                              }} />
                            </a>
                          ) : (
                            renderValue(pub.title)
                          )}
                        </h4>
                        <div style={{
                          display: "flex",
                          gap: "8px",
                          marginTop: "6px",
                          flexWrap: "wrap",
                          alignItems: "center"
                        }}>
                          {pub.publication_type && (
                            <span style={{
                              fontSize: "var(--text-xs)",
                              fontWeight: 600,
                              padding: "3px 8px",
                              background: "linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%)",
                              color: "var(--primary-800)",
                              border: "1px solid rgba(var(--primary-500-rgb), 0.25)",
                              borderRadius: "var(--radius-lg)",
                              textTransform: "capitalize"
                            }}>
                              {renderValue(pub.publication_type).replace(/_/g, ' ')}
                            </span>
                          )}
                          {pub.year && (
                            <span style={{
                              fontSize: "var(--text-xs)",
                              color: "var(--neutral-600)",
                              fontWeight: 500
                            }}>
                              {pub.year}
                            </span>
                          )}
                          {pub.venue && (
                            <span style={{
                              fontSize: "var(--text-xs)",
                              color: "var(--neutral-600)",
                              fontStyle: "italic"
                            }}>
                              {renderValue(pub.venue)}
                            </span>
                          )}
                        </div>
                        {pub.description && (
                          <div style={{
                            fontSize: "var(--text-sm)",
                            color: "var(--neutral-600)",
                            marginTop: "8px",
                            lineHeight: 1.5
                          }}>
                            {renderValue(pub.description)}
                          </div>
                        )}
                        {pub.doi && (
                          <div style={{
                            fontSize: "var(--text-xs)",
                            color: "var(--neutral-500)",
                            marginTop: "6px",
                            fontFamily: "var(--font-mono)"
                          }}>
                            DOI: {renderValue(pub.doi)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {key === "courses" && Array.isArray(data) && (
              <div className="flex flex-col gap-3">
                {data.map((course: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "14px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--primary-600)"
                    }}
                  >
                    <div className="flex justify-between items-start" style={{ marginBottom: "4px" }}>
                      <h4 style={{
                        fontSize: "var(--text-base)",
                        fontWeight: 600,
                        margin: 0,
                        color: "var(--neutral-900)"
                      }}>
                        {course.course_url ? (
                          <a
                            href={renderValue(course.course_url)}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: "var(--neutral-900)",
                              textDecoration: "none"
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.textDecoration = "underline"}
                            onMouseLeave={(e) => e.currentTarget.style.textDecoration = "none"}
                          >
                            {renderValue(course.name)}
                            <ExternalLink size={12} strokeWidth={2} style={{
                              marginLeft: "6px",
                              verticalAlign: "middle",
                              opacity: 0.6
                            }} />
                          </a>
                        ) : (
                          renderValue(course.name)
                        )}
                      </h4>
                      {course.year && (
                        <span style={{
                          fontSize: "var(--text-xs)",
                          fontWeight: 600,
                          color: "var(--neutral-500)",
                          whiteSpace: "nowrap",
                          marginLeft: "12px"
                        }}>
                          {renderValue(course.year)}
                        </span>
                      )}
                    </div>
                    {course.organization && (
                      <div style={{
                        fontSize: "var(--text-sm)",
                        color: "var(--neutral-600)",
                        fontWeight: 500,
                        marginTop: "6px"
                      }}>
                        {renderValue(course.organization)}
                      </div>
                    )}
                    {course.certificate_url && (
                      <a
                        href={renderValue(course.certificate_url)}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px",
                          marginTop: "8px",
                          fontSize: "var(--text-xs)",
                          color: "var(--primary-600)",
                          textDecoration: "none",
                          fontWeight: 500
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.textDecoration = "underline"}
                        onMouseLeave={(e) => e.currentTarget.style.textDecoration = "none"}
                      >
                        <ExternalLink size={12} strokeWidth={2} />
                        View Certificate
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Default rendering for other types */}
            {!["personal", "skills", "experience", "education", "projects", "languages", "publications", "scientific_contributions", "certifications", "awards", "courses"].includes(key) && (
              <div style={{ position: "relative" }}>
                <button
                  className="btn ghost"
                  onClick={() => handleCopy(JSON.stringify(data, null, 2), `section-${key}`)}
                  style={{
                    position: "absolute",
                    top: "4px",
                    right: "4px",
                    padding: "4px",
                    fontSize: "var(--text-xs)",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    background: copiedButtons.has(`section-${key}`) ? "var(--accent3-50)" : "var(--neutral-0)",
                    border: `1px solid ${copiedButtons.has(`section-${key}`) ? "var(--accent3-300)" : "var(--neutral-300)"}`,
                    zIndex: 1,
                    transition: "all 0.3s ease",
                    color: copiedButtons.has(`section-${key}`) ? "var(--accent3-600)" : "inherit"
                  }}
                  title={copiedButtons.has(`section-${key}`) ? "Copied!" : "Copy to clipboard"}
                >
                  {copiedButtons.has(`section-${key}`) ? (
                    <Check size={12} strokeWidth={2.5} />
                  ) : (
                    <Copy size={12} strokeWidth={2} />
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
      </CollapsibleSection>
    );
  };

  return (
    <PageWrapper>
      <PageContainer>
      <PageHeader
        title="Resume Processing Status"
        actions={
          <Link to="/upload" className="btn ghost">
            <RefreshCw size={16} strokeWidth={2} style={{ marginRight: "var(--space-1)" }} />
            Upload Another
          </Link>
        }
      />

      {error && (
        <div className="error mb-3">
          <strong>Error loading job:</strong> {error instanceof Error ? error.message : String(error)}
        </div>
      )}

      {!job && !error && (
        <div className="glass-card" style={{
          padding: "var(--space-6)",
          textAlign: "center"
        }}>
          <div className="spinner" style={{ width: "48px", height: "48px", margin: "0 auto var(--space-3)" }}></div>
          <p className="muted">Loading job details...</p>
        </div>
      )}

      {job && (
        <div className="glass-card" style={{
          borderTop: `3px solid ${getStatusColor(job.status)}`,
          marginBottom: "var(--space-3)"
        }}>
          <div className="flex justify-between items-center" style={{ marginBottom: "var(--space-3)" }}>
            <div className="flex items-center gap-3">
              <div style={{
                width: "48px",
                height: "48px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "var(--radius-full)",
                background: job.status === "completed" ? "rgba(var(--accent3-500-rgb), 0.1)" :
                           job.status === "processing" ? "rgba(var(--primary-500-rgb), 0.1)" :
                           job.status === "failed" ? "rgba(var(--accent2-500-rgb), 0.1)" : "var(--neutral-100)"
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
                    onClick={() => handleCopy(job.uid, "resume-id")}
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
                      color: "var(--neutral-600)"
                    }}
                    title={copiedButtons.has("resume-id") ? "Copied!" : `Resume ID: ${job.uid}`}
                    onMouseEnter={(e) => e.currentTarget.style.background = "var(--neutral-100)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                  >
                    {copiedButtons.has("resume-id") ? (
                      <Check size={14} style={{ color: "var(--success)" }} />
                    ) : (
                      <Hash size={14} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {job.status === "completed" && (
              <div className="flex gap-2">
                <Tooltip text={copiedButtons.has("copy-link") ? "Copied!" : "Copy link to clipboard"}>
                  <button
                    onClick={() => {
                      const url = `${window.location.origin}/resumes/${job.uid}`;
                      handleCopy(url, "copy-link");
                    }}
                    style={{
                      padding: "8px",
                      background: "var(--neutral-100)",
                      borderRadius: "var(--radius-lg)",
                      border: "none",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: "inherit"
                    }}
                  >
                    {copiedButtons.has("copy-link") ? (
                      <Check size={16} style={{ color: "var(--accent3-500)" }} />
                    ) : (
                      <Copy size={16} style={{ color: "var(--neutral-700)" }} />
                    )}
                  </button>
                </Tooltip>
                <Tooltip text="Open API endpoint">
                  <a
                    href={`${API_BASE_URL}/api/v1/resumes/${job.uid}/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: "8px",
                      background: "var(--neutral-100)",
                      borderRadius: "var(--radius-lg)",
                      cursor: "pointer",
                      textDecoration: "none",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center"
                    }}
                  >
                    <Code2 size={16} strokeWidth={2} style={{ color: "var(--neutral-700)" }} />
                  </a>
                </Tooltip>
                {result?.review && (
                  <Link
                    to={`/resumes/${job.uid}/review`}
                    style={{
                      padding: "6px 12px",
                      fontSize: "var(--text-sm)",
                      fontWeight: "600",
                      background: "var(--primary-600)",
                      border: "1px solid var(--primary-600)",
                      borderRadius: "var(--radius-lg)",
                      color: "var(--neutral-0)",
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
                      e.currentTarget.style.background = "var(--primary-800)";
                      e.currentTarget.style.borderColor = "var(--primary-800)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "var(--primary-600)";
                      e.currentTarget.style.borderColor = "var(--primary-600)";
                    }}
                  >
                    <FileText size={14} strokeWidth={2} style={{ color: "var(--neutral-0)" }} />
                    AI Review
                  </Link>
                )}
            </div>
            )}
          </div>

          {job.status === "processing" && (
            <div style={{
              padding: "var(--space-2)",
              background: "var(--primary-50)",
              borderRadius: "var(--radius-sm)",
              marginBottom: "var(--space-2)"
            }}>
              <div className="flex justify-between mb-2">
                <span className="small" style={{ fontWeight: 600 }}>Analyzing document content...</span>
                <span className="small muted">Please wait</span>
              </div>
              <div style={{
                height: "6px",
                background: "var(--neutral-200)",
                borderRadius: "var(--radius-full)",
                overflow: "hidden"
              }}>
                <div style={{
                  height: "100%",
                  width: "40%",
                  background: "var(--primary-600)",
                  borderRadius: "var(--radius-full)",
                  animation: "progress 2s ease-in-out infinite"
                }}></div>
              </div>
            </div>
          )}

          {job.error && (
            <div className="error" style={{ marginTop: 0 }}>
              <strong>Error:</strong> {job.error}
            </div>
          )}

          <div className="flex gap-4" style={{
            paddingTop: "var(--space-2)",
            marginTop: job.status === "processing" ? 0 : "var(--space-2)",
            flexWrap: "wrap",
            alignItems: "center"
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
            {result?.metadata && (
              <>
                {result.metadata.page_count && (
                  <Tooltip text={`Pages: ${result.metadata.page_count}`}>
                    <span style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                      fontSize: "var(--text-sm)",
                      color: "var(--neutral-700)",
                      cursor: "help"
                    }}>
                      <FileText size={14} style={{ color: "var(--primary-600)" }} strokeWidth={2} />
                      <span>{result.metadata.page_count}</span>
                    </span>
                  </Tooltip>
                )}
                <Tooltip text={`Saved to Graph DB: ${result.metadata.graph_stored ? 'Yes' : 'No'}`}>
                  <span style={{ cursor: "help", display: "inline-flex", alignItems: "center" }}>
                    <Network
                      size={14}
                      style={{ color: result.metadata.graph_stored ? "var(--accent3-500)" : "var(--accent2-500)" }}
                      strokeWidth={2}
                    />
                  </span>
                </Tooltip>
                <Tooltip text={`Saved to Vector DB: ${result.metadata.vector_stored ? 'Yes' : 'No'}`}>
                  <span style={{ cursor: "help", display: "inline-flex", alignItems: "center" }}>
                    <Database
                      size={14}
                      style={{ color: result.metadata.vector_stored ? "var(--accent3-500)" : "var(--accent2-500)" }}
                      strokeWidth={2}
                    />
                  </span>
                </Tooltip>
              </>
            )}
          </div>
        </div>
      )}

      {result && (
        <>
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
                      fontSize: "var(--text-xs)",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      background: copiedButtons.has("metadata-json") ? "var(--accent3-50)" : "var(--neutral-0)",
                      border: `1px solid ${copiedButtons.has("metadata-json") ? "var(--accent3-300)" : "var(--neutral-300)"}`,
                      zIndex: 1,
                      transition: "all 0.3s ease",
                      color: copiedButtons.has("metadata-json") ? "var(--accent3-600)" : "inherit"
                    }}
                    title={copiedButtons.has("metadata-json") ? "Copied!" : "Copy metadata to clipboard"}
                  >
                    {copiedButtons.has("metadata-json") ? (
                      <Check size={14} strokeWidth={2.5} />
                    ) : (
                      <Copy size={14} strokeWidth={2} />
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
                      fontSize: "var(--text-xs)",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      background: copiedButtons.has("main-json") ? "var(--accent3-50)" : "var(--neutral-0)",
                      border: `1px solid ${copiedButtons.has("main-json") ? "var(--accent3-300)" : "var(--neutral-300)"}`,
                      zIndex: 1,
                      transition: "all 0.3s ease",
                      color: copiedButtons.has("main-json") ? "var(--accent3-600)" : "inherit"
                    }}
                    title={copiedButtons.has("main-json") ? "Copied!" : "Copy JSON to clipboard"}
                  >
                    {copiedButtons.has("main-json") ? (
                      <Check size={14} strokeWidth={2.5} />
                    ) : (
                      <Copy size={14} strokeWidth={2} />
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
                        let workAuth: any = null;
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
                          if (r.personal_info.demographics?.work_authorization) {
                            workAuth = r.personal_info.demographics.work_authorization;
                          }
                        } else {
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
                              <h3 className="title" style={{ margin: 0, fontSize: "var(--text-sm)", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--neutral-600)", fontWeight: 600 }}>Personal Information</h3>
                              {resumeLang && (
                                <Tooltip text={`Resume Language: ${renderValue(resumeLang)}`}>
                                  <span style={{
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: "4px",
                                    padding: "2px 8px",
                                    background: "var(--primary-50)",
                                    border: "1px solid var(--primary-200)",
                                    borderRadius: "var(--radius-full)",
                                    fontSize: "var(--text-xs)",
                                    fontWeight: 600,
                                    color: "var(--primary-700)",
                                    textTransform: "uppercase",
                                    letterSpacing: "0.02em",
                                    cursor: "help"
                                  }}>
                                    <FileText size={10} strokeWidth={2.5} style={{ flexShrink: 0 }} />
                                    {renderValue(resumeLang)}
                                  </span>
                                </Tooltip>
                              )}
                            </div>

                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
                              {/* Name */}
                              <div>
                                <h4 style={{ fontSize: "var(--text-xl)", fontWeight: 700, margin: 0, lineHeight: 1.2, marginBottom: "4px", color: "var(--neutral-900)" }}>
                                  {renderValue(personal.name) || "—"}
                                </h4>
                                {personal.location && (
                                  <span style={{ fontSize: "var(--text-xs)", color: "var(--neutral-600)", display: "flex", alignItems: "center", gap: "4px" }}>
                                    <MapPin size={12} style={{ color: "var(--neutral-500)", flexShrink: 0 }} />
                                    {renderValue(personal.location)}
                                  </span>
                                )}
                              </div>

                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
                              {personal.email && (
                                <a href={`mailto:${renderValue(personal.email)}`} style={{
                                  fontSize: "var(--text-sm)",
                                  color: "var(--primary-600)",
                                  textDecoration: "none",
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "8px",
                                  padding: "6px 8px",
                                  borderRadius: "var(--radius-sm)",
                                  transition: "background 0.2s"
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = "var(--primary-50)"}
                                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                                  <Mail size={16} strokeWidth={2} style={{ flexShrink: 0 }} />
                                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                    {renderValue(personal.email)}
                                  </span>
                                </a>
                              )}

                              {personal.phone && (
                                <a href={`tel:${renderValue(personal.phone)}`} style={{
                                  fontSize: "var(--text-sm)",
                                  color: "var(--primary-600)",
                                  textDecoration: "none",
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "8px",
                                  padding: "6px 8px",
                                  borderRadius: "var(--radius-sm)",
                                  transition: "background 0.2s"
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.background = "var(--primary-50)"}
                                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                                  <Phone size={16} strokeWidth={2} style={{ flexShrink: 0 }} />
                                  {renderValue(personal.phone)}
                                </a>
                              )}
                            </div>

                            {(personal.linkedin || personal.github || personal.website) && (
                              <div style={{
                                display: "flex",
                                gap: "8px",
                                paddingTop: "var(--space-2)"
                              }}>
                                {personal.linkedin && (
                                  <a
                                    href={renderValue(personal.linkedin)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    title="LinkedIn"
                                    style={{
                                      padding: "8px",
                                      background: "var(--neutral-100)",
                                      borderRadius: "var(--radius-sm)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      transition: "all 0.2s",
                                      cursor: "pointer",
                                      color: "var(--neutral-700)"
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = "var(--primary-600)";
                                      e.currentTarget.style.color = "white";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = "var(--neutral-100)";
                                      e.currentTarget.style.color = "var(--neutral-700)";
                                    }}
                                  >
                                    <Linkedin size={16} />
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
                                      background: "var(--neutral-100)",
                                      borderRadius: "var(--radius-sm)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      transition: "all 0.2s",
                                      cursor: "pointer",
                                      color: "var(--neutral-700)"
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = "var(--neutral-900)";
                                      e.currentTarget.style.color = "white";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = "var(--neutral-100)";
                                      e.currentTarget.style.color = "var(--neutral-700)";
                                    }}
                                  >
                                    <Github size={16} />
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
                                      background: "var(--neutral-100)",
                                      borderRadius: "var(--radius-sm)",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      transition: "all 0.2s",
                                      cursor: "pointer",
                                      color: "var(--neutral-700)"
                                    }}
                                    onMouseEnter={(e) => {
                                      e.currentTarget.style.background = "var(--primary-600)";
                                      e.currentTarget.style.color = "white";
                                    }}
                                    onMouseLeave={(e) => {
                                      e.currentTarget.style.background = "var(--neutral-100)";
                                      e.currentTarget.style.color = "var(--neutral-700)";
                                    }}
                                  >
                                    <Globe size={16} />
                                  </a>
                                )}
                              </div>
                            )}

                            {workAuth && (workAuth.citizenship || workAuth.work_permit !== null || workAuth.visa_sponsorship_required !== null) && (
                              <div style={{
                                paddingTop: "var(--space-2)",
                                marginTop: "var(--space-2)"
                              }}>
                                <div style={{
                                  fontSize: "var(--text-xs)",
                                  fontWeight: 600,
                                  color: "var(--neutral-500)",
                                  textTransform: "uppercase",
                                  letterSpacing: "0.5px",
                                  marginBottom: "6px"
                                }}>
                                  Work Authorization
                                </div>
                                <div style={{
                                  display: "flex",
                                  flexDirection: "column",
                                  gap: "4px"
                                }}>
                                  {workAuth.citizenship && (
                                    <div style={{
                                      display: "flex",
                                      alignItems: "center",
                                      gap: "6px",
                                      fontSize: "var(--text-xs)",
                                      color: "var(--neutral-700)"
                                    }}>
                                      <Flag size={14} strokeWidth={2} style={{ color: "var(--neutral-500)", flexShrink: 0 }} />
                                      <span style={{ fontWeight: 500 }}>Citizenship:</span>
                                      <span>{renderValue(workAuth.citizenship)}</span>
                                    </div>
                                  )}
                                  {workAuth.work_permit !== null && (
                                    <div style={{
                                      display: "flex",
                                      alignItems: "center",
                                      gap: "6px",
                                      fontSize: "var(--text-xs)",
                                      color: "var(--neutral-700)"
                                    }}>
                                      {workAuth.work_permit ? (
                                        <CheckCircle2 size={14} strokeWidth={2} style={{ color: "var(--accent3-600)", flexShrink: 0 }} />
                                      ) : (
                                        <XCircle size={14} strokeWidth={2} style={{ color: "var(--neutral-500)", flexShrink: 0 }} />
                                      )}
                                      <span style={{ fontWeight: 500 }}>Work Permit:</span>
                                      <span>{workAuth.work_permit ? "Yes" : "No"}</span>
                                    </div>
                                  )}
                                  {workAuth.visa_sponsorship_required !== null && (
                                    <div style={{
                                      display: "flex",
                                      alignItems: "center",
                                      gap: "6px",
                                      fontSize: "var(--text-xs)",
                                      color: "var(--neutral-700)"
                                    }}>
                                      <FileCheck size={14} strokeWidth={2} style={{ color: workAuth.visa_sponsorship_required ? "var(--accent1-600)" : "var(--neutral-500)", flexShrink: 0 }} />
                                      <span style={{ fontWeight: 500 }}>Visa Sponsorship:</span>
                                      <span>{workAuth.visa_sponsorship_required ? "Required" : "Not Required"}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                          </>
                        );
                      })()}
                    </div>

                    <div className="glass-card">
                      <h3 className="title" style={{ marginBottom: "var(--space-2)" }}>Skills</h3>
                      <div style={{ position: "relative" }}>
                        <div ref={skillsContainerRef} className="chips" style={{ maxHeight: "min(400px, 50vh)", overflowY: "auto", paddingBottom: "var(--space-2)" }}>
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
                        {isSkillsOverflowing && (
                          <div style={{
                            position: "absolute",
                            bottom: 0,
                            left: 0,
                            right: 0,
                            height: "40px",
                            background: "linear-gradient(to bottom, rgba(var(--neutral-0-rgb), 0), rgba(var(--neutral-0-rgb), 0.95))",
                            pointerEvents: "none",
                            borderRadius: "0 0 var(--radius-sm) var(--radius-sm)",
                            opacity: isSkillsAtBottom ? 0 : 1,
                            transition: "opacity 0.3s ease"
                          }}></div>
                        )}
                      </div>
                    </div>
                  </div>
                  {RESUME_SECTIONS.map(section => {
                    const data: any = section.paths.reduce((found, path) => {
                      return found || result.resume[path];
                    }, null);

                    const isEmpty = !data ||
                                   (Array.isArray(data) && data.length === 0) ||
                                   (typeof data === 'object' && Object.keys(data).length === 0);

                    if (isEmpty && !section.alwaysShow) {
                      return null;
                    }

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
      </PageContainer>
    </PageWrapper>
  );
}