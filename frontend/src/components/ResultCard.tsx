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
    if (score >= 0.8) return "var(--success)";
    if (score >= 0.6) return "var(--blue-600)";
    if (score >= 0.4) return "var(--warning)";
    return "var(--gray-600)";
  };

  const topExperiences = result.experiences?.slice(0, 2);
  const topSkills = result.skills?.slice(0, 8);

  return (
    <div className="search-result">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="title flex items-center gap-2">
            {result.name}
            <span
              className="badge"
              style={{
                backgroundColor: `${getScoreColor(result.score)}20`,
                color: getScoreColor(result.score),
                fontWeight: 600
              }}
            >
              {(result.score * 100).toFixed(0)}% Match
            </span>
          </h3>
          <div className="flex items-center gap-3 mt-1">
            {result.email && (
              <a href={`mailto:${result.email}`} className="small" style={{ color: "var(--blue-600)" }}>
                {result.email}
              </a>
            )}
            {result.location && (
              <span className="small muted">
                📍 {typeof result.location === 'object' ?
                  `${result.location.city || ''} ${result.location.country || ''}`.trim() :
                  result.location}
              </span>
            )}
            {result.years_experience && (
              <span className="small muted">
                🕐 {formatYearsExperience(result.years_experience)}
              </span>
            )}
            {result.desired_role && (
              <span className="small muted">
                💼 {result.desired_role}
              </span>
            )}
          </div>
        </div>

        <button
          type="button"
          className="btn ghost"
          onClick={() => setExpanded(!expanded)}
          style={{ padding: "var(--space-1) var(--space-2)", fontSize: "var(--text-sm)" }}
        >
          {expanded ? "Show Less" : "Show More"}
        </button>
      </div>

      {/* Summary */}
      {result.summary && (
        <p className="muted small mb-3" style={{ lineHeight: "var(--leading-relaxed)" }}>
          {result.summary}
        </p>
      )}

      {/* Recent Experience */}
      {topExperiences && topExperiences.length > 0 && (
        <div className="mb-3">
          <h4 className="small mb-2" style={{ fontWeight: 600, color: "var(--gray-700)" }}>
            Recent Experience
          </h4>
          <div className="flex flex-col gap-2">
            {topExperiences.map((exp, idx) => (
              <div
                key={idx}
                className="flex justify-between"
                style={{
                  padding: "var(--space-1)",
                  background: "var(--gray-50)",
                  borderRadius: "var(--radius-sm)",
                }}
              >
                <div>
                  <strong className="small">{exp.position}</strong>
                  <span className="small muted"> at {exp.company}</span>
                </div>
                <span className="small muted">
                  {exp.duration_months ? `${Math.round(exp.duration_months / 12 * 10) / 10} years` :
                    (exp.start_date && exp.end_date ? `${exp.start_date} - ${exp.end_date}` : '')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skills */}
      {topSkills && topSkills.length > 0 && (
        <div className="mb-3">
          <h4 className="small mb-2" style={{ fontWeight: 600, color: "var(--gray-700)" }}>
            Key Skills
          </h4>
          <div className="chips">
            {topSkills.map((skill, idx) => (
              <span key={idx} className="chip" style={{ fontSize: "var(--text-xs)" }}>
                {skill}
              </span>
            ))}
            {result.skills && result.skills.length > 8 && (
              <span className="chip" style={{ fontSize: "var(--text-xs)", opacity: 0.6 }}>
                +{result.skills.length - 8} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Match Highlights */}
      {result.matches && result.matches.length > 0 && (
        <div className={expanded ? "" : "mb-0"}>
          <h4 className="small mb-2" style={{ fontWeight: 600, color: "var(--gray-700)" }}>
            Match Highlights
          </h4>
          <div className="matches">
            {(expanded ? result.matches : result.matches.slice(0, 2)).map((match, idx) => (
              <div key={idx} className="match">
                <div className="match-text">"{match.text}"</div>
                <div className="flex justify-between">
                  <span className="small muted">
                    {match.source || "Resume"}
                    {match.context && ` • ${match.context}`}
                  </span>
                  <span
                    className="small"
                    style={{ color: getScoreColor(match.score), fontWeight: 500 }}
                  >
                    {(match.score * 100).toFixed(0)}% relevance
                  </span>
                </div>
              </div>
            ))}
            {!expanded && result.matches.length > 2 && (
              <p className="small muted text-center mt-2">
                +{result.matches.length - 2} more matches
              </p>
            )}
          </div>
        </div>
      )}

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-3" style={{ paddingTop: "var(--space-2)", borderTop: "1px solid var(--gray-200)" }}>
          {/* Full Experience */}
          {result.experiences && result.experiences.length > 2 && (
            <div className="mb-3">
              <h4 className="small mb-2" style={{ fontWeight: 600, color: "var(--gray-700)" }}>
                Full Experience History
              </h4>
              <div className="flex flex-col gap-2">
                {result.experiences.slice(2).map((exp, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between"
                    style={{
                      padding: "var(--space-1)",
                      background: "var(--gray-50)",
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    <div>
                      <strong className="small">{exp.position}</strong>
                      <span className="small muted"> at {exp.company}</span>
                      {exp.employment_type && (
                        <span className="small muted"> • {exp.employment_type}</span>
                      )}
                    </div>
                    <span className="small muted">
                      {exp.duration_months ? `${Math.round(exp.duration_months / 12 * 10) / 10} years` :
                        (exp.start_date && exp.end_date ? `${exp.start_date} - ${exp.end_date}` : '')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {result.education && result.education.length > 0 && (
            <div className="mb-3">
              <h4 className="small mb-2" style={{ fontWeight: 600, color: "var(--gray-700)" }}>
                Education
              </h4>
              <div className="flex flex-col gap-2">
                {result.education.map((edu, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between"
                    style={{
                      padding: "var(--space-1)",
                      background: "var(--gray-50)",
                      borderRadius: "var(--radius-sm)",
                    }}
                  >
                    <div>
                      <strong className="small">{edu.degree || edu.qualification}</strong>
                      {edu.field && <span className="small muted"> in {edu.field}</span>}
                      {edu.institution && <span className="small muted"> • {edu.institution}</span>}
                    </div>
                    {edu.year && <span className="small muted">{edu.year}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* All Skills */}
          {result.skills && result.skills.length > 8 && (
            <div>
              <h4 className="small mb-2" style={{ fontWeight: 600, color: "var(--gray-700)" }}>
                All Skills ({result.skills.length})
              </h4>
              <div className="chips">
                {result.skills.map((skill, idx) => (
                  <span key={idx} className="chip" style={{ fontSize: "var(--text-xs)" }}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}