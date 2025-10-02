import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { AlertCircle, ChevronDown, ChevronUp, ArrowLeft, FileText, Sparkles, AlertTriangle, Info, Lightbulb } from "lucide-react";
import { useJobResult } from "../hooks/useJobStatus";
import {
  PageWrapper,
  PageContainer,
  FlexRow,
  FlexColumn,
  ErrorCard,
  EmptyStateCard,
  DecorativeBlur,
  Spinner
} from "../components/styled";
import {
  IconWrapper,
  ScoreHero,
  ScoreValue,
  FeedbackSection,
  SectionHeader,
  PriorityIndicator,
  FeedbackBadge,
  FeedbackDot,
  FeedbackItem
} from "../components/styled/Card";
import PageHeader from "../components/PageHeader";

export default function AIReview() {
  const { jobId = "" } = useParams();
  const { data: result, isLoading: loading, error: queryError } = useJobResult(jobId);
  const error = queryError ? (queryError as Error).message : null;
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
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
      <PageWrapper>
        <PageContainer>
          <FlexColumn align="center" justify="center" style={{ minHeight: "400px" }} gap="var(--space-3)">
            <Spinner />
            <div style={{ textAlign: "center" }}>
              <p style={{ fontSize: "var(--text-base)", fontWeight: 600, color: "var(--neutral-900)", marginBottom: "4px" }}>
                Analyzing Resume
              </p>
              <p className="small muted">This may take a moment...</p>
            </div>
          </FlexColumn>
        </PageContainer>
      </PageWrapper>
    );
  }

  if (error) {
    return (
      <PageWrapper>
        <PageContainer>
          <ErrorCard>
            <FlexRow gap="8px" style={{ marginBottom: "8px" }}>
              <AlertCircle size={18} style={{ color: "var(--accent2-600)" }} />
              <span style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--accent2-700)" }}>
                Error Loading Review
              </span>
            </FlexRow>
            <p className="small" style={{ color: "var(--accent2-700)", marginBottom: 0 }}>{error}</p>
          </ErrorCard>
          <Link to={`/jobs/${jobId}`} className="btn ghost">
            <ArrowLeft size={16} />
            Back to Job
          </Link>
        </PageContainer>
      </PageWrapper>
    );
  }

  if (!result || !result.review) {
    return (
      <PageWrapper>
        <PageContainer>
          <EmptyStateCard>
            <IconWrapper style={{ width: "64px", height: "64px", margin: "0 auto var(--space-3)", background: "var(--neutral-100)", border: "none" }}>
              <FileText size={32} style={{ color: "var(--neutral-400)" }} />
            </IconWrapper>
            <h3 style={{ marginBottom: "8px" }}>
              No Review Available
            </h3>
            <p className="small muted" style={{ marginBottom: "var(--space-4)", maxWidth: "400px", margin: "0 auto var(--space-4)" }}>
              AI analysis has not been generated for this resume yet. Reviews are typically available a few minutes after upload.
            </p>
            <Link to={`/jobs/${jobId}`} className="btn">View Job Status</Link>
          </EmptyStateCard>
        </PageContainer>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <DecorativeBlur />
      <DecorativeBlur position="bottom-left" />

      <PageContainer>
        <PageHeader
          icon={<Sparkles size={24} style={{ color: "white" }} />}
          title="AI Resume Analysis"
          subtitle="Comprehensive feedback powered by AI"
          actions={
            <Link to={`/jobs/${jobId}`} className="btn ghost">
              Back to Job Details
              <ArrowLeft size={16} style={{ transform: "rotate(180deg)" }} />
            </Link>
          }
        />

        {result.review.overall_score !== undefined && (
          <ScoreHero>
            <div style={{ position: "relative", zIndex: 1 }}>
              <FlexRow justify="space-between" style={{ marginBottom: "var(--space-4)" }}>
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
                <ScoreValue>
                  {result.review.overall_score}
                  <span>/100</span>
                </ScoreValue>
              </FlexRow>

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
          </ScoreHero>
        )}

        {typeof result.review === "object" && (
          <FlexColumn gap="var(--space-3)">
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
                const priorityLevel = mustCount > 0 ? "critical" : shouldCount > 0 ? "important" : "tip";

                const redPalette = {
                  dark: { main: "#dc2626", text: "#991b1b", bg: "#fecaca", bgLight: "rgba(254, 226, 226, 0.5)", border: "#fca5a5" },
                  medium: { main: "#ef4444", text: "#b91c1c", bg: "#fed7d7", bgLight: "rgba(254, 242, 242, 0.5)", border: "#fbb6b6" },
                  light: { main: "#f87171", text: "#dc2626", bg: "#fee2e2", bgLight: "rgba(254, 245, 245, 0.5)", border: "#fecaca" }
                };

                const orangePalette = {
                  dark: { main: "#ea580c", text: "#9a3412", bg: "#fed7aa", bgLight: "rgba(255, 237, 213, 0.5)", border: "#fdba74" },
                  light: { main: "#f97316", text: "#c2410c", bg: "#ffedd5", bgLight: "rgba(255, 247, 237, 0.5)", border: "#fed7aa" }
                };

                const bluePalette = {
                  main: "#2563eb", text: "#1e40af", bg: "#bfdbfe", bgLight: "rgba(219, 234, 254, 0.5)", border: "#93c5fd"
                };

                const colors = priorityLevel === "critical" ?
                  { must: redPalette.dark, should: redPalette.medium, advise: redPalette.light } :
                  priorityLevel === "important" ?
                  { should: orangePalette.dark, advise: orangePalette.light } :
                  { advise: bluePalette };

                const priorityColor = priorityLevel === "critical" ? redPalette.dark.main :
                                     priorityLevel === "important" ? orangePalette.dark.main :
                                     bluePalette.main;
                const priorityBg = priorityLevel === "critical" ? redPalette.dark.bgLight :
                                  priorityLevel === "important" ? orangePalette.dark.bgLight :
                                  bluePalette.bgLight;

                return (
                  <FeedbackSection key={section}>
                    <SectionHeader
                      onClick={() => toggleSection(section)}
                      isExpanded={isExpanded}
                      priorityColor={priorityColor}
                      priorityBg={priorityBg}
                    >
                      <FlexRow gap="var(--space-3)" style={{ flex: 1 }}>
                        <PriorityIndicator color={priorityColor} />
                        <div>
                          <h3 style={{ margin: "0 0 4px 0", textTransform: "capitalize" }}>
                            {section.replace(/_/g, " ")}
                          </h3>
                          <FlexRow gap="8px">
                            {mustCount > 0 && colors.must && (
                              <span style={{
                                padding: "2px 8px",
                                background: colors.must.bg,
                                color: colors.must.text,
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
                                  borderRadius: "50%",
                                  background: colors.must.main
                                }} />
                                {mustCount} Critical
                              </span>
                            )}
                            {shouldCount > 0 && colors.should && (
                              <span style={{
                                padding: "2px 8px",
                                background: colors.should.bg,
                                color: colors.should.text,
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
                                  borderRadius: "50%",
                                  background: colors.should.main
                                }} />
                                {shouldCount} Important
                              </span>
                            )}
                            {adviseCount > 0 && colors.advise && (
                              <span style={{
                                padding: "2px 8px",
                                background: colors.advise.bg,
                                color: colors.advise.text,
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
                                  borderRadius: "50%",
                                  background: colors.advise.main
                                }} />
                                {adviseCount} Tip
                              </span>
                            )}
                          </FlexRow>
                        </div>
                      </FlexRow>
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
                    </SectionHeader>

                    {isExpanded && (
                      <div style={{ padding: "var(--space-2)", animation: "fade-in 0.3s ease-out" }}>
                        {[
                          { items: feedback.must, color: colors.must, Icon: AlertTriangle, label: "Critical - Must Fix", key: "must" },
                          { items: feedback.should, color: colors.should, Icon: Info, label: "Important - Should Improve", key: "should" },
                          { items: feedback.advise, color: colors.advise, Icon: Lightbulb, label: "Optional - Consider These Tips", key: "advise" }
                        ].map(({ items, color, Icon, label, key }, sectionIdx) => {
                          if (!items || items.length === 0 || !color) return null;
                          const needsMargin = sectionIdx > 0 && (
                            (sectionIdx === 1 && feedback.must && feedback.must.length > 0) ||
                            (sectionIdx === 2 && ((feedback.must && feedback.must.length > 0) || (feedback.should && feedback.should.length > 0)))
                          );

                          return (
                            <div key={key} style={{ marginTop: needsMargin ? "var(--space-3)" : 0 }}>
                              <FlexRow gap="var(--space-2)" style={{ marginBottom: "var(--space-2)", paddingBottom: "var(--space-1)", borderBottom: `2px solid ${color.border}` }}>
                                <Icon size={18} color={color.main} strokeWidth={2.5} style={{ flexShrink: 0 }} />
                                <span style={{
                                  fontSize: "var(--text-sm)",
                                  fontWeight: 700,
                                  color: color.text,
                                  textTransform: "uppercase",
                                  letterSpacing: "var(--tracking-wide)"
                                }}>
                                  {label}
                                </span>
                              </FlexRow>
                              <FlexColumn gap="var(--space-2)">
                                {items.map((item: string, idx: number) => (
                                  <FeedbackItem key={idx} dotColor={color.main}>
                                    <span style={{ fontSize: "var(--text-sm)", color: key === "advise" ? "var(--neutral-700)" : "var(--neutral-800)", lineHeight: "var(--leading-relaxed)" }}>
                                      {item}
                                    </span>
                                  </FeedbackItem>
                                ))}
                              </FlexColumn>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </FeedbackSection>
                );
              })}
          </FlexColumn>
        )}

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

        {typeof result.review === "object" &&
         !Object.entries(result.review).some(([key, value]) =>
           key !== "overall_score" && key !== "summary" && value !== null) && (
          <EmptyStateCard>
            <p className="small muted" style={{ margin: 0 }}>
              No detailed feedback sections available. Check back later for a complete analysis.
            </p>
          </EmptyStateCard>
        )}
      </PageContainer>
    </PageWrapper>
  );
}
