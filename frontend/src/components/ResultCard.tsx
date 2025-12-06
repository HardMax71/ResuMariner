import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { SearchResult } from "../api/client";
import Chip from "./Chip";
import { Mail, MapPin, Briefcase, GraduationCap, Target, Globe, ChevronDown, Copy, Check, Sparkles, MessageCircle } from "lucide-react";
import { useSelection } from "../contexts/SelectionContext";

type Props = {
  result: SearchResult;
};

export default function ResultCard({ result }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const { isSelected, toggleSelection } = useSelection();
  const navigate = useNavigate();

  const selected = isSelected(result.uid);

  const handleCopyUid = async () => {
    await navigator.clipboard.writeText(result.uid);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatYearsExperience = (years?: number | null) => {
    if (!years) return null;
    if (years < 1) return "<1y";
    return `${years}y`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "var(--accent3-600)";
    if (score >= 0.6) return "var(--primary-600)";
    if (score >= 0.4) return "var(--accent1-500)";
    return "var(--neutral-500)";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 0.8) return "var(--accent3-50)";
    if (score >= 0.6) return "var(--primary-50)";
    if (score >= 0.4) return "var(--accent1-50)";
    return "var(--neutral-50)";
  };

  const getSourceColor = (source?: string) => {
    switch (source?.toLowerCase()) {
      case "skill":
      case "skills":
        return "var(--primary-500)";
      case "summary":
        return "var(--primary-700)";
      case "employment":
      case "experience":
        return "var(--accent3-600)";
      case "education":
        return "var(--accent1-600)";
      case "project":
      case "projects":
        return "var(--primary-600)";
      default:
        return "var(--neutral-500)";
    }
  };

  const getSourceBgColor = (source?: string) => {
    switch (source?.toLowerCase()) {
      case "skill":
      case "skills":
        return "var(--primary-50)";
      case "summary":
        return "var(--primary-100)";
      case "employment":
      case "experience":
        return "var(--accent3-50)";
      case "education":
        return "var(--accent1-50)";
      case "project":
      case "projects":
        return "var(--primary-50)";
      default:
        return "var(--neutral-50)";
    }
  };

  const getHighestEducation = () => {
    if (!result.education || result.education.length === 0) return null;

    const eduLevels = ["PhD", "Doctorate", "Master", "Bachelor", "Associate", "Diploma"];
    for (const level of eduLevels) {
      const edu = result.education.find(e =>
        (e.qualification || "").toLowerCase().includes(level.toLowerCase())
      );
      if (edu) {
        const status = edu.status === "ongoing" ? "ongoing" : "completed";
        return { level: level, status, field: edu.field };
      }
    }
    return null;
  };

  const topExperiences = result.experiences?.slice(0, 2);
  const topSkills = result.skills?.slice(0, 8);
  const highestEdu = getHighestEducation();

  return (
    <div className="search-result" style={{
      borderLeft: `3px solid ${getScoreColor(result.score)}`,
      background: "white"
    }}>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
      {/* Header */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <input
              type="checkbox"
              checked={selected}
              onChange={() => toggleSelection(result.uid, result.name)}
              style={{
                width: "18px",
                height: "18px",
                cursor: "pointer",
                accentColor: "var(--primary-600)"
              }}
            />
            <h3 className="title" style={{ marginBottom: 0 }}>
              {result.name}
            </h3>
            {result.email && (
              <a
                href={`mailto:${result.email}`}
                title={result.email}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "28px",
                  height: "28px",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--primary-600)",
                  transition: "all 0.2s",
                  cursor: "pointer"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "var(--primary-100)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                }}
              >
                <Mail size={16} strokeWidth={2} />
              </a>
            )}
            <button
              type="button"
              onClick={handleCopyUid}
              aria-label={copied ? "Copied!" : "Copy UID"}
              className="tooltip-btn"
              data-tooltip={copied ? "Copied!" : "Copy UID"}
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: "28px",
                height: "28px",
                borderRadius: "var(--radius-sm)",
                color: copied ? "var(--accent3-600)" : "var(--neutral-600)",
                background: "transparent",
                border: "none",
                transition: "all 0.2s",
                cursor: "pointer",
                padding: 0,
                position: "relative"
              }}
              onMouseEnter={(e) => {
                if (!copied) {
                  e.currentTarget.style.background = "var(--neutral-100)";
                  e.currentTarget.style.color = "var(--neutral-900)";
                }
              }}
              onMouseLeave={(e) => {
                if (!copied) {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.color = "var(--neutral-600)";
                }
              }}
            >
              {copied ? <Check size={16} strokeWidth={2} /> : <Copy size={16} strokeWidth={2} />}
            </button>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {/* Match Score Indicator */}
            <div style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              background: getScoreBgColor(result.score),
              padding: "6px 12px",
              borderRadius: "var(--radius-lg)",
              border: `2px solid ${getScoreColor(result.score)}`
            }}>
              <span style={{
                fontSize: "var(--text-xs)",
                fontWeight: 600,
                color: getScoreColor(result.score),
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                lineHeight: 1
              }}>
                Match
              </span>
              <span style={{
                fontSize: "var(--text-base)",
                fontWeight: 700,
                color: getScoreColor(result.score),
                lineHeight: 1
              }}>
                {Math.min(result.score * 100, 100).toFixed(0)}%
              </span>
            </div>

            <button
              type="button"
              className="btn ghost"
              onClick={() => setExpanded(!expanded)}
              style={{
                padding: "6px",
                fontSize: "var(--text-sm)",
                minWidth: "unset",
                width: "32px",
                height: "32px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "var(--radius-sm)"
              }}
            >
              <ChevronDown size={14} strokeWidth={2} style={{
                transform: expanded ? "rotate(180deg)" : "rotate(0)",
                transition: "transform 0.2s"
              }} />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {result.location && (
            <span className="small muted">
              <MapPin size={12} strokeWidth={2} style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }} />
              {typeof result.location === 'object' ?
                `${result.location.city || ''} ${result.location.country || ''}`.trim() :
                result.location}
            </span>
          )}

          {result.years_experience != null && result.years_experience > 0 && (
            <span className="small" style={{
              color: "var(--neutral-700)",
              background: "var(--neutral-50)",
              padding: "2px 8px",
              borderRadius: "var(--radius-lg)"
            }}>
              <Briefcase size={12} strokeWidth={2} style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }} />
              {formatYearsExperience(result.years_experience)}
            </span>
          )}

          {highestEdu && (
            <span className="small" style={{
              color: highestEdu.status === "ongoing" ? "var(--primary-600)" : "var(--accent3-600)",
              background: highestEdu.status === "ongoing" ? "var(--primary-50)" : "var(--accent3-50)",
              padding: "2px 8px",
              borderRadius: "var(--radius-lg)",
              fontWeight: 500
            }}>
              <GraduationCap size={12} strokeWidth={2} style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }} />
              {highestEdu.level} {highestEdu.status === "ongoing" && "(ongoing)"}
            </span>
          )}

          {result.desired_role && result.desired_role.trim() && (
            <span className="small muted">
              <Target size={12} strokeWidth={2} style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }} />
              {result.desired_role}
            </span>
          )}
        </div>

        <div style={{ display: "flex", gap: "var(--space-2)", marginTop: "var(--space-2)", flexWrap: "wrap" }}>
          <button
            onClick={() => navigate(`/rag/explain-match?uid=${result.uid}`)}
            className="btn"
            style={{
              background: "var(--accent1-600)",
              color: "white",
              border: "none",
              display: "flex",
              alignItems: "center",
              gap: "var(--space-1)",
              padding: "6px 12px",
              fontSize: "var(--text-sm)",
              fontWeight: 600
            }}
          >
            <Sparkles size={14} />
            Explain Match
          </button>

          <button
            onClick={() => navigate(`/rag/interview?uid=${result.uid}`)}
            className="btn"
            style={{
              background: "var(--accent2-600)",
              color: "white",
              border: "none",
              display: "flex",
              alignItems: "center",
              gap: "var(--space-1)",
              padding: "6px 12px",
              fontSize: "var(--text-sm)",
              fontWeight: 600
            }}
          >
            <MessageCircle size={14} />
            Interview
          </button>
        </div>
      </div>

      {/* Summary */}
      {result.summary && (
        <div style={{
          position: "relative",
          padding: "12px 12px 12px 16px",
          background: "var(--neutral-50)",
          borderRadius: "var(--radius-sm)",
          borderLeft: "3px solid var(--primary-500)"
        }}>
          <p className="small" style={{
            lineHeight: "1.6",
            wordBreak: "break-word",
            whiteSpace: "pre-wrap",
            color: "var(--neutral-700)",
            fontStyle: "italic",
            margin: 0
          }}>
            {result.summary}
          </p>
        </div>
      )}

      {/* Skills - Show limited in preview, all when expanded */}
      {result.skills && result.skills.length > 0 && (
        <div>
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "calc(var(--space-1) / 2)",
            maxWidth: "100%",
            overflow: "hidden"
          }}>
            {(expanded ? result.skills || [] : topSkills || []).map((skill, idx) => (
              <Chip key={idx} style={{
                fontSize: "var(--text-xs)",
                padding: "calc(var(--space-1) * 0.4) var(--space-1)",
                background: "var(--neutral-100)",
                color: "var(--neutral-700)",
                display: "inline-block",
                flexShrink: 0,
                maxWidth: "50%",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap"
              }}>
                {skill}
              </Chip>
            ))}
            {!expanded && result.skills && result.skills.length > 8 && (
              <Chip style={{
                fontSize: "var(--text-xs)",
                padding: "3px 8px",
                background: "var(--primary-50)",
                color: "var(--primary-600)",
                border: "1px solid var(--primary-200)",
                fontWeight: 600,
                display: "inline-block",
                flexShrink: 0
              }}>
                +{result.skills.length - 8} more
              </Chip>
            )}
          </div>
        </div>
      )}

      {/* Languages */}
      {result.languages && result.languages.length > 0 && result.languages.filter(lang => lang.language && lang.cefr).length > 0 && (
        <div>
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "4px",
            maxWidth: "100%",
            overflow: "hidden"
          }}>
            {result.languages
              .filter(lang => lang.language && lang.cefr)
              .map((lang, idx) => (
              <Chip key={idx} style={{
                fontSize: "var(--text-xs)",
                padding: "3px 8px",
                background: "var(--primary-50)",
                color: "var(--primary-700)",
                border: "1px solid var(--primary-200)",
                display: "inline-block",
                flexShrink: 0,
                fontWeight: 500
              }}>
                <Globe size={10} strokeWidth={2} style={{ display: "inline", marginRight: "4px", verticalAlign: "-1px" }} />
                {lang.language}: {lang.cefr}
              </Chip>
            ))}
          </div>
        </div>
      )}

      {/* Experience - Only show when expanded */}
      {expanded && result.experiences && result.experiences.length > 0 && (
        <div>
          <h4 style={{
            fontWeight: 700,
            color: "var(--neutral-900)",
            fontSize: "var(--text-sm)",
            textTransform: "uppercase",
            letterSpacing: "0.8px",
            marginBottom: "12px"
          }}>
            Experience
          </h4>
          <div className="flex flex-col gap-2">
            {result.experiences.map((exp, idx) => {
              const showDetails = idx < 2; // Top 2 get full details with bullet points

              if (showDetails) {
                return (
                  <div
                    key={idx}
                    style={{
                      padding: "12px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-lg)",
                      borderLeft: "3px solid var(--primary-500)",
                      transition: "all 0.2s"
                    }}
                  >
                    <div style={{
                      display: "flex",
                      alignItems: "flex-start",
                      justifyContent: "space-between",
                      marginBottom: exp.key_points?.length ? "10px" : "0"
                    }}>
                      <div style={{ flex: 1 }}>
                        <div className="small" style={{ fontWeight: 600, color: "var(--neutral-800)" }}>
                          {exp.position}
                        </div>
                        <div className="small muted">
                          {exp.company}
                          {exp.employment_type && ` - ${exp.employment_type}`}
                          {exp.work_mode && ` - ${exp.work_mode}`}
                        </div>
                      </div>
                      <span className="small" style={{
                        color: "var(--primary-600)",
                        fontWeight: 600,
                        background: "var(--primary-50)",
                        padding: "2px 8px",
                        borderRadius: "var(--radius-lg)",
                        flexShrink: 0
                      }}>
                        {(() => {
                          const parts = [];
                          if (exp.start) {
                            const endDate = exp.end || 'Present';
                            parts.push(`${exp.start} - ${endDate}`);
                          }
                          if (exp.duration_months) {
                            const years = Math.round(exp.duration_months / 12 * 10) / 10;
                            parts.push(`${years}y`);
                          }
                          return parts.join(' - ') || 'N/A';
                        })()}
                      </span>
                    </div>
                    {exp.key_points && exp.key_points.length > 0 && (
                      <ul style={{
                        margin: "0",
                        paddingLeft: "12px",
                        listStyleType: "none"
                      }}>
                        {exp.key_points.map((point, pidx, arr) => (
                          <li key={pidx} style={{
                            fontSize: "var(--text-xs)",
                            color: "var(--neutral-600)",
                            lineHeight: "1.5",
                            marginBottom: pidx < arr.length - 1 ? "4px" : "0"
                          }}>
                            - {point}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                );
              } else {
                // Condensed view for rest
                return (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "8px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-lg)"
                    }}
                  >
                    <div>
                      <div className="small" style={{ fontWeight: 500 }}>
                        {exp.position} at {exp.company}
                      </div>
                      {(exp.employment_type || exp.work_mode) && (
                        <div className="small muted" style={{ fontSize: "var(--text-xs)" }}>
                          {[exp.employment_type, exp.work_mode].filter(Boolean).join(" - ")}
                        </div>
                      )}
                    </div>
                    <span className="small muted" style={{ fontSize: "var(--text-xs)" }}>
                      {(() => {
                        const parts = [];
                        if (exp.start) {
                          const endDate = exp.end || 'Present';
                          parts.push(`${exp.start} - ${endDate}`);
                        }
                        if (exp.duration_months) {
                          const years = Math.round(exp.duration_months / 12 * 10) / 10;
                          parts.push(`${years}y`);
                        }
                        return parts.join(' - ') || 'N/A';
                      })()}
                    </span>
                  </div>
                );
              }
            })}
          </div>
        </div>
      )}

      {/* Match Highlights with Source Colors */}
      {result.matches && result.matches.length > 0 && (
        <div>
          <h4 style={{
            fontWeight: 700,
            color: "var(--neutral-900)",
            fontSize: "var(--text-sm)",
            textTransform: "uppercase",
            letterSpacing: "0.8px",
            marginBottom: "12px"
          }}>
            Relevance Highlights
          </h4>
          <div className="flex flex-col gap-2">
            {(expanded ? result.matches : result.matches.slice(0, 3)).map((match, idx) => (
              <div key={idx} style={{
                padding: "8px 10px",
                background: "var(--neutral-50)",
                borderRadius: "var(--radius-lg)",
                borderLeft: `3px solid ${getSourceColor(match.source)}`,
                fontSize: "var(--text-sm)"
              }}>
                <div style={{
                  marginBottom: "4px",
                  color: "var(--neutral-800)",
                  fontStyle: "italic",
                  wordBreak: "break-word",
                  whiteSpace: "pre-wrap"
                }}>
                  "{match.text}"
                </div>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span style={{
                      fontSize: "var(--text-xs)",
                      padding: "2px 6px",
                      background: getSourceBgColor(match.source),
                      color: getSourceColor(match.source),
                      borderRadius: "var(--radius-lg)",
                      fontWeight: 600,
                      textTransform: "uppercase"
                    }}>
                      {match.source || "Resume"}
                    </span>
                    {match.context && (
                      <span className="small muted" style={{ fontSize: "var(--text-xs)" }}>
                        {match.context}
                      </span>
                    )}
                  </div>
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "4px"
                  }}>
                    <div style={{
                      width: "30px",
                      height: "4px",
                      background: "var(--neutral-200)",
                      borderRadius: "var(--radius-sm)",
                      position: "relative",
                      overflow: "hidden"
                    }}>
                      <div style={{
                        width: `${match.score * 100}%`,
                        height: "100%",
                        background: getScoreColor(match.score),
                        borderRadius: "var(--radius-sm)"
                      }}/>
                    </div>
                    <span style={{
                      fontSize: "var(--text-xs)",
                      fontWeight: 600,
                      color: getScoreColor(match.score)
                    }}>
                      {(match.score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {!expanded && result.matches.length > 3 && (
              <p className="small muted text-center" style={{ fontSize: "var(--text-xs)", marginTop: "4px" }}>
                +{result.matches.length - 3} more highlights
              </p>
            )}
          </div>
        </div>
      )}

      {/* Expanded Details */}
      {expanded && (
        <div style={{
          paddingTop: "12px"
        }}>
          {/* Education */}
          {result.education && result.education.length > 0 && (
            <div>
              <h4 style={{
                fontWeight: 700,
                color: "var(--neutral-900)",
                fontSize: "var(--text-sm)",
                textTransform: "uppercase",
                letterSpacing: "0.8px",
                marginBottom: "12px"
              }}>
                Education
              </h4>
              <div className="flex flex-col gap-2">
                {result.education.map((edu, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "8px",
                      background: "var(--neutral-50)",
                      borderRadius: "var(--radius-lg)"
                    }}
                  >
                    <div>
                      <div className="small" style={{ fontWeight: 500 }}>
                        {edu.qualification}
                        {edu.field && ` in ${edu.field}`}
                      </div>
                      {edu.institution && (
                        <div className="small muted" style={{ fontSize: "var(--text-xs)" }}>
                          {edu.institution}
                        </div>
                      )}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      {edu.status && (
                        <span style={{
                          fontSize: "var(--text-xs)",
                          padding: "2px 6px",
                          background: edu.status === "ongoing" ? "var(--primary-100)" : "var(--accent3-100)",
                          color: edu.status === "ongoing" ? "var(--primary-700)" : "var(--accent3-700)",
                          borderRadius: "var(--radius-lg)",
                          fontWeight: 600,
                          textTransform: "uppercase"
                        }}>
                          {edu.status}
                        </span>
                      )}
                      {(edu.year || edu.start || edu.end) && (
                        <span className="small muted" style={{ fontSize: "var(--text-xs)" }}>
                          {edu.year || (edu.start && edu.end ? `${edu.start} - ${edu.end}` : edu.start ? `${edu.start} - Present` : edu.end)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      </div>
    </div>
  );
}