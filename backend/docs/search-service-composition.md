# Why search services return different types (and why that's correct)

## The "they should all be the same!" trap

When I first built out the search architecture, I had this nagging feeling that something was "wrong" with my design.

`VectorSearchService` returns `list[VectorHit]`, but `GraphSearchService` and `HybridSearchService` both return `list[ResumeSearchResult]`.

My brain kept screaming "INCONSISTENCY! BAD DESIGN! THEY SHOULD ALL RETURN THE SAME TYPE!"

I mean, it made sense on the surface. If they all returned the same type, I could wrap them, decorate them, swap them out easily. Classic Gang of Four stuff, right? The services would be perfectly composable and follow the Liskov Substitution Principle or whatever.

So I tried it. And it was an absolute disaster.

## What happens when you force uniformity

Here's what happened when I tried to make `VectorSearchService.search()` return `list[ResumeSearchResult]`:

```python
class VectorSearchService:
    def __init__(self, graph_service: GraphSearchService):  # Wait, what?
        self.qdrant = AsyncQdrantClient(...)
        self.graph = graph_service  # Ugh, tight coupling already

    async def search(...) -> list[ResumeSearchResult]:
        # Step 1: Search Qdrant for matching chunks
        points = await self.qdrant.query_points(...)

        # Step 2: Now I need to fetch complete resumes from Neo4j
        uids = [point.payload["uid"] for point in points]
        resumes = await self.graph.get_resumes_by_ids(uids)  # Calling another service!

        return resumes
```

**Problems immediately:**

1. **VectorSearchService now depends on GraphSearchService** - So much for separation of concerns
2. **Can't use vector search as a building block anymore** - It's doing too much
3. **Performance tank** - Every vector search triggers a Neo4j query, even when I don't need full resume data
4. **Circular dependency risk** - If GraphSearch ever needs VectorSearch, we're screwed
5. **Violates Single Responsibility** - Vector service is now responsible for both vector search AND graph enrichment

The kicker? I still needed a way to get just the vector chunks for hybrid search, so I ended up adding a `search_raw()` method that returned `list[VectorHit]` anyway. So I didn't even eliminate the different return types - I just made the API uglier.

## What these services actually represent

Here's what finally clicked for me: **these services operate at different levels of abstraction.**

### VectorSearchService: The primitive

This is a **low-level building block**. It searches text chunks stored in Qdrant and returns matches:

```python
VectorHit(
    uid="resume-123",              # Which resume this came from
    text="Built Python microservices using FastAPI and Redis",
    score=0.87,                     # Semantic similarity
    source="job_experience",        # What part of the resume
    context="Senior Backend Engineer at TechCorp"
)
```

