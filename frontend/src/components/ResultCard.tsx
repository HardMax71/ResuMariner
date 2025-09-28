import { useState } from "react";
import type { SearchResult } from "../lib/api";

type Props = {
  result: SearchResult;
};

export default function ResultCard({ result }: Props) {
  const [expanded, setExpanded] = useState(false);

  const formatYearsExperience = (years?: number | null) => {
    if (!years) return null;
    if (years < 1) return "< 1 year";
    if (years === 1) return "1 year";
    return `${years} years`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "var(--green-600)";
    if (score >= 0.6) return "var(--blue-600)";
    if (score >= 0.4) return "var(--orange-500)";
    return "var(--gray-500)";
  };

  const getSourceColor = (source?: string) => {
    switch (source?.toLowerCase()) {
      case "skill":
      case "skills":
        return "var(--blue-500)";
      case "summary":
        return "var(--purple-600)";
      case "employment":
      case "experience":
        return "var(--green-600)";
      case "education":
        return "var(--orange-600)";
      case "project":
      case "projects":
        return "var(--blue-600)";
      default:
        return "var(--gray-500)";
    }
  };

  const getHighestEducation = () => {
    if (!result.education || result.education.length === 0) return null;

    const eduLevels = ["PhD", "Doctorate", "Master", "Bachelor", "Associate", "Diploma"];
    for (const level of eduLevels) {
      const edu = result.education.find(e =>
        (e.degree || e.qualification || "").toLowerCase().includes(level.toLowerCase())
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
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div style={{ flex: 1 }}>
          <div className="flex items-center gap-3">
            <h3 className="title" style={{ marginBottom: 0 }}>
              {result.name}
            </h3>
            {/* Visual Score Indicator */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              background: "var(--gray-50)",
              padding: "4px 10px",
              borderRadius: "16px",
              border: `1px solid ${getScoreColor(result.score)}22`
            }}>
              <div style={{
                width: "60px",
                height: "6px",
                background: "var(--gray-200)",
                borderRadius: "3px",
                position: "relative",
                overflow: "hidden"
              }}>
                <div style={{
                  width: `${Math.min(result.score * 100, 100)}%`,
                  height: "100%",
                  background: getScoreColor(result.score),
                  borderRadius: "3px",
                  transition: "width 0.3s ease"
                }}/>
              </div>
              <span style={{
                fontSize: "12px",
                fontWeight: 600,
                color: getScoreColor(result.score)
              }}>
                {Math.min(result.score * 100, 100).toFixed(0)}%
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 mt-2 flex-wrap">
            {result.email && (
              <a href={`mailto:${result.email}`} className="small" style={{
                color: "var(--blue-600)",
                textDecoration: "none"
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }}>
                  <rect x="2" y="4" width="20" height="16" rx="2"/>
                  <path d="m22 7-10 5L2 7"/>
                </svg>
                {result.email}
              </a>
            )}

            {result.location && (
              <span className="small muted">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }}>
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                {typeof result.location === 'object' ?
                  `${result.location.city || ''} ${result.location.country || ''}`.trim() :
                  result.location}
              </span>
            )}

            {result.years_experience && (
              <span className="small" style={{
                color: "var(--gray-700)",
                background: "var(--gray-50)",
                padding: "2px 8px",
                borderRadius: "12px"
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }}>
                  <rect x="2" y="7" width="20" height="14" rx="2"/>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                </svg>
                {formatYearsExperience(result.years_experience)} exp
              </span>
            )}

            {highestEdu && (
              <span className="small" style={{
                color: highestEdu.status === "ongoing" ? "var(--blue-600)" : "var(--green-600)",
                background: highestEdu.status === "ongoing" ? "var(--blue-50)" : "var(--green-50)",
                padding: "2px 8px",
                borderRadius: "12px",
                fontWeight: 500
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }}>
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                  <path d="M6 12v5c0 1.7 3.3 3 6 3s6-1.3 6-3v-5"/>
                </svg>
                {highestEdu.level} {highestEdu.status === "ongoing" && "(ongoing)"}
              </span>
            )}

            {result.desired_role && (
              <span className="small muted">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }}>
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
                {result.desired_role}
              </span>
            )}
          </div>
        </div>

        <button
          type="button"
          className="btn ghost"
          onClick={() => setExpanded(!expanded)}
          style={{
            padding: "6px",
            fontSize: "13px",
            minWidth: "unset",
            width: "32px",
            height: "32px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: "var(--radius-sm)"
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{
            transform: expanded ? "rotate(180deg)" : "rotate(0)",
            transition: "transform 0.2s"
          }}>
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>
      </div>

      {/* Summary */}
      {result.summary && (
        <p className="small muted mb-3" style={{
          lineHeight: "1.5",
          paddingLeft: "16px",
          borderLeft: "2px solid var(--gray-100)",
          wordBreak: "break-word",
          whiteSpace: "pre-wrap"
        }}>
          {result.summary}
        </p>
      )}

      {/* Experience Cards - Only show when expanded */}
      {expanded && topExperiences && topExperiences.length > 0 && (
        <div className="mb-3">
          <h4 className="small mb-2" style={{
            fontWeight: 600,
            color: "var(--gray-700)",
            fontSize: "12px",
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            Recent Experience
          </h4>
          <div className="flex flex-col gap-2">
            {topExperiences.map((exp, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "10px",
                  background: "linear-gradient(90deg, var(--gray-50) 0%, transparent 100%)",
                  borderRadius: "6px",
                  borderLeft: "2px solid var(--blue-500)"
                }}
              >
                <div>
                  <div className="small" style={{ fontWeight: 600, color: "var(--gray-800)" }}>
                    {exp.position}
                  </div>
                  <div className="small muted">
                    {exp.company}
                    {exp.employment_type && ` • ${exp.employment_type}`}
                    {exp.work_mode && ` • ${exp.work_mode}`}
                  </div>
                </div>
                <span className="small" style={{
                  color: "var(--gray-600)",
                  fontWeight: 500
                }}>
                  {exp.duration_months ?
                    `${Math.round(exp.duration_months / 12 * 10) / 10}y` :
                    (exp.start_date && exp.end_date ? `${exp.start_date} - ${exp.end_date}` : '')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skills - Show limited in preview, all when expanded */}
      {result.skills && result.skills.length > 0 && (
        <div className="mb-3">
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "4px",
            maxWidth: "100%",
            overflow: "hidden"
          }}>
            {(expanded ? result.skills : topSkills).map((skill, idx) => (
              <span key={idx} className="chip" style={{
                fontSize: "11px",
                padding: "3px 8px",
                background: "var(--gray-100)",
                color: "var(--gray-700)",
                border: "1px solid var(--gray-200)",
                display: "inline-block",
                flexShrink: 0,
                maxWidth: "200px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap"
              }}>
                {skill}
              </span>
            ))}
            {!expanded && result.skills && result.skills.length > 8 && (
              <span className="chip" style={{
                fontSize: "11px",
                padding: "3px 8px",
                background: "var(--blue-50)",
                color: "var(--blue-600)",
                border: "1px solid var(--blue-200)",
                fontWeight: 600,
                display: "inline-block",
                flexShrink: 0
              }}>
                +{result.skills.length - 8} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Match Highlights with Source Colors */}
      {result.matches && result.matches.length > 0 && (
        <div>
          <h4 className="small mb-2" style={{
            fontWeight: 600,
            color: "var(--gray-700)",
            fontSize: "12px",
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            Relevance Highlights
          </h4>
          <div className="flex flex-col gap-2">
            {(expanded ? result.matches : result.matches.slice(0, 3)).map((match, idx) => (
              <div key={idx} style={{
                padding: "8px 10px",
                background: "var(--gray-50)",
                borderRadius: "6px",
                borderLeft: `3px solid ${getSourceColor(match.source)}`,
                fontSize: "13px"
              }}>
                <div style={{
                  marginBottom: "4px",
                  color: "var(--gray-800)",
                  fontStyle: "italic",
                  wordBreak: "break-word",
                  whiteSpace: "pre-wrap"
                }}>
                  "{match.text}"
                </div>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span style={{
                      fontSize: "11px",
                      padding: "2px 6px",
                      background: `${getSourceColor(match.source)}22`,
                      color: getSourceColor(match.source),
                      borderRadius: "10px",
                      fontWeight: 600,
                      textTransform: "uppercase"
                    }}>
                      {match.source || "Resume"}
                    </span>
                    {match.context && (
                      <span className="small muted" style={{ fontSize: "11px" }}>
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
                      background: "var(--gray-200)",
                      borderRadius: "2px",
                      position: "relative",
                      overflow: "hidden"
                    }}>
                      <div style={{
                        width: `${match.score * 100}%`,
                        height: "100%",
                        background: getScoreColor(match.score),
                        borderRadius: "2px"
                      }}/>
                    </div>
                    <span style={{
                      fontSize: "11px",
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
              <p className="small muted text-center" style={{ fontSize: "12px", marginTop: "4px" }}>
                +{result.matches.length - 3} more highlights
              </p>
            )}
          </div>
        </div>
      )}

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-3" style={{
          paddingTop: "12px",
          borderTop: "1px solid var(--gray-200)"
        }}>
          {/* Additional Experience (if more than 2) */}
          {result.experiences && result.experiences.length > 2 && (
            <div className="mb-3">
              <h4 className="small mb-2" style={{
                fontWeight: 600,
                color: "var(--gray-700)",
                fontSize: "12px",
                textTransform: "uppercase",
                letterSpacing: "0.5px"
              }}>
                Earlier Experience
              </h4>
              <div className="flex flex-col gap-2">
                {result.experiences.slice(2).map((exp, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "8px",
                      background: "var(--gray-50)",
                      borderRadius: "4px"
                    }}
                  >
                    <div>
                      <div className="small" style={{ fontWeight: 500 }}>
                        {exp.position} at {exp.company}
                      </div>
                      {(exp.employment_type || exp.work_mode) && (
                        <div className="small muted" style={{ fontSize: "11px" }}>
                          {[exp.employment_type, exp.work_mode].filter(Boolean).join(" • ")}
                        </div>
                      )}
                    </div>
                    <span className="small muted" style={{ fontSize: "12px" }}>
                      {exp.duration_months ?
                        `${Math.round(exp.duration_months / 12 * 10) / 10}y` :
                        (exp.start_date || exp.end_date || '')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {result.education && result.education.length > 0 && (
            <div>
              <h4 className="small mb-2" style={{
                fontWeight: 600,
                color: "var(--gray-700)",
                fontSize: "12px",
                textTransform: "uppercase",
                letterSpacing: "0.5px"
              }}>
                Education Background
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
                      background: "var(--gray-50)",
                      borderRadius: "4px"
                    }}
                  >
                    <div>
                      <div className="small" style={{ fontWeight: 500 }}>
                        {edu.degree || edu.qualification}
                        {edu.field && ` in ${edu.field}`}
                      </div>
                      {edu.institution && (
                        <div className="small muted" style={{ fontSize: "11px" }}>
                          {edu.institution}
                        </div>
                      )}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      {edu.status && (
                        <span style={{
                          fontSize: "10px",
                          padding: "2px 6px",
                          background: edu.status === "ongoing" ? "var(--blue-100)" : "var(--green-100)",
                          color: edu.status === "ongoing" ? "var(--blue-700)" : "var(--green-700)",
                          borderRadius: "8px",
                          fontWeight: 600,
                          textTransform: "uppercase"
                        }}>
                          {edu.status}
                        </span>
                      )}
                      {(edu.year || edu.start || edu.end) && (
                        <span className="small muted" style={{ fontSize: "12px" }}>
                          {edu.year || edu.start || edu.end}
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
  );
}