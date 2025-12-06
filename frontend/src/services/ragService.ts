import {
  v1RagExplainMatchCreate,
  v1RagCompareCreate,
  v1RagInterviewQuestionsCreate,
  type ExplainMatchRequest,
  type CompareCandidatesRequest,
  type InterviewQuestionsRequest,
} from '../api/client';

export interface MatchStrength {
  category: string;
  detail: string;
  relevance_score: number;
}

export interface MatchConcern {
  category: string;
  detail: string;
  severity: 'critical' | 'moderate' | 'minor';
  mitigation?: string | null;
}

export interface JobMatchExplanation {
  match_score: number;
  recommendation: 'strong_fit' | 'moderate_fit' | 'weak_fit';
  strengths: MatchStrength[];
  concerns: MatchConcern[];
  summary: string;
  key_discussion_points: string[];
}

export interface CandidateScore {
  uid: string;
  name: string;
  technical_skills: number;
  experience_level: number;
  domain_expertise: number;
  cultural_indicators: number;
  overall_score: number;
}

export interface DimensionComparison {
  dimension: string;
  candidates: Record<string, string>;
  winner: string;
  analysis: string;
}

export interface ComparisonRecommendation {
  scenario: string;
  recommended_uid: string;
  recommended_name: string;
  rationale: string;
}

export interface RiskAssessment {
  uid: string;
  risk: string;
}

export interface CandidateComparison {
  executive_summary: string;
  scores: CandidateScore[];
  dimension_comparisons: DimensionComparison[];
  recommendations: ComparisonRecommendation[];
  risk_assessment: RiskAssessment[];
  ranked_uids: string[];
}

export interface InterviewQuestion {
  category: 'technical_deep_dive' | 'behavioral' | 'project_architecture' | 'problem_solving' | 'system_design';
  question: string;
  assesses: string;
  follow_ups: string[];
  red_flags: string[];
  good_answer_indicators: string[];
  difficulty_level: 'junior' | 'mid_level' | 'senior' | 'staff_plus';
  time_estimate_minutes: number;
}

export interface InterviewQuestionSet {
  candidate_uid: string;
  candidate_name: string;
  candidate_summary: string;
  seniority_level: 'junior' | 'mid_level' | 'senior' | 'staff_plus';
  questions: InterviewQuestion[];
  recommended_duration_minutes: number;
  focus_areas: string[];
  preparation_notes: string;
}

export async function explainMatch(request: ExplainMatchRequest): Promise<JobMatchExplanation> {
  const { data, error } = await v1RagExplainMatchCreate({ body: request });
  if (error) throw new Error(String(error));
  return data as JobMatchExplanation;
}

export async function compareCandidates(request: CompareCandidatesRequest): Promise<CandidateComparison> {
  const { data, error } = await v1RagCompareCreate({ body: request });
  if (error) throw new Error(String(error));
  return data as CandidateComparison;
}

export async function generateInterviewQuestions(request: InterviewQuestionsRequest): Promise<InterviewQuestionSet> {
  const { data, error } = await v1RagInterviewQuestionsCreate({ body: request });
  if (error) throw new Error(String(error));
  return data as InterviewQuestionSet;
}
