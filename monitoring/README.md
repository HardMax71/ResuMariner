# Monitoring Setup

## Why this exists

Started with just print statements. Then Django logs. Then someone asked "how many requests per second can it handle?" and "which database queries are slow?" Print statements don't answer that.

Built proper monitoring because debugging production issues at 2am without metrics is like fixing your car in the dark. You need to see what's happening inside.

## What we're tracking

### Backend (Django)
The middleware intercepts every HTTP request. Tracks:
- Request count by endpoint, method, and status code
- Response times for each endpoint
- Which endpoints get hit most (spoiler: it's always health checks)

No manual instrumentation needed. The middleware (`backend/core/middleware.py`) catches everything automatically. Way better than decorating every view.

### Redis
Using redis_exporter because Redis doesn't expose Prometheus metrics natively. Tracks:
- Commands per second (mostly queue operations from our workers)
- Memory usage (Redis eats RAM for breakfast)
- Cache hit rates
- Network I/O

### Neo4j
Neo4j Community Edition doesn't have built-in Prometheus support - that's Enterprise only. Using a third-party exporter (https://github.com/petrov-e/neo4j_exporter) that connects via Bolt protocol and runs Cypher queries to collect metrics.

The setup:
1. Exporter connects to Neo4j with credentials embedded in the bolt URI (`bolt://user:password@host:7687`)
2. Runs background queries every minute to collect stats
3. Exposes metrics on port 5000
4. Prometheus scrapes from the exporter

Tracks:
- Database online/offline status (neo4j_db_status)
- Slow running queries >10s (neo4j_db_slow_query)
- Query execution times
- Page hits per query (neo4j_db_slow_query_page_hits)

Limited compared to Enterprise metrics, but shows what matters - database health and slow queries that need optimization.

### Qdrant
Easy one. Qdrant has native Prometheus support on `/metrics`. Tracks:
- Collection count
- Memory usage
- REST API response rates by status
- Cluster info (we're single-node but it's there)

## How it works

```
Services → Metrics endpoints → Prometheus → Grafana
```

Prometheus scrapes metrics every 5-30 seconds (depending on the service). Stores them in time-series database. Grafana queries Prometheus and draws the pretty graphs.

### Port mapping
- Prometheus: http://prometheus.internal.localhost:8081
- Grafana: http://grafana.localhost:8081 (admin/admin)
- Neo4j Exporter: internal only on port 5000
- Redis Exporter: internal only on port 9121

## Configuration files

```
monitoring/
├── prometheus.yml              # What to scrape, how often
└── grafana/
    ├── datasources/
    │   └── prometheus.yml      # Tell Grafana where Prometheus lives
    └── dashboards/
        ├── dashboards.yml      # Dashboard auto-provisioning config
        ├── backend.json        # Django metrics dashboard
        ├── redis.json          # Cache/queue metrics
        ├── neo4j.json          # Graph DB metrics
        └── qdrant.json         # Vector DB metrics
```

## Why third-party exporter for Neo4j?

Neo4j Community Edition doesn't have Prometheus metrics. Period. Options were:
1. Pay for Enterprise (lol no)
2. Use third-party exporter that queries Neo4j directly (winner)

The petrov-e/neo4j_exporter connects via Bolt and runs Cypher queries to gather metrics. Not as efficient as native metrics, but works with Community Edition. Shows database status and slow queries, which is 90% of what you need for troubleshooting anyway.

## Dashboards

Four dashboards, one per service. Auto-imported when Grafana starts.

**Backend Metrics**: Request rates, latencies, error rates. The P95 latency graph tells you when your database queries are getting slow.

**Redis Metrics**: Shows if Redis is actually caching things or just eating memory. The keyspace hit rate should be >90% or your cache strategy sucks.

**Neo4j Metrics**: Database status and slow queries (>10s). Shows which queries are hitting page cache hard. If you see many slow queries, either add indexes or your graph is getting too big for available RAM.

**Qdrant Metrics**: Vector search performance. Collection count should match your resume count. Memory usage grows with embeddings.

## Adding new metrics

Django endpoints are auto-tracked. For custom metrics:

1. Add to `backend/core/metrics.py`
2. Increment/observe in your code
3. Prometheus will pick it up automatically

For new services:
1. Add exporter to docker-compose
2. Add scrape job to `prometheus.yml`
3. Create dashboard in Grafana, export JSON, save to `grafana/dashboards/`

## Troubleshooting

**"No data" in Grafana**: Check Prometheus targets at http://prometheus.internal.localhost:8081/targets. Should all say "UP".

**Neo4j metrics missing**: Exporter probably can't connect. Check `docker logs resumariner-neo4j-exporter-1`. Look for "Error connecting to the database". Verify Neo4j password in .env matches NEO4J_PASSWORD. The exporter authenticates using credentials embedded in NEO4J_SERVICE environment variable.

**High memory usage**: That's Prometheus storing time series data. Default retention is 200 hours. Lower it in prometheus command args if needed.

**Grafana password**: admin/admin. Change it or don't, it's internal-only anyway.