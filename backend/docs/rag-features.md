# RAG features and how they actually work

## The gap between search and decisions

The search infrastructure was working great. You could find candidates by specific skills, filter by years of experience, run semantic searches to match concepts without needing exact keywords. But then I kept watching people use the system and noticed the same pattern repeating.

Someone would search for candidates, get back a list of matches, and then... copy-paste resume data into ChatGPT. Or spend an hour manually comparing three finalists in a spreadsheet. Or Google generic interview questions because they had no idea what to actually ask this specific person. The search found the candidates, but all the analysis work happened outside the system.

This seemed backward. The infrastructure was already there. Resumes parsed by LLMs into structured data. Embeddings generated for semantic search. Neo4j holding complete candidate profiles. Qdrant storing vectorized resume chunks. Why not use these same components to help with the actual decision-making instead of just returning a list of names?

That's where RAG comes in.

## What RAG actually means

Retrieval-Augmented Generation is one of those terms that sounds more complicated than it is. Break it down: retrieval means pulling relevant data from your databases. Generation means asking an LLM to produce insights based on that data. Augmented just means the LLM isn't making stuff up from its training data, it's working with real information you gave it.

In practice, it's a three-step pattern that shows up everywhere in this system now. First you retrieve the data you need. Then you assemble it into context that an LLM can work with. Finally you generate structured insights by sending that context to the LLM with a carefully designed prompt.

The key difference from regular search is what you get back. Search gives you candidates who match your criteria. RAG gives you analysis of those candidates. Explanations of fit. Structured comparisons. Tailored interview questions. Things that would take a human recruiter thirty minutes to produce, delivered in three seconds.

## The three features I built

### Job match explanation

You've got a resume and a job description. You want to know if they're a good match and why. The naive approach is reading the resume yourself and making a gut decision. The slightly better approach is writing down the job requirements and checking them off against what the candidate has. The RAG approach is letting the system do this analysis systematically.

You send in a resume UID and job description text. The system fetches the complete resume from Neo4j, all the employment history and skills and education. It uses an LLM to parse the job description into structured requirements, pulling out things like required skills, years of experience, seniority level. It computes semantic similarity between the resume and job description using the existing vector embeddings. It figures out which skills overlap and which are missing.

All of this data gets assembled into a context block that looks like a candidate profile on one side and parsed requirements on the other, with analysis in the middle showing matches and gaps. This context goes to the LLM with a system prompt that says "you're a senior technical recruiter, analyze this fit."

What comes back isn't text. It's a Pydantic model called JobMatchExplanation with typed fields. A numeric match score from 0.0 to 1.0. A categorical recommendation of strong fit, moderate fit, or weak fit. A list of 1-5 specific strengths with relevance scores. A list of 0-5 concerns with severity levels and suggested mitigations. An executive summary in 2-3 sentences. Three key discussion points for the interview.

The strengths are concrete things like "8 years Python experience exceeds 5+ requirement" or "Built payment systems at FinTech Corp matching job's fintech focus." The concerns include context, like "No Kubernetes production experience, but transferable Docker skills suggest quick ramp-up." This is what you'd get from a really good recruiter who actually read both the resume and job description carefully.

### Candidate comparison

Once you've narrowed down to a few finalists, you need to pick one. Or at least understand what you're choosing between.

You send in 2-5 resume UIDs plus optional criteria you care about and context about the role. The system fetches all the resumes, computes overlaps between them to see where candidates are similar and where they differ, identifies unique strengths each person brings.

The response is a structured comparison. Each candidate gets scored on four dimensions - technical skills, experience level, domain expertise, and cultural indicators based on things like company types they've worked at and career trajectory. Then there are head-to-head comparisons for specific dimensions. "Python expertise: Alice has 8 years focused on ML pipelines, Bob has 10 years in enterprise backend systems, winner: Bob for breadth but Alice for specialization."
The part I find most useful is scenario-based recommendations. Instead of declaring an overall winner, it acknowledges different candidates fit different needs. One person might be recommended for "immediate impact" because they have tons of relevant experience. Another for "innovation and growth" because they bring cutting-edge skills from a startup background. A third for "team building" because their history shows mentorship and leadership.

Each candidate also gets a risk assessment. Not to disqualify them, but to surface potential challenges. Things like "limited large-scale production experience, may need mentorship on enterprise patterns" or "exclusively enterprise background, might struggle with startup ambiguity." The kind of nuance that matters in actual hiring decisions.

### Interview question generation

You've decided to interview someone. Now you need to prepare questions that actually probe their experience instead of asking generic stuff from a list.

You send in the resume UID plus optionally some context about the role and areas you want to focus on. The system analyzes the resume to infer seniority level based on years of experience, identifies complex projects that would be interesting to discuss, estimates depth in different skill areas based on how much they show up across jobs.
What comes back is 6-12 interview questions tailored to this specific person. Not "Tell me about a time you used Python." More like "You built a recommendation system at StreamCo that served 5M users. Walk me through your approach to the cold start problem and how you measured recommendation quality."

Each question includes what it's assessing (ML system design, metrics-driven thinking), 1-4 follow-up questions to probe deeper, red flags to watch for in their answer (can't explain cold start approach, no mention of A/B testing), indicators of a good answer (discusses specific techniques, references concrete metrics), difficulty level matched to their seniority, and estimated time to discuss it.
The question set also includes a candidate summary, recommended total interview duration, focus areas to emphasize, and preparation notes for the interviewer. Everything you need to run a thoughtful technical interview instead of winging it.

