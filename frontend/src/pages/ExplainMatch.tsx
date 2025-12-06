import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { PageWrapper, PageContainer, GlassCard, FlexColumn, ErrorCard, Spinner } from "../components/styled";
import PageHeader from "../components/PageHeader";
import Badge from "../components/Badge";
import { AlertCircle, CheckCircle, AlertTriangle, TrendingUp, MessageCircle, Lightbulb, XCircle } from "lucide-react";
import { explainMatch, type JobMatchExplanation } from "../services/ragService";
import type { AppError } from "../lib/api";

export default function ExplainMatch() {
  const [searchParams] = useSearchParams();
  const [resumeUid, setResumeUid] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  useEffect(() => {
    const uidParam = searchParams.get('uid');
    if (uidParam) {
      setResumeUid(uidParam);
    }
  }, [searchParams]);

  const mutation = useMutation({
    mutationFn: explainMatch,
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (resumeUid.trim() && jobDescription.trim()) {
      mutation.mutate({ resume_uid: resumeUid.trim(), job_description: jobDescription.trim() });
    }
  };

  const result = mutation.data;
  const error = mutation.error;
  const loading = mutation.isPending;

  const getRecommendationColor = (rec: string) => {
    if (rec === 'strong_fit') return 'var(--accent1-600)';
    if (rec === 'moderate_fit') return 'var(--primary-600)';
    return 'var(--accent2-600)';
  };

  const getRecommendationIcon = (rec: string) => {
    if (rec === 'strong_fit') return CheckCircle;
    if (rec === 'moderate_fit') return TrendingUp;
    return AlertTriangle;
  };

  return (
    <PageWrapper>
      <PageContainer>
        <PageHeader title="Job Match Explanation" />

        <GlassCard style={{ marginBottom: 'var(--space-4)' }}>
          <form onSubmit={onSubmit}>
            <FlexColumn gap="var(--space-3)">
              <div>
                <label className="label">Resume UID</label>
                <input
                  type="text"
                  className="input"
                  placeholder="Enter resume UID"
                  value={resumeUid}
                  onChange={(e) => setResumeUid(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="label">Job Description</label>
                <textarea
                  className="input"
                  placeholder="Paste job description here (minimum 50 characters)..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={8}
                  required
                  style={{ resize: 'vertical', minHeight: '120px' }}
                />
                <div className="muted small" style={{ marginTop: 'var(--space-1)' }}>
                  {jobDescription.length} characters
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !resumeUid.trim() || jobDescription.trim().length < 50}
              >
                {loading ? 'Analyzing...' : 'Explain Match'}
              </button>
            </FlexColumn>
          </form>
        </GlassCard>

        {error && (
          <ErrorCard>
            <div className="flex align-center gap-2">
              <AlertCircle size={20} />
              <span>{(error as AppError).message}</span>
            </div>
          </ErrorCard>
        )}

        {loading && (
          <GlassCard style={{ display: 'flex', justifyContent: 'center', padding: 'var(--space-8)' }}>
            <Spinner />
          </GlassCard>
        )}

        {result && (
          <FlexColumn gap="var(--space-4)">
            <GlassCard>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', marginBottom: 'var(--space-3)' }}>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <div style={{
                    fontSize: 'var(--text-5xl)',
                    fontWeight: '800',
                    color: getRecommendationColor(result.recommendation),
                    fontFamily: 'var(--font-display)',
                    lineHeight: 1
                  }}>
                    {Math.round(result.match_score * 100)}%
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 'var(--space-1)'
                }}>
                  <div className="flex align-center gap-2">
                    {(() => {
                      const Icon = getRecommendationIcon(result.recommendation);
                      return <Icon size={20} color={getRecommendationColor(result.recommendation)} />;
                    })()}
                    <span style={{
                      fontSize: 'var(--text-lg)',
                      fontWeight: '700',
                      color: getRecommendationColor(result.recommendation),
                      textTransform: 'capitalize'
                    }}>
                      {result.recommendation.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="muted">Overall Match Score</div>
                </div>
              </div>
              <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--neutral-700)' }}>
                {result.summary}
              </p>
            </GlassCard>

            {(result.strengths.length > 0 || result.concerns.length > 0) && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 18rem), 1fr))',
                gap: 'var(--space-4)',
                alignItems: 'stretch'
              }}>
                {result.strengths.length > 0 && (
                  <GlassCard style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <h3 className="card-title" style={{ marginBottom: 'var(--space-3)' }}>
                      Key Strengths ({result.strengths.length})
                    </h3>
                    <FlexColumn gap="var(--space-2)">
                      {result.strengths.map((strength, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: 'var(--space-2)',
                            background: 'var(--accent1-50)',
                            border: '1px solid var(--accent1-200)',
                            borderRadius: 'var(--radius-sm)'
                          }}
                        >
                          <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-2)' }}>
                            <Badge style={{
                              backgroundColor: 'var(--accent1-600)',
                              color: 'white',
                              fontSize: 'var(--text-xs)'
                            }}>
                              {strength.category}
                            </Badge>
                            <span
                              style={{
                                marginLeft: 'auto',
                                color: 'var(--accent1-700)',
                                fontSize: 'var(--text-xs)',
                                fontWeight: '600',
                                fontFamily: 'var(--font-display)'
                              }}
                            >
                              {Math.round(strength.relevance_score * 100)}%
                            </span>
                          </div>
                          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--neutral-700)', margin: 0, lineHeight: '1.5' }}>{strength.detail}</p>
                        </div>
                      ))}
                    </FlexColumn>
                  </GlassCard>
                )}

                {result.concerns.length > 0 && (
                  <GlassCard style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <h3 className="card-title" style={{ marginBottom: 'var(--space-3)' }}>
                      Concerns ({result.concerns.length})
                    </h3>
                    <FlexColumn gap="var(--space-2)">
                      {result.concerns.map((concern, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: 'var(--space-2)',
                            background: 'var(--accent2-50)',
                            border: '1px solid var(--accent2-200)',
                            borderRadius: 'var(--radius-sm)'
                          }}
                        >
                          <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-2)' }}>
                            <Badge style={{
                              backgroundColor: 'var(--accent2-600)',
                              color: 'white',
                              fontSize: 'var(--text-xs)'
                            }}>
                              {concern.category}
                            </Badge>
                            <Badge
                              style={{
                                backgroundColor:
                                  concern.severity === 'critical' ? 'var(--accent2-600)' :
                                  concern.severity === 'moderate' ? 'var(--accent1-500)' :
                                  'var(--neutral-500)',
                                color: 'white',
                                fontWeight: '600',
                                fontSize: 'var(--text-xs)'
                              }}
                            >
                              {concern.severity}
                            </Badge>
                          </div>
                          <p style={{
                            fontSize: 'var(--text-sm)',
                            color: 'var(--neutral-700)',
                            margin: 0,
                            marginBottom: concern.mitigation ? 'var(--space-2)' : 0,
                            lineHeight: '1.5'
                          }}>
                            {concern.detail}
                          </p>
                          {concern.mitigation && (
                            <div style={{
                              display: 'flex',
                              gap: 'var(--space-1)',
                              fontSize: 'var(--text-sm)',
                              color: 'var(--neutral-600)',
                              padding: 'var(--space-1)',
                              background: 'var(--neutral-50)',
                              borderRadius: 'var(--radius-sm)',
                              alignItems: 'flex-start'
                            }}>
                              <Lightbulb size={14} style={{ flexShrink: 0, marginTop: '1px', color: 'var(--accent1-500)' }} />
                              <span style={{ lineHeight: '1.5' }}>{concern.mitigation}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </FlexColumn>
                  </GlassCard>
                )}
              </div>
            )}

            {result.key_discussion_points.length > 0 && (
              <GlassCard>
                <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-3)' }}>
                  <MessageCircle size={20} color="var(--primary-600)" />
                  <h3 className="card-title">Interview Discussion Points</h3>
                </div>
                <FlexColumn gap="var(--space-2)">
                  {result.key_discussion_points.map((point, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--space-2) var(--space-3)',
                        background: 'var(--primary-50)',
                        border: '1px solid var(--primary-200)',
                        borderRadius: 'var(--radius-xs)',
                        fontSize: 'var(--text-sm)',
                        color: 'var(--neutral-700)'
                      }}
                    >
                      <span style={{ fontWeight: '600', marginRight: 'var(--space-2)' }}>{idx + 1}.</span>
                      {point}
                    </div>
                  ))}
                </FlexColumn>
              </GlassCard>
            )}
          </FlexColumn>
        )}
      </PageContainer>
    </PageWrapper>
  );
}
