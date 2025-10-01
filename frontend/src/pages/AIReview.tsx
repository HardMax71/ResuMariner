import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getJobResult, type JobResult } from "../lib/api";
import { AlertCircle, ChevronDown, ChevronUp, ArrowLeft, FileText, Sparkles } from "lucide-react";
import Badge from "../components/Badge";

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
    if (score >= 80) return { color: "var(--success)", bg: "#10b98120" };
    if (score >= 60) return { color: "var(--primary-600)", bg: "var(--primary-50)" };
    if (score >= 40) return { color: "var(--accent1-600)", bg: "var(--accent1-50)" };
    return { color: "var(--accent2-600)", bg: "var(--accent2-50)" };
  };

  const getScoreGrade = (score: number) => {
    if (score >= 90) return "Exceptional";
    if (score >= 80) return "Excellent";
    if (score >= 70) return "Very Good";
    if (score >= 60) return "Good";
    if (score >= 50) return "Fair";
    return "Needs Work";
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="page-container-narrow">
          <div style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "400px",
            gap: "var(--space-3)"
          }}>
            <div style={{
              width: "48px",
              height: "48px",
              border: "3px solid var(--primary-100)",
              borderTopColor: "var(--primary-600)",
              borderRadius: "50%",
              animation: "spin 1s linear infinite"
            }}></div>
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: "var(--text-base)", fontWeight: 600, color: "var(--neutral-900)", marginBottom: "4px" }}>
                Analyzing Resume
              </p>
              <p className="small muted">This may take a moment...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-wrapper">
        <div className="page-container-narrow">
          <div style={{
            background: "var(--accent2-50)",
            border: "1px solid var(--accent2-200)",
            borderRadius: "var(--radius-sm)",
            padding: "var(--space-4)",
            marginBottom: "var(--space-3)"
          }}>
            <div className="flex items-center gap-2" style={{ marginBottom: "8px" }}>
              <AlertCircle size={18} style={{ color: "var(--accent2-600)" }} />
              <span style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--accent2-700)" }}>
                Error Loading Review
              </span>
            </div>
            <p className="small" style={{ color: "var(--accent2-700)", marginBottom: 0 }}>{error}</p>
          </div>
          <Link to={`/jobs/${jobId}`} className="btn ghost">
            <ArrowLeft size={16} />
            Back to Job
          </Link>
        </div>
      </div>
    );
  }

  if (!result || !result.review) {
    return (
      <div className="page-wrapper">
        <div className="page-container-narrow">
          <div className="glass-card" style={{
            textAlign: "center",
            padding: "var(--space-8) var(--space-4)"
          }}>
            <div style={{
              width: "64px",
              height: "64px",
              margin: "0 auto var(--space-3)",
              background: "var(--neutral-100)",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <FileText size={32} style={{ color: "var(--neutral-400)" }} />
            </div>
            <h3 style={{ marginBottom: "8px" }}>
              No Review Available
            </h3>
            <p className="small muted" style={{ marginBottom: "var(--space-4)", maxWidth: "400px", margin: "0 auto var(--space-4)" }}>
              AI analysis has not been generated for this resume yet. Reviews are typically available a few minutes after upload.
            </p>
            <Link to={`/jobs/${jobId}`} className="btn">View Job Status</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      {/* Decorative background elements */}
      <div className="decorative-blur" style={{
        position: "absolute",
        top: "10%",
        right: "-5%",
        width: "500px",
        height: "500px",
        background: "radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)",
        borderRadius: "50%",
        filter: "blur(60px)",
        pointerEvents: "none"
      }}></div>
      <div className="decorative-blur" style={{
        position: "absolute",
        bottom: "20%",
        left: "-5%",
        width: "400px",
        height: "400px",
        background: "radial-gradient(circle, rgba(245, 158, 11, 0.06) 0%, transparent 70%)",
        borderRadius: "50%",
        filter: "blur(60px)",
        pointerEvents: "none"
      }}></div>

      <div className="page-container-narrow">
        {/* Header */}
        <div style={{ marginBottom: "var(--space-5)" }}>
          <Link
            to={`/jobs/${jobId}`}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              fontSize: "var(--text-sm)",
              color: "var(--neutral-600)",
              textDecoration: "none",
              marginBottom: "var(--space-2)",
              transition: "color var(--transition-fast)"
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = "var(--primary-600)"}
            onMouseLeave={(e) => e.currentTarget.style.color = "var(--neutral-600)"}
          >
            <ArrowLeft size={16} />
            Back to Job Details
          </Link>
          <div className="flex items-center gap-3">
            <div style={{
              width: "40px",
              height: "40px",
              background: "linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%)",
              borderRadius: "var(--radius-sm)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(67, 56, 202, 0.25)"
            }}>
              <Sparkles size={20} style={{ color: "white" }} />
            </div>
            <div>
              <h1 style={{ margin: 0 }}>
                AI Resume Analysis
              </h1>
              <p className="small muted" style={{ margin: 0 }}>
                Comprehensive feedback powered by AI
              </p>
            </div>
          </div>
        </div>

        {/* Overall Score Card - Hero Section */}
        {result.review.overall_score !== undefined && (
          <div style={{
            background: "linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%)",
            borderRadius: "var(--radius-sm)",
            padding: "var(--space-6)",
            marginBottom: "var(--space-5)",
            boxShadow: "0 8px 24px rgba(67, 56, 202, 0.2)",
            position: "relative",
            overflow: "hidden"
          }}>
            {/* Decorative gradient overlay */}
            <div style={{
              position: "absolute",
              top: 0,
              right: 0,
              width: "400px",
              height: "400px",
              background: "radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%)",
              pointerEvents: "none"
            }}></div>

            <div style={{ position: "relative", zIndex: 1 }}>
              <div className="flex items-center justify-between" style={{ marginBottom: "var(--space-4)" }}>
                <div>
                  <p style={{
                    fontSize: "var(--text-sm)",
                    fontWeight: 600,
                    color: "rgba(255, 255, 255, 0.8)",
                    textTransform: "uppercase",
                    letterSpacing: "var(--tracking-wide)",
                    marginBottom: "4px"
                  }}>
                    Overall Score
                  </p>
                  <p style={{
                    fontSize: "var(--text-base)",
                    color: "rgba(255, 255, 255, 0.9)",
                    margin: 0,
                    lineHeight: "var(--leading-relaxed)"
                  }}>
                    {getScoreGrade(result.review.overall_score)}
                  </p>
                </div>
                <div style={{
                  fontSize: "64px",
                  fontWeight: 800,
                  fontFamily: "var(--font-display)",
                  color: "white",
                  lineHeight: 1,
                  textShadow: "0 2px 8px rgba(0, 0, 0, 0.15)"
                }}>
                  {result.review.overall_score}
                  <span style={{ fontSize: "32px", fontWeight: 700, opacity: 0.8 }}>/100</span>
                </div>
              </div>

              {result.review.summary && (
                <div style={{
                  background: "rgba(255, 255, 255, 0.15)",
                  backdropFilter: "blur(10px)",
                  borderRadius: "var(--radius-sm)",
                  padding: "var(--space-3)",
                  border: "1px solid rgba(255, 255, 255, 0.2)"
                }}>
                  <p style={{
                    fontSize: "var(--text-base)",
                    color: "white",
                    margin: 0,
                    lineHeight: "var(--leading-relaxed)"
                  }}>
                    {result.review.summary}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Feedback Sections */}
        {typeof result.review === "object" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
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
                const priorityColor = mustCount > 0 ? "var(--accent2-600)" :
                                    shouldCount > 0 ? "var(--accent1-600)" :
                                    "var(--primary-600)";
                const priorityBg = mustCount > 0 ? "var(--accent2-50)" :
                                  shouldCount > 0 ? "var(--accent1-50)" :
                                  "var(--primary-50)";

                return (
                  <div
                    key={section}
                    className="glass-card"
                    style={{
                      padding: 0,
                      overflow: "hidden",
                      transition: "all var(--transition-base)",
                      cursor: "pointer"
                    }}
                  >
                    {/* Section Header */}
                    <div
                      onClick={() => toggleSection(section)}
                      style={{
                        padding: "var(--space-3) var(--space-4)",
                        background: priorityBg,
                        borderBottom: isExpanded ? `1px solid ${priorityColor}20` : "none",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        userSelect: "none",
                        transition: "background var(--transition-fast)"
                      }}
                      onMouseEnter={(e) => {
                        if (!isExpanded) e.currentTarget.style.background = `${priorityColor}15`;
                      }}
                      onMouseLeave={(e) => {
                        if (!isExpanded) e.currentTarget.style.background = priorityBg;
                      }}
                    >
                      <div className="flex items-center gap-3" style={{ flex: 1 }}>
                        <div style={{
                          width: "4px",
                          height: "32px",
                          background: priorityColor,
                          borderRadius: "var(--radius-full)"
                        }}></div>
                        <div>
                          <h3 style={{
                            margin: "0 0 4px 0",
                            textTransform: "capitalize"
                          }}>
                            {section.replace(/_/g, " ")}
                          </h3>
                          <div className="flex gap-2">
                            {mustCount > 0 && (
                              <Badge variant="primary" style={{
                                padding: "2px 8px",
                                background: "var(--accent2-100)",
                                color: "var(--accent2-700)",
                                fontSize: "var(--text-xs)",
                                fontWeight: 600,
                                borderRadius: "var(--radius-full)",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "4px"
                              }}>
                                <span style={{
                                  width: "6px",
                                  height: "6px",
                                  background: "var(--accent2-600)",
                                  borderRadius: "50%"
                                }}></span>
                                {mustCount} Critical
                              </Badge>
                            )}
                            {shouldCount > 0 && (
                              <Badge variant="primary" style={{
                                padding: "2px 8px",
                                background: "var(--accent1-100)",
                                color: "var(--accent1-700)",
                                fontSize: "var(--text-xs)",
                                fontWeight: 600,
                                borderRadius: "var(--radius-full)",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "4px"
                              }}>
                                <span style={{
                                  width: "6px",
                                  height: "6px",
                                  background: "var(--accent1-600)",
                                  borderRadius: "50%"
                                }}></span>
                                {shouldCount} Important
                              </Badge>
                            )}
                            {adviseCount > 0 && (
                              <Badge variant="primary" style={{
                                padding: "2px 8px",
                                background: "var(--primary-100)",
                                color: "var(--primary-700)",
                                fontSize: "var(--text-xs)",
                                fontWeight: 600,
                                borderRadius: "var(--radius-full)",
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "4px"
                              }}>
                                <span style={{
                                  width: "6px",
                                  height: "6px",
                                  background: "var(--primary-600)",
                                  borderRadius: "50%"
                                }}></span>
                                {adviseCount} Tip
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      <div style={{
                        width: "32px",
                        height: "32px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        borderRadius: "50%",
                        background: "rgba(255, 255, 255, 0.8)",
                        transition: "transform var(--transition-base)"
                      }}>
                        {isExpanded ? (
                          <ChevronUp size={18} style={{ color: priorityColor }} />
                        ) : (
                          <ChevronDown size={18} style={{ color: priorityColor }} />
                        )}
                      </div>
                    </div>

                    {/* Section Content */}
                    {isExpanded && (
                      <div style={{
                        padding: "var(--space-2)",
                        animation: "fade-in 0.3s ease-out"
                      }}>
                        {feedback.must && feedback.must.length > 0 && (
                          <div>
                            <div style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "var(--space-1)",
                              marginBottom: "var(--space-1)",
                              paddingBottom: "var(--space-1)",
                              borderBottom: "2px solid var(--accent2-200)"
                            }}>
                              <div style={{
                                width: "24px",
                                height: "24px",
                                background: "var(--accent2-600)",
                                borderRadius: "50%",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center"
                              }}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                  <line x1="12" y1="9" x2="12" y2="13"/>
                                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                                </svg>
                              </div>
                              <span style={{
                                fontSize: "var(--text-sm)",
                                fontWeight: 700,
                                color: "var(--accent2-700)",
                                textTransform: "uppercase",
                                letterSpacing: "var(--tracking-wide)"
                              }}>
                                Critical - Must Fix
                              </span>
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
                              {feedback.must.map((item: string, idx: number) => (
                                <div
                                  key={idx}
                                  style={{
                                    padding: "var(--space-1) var(--space-2)",
                                    background: "var(--accent2-50)",
                                    border: "1px solid var(--accent2-200)",
                                    borderRadius: "var(--radius-sm)",
                                    display: "flex",
                                    gap: "var(--space-1)"
                                  }}
                                >
                                  <span style={{
                                    color: "var(--accent2-600)",
                                    fontWeight: 700,
                                    fontSize: "var(--text-sm)",
                                    flexShrink: 0
                                  }}>
                                    •
                                  </span>
                                  <span style={{
                                    fontSize: "var(--text-sm)",
                                    color: "var(--neutral-800)",
                                    lineHeight: "var(--leading-relaxed)"
                                  }}>
                                    {item}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {feedback.should && feedback.should.length > 0 && (
                          <div style={{ marginTop: feedback.must && feedback.must.length > 0 ? "var(--space-3)" : 0 }}>
                            <div style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "var(--space-1)",
                              marginBottom: "var(--space-1)",
                              paddingBottom: "var(--space-1)",
                              borderBottom: "2px solid var(--accent1-200)"
                            }}>
                              <div style={{
                                width: "24px",
                                height: "24px",
                                background: "var(--accent1-600)",
                                borderRadius: "50%",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center"
                              }}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                                  <circle cx="12" cy="12" r="10"/>
                                  <line x1="12" y1="8" x2="12" y2="12"/>
                                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                                </svg>
                              </div>
                              <span style={{
                                fontSize: "var(--text-sm)",
                                fontWeight: 700,
                                color: "var(--accent1-700)",
                                textTransform: "uppercase",
                                letterSpacing: "var(--tracking-wide)"
                              }}>
                                Important - Should Improve
                              </span>
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
                              {feedback.should.map((item: string, idx: number) => (
                                <div
                                  key={idx}
                                  style={{
                                    padding: "var(--space-1) var(--space-2)",
                                    background: "var(--accent1-50)",
                                    border: "1px solid var(--accent1-200)",
                                    borderRadius: "var(--radius-sm)",
                                    display: "flex",
                                    gap: "var(--space-1)"
                                  }}
                                >
                                  <span style={{
                                    color: "var(--accent1-600)",
                                    fontWeight: 700,
                                    fontSize: "var(--text-sm)",
                                    flexShrink: 0
                                  }}>
                                    •
                                  </span>
                                  <span style={{
                                    fontSize: "var(--text-sm)",
                                    color: "var(--neutral-800)",
                                    lineHeight: "var(--leading-relaxed)"
                                  }}>
                                    {item}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {feedback.advise && feedback.advise.length > 0 && (
                          <div style={{ marginTop: (feedback.must && feedback.must.length > 0) || (feedback.should && feedback.should.length > 0) ? "var(--space-3)" : 0 }}>
                            <div style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "var(--space-1)",
                              marginBottom: "var(--space-1)",
                              paddingBottom: "var(--space-1)",
                              borderBottom: "2px solid var(--primary-200)"
                            }}>
                              <div style={{
                                width: "24px",
                                height: "24px",
                                background: "var(--primary-600)",
                                borderRadius: "50%",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center"
                              }}>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                                </svg>
                              </div>
                              <span style={{
                                fontSize: "var(--text-sm)",
                                fontWeight: 700,
                                color: "var(--primary-700)",
                                textTransform: "uppercase",
                                letterSpacing: "var(--tracking-wide)"
                              }}>
                                Optional - Consider These Tips
                              </span>
                            </div>
                            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
                              {feedback.advise.map((item: string, idx: number) => (
                                <div
                                  key={idx}
                                  style={{
                                    padding: "var(--space-1) var(--space-2)",
                                    background: "var(--primary-50)",
                                    border: "1px solid var(--primary-200)",
                                    borderRadius: "var(--radius-sm)",
                                    display: "flex",
                                    gap: "var(--space-1)"
                                  }}
                                >
                                  <span style={{
                                    color: "var(--primary-600)",
                                    fontWeight: 700,
                                    fontSize: "var(--text-sm)",
                                    flexShrink: 0
                                  }}>
                                    •
                                  </span>
                                  <span style={{
                                    fontSize: "var(--text-sm)",
                                    color: "var(--neutral-700)",
                                    lineHeight: "var(--leading-relaxed)"
                                  }}>
                                    {item}
                                  </span>
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
          <div className="glass-card-lg">
            <p style={{
              margin: 0,
              fontSize: "var(--text-base)",
              color: "var(--neutral-700)",
              lineHeight: "var(--leading-relaxed)"
            }}>
              {result.review}
            </p>
          </div>
        )}

        {/* Empty State */}
        {typeof result.review === "object" &&
         !Object.entries(result.review).some(([key, value]) =>
           key !== "overall_score" && key !== "summary" && value !== null) && (
          <div className="glass-card" style={{
            textAlign: "center",
            padding: "var(--space-6)"
          }}>
            <p className="small muted" style={{ margin: 0 }}>
              No detailed feedback sections available. Check back later for a complete analysis.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