## How the implementation actually works

There's a service called RAGService that lives in the `rag` Django app. It doesn't touch the core search infrastructure at all. Vector search, graph search, hybrid search, all of that stays exactly the same. RAG sits on top as an additional layer that uses the same underlying data sources.

Each RAG feature follows the same pattern. Retrieval first. For job match explanation, that means fetching the resume from Neo4j and potentially doing vector similarity computation between the resume and job description. For candidate comparison, it's fetching multiple resumes and computing overlaps. For interview questions, it's getting the resume and analyzing its structure.

Then comes context assembly. This is where the magic happens, or more accurately, where careful prompt engineering happens. Take all the structured data from retrieval and format it into a context block that gives the LLM everything it needs to make an informed analysis. For job match, that's candidate profile on one side, job requirements on the other, analysis of matches and gaps in the middle. For comparison, it's all the candidate profiles plus computed overlaps and unique strengths. For interview questions, it's the resume with emphasis on complex projects and skill depth.

Finally generation. Send the assembled context to an LLM with a system prompt and get back a structured response. The key is that system prompt and the output schema. The prompt defines the role the LLM should take (senior technical recruiter, experienced hiring manager, technical interviewer) and what kind of analysis to provide. The output schema is a Pydantic model that enforces structure.

This is the same LLMService that powers resume parsing, just used differently. Same circuit breaker logic, same retry handling, same metrics tracking. Just different system prompts and different output types.

## Why structured outputs changed everything

Early experiments used the LLM to generate markdown. The results were sometimes good, sometimes terrible, always unpredictable. Sometimes it would skip sections. Sometimes it would add extra sections. Sometimes it would format lists differently. You couldn't build a UI on top of markdown that might or might not have the fields you need.
`Pydantic-ai` forces structured outputs by defining a Pydantic model as the response type. The LLM has to return data that conforms to that model. If it tries to return something invalid, pydantic-ai catches it during validation and can retry automatically. The frontend gets JSON with guaranteed fields, guaranteed types, guaranteed constraints.

A match score is always a float between 0.0 and 1.0. Strengths are always a list with 1-5 items, each having category, detail, and relevance_score fields. Recommendations are always one of three enum values: `strong_fit`, `moderate_fit`, `weak_fit`. This predictability makes everything downstream trivial. Frontend rendering, caching, testing, API documentation all benefit from knowing exactly what shape the data will have.

It also makes the prompts more effective. When you tell the model "return JobMatchExplanation following this schema," it has a clear target. The model knows it needs to provide 1-5 strengths, that each strength needs a relevance score, that the summary must be 50-500 characters. The constraints help produce better results because the model isn't free-forming, it's filling in a structured template.

## The caching strategy

Every RAG request potentially hits an external LLM API. That costs money and takes time. The solution is aggressive caching backed by Redis.

Job match explanations cache for 24 hours. The reasoning is simple - a resume and job description don't change within a day. If you analyze the same pairing twice, you should get the exact same result. Why pay for another LLM call? The cache key includes both the resume UID and a hash of the job description, so different job descriptions for the same candidate generate different cache keys.

Candidate comparisons cache for only 1 hour. These are more contextual - you might be comparing different sets of candidates, or asking for different criteria, or providing different job context. The comparisons are also more exploratory. People refine their thinking as they use the feature. So shorter TTL makes sense.

Interview questions cache for 7 days. These are expensive to generate because of high output token counts, but they're based solely on resume content. Once you've generated questions for a candidate, those questions remain relevant until you actually interview them. The questions don't depend on job descriptions or comparison context, just the resume itself.

When a resume gets deleted, all cached RAG results for that UID get invalidated. This happens automatically in the deletion flow using cache pattern matching. No separate tracking needed, just a pattern like `*:rag:*:uids:*{uid}*` and delete all matches.

## What this doesn't replace

RAG isn't replacing search. It's augmenting it. You still need search to find candidates in the first place. RAG helps you understand and compare the candidates search surfaces.

It's also not replacing human judgment. The match explanations and comparisons are tools to help hiring managers make informed decisions, not automated hiring systems. A strong_fit recommendation doesn't mean auto-hire. It means this candidate deserves a closer look and here's specifically why.

The interview questions are a starting point for preparation, not a rigid script. Good interviewers adapt based on how the conversation flows. But having specific questions that reference the candidate's actual experience is way better than walking in cold or asking the same generic questions to everyone.

## The response structure

A typical job match explanation is 500-800 tokens of JSON. You get the numeric score, the categorical recommendation, 3-5 strengths with scores, 0-3 concerns with severity and mitigation, a summary, and discussion points.

Candidate comparisons are larger, maybe 1500-2000 tokens when comparing 4-5 people. Scores for each person across multiple dimensions, head-to-head dimension comparisons, scenario recommendations, risk assessments, ranked UIDs.

Interview question sets are the most verbose at 2000-3000 tokens. Each of 6-12 questions includes the question text, what it assesses, follow-ups, red flags, good answer indicators, difficulty level, time estimates. Plus candidate summary, focus areas, prep notes.

All of it is Pydantic-validated structured data. Field types enforced, required fields checked, value ranges validated. If the LLM somehow returns invalid data, the system catches it during deserialization and can retry or fail gracefully instead of passing garbage to the frontend.
