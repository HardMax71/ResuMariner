import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { PageWrapper, PageContainer, GlassCard, FlexColumn, ErrorCard, Spinner } from "../components/styled";
import PageHeader from "../components/PageHeader";
import Badge from "../components/Badge";
import CollapsibleSection from "../components/CollapsibleSection";
import { AlertCircle, MessageCircle, Clock, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { generateInterviewQuestions } from "../services/ragService";

export default function InterviewQuestions() {
  const [searchParams] = useSearchParams();
  const [resumeUid, setResumeUid] = useState("");
  const [interviewType, setInterviewType] = useState<'technical' | 'behavioral' | 'general'>('technical');
  const [roleContext, setRoleContext] = useState('');
  const [focusAreas, setFocusAreas] = useState('');

  useEffect(() => {
    const uidParam = searchParams.get('uid');
    if (uidParam) {
      setResumeUid(uidParam);
    }
  }, [searchParams]);

  const mutation = useMutation({
    mutationFn: generateInterviewQuestions,
  });

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (resumeUid.trim()) {
      mutation.mutate({
        resume_uid: resumeUid.trim(),
        interview_type: interviewType,
        role_context: roleContext.trim() || null,
        focus_areas: focusAreas.trim() ? focusAreas.split(',').map(a => a.trim()).filter(Boolean) : null,
      });
    }
  };

  const result = mutation.data;
  const error = mutation.error;
  const loading = mutation.isPending;

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      technical_deep_dive: 'var(--primary-600)',
      behavioral: 'var(--accent1-600)',
      project_architecture: 'var(--accent2-600)',
      problem_solving: 'var(--accent3-500)',
      system_design: 'var(--accent1-500)'
    };
    return colors[category] || 'var(--neutral-600)';
  };

  const getSeniorityBadge = (level: string) => {
    const colors: Record<string, string> = {
      junior: 'var(--accent1-600)',
      mid_level: 'var(--primary-600)',
      senior: 'var(--accent2-600)',
      staff_plus: 'var(--primary-500)'
    };
    return colors[level] || 'var(--neutral-600)';
  };

  return (
    <PageWrapper>
      <PageContainer>
        <PageHeader title="Interview Questions" />

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
                <label className="label">Interview Type</label>
                <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
                  {(['technical', 'behavioral', 'general'] as const).map(type => (
                    <button
                      key={type}
                      type="button"
                      className="btn"
                      onClick={() => setInterviewType(type)}
                      style={{
                        flex: '1 1 auto',
                        minWidth: 'min(7.5rem, 30%)',
                        textTransform: 'capitalize',
                        backgroundColor: interviewType === type ? 'var(--primary-600)' : 'transparent',
                        color: interviewType === type ? 'white' : 'var(--neutral-700)',
                        border: `1.5px solid ${interviewType === type ? 'var(--primary-600)' : 'var(--neutral-300)'}`,
                        fontWeight: interviewType === type ? '700' : '600',
                        padding: 'clamp(0.5rem, 2vw, 0.75rem) clamp(0.75rem, 3vw, 1rem)',
                        fontSize: 'clamp(var(--text-xs), 3vw, var(--text-sm))',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">Role Context (optional)</label>
                <textarea
                  className="input"
                  placeholder="e.g., Senior Backend Engineer for microservices team"
                  value={roleContext}
                  onChange={(e) => setRoleContext(e.target.value)}
                  rows={3}
                  style={{ resize: 'vertical' }}
                />
              </div>

              <div>
                <label className="label">Focus Areas (optional)</label>
                <textarea
                  className="input"
                  placeholder="e.g., Python, Distributed Systems, Leadership (comma-separated)"
                  value={focusAreas}
                  onChange={(e) => setFocusAreas(e.target.value)}
                  rows={2}
                  style={{ resize: 'vertical' }}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !resumeUid.trim()}
              >
                {loading ? 'Generating...' : 'Generate Questions'}
              </button>
            </FlexColumn>
          </form>
        </GlassCard>

        {error && (
          <ErrorCard>
            <div className="flex align-center gap-2">
              <AlertCircle size={20} />
              <span>{error instanceof Error ? error.message : 'Failed to generate questions'}</span>
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
              <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-3)', flexWrap: 'wrap' }}>
                <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: '700', margin: 0, color: 'var(--neutral-900)' }}>
                  {result.candidate_name}
                </h2>
                <Badge
                  style={{
                    backgroundColor: getSeniorityBadge(result.seniority_level),
                    color: 'white',
                    textTransform: 'capitalize'
                  }}
                >
                  {result.seniority_level.replace('_', ' ')}
                </Badge>
                <Badge variant="primary">
                  <Clock size={14} style={{ marginRight: 'calc(var(--space-1) / 2)' }} />
                  ~{result.recommended_duration_minutes} min
                </Badge>
                <Badge>{result.questions.length} questions</Badge>
              </div>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--neutral-700)', marginBottom: 'var(--space-3)' }}>
                {result.candidate_summary}
              </p>
              {result.focus_areas.length > 0 && (
                <div>
                  <div className="muted small" style={{ marginBottom: 'var(--space-1)' }}>Focus Areas:</div>
                  <div style={{ display: 'flex', gap: 'var(--space-1)', flexWrap: 'wrap', alignItems: 'flex-start' }}>
                    {result.focus_areas.map((area, idx) => (
                      <Badge
                        key={idx}
                        variant="primary"
                        style={{
                          display: 'inline-block',
                          maxWidth: '100%',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                        title={area}
                      >
                        {area}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </GlassCard>

            {result.preparation_notes && (
              <GlassCard style={{ background: 'var(--primary-50)', border: '1px solid var(--primary-200)' }}>
                <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-2)' }}>
                  <MessageCircle size={18} color="var(--primary-600)" />
                  <h3 style={{ fontSize: 'var(--text-base)', fontWeight: '700' }}>Preparation Notes</h3>
                </div>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--neutral-700)' }}>{result.preparation_notes}</p>
              </GlassCard>
            )}

            <FlexColumn gap="var(--space-3)">
              {result.questions.map((q, idx) => (
                <GlassCard key={idx} style={{ padding: 0 }}>
                  <CollapsibleSection
                    title={
                      <div className="flex align-center gap-2" style={{ flex: 1, flexWrap: 'wrap' }}>
                        <span style={{ flex: '1 1 auto', minWidth: '50%' }}>{q.question}</span>
                        <div style={{ display: 'flex', gap: 'var(--space-1)', alignItems: 'center', flexShrink: 0 }}>
                          <Badge
                            style={{
                              backgroundColor: getCategoryColor(q.category),
                              color: 'white',
                              fontSize: 'var(--text-xs)',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {q.category.replace(/_/g, ' ')}
                          </Badge>
                          <Badge variant="primary" style={{ fontSize: 'var(--text-xs)', whiteSpace: 'nowrap' }}>
                            {q.time_estimate_minutes}min
                          </Badge>
                        </div>
                      </div>
                    }
                    defaultOpen={idx === 0}
                    headerStyle={{
                      padding: 'var(--space-3)',
                      borderBottom: '1px solid var(--neutral-200)'
                    }}
                    containerStyle={{
                      background: 'transparent'
                    }}
                  >
                    <div style={{ padding: 'var(--space-3)' }}>
                      <FlexColumn gap="var(--space-2)">
                        <div style={{ fontSize: 'var(--text-sm)', lineHeight: '1.5' }}>
                          <span className="muted small">Assesses:</span> <span style={{ color: 'var(--neutral-700)' }}>{q.assesses}</span>
                        </div>

                    {q.follow_ups.length > 0 && (
                      <div
                        style={{
                          marginLeft: 'calc(-1 * var(--space-3))',
                          marginRight: 'calc(-1 * var(--space-3))',
                          padding: 'var(--space-1) var(--space-3)',
                          background: 'var(--neutral-50)',
                          border: '1px solid var(--neutral-200)',
                          borderRadius: 'var(--radius-sm)'
                        }}
                      >
                        <div style={{ fontSize: 'var(--text-xs)', fontWeight: '600', color: 'var(--neutral-700)', marginBottom: 'var(--space-1)' }}>
                          Follow-up Questions:
                        </div>
                        <FlexColumn gap="var(--space-1)">
                          {q.follow_ups.map((followUp, fidx) => (
                            <div
                              key={fidx}
                              style={{
                                fontSize: 'var(--text-sm)',
                                color: 'var(--neutral-700)',
                                lineHeight: '1.5'
                              }}
                            >
                              {fidx + 1}. {followUp}
                            </div>
                          ))}
                        </FlexColumn>
                      </div>
                    )}

                        <div style={{ display: 'grid', gap: 'var(--space-2)', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 17rem), 1fr))' }}>
                          <div
                            style={{
                              padding: 'var(--space-2)',
                              background: 'var(--accent1-50)',
                              border: '1px solid var(--accent1-200)',
                              borderRadius: 'var(--radius-sm)'
                            }}
                          >
                            <div style={{ fontSize: 'var(--text-xs)', lineHeight: '1.5', marginBottom: 'var(--space-1)' }}>
                              <CheckCircle size={14} color="var(--accent1-600)" style={{ display: 'inline', verticalAlign: 'middle', marginRight: 'calc(var(--space-1) / 2)' }} />
                              <span style={{ fontWeight: '700', color: 'var(--accent1-700)' }}>
                                Good Answer Indicators
                              </span>
                            </div>
                            <FlexColumn gap="var(--space-1)">
                              {q.good_answer_indicators.map((indicator, iidx) => (
                                <div key={iidx} style={{ fontSize: 'var(--text-xs)', color: 'var(--neutral-700)' }}>
                                  • {indicator}
                                </div>
                              ))}
                            </FlexColumn>
                          </div>

                          <div
                            style={{
                              padding: 'var(--space-2)',
                              background: 'var(--accent2-50)',
                              border: '1px solid var(--accent2-200)',
                              borderRadius: 'var(--radius-sm)'
                            }}
                          >
                            <div style={{ fontSize: 'var(--text-xs)', lineHeight: '1.5', marginBottom: 'var(--space-1)' }}>
                              <XCircle size={14} color="var(--accent2-600)" style={{ display: 'inline', verticalAlign: 'middle', marginRight: 'calc(var(--space-1) / 2)' }} />
                              <span style={{ fontWeight: '700', color: 'var(--accent2-700)' }}>
                                Red Flags
                              </span>
                            </div>
                            <FlexColumn gap="var(--space-1)">
                              {q.red_flags.map((flag, ridx) => (
                                <div key={ridx} style={{ fontSize: 'var(--text-xs)', color: 'var(--neutral-700)' }}>
                                  • {flag}
                                </div>
                              ))}
                            </FlexColumn>
                          </div>
                        </div>
                      </FlexColumn>
                    </div>
                  </CollapsibleSection>
                </GlassCard>
              ))}
            </FlexColumn>
          </FlexColumn>
        )}
      </PageContainer>
    </PageWrapper>
  );
}
