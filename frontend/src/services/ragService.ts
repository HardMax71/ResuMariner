import { apiPost } from '../lib/api';

export type MatchRecommendation = 'strong_fit' | 'moderate_fit' | 'weak_fit';

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
  recommendation: MatchRecommendation;
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

export type QuestionCategory =
  | 'technical_deep_dive'
  | 'behavioral'
  | 'project_architecture'
  | 'problem_solving'
  | 'system_design';

export type SeniorityLevel = 'junior' | 'mid_level' | 'senior' | 'staff_plus';

export interface InterviewQuestion {
  category: QuestionCategory;
  question: string;
  assesses: string;
  follow_ups: string[];
  red_flags: string[];
  good_answer_indicators: string[];
  difficulty_level: SeniorityLevel;
  time_estimate_minutes: number;
}

export interface InterviewQuestionSet {
  candidate_uid: string;
  candidate_name: string;
  candidate_summary: string;
  seniority_level: SeniorityLevel;
  questions: InterviewQuestion[];
  recommended_duration_minutes: number;
  focus_areas: string[];
  preparation_notes: string;
}

export interface ExplainMatchRequest {
  resume_uid: string;
  job_description: string;
}

export interface CompareCandidatesRequest {
  resume_uids: string[];
  criteria?: string[] | null;
  job_context?: string | null;
}

export interface InterviewQuestionsRequest {
  resume_uid: string;
  interview_type?: 'technical' | 'behavioral' | 'general';
  role_context?: string | null;
  focus_areas?: string[] | null;
}

export async function explainMatch(request: ExplainMatchRequest): Promise<JobMatchExplanation> {
  return apiPost<JobMatchExplanation>('/api/v1/rag/explain-match/', request, { timeout: 90000 });
}

export async function compareCandidates(request: CompareCandidatesRequest): Promise<CandidateComparison> {
  return apiPost<CandidateComparison>('/api/v1/rag/compare/', request, { timeout: 120000 });
}

export async function generateInterviewQuestions(request: InterviewQuestionsRequest): Promise<InterviewQuestionSet> {
  return apiPost<InterviewQuestionSet>('/api/v1/rag/interview-questions/', request, { timeout: 90000 });
}
