import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { AlertCircle, ChevronDown, ChevronUp, ArrowLeft, FileText, Sparkles, AlertTriangle, Info, Lightbulb } from "lucide-react";
import { useResumeStatus } from "../hooks/useJobStatus";
import type { AppError, ReviewData, ReviewFeedback } from "../lib/api";
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

const COLOR_PALETTES = {
  red: {
    dark: { main: "var(--accent2-600)", text: "var(--accent2-800)", bg: "var(--accent2-200)", bgLight: "rgba(var(--accent2-500-rgb), 0.15)", border: "var(--accent2-300)" },
    medium: { main: "var(--accent2-500)", text: "var(--accent2-700)", bg: "var(--accent2-100)", bgLight: "rgba(var(--accent2-500-rgb), 0.1)", border: "var(--accent2-200)" },
    light: { main: "var(--accent2-400)", text: "var(--accent2-600)", bg: "var(--accent2-100)", bgLight: "rgba(var(--accent2-500-rgb), 0.08)", border: "var(--accent2-200)" }
  },
  orange: {
    dark: { main: "var(--accent1-600)", text: "var(--accent1-800)", bg: "var(--accent1-200)", bgLight: "rgba(var(--accent1-500-rgb), 0.15)", border: "var(--accent1-300)" },
    light: { main: "var(--accent1-500)", text: "var(--accent1-700)", bg: "var(--accent1-100)", bgLight: "rgba(var(--accent1-500-rgb), 0.1)", border: "var(--accent1-200)" }
  },
  blue: {
    main: "var(--primary-600)", text: "var(--primary-800)", bg: "var(--primary-200)", bgLight: "rgba(var(--primary-500-rgb), 0.15)", border: "var(--primary-300)"
  }
} as const;

