import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1 className="hero-title">ResuMariner</h1>
          <p className="hero-subtitle">
            Advanced CV processing and semantic search platform powered by AI,
            Neo4j graph database, and vector embeddings
          </p>
          <div className="flex justify-center gap-2">
            <Link to="/upload" className="btn btn-lg">
              Start Processing CVs
            </Link>
            <Link to="/search" className="btn ghost btn-lg">
              Search Candidates
            </Link>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="section">
        <div className="container">
          <h2 className="text-center mb-4">Core Capabilities</h2>
          <div className="grid grid-3">
            <div className="feature">
              <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <h3 className="feature-title">Smart Processing</h3>
              <p className="feature-description">
                Upload PDFs, DOCX, or images. Our LLM-powered parser extracts
                structured data with 95% accuracy.
              </p>
            </div>

            <div className="feature">
              <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <h3 className="feature-title">Semantic Search</h3>
              <p className="feature-description">
                Find candidates using natural language. Search "Python developer
                with microservices" and get relevant matches.
              </p>
            </div>

            <div className="feature">
              <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="feature-title">Graph Storage</h3>
              <p className="feature-description">
                Neo4j stores relationships between skills, experience, and roles
                for powerful structured queries.
              </p>
            </div>

            <div className="feature">
              <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <h3 className="feature-title">Vector Search</h3>
              <p className="feature-description">
                Each CV section embedded separately using OpenAI models for
                precise semantic matching.
              </p>
            </div>

            <div className="feature">
              <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <h3 className="feature-title">Privacy First</h3>
              <p className="feature-description">
                All data processed locally. Your API keys stay on your server.
                Full control over candidate data.
              </p>
            </div>

            <div className="feature">
              <svg className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              <h3 className="feature-title">API Ready</h3>
              <p className="feature-description">
                RESTful API with OpenAPI docs. Integrate CV processing into
                your existing ATS or workflow.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section section-alt">
        <div className="container">
          <h2 className="text-center mb-4">How It Works</h2>
          <div className="grid grid-3">
            <div className="card text-center">
              <div className="badge badge-primary mb-2">Step 1</div>
              <h4>Upload CV Files</h4>
              <p className="muted small">
                Drop PDF, DOCX, or image files. The system queues them
                for processing automatically.
              </p>
            </div>

            <div className="card text-center">
              <div className="badge badge-primary mb-2">Step 2</div>
              <h4>AI Processing</h4>
              <p className="muted small">
                LLMs extract structured data. Each section is embedded
                separately for precise matching.
              </p>
            </div>

            <div className="card text-center">
              <div className="badge badge-primary mb-2">Step 3</div>
              <h4>Search & Match</h4>
              <p className="muted small">
                Use semantic, structured, or hybrid search to find the
                perfect candidates instantly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="section">
        <div className="container">
          <h2 className="text-center mb-4">System Architecture</h2>
          <div className="card">
            <p className="text-center muted mb-4">
              ResuMariner v2 is a Django monolith that consolidates CV processing,
              storage, and search into a unified platform
            </p>

            <div className="grid grid-2 gap-4">
              <div>
                <h4 className="mb-3">Core Components</h4>
                <div className="flex flex-col gap-2">
                  <div className="flex gap-2">
                    <span className="text-center" style={{color: "var(--blue-600)", minWidth: "24px"}}>▸</span>
                    <div>
                      <strong>Processor App</strong>
                      <p className="muted small">Handles uploads and LLM processing</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-center" style={{color: "var(--blue-600)", minWidth: "24px"}}>▸</span>
                    <div>
                      <strong>Storage App</strong>
                      <p className="muted small">Manages Neo4j and Qdrant persistence</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-center" style={{color: "var(--blue-600)", minWidth: "24px"}}>▸</span>
                    <div>
                      <strong>Search App</strong>
                      <p className="muted small">Provides semantic, structured, and hybrid search</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-center" style={{color: "var(--blue-600)", minWidth: "24px"}}>▸</span>
                    <div>
                      <strong>Background Workers</strong>
                      <p className="muted small">Process jobs via Redis queues</p>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="mb-3">Technology Stack</h4>
                <div className="chips">
                  <span className="chip">Django 5.1</span>
                  <span className="chip">Neo4j</span>
                  <span className="chip">Qdrant</span>
                  <span className="chip">Redis</span>
                  <span className="chip">OpenAI API</span>
                  <span className="chip">React</span>
                  <span className="chip">PostgreSQL</span>
                  <span className="chip">Docker</span>
                  <span className="chip">Traefik</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="section section-alt">
        <div className="container">
          <div className="grid grid-4 text-center">
            <div>
              <div style={{fontSize: "var(--text-4xl)", fontWeight: 800, color: "var(--blue-600)"}}>95%</div>
              <p className="muted small">Extraction Accuracy</p>
            </div>
            <div>
              <div style={{fontSize: "var(--text-4xl)", fontWeight: 800, color: "var(--blue-600)"}}>30s</div>
              <p className="muted small">Avg Processing Time</p>
            </div>
            <div>
              <div style={{fontSize: "var(--text-4xl)", fontWeight: 800, color: "var(--blue-600)"}}>100%</div>
              <p className="muted small">Data Privacy</p>
            </div>
            <div>
              <div style={{fontSize: "var(--text-4xl)", fontWeight: 800, color: "var(--blue-600)"}}>5+</div>
              <p className="muted small">File Formats</p>
            </div>
          </div>
        </div>
      </section>

      {/* Integration Example */}
      <section className="section">
        <div className="container">
          <h2 className="text-center mb-4">Easy Integration</h2>
          <div className="card">
            <div className="tabs mb-3">
              <button className="tab active">REST API</button>
              <button className="tab">Python SDK</button>
              <button className="tab">Docker Compose</button>
            </div>

            <div className="json-view">
              <pre style={{margin: 0}}>{`# Upload CV
POST /api/v1/upload/
Content-Type: multipart/form-data

{
  "file": "resume.pdf"
}

# Response
{
  "job_id": "550e8400-e29b-41d4-a716",
  "status": "processing",
  "created_at": "2024-01-01T00:00:00Z"
}

# Search candidates
POST /search/semantic/
Content-Type: application/json

{
  "query": "Senior Python developer with Django and microservices",
  "limit": 10,
  "min_score": 0.7
}`}</pre>
            </div>

            <p className="muted small mt-2">
              Full OpenAPI documentation available at <code>/api/docs</code>
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section section-alt">
        <div className="container text-center">
          <h2 className="mb-2">Ready to Start?</h2>
          <p className="muted mb-4">
            Process your first CV in under 30 seconds. No credit card required.
          </p>
          <div className="flex justify-center gap-2">
            <Link to="/upload" className="btn btn-lg">
              Try It Now
            </Link>
            <a
              href="https://github.com/HardMax71/ResuMariner"
              target="_blank"
              rel="noopener noreferrer"
              className="btn ghost btn-lg"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>
    </>
  );
}