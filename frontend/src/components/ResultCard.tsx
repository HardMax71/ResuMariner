import { useState } from "react";
import type { SearchResult } from "../lib/api";
import Chip from "./Chip";
import { Mail, MapPin, Briefcase, GraduationCap, Target, Globe, ChevronDown } from "lucide-react";

type Props = {
  result: SearchResult;
};

export default function ResultCard({ result }: Props) {
  const [expanded, setExpanded] = useState(false);

  const formatYearsExperience = (years?: number | null) => {
    if (!years) return null;
    if (years < 1) return "<1y";
    return `${years}y`;
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
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {/* Match Score Indicator */}
            <div style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              background: `${getScoreColor(result.score)}15`,
              padding: "6px 12px",
              borderRadius: "18px",
              border: `2px solid ${getScoreColor(result.score)}`
            }}>
              <span style={{
                fontSize: "11px",
                fontWeight: 600,
                color: getScoreColor(result.score),
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                lineHeight: 1
              }}>
                Match
              </span>
              <span style={{
                fontSize: "16px",
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
              color: "var(--gray-700)",
              background: "var(--gray-50)",
              padding: "2px 8px",
              borderRadius: "12px"
            }}>
              <Briefcase size={12} strokeWidth={2} style={{ display: "inline", marginRight: "4px", verticalAlign: "-2px" }} />
              {formatYearsExperience(result.years_experience)}
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
      </div>

      {/* Summary */}
      {result.summary && (
        <div style={{
          position: "relative",
          padding: "12px 12px 12px 16px",
          background: "linear-gradient(135deg, var(--gray-50) 0%, transparent 100%)",
          borderRadius: "var(--radius-sm)",
          border: "1px solid var(--gray-100)",
          borderLeft: "3px solid var(--blue-500)"
        }}>
          <p className="small" style={{
            lineHeight: "1.6",
            wordBreak: "break-word",
            whiteSpace: "pre-wrap",
            color: "var(--gray-700)",
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
            gap: "4px",
            maxWidth: "100%",
            overflow: "hidden"
          }}>
            {(expanded ? result.skills : topSkills).map((skill, idx) => (
              <Chip key={idx} style={{
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
              </Chip>
            ))}
            {!expanded && result.skills && result.skills.length > 8 && (
              <Chip style={{
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
                fontSize: "11px",
                padding: "3px 8px",
                background: "var(--blue-50)",
                color: "var(--blue-700)",
                border: "1px solid var(--blue-200)",
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
            color: "var(--gray-900)",
            fontSize: "13px",
            textTransform: "uppercase",
            letterSpacing: "0.8px",
            marginBottom: "12px",
            paddingBottom: "6px",
            borderBottom: "2px solid var(--gray-200)"
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
                      background: "white",
                      border: "1px solid var(--gray-200)",
                      borderRadius: "8px",
                      borderLeft: "3px solid var(--blue-500)",
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
                        color: "var(--blue-600)",
                        fontWeight: 600,
                        background: "var(--blue-50)",
                        padding: "2px 8px",
                        borderRadius: "12px",
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
                          return parts.join(' • ') || 'N/A';
                        })()}
                      </span>
                    </div>
                    {exp.key_points && exp.key_points.length > 0 && (
                      <ul style={{
                        margin: "0",
                        paddingLeft: "20px",
                        listStyleType: "none",
                        position: "relative"
                      }}>
                        {exp.key_points.map((point, pidx) => (
                          <li key={pidx} style={{
                            fontSize: "12px",
                            color: "var(--gray-600)",
                            lineHeight: "1.5",
                            marginBottom: pidx < exp.key_points.length - 1 ? "4px" : "0",
                            position: "relative",
                            paddingLeft: "0"
                          }}>
                            <span style={{
                              position: "absolute",
                              left: "-16px",
                              top: "5px",
                              width: "4px",
                              height: "4px",
                              background: "var(--blue-400)",
                              borderRadius: "50%"
                            }}/>
                            {typeof point === 'string' ? point : point.text || point.description}
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
                        return parts.join(' • ') || 'N/A';
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
            color: "var(--gray-900)",
            fontSize: "13px",
            textTransform: "uppercase",
            letterSpacing: "0.8px",
            marginBottom: "12px",
            paddingBottom: "6px",
            borderBottom: "2px solid var(--gray-200)"
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
        <div style={{
          paddingTop: "12px",
          borderTop: "1px solid var(--gray-200)"
        }}>
          {/* Education */}
          {result.education && result.education.length > 0 && (
            <div>
              <h4 style={{
                fontWeight: 700,
                color: "var(--gray-900)",
                fontSize: "13px",
                textTransform: "uppercase",
                letterSpacing: "0.8px",
                marginBottom: "12px",
                paddingBottom: "6px",
                borderBottom: "2px solid var(--gray-200)"
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
                      background: "var(--gray-50)",
                      borderRadius: "4px"
                    }}
                  >
                    <div>
                      <div className="small" style={{ fontWeight: 500 }}>
                        {edu.qualification}
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