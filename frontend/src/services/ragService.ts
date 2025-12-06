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
