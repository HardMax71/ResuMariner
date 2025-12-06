import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { PageWrapper, PageContainer, GlassCard, FlexColumn, FlexRow, ErrorCard, Spinner } from "../components/styled";
import PageHeader from "../components/PageHeader";
import Badge from "../components/Badge";
import { AlertCircle, Users, TrendingUp, Award, X } from "lucide-react";
import { compareCandidates } from "../services/ragService";

export default function CompareCandidates() {
  const [searchParams] = useSearchParams();
  const [candidateUids, setCandidateUids] = useState<string[]>(['', '']);
  const [criteria, setCriteria] = useState('');
  const [jobContext, setJobContext] = useState('');

  useEffect(() => {
    const uidsParam = searchParams.get('uids');
    if (uidsParam) {
      const uids = uidsParam.split(',').filter(Boolean);
      if (uids.length >= 2) {
        setCandidateUids(uids);
      }
    }
  }, [searchParams]);

  const mutation = useMutation({
    mutationFn: compareCandidates,
  });

  const addCandidate = () => {
    if (candidateUids.length < 5) {
      setCandidateUids([...candidateUids, '']);
    }
  };

  const removeCandidate = (index: number) => {
    if (candidateUids.length > 2) {
      setCandidateUids(candidateUids.filter((_, i) => i !== index));
    }
  };

  const updateCandidate = (index: number, value: string) => {
    const updated = [...candidateUids];
    updated[index] = value;
    setCandidateUids(updated);
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validUids = candidateUids.filter(uid => uid.trim());
    if (validUids.length >= 2) {
      mutation.mutate({
        resume_uids: validUids,
        criteria: criteria.trim() ? criteria.split(',').map(c => c.trim()).filter(Boolean) : null,
        job_context: jobContext.trim() || null,
      });
    }
  };

  const result = mutation.data;
  const error = mutation.error;
  const loading = mutation.isPending;

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'var(--accent1-600)';
    if (score >= 6) return 'var(--primary-600)';
    return 'var(--accent2-600)';
  };

  return (
    <PageWrapper>
      <PageContainer>
        <PageHeader title="Compare Candidates" />

        <GlassCard style={{ marginBottom: 'var(--space-4)' }}>
          <form onSubmit={onSubmit}>
            <FlexColumn gap="var(--space-3)">
              <div>
                <div className="flex justify-between" style={{ marginBottom: 'var(--space-2)', alignItems: 'flex-end' }}>
                  <label className="label">Candidate UIDs (2-5)</label>
                  {candidateUids.length < 5 && (
                    <button type="button" className="btn btn-sm" onClick={addCandidate}>
                      + Add Candidate
                    </button>
                  )}
                </div>
                <FlexColumn gap="var(--space-2)">
                  {candidateUids.map((uid, idx) => (
                    <div key={idx} className="flex gap-2">
                      <input
                        type="text"
                        className="input"
                        placeholder={`Candidate ${idx + 1} UID`}
                        value={uid}
                        onChange={(e) => updateCandidate(idx, e.target.value)}
                        style={{ flex: 1 }}
                        required
                      />
                      {candidateUids.length > 2 && (
                        <button
                          type="button"
                          className="btn"
                          onClick={() => removeCandidate(idx)}
                          style={{ padding: '0 12px' }}
                        >
                          <X size={16} />
                        </button>
                      )}
                    </div>
                  ))}
                </FlexColumn>
              </div>

              <div>
                <label className="label">Comparison Criteria (optional)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Python expertise, Leadership, AWS experience (comma-separated)"
                  value={criteria}
                  onChange={(e) => setCriteria(e.target.value)}
                />
              </div>

              <div>
                <label className="label">Job Context (optional)</label>
                <textarea
                  className="input"
                  placeholder="Provide context about the role or team..."
                  value={jobContext}
                  onChange={(e) => setJobContext(e.target.value)}
                  rows={4}
                  style={{ resize: 'vertical' }}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || candidateUids.filter(uid => uid.trim()).length < 2}
              >
                {loading ? 'Comparing...' : 'Compare Candidates'}
              </button>
            </FlexColumn>
          </form>
        </GlassCard>

        {error && (
          <ErrorCard>
            <div className="flex align-center gap-2">
              <AlertCircle size={20} />
              <span>{(error as Error).message}</span>
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
              <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-3)' }}>
                <Users size={20} color="var(--primary-600)" />
                <h3 className="card-title">Executive Summary</h3>
              </div>
              <p style={{ fontSize: 'var(--text-base)', lineHeight: '1.6', color: 'var(--neutral-700)' }}>
                {result.executive_summary}
              </p>
            </GlassCard>

            <GlassCard>
              <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-3)' }}>
                <TrendingUp size={20} color="var(--primary-600)" />
                <h3 className="card-title">Overall Scores</h3>
              </div>
              <div style={{ display: 'grid', gap: 'var(--space-3)', gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 17rem), 1fr))' }}>
                {result.scores.map((score) => (
                  <div
                    key={score.uid}
                    style={{
                      padding: 'var(--space-3)',
                      background: 'var(--neutral-50)',
                      borderRadius: 'var(--radius-xs)'
                    }}
                  >
                    <div className="flex align-center justify-between" style={{ marginBottom: 'var(--space-2)' }}>
                      <h4 style={{ fontSize: 'var(--text-base)', fontWeight: '700', color: 'var(--neutral-900)' }}>
                        {score.name}
                      </h4>
                      <div style={{
                        fontSize: 'var(--text-2xl)',
                        fontWeight: '800',
                        color: getScoreColor(score.overall_score),
                        fontFamily: 'var(--font-display)'
                      }}>
                        {score.overall_score.toFixed(1)}
                      </div>
                    </div>
                    <FlexColumn gap="var(--space-1)">
                      <ScoreStat label="Technical" value={score.technical_skills} />
                      <ScoreStat label="Experience" value={score.experience_level} />
                      <ScoreStat label="Domain" value={score.domain_expertise} />
                      <ScoreStat label="Cultural Fit" value={score.cultural_indicators} />
                    </FlexColumn>
                  </div>
                ))}
              </div>
            </GlassCard>

            {result.dimension_comparisons.length > 0 && (
              <GlassCard>
                <h3 className="card-title" style={{ marginBottom: 'var(--space-3)' }}>
                  Dimension Comparisons
                </h3>
                <FlexColumn gap="var(--space-3)">
                  {result.dimension_comparisons.map((dim, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--space-3)',
                        background: 'var(--primary-50)',
                        border: '1px solid var(--primary-200)',
                        borderRadius: 'var(--radius-xs)'
                      }}
                    >
                      <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-2)' }}>
                        <h4 style={{ fontSize: 'var(--text-base)', fontWeight: '700' }}>{dim.dimension}</h4>
                        <Badge variant="success" style={{ marginLeft: 'auto' }}>
                          Winner: {result.scores.find(s => s.uid === dim.winner)?.name || dim.winner}
                        </Badge>
                      </div>
                      <FlexColumn gap="var(--space-2)">
                        {Object.entries(dim.candidates).map(([key, value]) => {
                          const isValueUid = value.length === 36 && value.includes('-');
                          const uid = isValueUid ? value : key;
                          const assessment = isValueUid ? key : value;
                          const candidateName = result.scores.find(s => s.uid === uid)?.name;

                          if (!candidateName) return null;

                          return (
                            <div key={uid} style={{ fontSize: 'var(--text-sm)', color: 'var(--neutral-700)' }}>
                              <span style={{ fontWeight: '600' }}>
                                {candidateName}:
                              </span>{' '}
                              {assessment}
                            </div>
                          );
                        })}
                      </FlexColumn>
                      <p style={{
                        fontSize: 'var(--text-sm)',
                        color: 'var(--neutral-600)',
                        marginTop: 'var(--space-2)',
                        fontStyle: 'italic'
                      }}>
                        {dim.analysis}
                      </p>
                    </div>
                  ))}
                </FlexColumn>
              </GlassCard>
            )}

            {result.recommendations.length > 0 && (
              <GlassCard>
                <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-3)' }}>
                  <Award size={20} color="var(--accent1-600)" />
                  <h3 className="card-title">Recommendations by Scenario</h3>
                </div>
                <FlexColumn gap="var(--space-2)">
                  {result.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 'var(--space-3)',
                        background: 'var(--accent1-50)',
                        border: '1px solid var(--accent1-200)',
                        borderRadius: 'var(--radius-xs)'
                      }}
                    >
                      <div className="flex align-center gap-2" style={{ marginBottom: 'var(--space-1)' }}>
                        <Badge style={{ backgroundColor: 'var(--accent1-600)', color: 'white' }}>
                          {rec.scenario}
                        </Badge>
                        <span style={{ fontSize: 'var(--text-base)', fontWeight: '700', color: 'var(--accent1-700)' }}>
                          {rec.recommended_name}
                        </span>
                      </div>
                      <p style={{ fontSize: 'var(--text-sm)', color: 'var(--neutral-700)' }}>{rec.rationale}</p>
                    </div>
                  ))}
                </FlexColumn>
              </GlassCard>
            )}

            {result.risk_assessment.length > 0 && (
              <GlassCard>
                <h3 className="card-title" style={{ marginBottom: 'var(--space-3)' }}>
                  Risk Assessment
                </h3>
                <FlexColumn gap="var(--space-2)">
                  {result.risk_assessment.map((assessment) => (
                    <div
                      key={assessment.uid}
                      style={{
                        padding: 'var(--space-2) var(--space-3)',
                        background: 'var(--accent2-50)',
                        border: '1px solid var(--accent2-200)',
                        borderRadius: 'var(--radius-xs)',
                        fontSize: 'var(--text-sm)',
                        color: 'var(--neutral-700)'
                      }}
                    >
                      <span style={{ fontWeight: '700' }}>
                        {result.scores.find(s => s.uid === assessment.uid)?.name}:
                      </span>{' '}
                      {assessment.risk}
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

function ScoreStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex align-center justify-between" style={{ fontSize: 'var(--text-sm)' }}>
      <span className="muted">{label}</span>
      <span style={{ fontWeight: '600', color: 'var(--neutral-700)' }}>{value.toFixed(1)}/10</span>
    </div>
  );
}