export default function AIReview() {
  const { uid = "" } = useParams();
  const { data: job, isLoading: loading, error: queryError } = useResumeStatus(uid);
  const error = queryError ? (queryError as AppError).message : null;
  const result = job?.status === "completed" ? job.result : null;
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
          <Link to={`/resumes/${uid}`} className="btn ghost">
            <ArrowLeft size={16} />
            Back to Resume
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
            <h3 style={{ marginBottom: "var(--space-1)" }}>
              No Review Available
            </h3>
            <p className="small muted" style={{ marginBottom: "var(--space-4)", maxWidth: "80%", margin: "0 auto var(--space-4)" }}>
              AI analysis has not been generated for this resume yet. Reviews are typically available a few minutes after upload.
            </p>
            <Link to={`/resumes/${uid}`} className="btn">View Resume Status</Link>
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
            <Link to={`/resumes/${uid}`} className="btn ghost">
              Back to Resume Details
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
                    color: "rgba(var(--neutral-0-rgb), 0.8)",
                    textTransform: "uppercase",
                    letterSpacing: "var(--tracking-wide)",
                    marginBottom: "4px"
                  }}>
                    Overall Score
                  </p>
                  <p style={{
                    fontSize: "var(--text-base)",
                    color: "rgba(var(--neutral-0-rgb), 0.9)",
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
                  background: "rgba(var(--neutral-0-rgb), 0.15)",
                  backdropFilter: "blur(10px)",
                  borderRadius: "var(--radius-sm)",
                  padding: "var(--space-3)",
                  border: "1px solid rgba(var(--neutral-0-rgb), 0.2)"
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

        {result.review && (
          <FlexColumn gap="var(--space-3)">
            {Object.entries(result.review)
              .filter(([key, value]) => {
                if (key === "overall_score" || key === "summary" || value === null || value === undefined) return false;
                // Check if it's a ReviewFeedback object by looking for feedback properties
                const asFeedback = value as ReviewFeedback;
                return asFeedback.must !== undefined || asFeedback.should !== undefined || asFeedback.advise !== undefined;
              })
              .map(([section, value]) => {
                const feedback = value as ReviewFeedback;
                const mustCount = feedback.must?.length ?? 0;
                const shouldCount = feedback.should?.length ?? 0;
                const adviseCount = feedback.advise?.length ?? 0;
                const totalCount = mustCount + shouldCount + adviseCount;

                if (totalCount === 0) return null;

                const isExpanded = expandedSections.has(section);
                const priorityLevel = mustCount > 0 ? "critical" : shouldCount > 0 ? "important" : "tip";

                const colors = priorityLevel === "critical" ?
                  { must: COLOR_PALETTES.red.dark, should: COLOR_PALETTES.red.medium, advise: COLOR_PALETTES.red.light } :
                  priorityLevel === "important" ?
                  { should: COLOR_PALETTES.orange.dark, advise: COLOR_PALETTES.orange.light } :
                  { advise: COLOR_PALETTES.blue };

                const priorityColor = priorityLevel === "critical" ? COLOR_PALETTES.red.dark.main :
                                     priorityLevel === "important" ? COLOR_PALETTES.orange.dark.main :
                                     COLOR_PALETTES.blue.main;
                const priorityBg = priorityLevel === "critical" ? COLOR_PALETTES.red.dark.bgLight :
                                  priorityLevel === "important" ? COLOR_PALETTES.orange.dark.bgLight :
                                  COLOR_PALETTES.blue.bgLight;

                const ALIGN_CENTER = 14;

                return (
                  <FeedbackSection key={section}>
                    <SectionHeader
                      onClick={() => toggleSection(section)}
                      isExpanded={isExpanded}
                      priorityColor={priorityColor}
                      priorityBg={priorityBg}
                      style={{ padding: "var(--space-3) var(--space-2)" }}
                    >
                      <div style={{ display: "grid", gridTemplateColumns: `${ALIGN_CENTER * 2}px 1fr auto`, alignItems: "center", width: "100%" }}>
                        <div style={{ display: "flex", justifyContent: "center" }}>
                          <PriorityIndicator color={priorityColor} />
                        </div>
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
                        <div style={{
                          width: "32px",
                          height: "32px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          borderRadius: "50%",
                          background: "rgba(var(--neutral-0-rgb), 0.8)",
                          transition: "transform var(--transition-base)",
                          transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)"
                        }}>
                          <ChevronDown size={18} style={{ color: priorityColor }} />
                        </div>
                      </div>
                    </SectionHeader>

                    <div style={{
                      maxHeight: isExpanded ? "800px" : "0",
                      opacity: isExpanded ? 1 : 0,
                      overflow: "hidden",
                      transition: "all var(--transition-base)",
                      paddingTop: isExpanded ? "var(--space-2)" : "0",
                      paddingBottom: isExpanded ? "var(--space-2)" : "0",
                      paddingLeft: "var(--space-2)",
                      paddingRight: "var(--space-2)"
                    }}>
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
                              <div style={{
                                display: "grid",
                                gridTemplateColumns: `${ALIGN_CENTER * 2}px 1fr`,
                                marginBottom: "var(--space-2)"
                              }}>
                                <div style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
                                  <Icon size={18} color={color.main} strokeWidth={2.5} />
                                </div>
                                <span style={{
                                  fontSize: "var(--text-sm)",
                                  fontWeight: 700,
                                  color: color.text,
                                  textTransform: "uppercase",
                                  letterSpacing: "var(--tracking-wide)"
                                }}>
                                  {label}
                                </span>
                              </div>
                              <FlexColumn gap="var(--space-2)">
                                {items.map((item: string, idx: number) => (
                                  <div key={idx} style={{
                                    display: "grid",
                                    gridTemplateColumns: `${ALIGN_CENTER * 2}px 1fr`
                                  }}>
                                    <div style={{ display: "flex", justifyContent: "center", paddingTop: "6px" }}>
                                      <span style={{
                                        width: "6px",
                                        height: "6px",
                                        borderRadius: "50%",
                                        background: color.main,
                                        flexShrink: 0
                                      }} />
                                    </div>
                                    <span style={{
                                      fontSize: "var(--text-sm)",
                                      color: key === "advise" ? "var(--neutral-700)" : "var(--neutral-800)",
                                      lineHeight: "var(--leading-relaxed)"
                                    }}>
                                      {item}
                                    </span>
                                  </div>
                                ))}
                              </FlexColumn>
                            </div>
                          );
                        })}
                    </div>
                  </FeedbackSection>
                );
              })}
          </FlexColumn>
        )}

        {result.review &&
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
