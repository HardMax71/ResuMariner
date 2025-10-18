# Rate limiting and API protection

## Why this matters

When I first deployed this system, I naively assumed people would use it reasonably. 
Upload a resume, maybe run a few searches, move on with their day. 
'Then I looked at the actual operations happening behind each API call and realized how catastrophically wrong I was.

Every time someone uploads a resume, the system kicks off a chain reaction. 
First there's file parsing, which for images means calling out to OpenAI's vision model to do OCR. 
Then the worker picks up the job and sends the entire parsed resume to Claude or GPT to extract structured data. After that, it generates embeddings for every single section of the resume - sometimes 20 or 30 API calls to OpenAI's embedding service. All of this hits external APIs that charge per request and have their own rate limits.

A single resume upload can easily burn through 50 API calls and cost anywhere from $0.10 to $0.50 depending on the file format and content length. 
Without rate limiting, someone could write a simple script to spam the upload endpoint and rack up thousands of dollars in API costs in an afternoon. Not theoretical costs - actual money flowing out of the bank account.

Search isn't quite as expensive, but it's not free either. 
Every semantic search query gets embedded through OpenAI's API before hitting Qdrant. 
Even structured searches are hitting Neo4j with complex Cypher queries that can get expensive at scale. Someone running searches in a tight loop could easily overwhelm the system.

## How I'm handling it

Django REST Framework has built-in throttling that's perfect for this. It tracks requests by IP address and enforces limits without requiring any external dependencies. The configuration lives in settings.py and looks like this:

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/hour",
        "upload": "10/hour",
        "search": "100/hour",
    },
}
```

The general anonymous rate limit is set to 1000 requests per hour, which covers all the lightweight endpoints like fetching job status or getting configuration info. This is generous enough that normal users will never hit it, but prevents someone from completely hammering the API.

For uploads, I went conservative at 10 per hour. This is where the expensive LLM operations happen, so I wanted to be careful. Ten resumes an hour is more than enough for any legitimate use case - even a busy recruiter isn't processing resumes at that pace. But it completely shuts down abuse attempts.

Search gets 100 requests per hour, which feels about right. Someone doing real work might run 20 or 30 searches while refining their query, but 100 searches in an hour suggests automated abuse rather than human use.

## The technical implementation

DRF's throttling works by checking request metadata against stored counters. For anonymous users, it uses the IP address as the key. When a request comes in, the framework increments the counter for that IP and checks if they've exceeded their limit for the current time window.

The neat thing is that this uses whatever cache backend Django is configured with. Since Redis is already in the stack for job queuing, DRF automatically uses it for throttle tracking too. No extra infrastructure needed.

When someone hits their rate limit, they get back a 429 status code with a clear error message that includes how long they need to wait. The response headers also include X-RateLimit-Remaining so clients can see how many requests they have left before hitting the limit.

I'm using scoped throttling for the expensive endpoints. This means the upload endpoint and search endpoints each have their own independent limits. Someone can't burn through their upload quota by running searches, and vice versa. Each scope tracks separately but both enforce their limits strictly.

## Configuring the limits

The rates are easy to adjust based on actual usage patterns. The format is straightforward - a number followed by a slash and a time unit. "10/hour" means 10 requests per hour. "5/minute" would be 5 per minute. "1000/day" would be a daily limit.

I went with hourly limits because they feel natural for this kind of API. Daily limits are too coarse - someone could blast through their entire quota in the first few minutes and then be locked out for 23 hours. Per-minute limits are too fine-grained and would catch legitimate burst usage.

If the system sees heavier usage than expected, I can bump these numbers up without changing any code. Just update settings.py and restart. Going the other way works too - if abuse becomes a problem, I can tighten the limits immediately.

## What gets throttled

Resume uploads are the most heavily restricted at 10 per hour. This covers the POST endpoint at /api/v1/resumes/ that triggers all the expensive LLM processing.

All three search endpoints get the same 100 requests per hour limit. This includes semantic search, structured search, and hybrid search. They all hit external services or expensive database operations, so they all need protection.

Everything else falls under the general 1000 requests per hour limit. This covers listing resumes, checking job status, deleting resumes, fetching filter options, and getting file type configuration. These operations are cheap enough that they don't need special protection beyond preventing outright flooding.

## How users see it

When someone hits a rate limit, they get a clear error response. The API returns HTTP 429 with a JSON body that explains what happened. The message includes the specific limit they exceeded - "Rate limit exceeded (10/hour)" for uploads or "Rate limit exceeded (100/hour)" for searches.

The OpenAPI documentation (accessible through /api/schema/swagger/) shows these rate limits in the endpoint descriptions. Each protected endpoint lists the 429 response with the specific limit that applies. This way developers integrating with the API know what to expect and can design their applications accordingly.

Response headers provide machine-readable rate limit information. X-RateLimit-Limit tells them the total allowed requests. X-RateLimit-Remaining shows how many they have left. When they hit the limit, Retry-After tells them exactly how many seconds until the window resets.

## What's not covered

This throttling only protects the API endpoints. If someone gets access to the worker code and starts submitting jobs directly to Redis, these limits won't help. That's a different security problem requiring proper network isolation and access controls.

The limits are per IP address, which works fine for most cases but has some blind spots. Users behind a corporate NAT or a shared VPN will share rate limit counters. This could cause issues where legitimate users get throttled because someone else on the same IP is being aggressive. So far this hasn't been a problem, but it's something to watch for.

There's no authenticated user tracking because the API doesn't have authentication yet. When that gets added, the system can switch to per-user rate limits instead of per-IP, which would be more precise and harder to circumvent.

## Monitoring and adjustments

I'm watching the throttle rejection rate in the logs. If legitimate users start hitting limits regularly, that's a sign the thresholds are too aggressive. On the flip side, if I see patterns of requests that max out right at the limit threshold repeatedly, that suggests someone testing the boundaries or trying to work around them.

The nice thing about this setup is that adjustments are trivial. If uploads need to be more restrictive, change "10/hour" to "5/hour". If searches need more headroom, bump "100/hour" to "200/hour". No code changes, no deployment complexity, just a settings update and a restart.

Long term, I might add different tiers. Free tier users get the current limits, while paid users get higher limits or no limits at all. DRF supports this through custom throttle classes that can check user attributes. But for now, the simple IP-based approach does exactly what's needed - it protects the system from abuse without getting in the way of legitimate use.
