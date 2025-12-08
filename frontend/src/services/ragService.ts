import {
  v1RagExplainMatchCreate,
  v1RagCompareCreate,
  v1RagInterviewQuestionsCreate,
  type ExplainMatchRequest,
  type CompareCandidatesRequest,
  type InterviewQuestionsRequest,
  type JobMatchExplanation,
  type CandidateComparison,
  type InterviewQuestionSet,
} from '../api/client';

export type { JobMatchExplanation, CandidateComparison, InterviewQuestionSet };

export async function explainMatch(request: ExplainMatchRequest): Promise<JobMatchExplanation> {
  const { data, error } = await v1RagExplainMatchCreate({ body: request });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}

export async function compareCandidates(request: CompareCandidatesRequest): Promise<CandidateComparison> {
  const { data, error } = await v1RagCompareCreate({ body: request });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}

export async function generateInterviewQuestions(request: InterviewQuestionsRequest): Promise<InterviewQuestionSet> {
  const { data, error } = await v1RagInterviewQuestionsCreate({ body: request });
  if (error || !data) throw new Error(error ? String(error) : 'No data returned');
  return data;
}