**What it CANNOT provide:**
- The person's name (not stored in Qdrant)
- Their email address (not in Qdrant)
- Complete work history (that's in Neo4j)
- Education details (also in Neo4j)
- Total years of experience (calculated from Neo4j data)

It's a chunk of text that matched the query. That's it. Asking it to return a complete `ResumeSearchResult` is like asking a dictionary to also fetch definitions from Wikipedia. It's just not its job.

### GraphSearchService/HybridSearchService: The composites

These are **high-level operations** that return complete, ready-to-display results:

```python
ResumeSearchResult(
    uid="resume-123",
    name="Jane Smith",                  # From Neo4j
    email="jane@example.com",           # From Neo4j
    score=0.92,
    matches=[VectorHit, VectorHit],     # Embedded vector hits
    summary="Senior engineer with...",  # From Neo4j
    skills=["Python", "Redis", ...],    # From Neo4j
    experiences=[{...}, {...}],         # From Neo4j
    education=[{...}],                  # From Neo4j
    years_experience=8,                 # Calculated from Neo4j
    location={"country": "USA", ...},   # From Neo4j
)
```

These services know how to orchestrate multiple data sources and return everything a frontend needs to display a search result.

## How they actually compose (and why it works)

The magic happens in `SearchCoordinator`. It's a **facade** that knows how to compose the low-level primitives into high-level operations:

### Semantic search: Vector → Graph enrichment

```python
async def _semantic_search(self, request: SearchRequest):
    # Step 1: Low-level vector search (returns chunks)
    vector_hits = await self.vector_search.search(
        query_vector=query_vector,
        limit=request.limit * 5,  # Over-fetch for grouping
    )
    # Returns: list[VectorHit]

    # Step 2: Group hits by resume UID
    grouped = self._group_vector_hits_by_uid(vector_hits)

    # Step 3: Fetch complete resume data from Neo4j
    uids = list(grouped.keys())
    complete_resumes = await self.graph_search.get_resumes_by_ids(uids)
    # Returns: list[ResumeSearchResult]

    # Step 4: Attach vector matches to resumes
    for uid, hits in grouped.items():
        resume = resume_map[uid]
        resume.matches = hits[:max_matches]
        resume.score = max(hit.score for hit in hits)

    return results  # list[ResumeSearchResult]
```

**This is good composition.** VectorSearch does its one job (find matching chunks), GraphSearch does its one job (fetch complete resume data), and SearchCoordinator orchestrates them.

### Hybrid search: Graph → Vector within candidates → Enrichment

```python
async def _hybrid_search(self, request: SearchRequest):
    # Step 1: Get candidate UIDs from structured filters
    graph_results = await self.graph_search.search(
        filters=request.filters,
        limit=limit * 3,
    )
    # Returns: list[ResumeSearchResult]

    candidate_uids = [r.uid for r in graph_results]

    # Step 2: Vector search ONLY within those candidates
    vector_hits = await self.vector_search.search(
        query_vector=query_vector,
        candidate_uids=candidate_uids,  # Pre-filter!
    )
    # Returns: list[VectorHit]

    # Step 3: Group and enrich (same as semantic search)
    grouped = self._group_by_uid(vector_hits)
    uids = list(grouped.keys())
    complete_resumes = await self.graph_search.get_resumes_by_ids(uids)

    # Attach matches, sort by semantic score
    return enriched_results  # list[ResumeSearchResult]
```

**This is also good composition.** We use graph search to pre-filter candidates, then use vector search as a building block to rank them semantically.

If `VectorSearchService.search()` returned `list[ResumeSearchResult]`, we couldn't do this pre-filtering because the service would have already fetched all the resume data before we could tell it "only search these specific UIDs."

## The architecture diagram that finally made sense

```
┌─────────────────────────────────────────────────┐
│       SearchCoordinator (Facade)                │  ← High-level API
│  Returns: list[ResumeSearchResult]              │
│                                                 │
│  Knows how to:                                  │
│  • Semantic: Vector → Enrich with Neo4j         │
│  • Structured: Graph only                       │
│  • Hybrid: Graph filter → Vector rank → Enrich  │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────────┬──────────────────────┐
        ▼                           ▼                      ▼
┌─────────────────┐      ┌─────────────────┐   ┌──────────────────┐
│ VectorSearch    │      │ GraphSearch     │   │ HybridSearch     │
│ Service         │      │ Service         │   │ Service          │
├─────────────────┤      ├─────────────────┤   ├──────────────────┤
│ PRIMITIVE       │      │ COMPOSITE       │   │ COMPOSITE        │
│                 │      │                 │   │                  │
│ Returns:        │      │ Returns:        │   │ Returns:         │
│ list[VectorHit] │      │ list[Resume]    │   │ list[Resume]     │
│                 │      │                 │   │                  │
│ Does:           │      │ Does:           │   │ Does:            │
│ • Text chunks   │      │ • Filter Neo4j  │   │ • Compose both   │
│ • Semantic sim  │      │ • Full data     │   │ • Hard filtering │
└─────────────────┘      └─────────────────┘   └──────────────────┘
        │                        │
        ▼                        ▼
     [Qdrant]                 [Neo4j]
```

The types reflect the abstraction levels. It's not inconsistency - it's intentional layering.

## What I learned about abstraction boundaries

**Different return types are fine if services operate at different abstraction levels.**

VectorSearchService is like a `SELECT` statement in SQL - it returns raw data rows. 
GraphSearchService is like a view with joins - it returns complete, enriched records. 
You wouldn't complain that a SELECT and a VIEW have different return types.

The key insight: **composability doesn't require identical types**. It requires **clear contracts and sensible boundaries**.

VectorSearch's contract: "Give me a query vector, I'll return matching text chunks"
GraphSearch's contract: "Give me filters or UIDs, I'll return complete resumes"
HybridSearch's contract: "Give me a query + filters, I'll return semantically ranked filtered resumes"

These contracts are **complementary**, not **conflicting**.

## What would actually break composition

You know what would REALLY break composition? Having methods with unpredictable side effects:

```python
# BAD: Saves to database as a side effect
async def search(...) -> list[ResumeSearchResult]:
    results = await self._search_internal(...)
    await self._cache_results(results)  # Surprise! I'm writing to Redis!
    await self._log_analytics(results)  # And to the analytics DB!
    return results
```

Or having brittle coupling:

```python
# BAD: Expects exact initialization order
class SearchCoordinator:
    def __init__(self):
        self.graph = GraphSearchService()
        self.vector = VectorSearchService(self.graph)  # Must pass graph!
        self.hybrid = HybridSearchService(self.vector, self.graph)  # Must pass both!
```

My services don't do either of these things. They're **pure**, **explicit**, and have **minimal dependencies**.

## The alternatives I considered

### Option 1: Interface/Protocol with multiple methods

```python
class SearchService(Protocol):
    async def search_raw(...) -> list[VectorHit]: ...
    async def search_enriched(...) -> list[ResumeSearchResult]: ...
```

This unifies the interface but makes every service implement methods it might not need. 
VectorSearchService would have an empty `search_enriched()` that just raises `NotImplementedError`. 
Seems worse than just accepting different return types.

### Option 2: Generic return type

```python
class SearchService(Generic[T]):
    async def search(...) -> list[T]: ...

class VectorSearchService(SearchService[VectorHit]): ...
class GraphSearchService(SearchService[ResumeSearchResult]): ...
```

This is technically elegant but adds complexity for zero benefit. The services still return different types - we're just hiding it behind generics. 
And now every caller has to deal with type variables.

### Option 3: Adapter pattern

```python
class VectorToResumeAdapter:
    def __init__(self, vector_service, graph_service):
        ...

    async def search(...) -> list[ResumeSearchResult]:
        hits = await vector_service.search(...)
        return await self._enrich(hits)
```

This is basically what SearchCoordinator already does! Why create a separate adapter when the coordinator naturally handles composition?

## When uniformity actually matters

I'm not saying different types are always fine. There are cases where uniformity matters:

**Multiple implementations of the same abstraction:**
- Different embedding providers (OpenAI, Cohere, Anthropic) should all return the same embedding format
- Different PDF parsers should all return the same document structure
- Different LLM providers should have identical interfaces

**Swappable strategies:**
- Multiple ranking algorithms
- Different caching strategies
- Various retry policies

But VectorSearchService and GraphSearchService aren't multiple implementations of the same thing - they're **fundamentally different operations** that happen to both involve searching resumes.

## The real lesson

**Don't force uniformity for the sake of uniformity.**

Yes, uniform interfaces make some patterns easier (Strategy, Decorator, Factory). 
But forcing everything into the same mold can make your code worse, not better.

Sometimes the right answer is: "These things are different, and that's okay."

My search services have different return types because they do different things at different levels of abstraction. 
The VectorSearchService is a primitive building block. The GraphSearchService and HybridSearchService are high-level operations. 
They compose beautifully through SearchCoordinator without needing identical signatures.

And you know what? The code is clearer for it. When I see `list[VectorHit]` I know I'm working with raw chunks. 
When I see `list[ResumeSearchResult]` I know I have complete, displayable data. The types tell the story of what the code does.

---

**TL;DR:** VectorSearchService returns chunks because it searches chunks. GraphSearchService returns resumes because it fetches resumes. They compose via SearchCoordinator. Forcing them to return the same type would make the code worse, not better. Different abstractions, different types - and that's fine.
