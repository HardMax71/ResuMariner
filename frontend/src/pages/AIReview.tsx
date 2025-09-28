import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getJobResult, type JobResult } from "../lib/api";

export default function AIReview() {
  const { jobId = "" } = useParams();
  const [result, setResult] = useState<JobResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await getJobResult(jobId);
        setResult(data);
      } catch (err: any) {
        setError(err.message || "Failed to load review");
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      fetchResult();
    }
  }, [jobId]);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "var(--green-600)";
    if (score >= 60) return "var(--blue-600)";
    if (score >= 40) return "var(--orange-500)";
    return "var(--red-500)";
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return "var(--green-50)";
    if (score >= 60) return "var(--blue-50)";
    if (score >= 40) return "var(--orange-50)";
    return "var(--red-50)";
  };

  if (loading) {
    return (
      <div className="container" style={{ maxWidth: "900px" }}>
        <div style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "400px"
        }}>
          <div style={{ textAlign: "center" }}>
            <div className="spinner" style={{
              width: "32px",
              height: "32px",
              margin: "0 auto 12px"
            }}></div>
            <p className="small muted">Analyzing resume...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ maxWidth: "900px" }}>
        <div style={{
          background: "var(--red-50)",
          border: "1px solid var(--red-200)",
          borderRadius: "6px",
          padding: "16px",
          marginBottom: "16px"
        }}>
          <div className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--red-600)" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span className="small" style={{ color: "var(--red-700)" }}>{error}</span>
          </div>
        </div>
        <Link to={`/jobs/${jobId}`} className="btn ghost">← Back to Job</Link>
      </div>
    );
  }

  if (!result || !result.review) {
    return (
      <div className="container" style={{ maxWidth: "900px" }}>
        <div style={{
          textAlign: "center",
          padding: "48px 16px",
          background: "var(--gray-50)",
          borderRadius: "8px"
        }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--gray-400)" strokeWidth="1.5" style={{ margin: "0 auto 16px" }}>
            <path d="M9 11H6a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-3m-6 0V3m0 8l3-3m-3 3L6 8"/>
          </svg>
          <h3 style={{ marginBottom: "8px", color: "var(--gray-700)" }}>No Review Available</h3>
          <p className="small muted" style={{ marginBottom: "24px" }}>
            AI analysis has not been generated for this resume yet
          </p>
          <Link to={`/jobs/${jobId}`} className="btn">View Job Status</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: "900px" }}>
      {/* Modern Minimal Header */}
      <div style={{
        marginBottom: "24px",
        paddingBottom: "16px",
        borderBottom: "1px solid var(--gray-200)"
      }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              to={`/jobs/${jobId}`}
              className="small"
              style={{
                color: "var(--gray-600)",
                textDecoration: "none",
                display: "flex",
                alignItems: "center",
                gap: "4px",
                transition: "color 0.2s"
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = "var(--gray-900)"}
              onMouseLeave={(e) => e.currentTarget.style.color = "var(--gray-600)"}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
              Job Details
            </Link>
            <span style={{ color: "var(--gray-300)" }}>|</span>
            <h1 style={{
              fontSize: "18px",
              fontWeight: 600,
              color: "var(--gray-900)",
              margin: 0
            }}>
              AI Resume Analysis
            </h1>
          </div>
          <Link
            to="/upload"
            className="btn ghost"
            style={{
              padding: "6px 12px",
              fontSize: "13px",
              fontWeight: 500
            }}
          >
            New Upload
          </Link>
        </div>
      </div>

      {/* Score Card - Modern Flat Design */}
      {result.review.overall_score !== undefined && (
        <div style={{
          background: "white",
          border: "1px solid var(--gray-200)",
          borderRadius: "8px",
          padding: "20px",
          marginBottom: "20px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
        }}>
          <div>
            <div className="flex items-center justify-between">
              <div>
                <h2 style={{
                  fontSize: "14px",
                  fontWeight: 600,
                  color: "var(--gray-800)",
                  margin: 0,
                  textTransform: "uppercase",
                  letterSpacing: "0.5px"
                }}>
                  Overall Score
                </h2>
                {result.review.summary && (
                  <p className="small muted" style={{ marginTop: "4px", marginBottom: 0 }}>
                    {result.review.summary}
                  </p>
                )}
              </div>
              <div style={{
                fontSize: "32px",
                fontWeight: 700,
                color: getScoreColor(result.review.overall_score)
              }}>
                {result.review.overall_score}/100
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feedback Sections - Card-based Design */}
      {typeof result.review === "object" && (
        <div style={{ display: "grid", gap: "12px" }}>
          {Object.entries(result.review)
            .filter(([key, value]) =>
              key !== "overall_score" &&
              key !== "summary" &&
              value !== null &&
              typeof value === "object"
            )
            .map(([section, feedback]: [string, any]) => {
              const mustCount = feedback.must?.length || 0;
              const shouldCount = feedback.should?.length || 0;
              const adviseCount = feedback.advise?.length || 0;
              const totalCount = mustCount + shouldCount + adviseCount;

              if (totalCount === 0) return null;

              const isExpanded = expandedSections.has(section);
              const priorityColor = mustCount > 0 ? "var(--red-500)" :
                                  shouldCount > 0 ? "var(--orange-500)" :
                                  "var(--blue-500)";

              return (
                <div
                  key={section}
                  style={{
                    background: "white",
                    border: "1px solid var(--gray-200)",
                    borderRadius: "8px",
                    overflow: "hidden",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                    transition: "all 0.2s"
                  }}
                >
                  {/* Section Header */}
                  <div
                    onClick={() => toggleSection(section)}
                    style={{
                      padding: "12px 16px",
                      cursor: "pointer",
                      background: "var(--gray-50)",
                      borderBottom: isExpanded ? "1px solid var(--gray-200)" : "none",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      userSelect: "none"
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div style={{
                        width: "4px",
                        height: "20px",
                        background: priorityColor,
                        borderRadius: "2px"
                      }}/>
                      <h3 style={{
                        fontSize: "14px",
                        fontWeight: 600,
                        color: "var(--gray-800)",
                        margin: 0,
                        textTransform: "capitalize"
                      }}>
                        {section.replace(/_/g, " ")}
                      </h3>
                      <div className="flex gap-2">
                        {mustCount > 0 && (
                          <span style={{
                            padding: "2px 6px",
                            background: "var(--red-100)",
                            color: "var(--red-700)",
                            fontSize: "11px",
                            fontWeight: 600,
                            borderRadius: "12px"
                          }}>
                            {mustCount} critical
                          </span>
                        )}
                        {shouldCount > 0 && (
                          <span style={{
                            padding: "2px 6px",
                            background: "var(--orange-100)",
                            color: "var(--orange-700)",
                            fontSize: "11px",
                            fontWeight: 600,
                            borderRadius: "12px"
                          }}>
                            {shouldCount} important
                          </span>
                        )}
                        {adviseCount > 0 && (
                          <span style={{
                            padding: "2px 6px",
                            background: "var(--blue-100)",
                            color: "var(--blue-700)",
                            fontSize: "11px",
                            fontWeight: 600,
                            borderRadius: "12px"
                          }}>
                            {adviseCount} tips
                          </span>
                        )}
                      </div>
                    </div>
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="var(--gray-500)"
                      strokeWidth="2"
                      style={{
                        transform: isExpanded ? "rotate(180deg)" : "rotate(0)",
                        transition: "transform 0.2s"
                      }}
                    >
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </div>

                  {/* Section Content */}
                  {isExpanded && (
                    <div style={{ padding: "16px" }}>
                      {feedback.must && feedback.must.length > 0 && (
                        <div style={{ marginBottom: "12px" }}>
                          <div style={{
                            fontSize: "11px",
                            fontWeight: 600,
                            color: "var(--red-600)",
                            textTransform: "uppercase",
                            letterSpacing: "0.5px",
                            marginBottom: "8px",
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                          }}>
                            <div style={{
                              width: "3px",
                              height: "3px",
                              background: "var(--red-500)",
                              borderRadius: "50%"
                            }}/>
                            Must Fix
                          </div>
                          <div style={{ paddingLeft: "12px" }}>
                            {feedback.must.map((item: string, idx: number) => (
                              <div
                                key={idx}
                                className="small"
                                style={{
                                  color: "var(--gray-700)",
                                  marginBottom: "6px",
                                  lineHeight: 1.5
                                }}
                              >
                                • {item}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {feedback.should && feedback.should.length > 0 && (
                        <div style={{ marginBottom: "12px" }}>
                          <div style={{
                            fontSize: "11px",
                            fontWeight: 600,
                            color: "var(--orange-600)",
                            textTransform: "uppercase",
                            letterSpacing: "0.5px",
                            marginBottom: "8px",
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                          }}>
                            <div style={{
                              width: "3px",
                              height: "3px",
                              background: "var(--orange-500)",
                              borderRadius: "50%"
                            }}/>
                            Should Improve
                          </div>
                          <div style={{ paddingLeft: "12px" }}>
                            {feedback.should.map((item: string, idx: number) => (
                              <div
                                key={idx}
                                className="small"
                                style={{
                                  color: "var(--gray-700)",
                                  marginBottom: "6px",
                                  lineHeight: 1.5
                                }}
                              >
                                • {item}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {feedback.advise && feedback.advise.length > 0 && (
                        <div>
                          <div style={{
                            fontSize: "11px",
                            fontWeight: 600,
                            color: "var(--blue-600)",
                            textTransform: "uppercase",
                            letterSpacing: "0.5px",
                            marginBottom: "8px",
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                          }}>
                            <div style={{
                              width: "3px",
                              height: "3px",
                              background: "var(--blue-500)",
                              borderRadius: "50%"
                            }}/>
                            Consider
                          </div>
                          <div style={{ paddingLeft: "12px" }}>
                            {feedback.advise.map((item: string, idx: number) => (
                              <div
                                key={idx}
                                className="small muted"
                                style={{
                                  marginBottom: "6px",
                                  lineHeight: 1.5
                                }}
                              >
                                • {item}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      )}

      {/* String Review Fallback */}
      {typeof result.review === "string" && (
        <div style={{
          background: "white",
          border: "1px solid var(--gray-200)",
          borderRadius: "8px",
          padding: "20px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
        }}>
          <p className="small" style={{
            margin: 0,
            color: "var(--gray-700)",
            lineHeight: 1.6
          }}>
            {result.review}
          </p>
        </div>
      )}

      {/* Empty State */}
      {typeof result.review === "object" &&
       !Object.entries(result.review).some(([key, value]) =>
         key !== "overall_score" && key !== "summary" && value !== null) && (
        <div style={{
          textAlign: "center",
          padding: "32px",
          background: "var(--gray-50)",
          borderRadius: "8px",
          marginTop: "20px"
        }}>
          <p className="small muted" style={{ margin: 0 }}>
            No detailed feedback sections available
          </p>
        </div>
      )}
    </div>
  );
}