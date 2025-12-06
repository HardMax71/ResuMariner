import { Link } from "react-router-dom";
import { useEffect, useRef, useState, useCallback } from "react";
import { API_BASE_URL } from "../api/client";
import { ArrowRight } from 'lucide-react';
import AnimatedTerminal from '../components/AnimatedTerminal';

// Code examples defined outside component to avoid recreation on each render
const CODE_EXAMPLES = {
  curl: `curl -X POST ${API_BASE_URL}/api/v1/resumes/ \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@resume.pdf"`,

  python: `import requests

response = requests.post(
    '${API_BASE_URL}/api/v1/resumes/',
    files={'file': open('resume.pdf', 'rb')}
)
print(response.json())`,

  node: `const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('resume.pdf'));

fetch('${API_BASE_URL}/api/v1/resumes/', {
  method: 'POST',
  body: form
}).then(r => r.json()).then(console.log);`
} as const;

// Static data
const TECH_PILLS = ['Vector Search', 'Graph DB', 'AI Reviews'] as const;
const STATS = [
  { value: '<30s', label: 'Processing' },
  { value: 'Semantic', label: 'Matching' },
  { value: 'MIT', label: 'License' }
] as const;

interface Feature {
  title: string;
  description: string;
  wide?: boolean;
  tall?: boolean;
  small?: boolean;
}

const FEATURES: Feature[] = [
  {
    title: 'Vector Search',
    description: 'Qdrant-powered semantic search. Find candidates by meaning, not keywords. 768-dimensional embeddings capture context.',
    wide: true
  },
  {
    title: 'Sub-30s Processing',
    description: 'Async workers with Redis queue. Process thousands of resumes concurrently with automatic retry logic.',
    tall: true
  },
  {
    title: 'Graph Relations',
    description: 'Neo4j maps skills → companies → roles. Unlimited relationships.',
    small: true
  },
  {
    title: 'LLM Extraction',
    description: 'Structured Pydantic models. Claude/GPT-4 parse with context awareness.',
    tall: true
  },
  {
    title: 'Self-Hosted',
    description: 'Your data never leaves your infrastructure. Full control.',
    small: true
  },
  {
    title: 'Open Source',
    description: 'MIT licensed. Inspect, modify, contribute. Zero vendor lock-in.',
    small: true
  }
];

export default function Landing() {
  const [visibleSections, setVisibleSections] = useState(new Set<string>());
  const [activeTab, setActiveTab] = useState<keyof typeof CODE_EXAMPLES>('curl');
  const [copiedCode, setCopiedCode] = useState(false);
  const visibleSectionsRef = useRef(visibleSections);

  // Keep ref in sync
  useEffect(() => {
    visibleSectionsRef.current = visibleSections;
  }, [visibleSections]);

  // Intersection observer for scroll animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const current = visibleSectionsRef.current;
          if (entry.isIntersecting && !current.has(entry.target.id)) {
            setVisibleSections(prev => new Set([...prev, entry.target.id]));
          } else if (!entry.isIntersecting && current.has(entry.target.id)) {
            setVisibleSections(prev => {
              const next = new Set(prev);
              next.delete(entry.target.id);
              return next;
            });
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('.observe-me').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const copyCode = useCallback(() => {
    navigator.clipboard.writeText(CODE_EXAMPLES[activeTab]);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  }, [activeTab]);

  return (
    <div className="landing-page-wrapper">
      {/* Skip Link for Accessibility */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* PAGE 1: HERO */}
      <section
        className="observe-me landing-section landing-section-dark landing-padding-hero"
        id="hero"
        aria-label="Hero section"
      >
        <div className="landing-gradient-overlay" aria-hidden="true" />
        <div className="landing-grid-overlay" aria-hidden="true" />

        <div className="landing-container">
          <div className="landing-hero-grid">
            {/* Left: Text Content */}
            <div
              className={`landing-hero-content ${visibleSections.has('hero') ? 'fade-in' : 'opacity-0'}`}
            >
              <h1 className="landing-h1" id="main-content">
                The Resume Parser
                <br />
                <span className="landing-gradient-text">Built for Scale</span>
              </h1>

              <p className="landing-lead landing-lead-light">
                Vector search, graph relationships, and LLM extraction.
                Process thousands of resumes with enterprise-grade accuracy.
              </p>

              {/* Tech Stack Pills */}
              <div className="landing-pills-grid" role="list" aria-label="Key features">
                {TECH_PILLS.map((label) => (
                  <div
                    key={label}
                    className="landing-pill"
                    role="listitem"
                    tabIndex={0}
                  >
                    {label}
                  </div>
                ))}
              </div>

              {/* CTAs */}
              <div className="landing-cta-grid">
                <Link to="/upload" className="landing-btn-primary">
                  Start Processing
                  <ArrowRight size={20} aria-hidden="true" />
                </Link>
                <Link to="/search" className="landing-btn-secondary">
                  Search Demo
                </Link>
              </div>
            </div>

            {/* Right: Terminal Mockup */}
            <div
              className={`landing-terminal-wrapper animation-delay-2 ${visibleSections.has('hero') ? 'fade-in' : 'opacity-0'}`}
            >
              <AnimatedTerminal isVisible={visibleSections.has('hero')} />
            </div>
          </div>

          {/* Stats Bar */}
          <div
            className={`animation-delay-4 ${visibleSections.has('hero') ? 'fade-in' : 'opacity-0'}`}
          >
            <div className="landing-stats-bar" role="list" aria-label="Key statistics">
              {STATS.map((stat) => (
                <div key={stat.label} className="landing-stat" role="listitem">
                  <div className="landing-stat-value">{stat.value}</div>
                  <div className="landing-stat-label">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* PAGE 2: PROBLEM / SOLUTION */}
      <section
        className="observe-me landing-section"
        id="problem-solution"
        aria-label="Problem and solution"
      >
        {/* Problem Section */}
        <div className="landing-problem-section">
          <div className="landing-container">
            <div className="landing-content-narrow text-center">
              <div className="landing-badge landing-badge-problem">
                <span className="landing-badge-text landing-badge-text-white">
                  The Problem
                </span>
              </div>

              <h2 className="landing-problem-heading">
                88% of Qualified Candidates
                <br />
                Lost to Rigid ATS Matching
                <sup className="landing-citation">
                  <a
                    href="https://www.hbs.edu/managing-the-future-of-work/Documents/research/hiddenworkers09032021.pdf"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="landing-citation-link"
                    aria-label="Source: Harvard Business School research (opens in new tab)"
                  >
                    1
                  </a>
                </sup>
              </h2>

              <p className="landing-problem-text">
                Regex patterns miss context. Keyword matching fails on synonyms.
                Your perfect candidate gets filtered out because they wrote
                "Python" instead of "python".
              </p>

              <div className="landing-code-box landing-code-box-problem">
                "Python" !== "python" !== "Python3"
              </div>
            </div>
          </div>
        </div>

        {/* Solution Section */}
        <div className="landing-solution-section">
          <div className="landing-container">
            <div className="landing-content-narrow text-center">
              <div className="landing-badge landing-badge-solution">
                <span className="landing-badge-text landing-badge-text-white">
                  Our Solution
                </span>
              </div>

              <h2 className="landing-solution-heading">
                LLM-Powered Semantic
                <br />
                Understanding
              </h2>

              <p className="landing-solution-text">
                Vector embeddings understand meaning. Graph databases map relationships.
                Find "ML engineer" when they wrote "deep learning specialist".
              </p>

              <div className="landing-code-box landing-code-box-solution">
                Python ≈ python ≈ Python3 ≈ py
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PAGE 2.5: CODE INTEGRATION */}
      <section
        className="observe-me landing-section landing-section-dark landing-padding-lg"
        id="code"
        aria-label="API integration"
      >
        <div className="landing-grid-overlay" aria-hidden="true" />

        <div className="landing-container">
          <div className="landing-content-narrow text-center">
            <div className="landing-badge landing-badge-accent">
              <span className="landing-badge-text landing-badge-text-accent">
                Developer First
              </span>
            </div>

            <h2 className="landing-h2 landing-h2-dark">
              Deploy in 30 Seconds
            </h2>

            <p className="landing-code-description">
              Simple REST API. Your backend dev can integrate it before lunch.
            </p>

            {/* Code tabs and content */}
            <div className="landing-code-container">
              {/* Header with dots */}
              <div className="landing-code-header">
                <div className="landing-code-dots" aria-hidden="true">
                  <div className="landing-code-dot landing-code-dot-red" />
                  <div className="landing-code-dot landing-code-dot-yellow" />
                  <div className="landing-code-dot landing-code-dot-green" />
                </div>
                <span className="landing-code-title">api-examples</span>
              </div>

              {/* Tabs */}
              <div className="landing-code-tabs" role="tablist" aria-label="Code examples">
                {(['curl', 'python', 'node'] as const).map(lang => (
                  <button
                    key={lang}
                    role="tab"
                    aria-selected={activeTab === lang}
                    aria-controls={`tabpanel-${lang}`}
                    id={`tab-${lang}`}
                    className={`landing-code-tab ${activeTab === lang ? 'active' : ''}`}
                    onClick={() => setActiveTab(lang)}
                  >
                    {lang === 'node' ? 'NodeJS' : lang}
                  </button>
                ))}
                <button
                  onClick={copyCode}
                  className={`landing-code-copy ${copiedCode ? 'copied' : ''}`}
                  aria-label={copiedCode ? 'Copied to clipboard' : 'Copy code to clipboard'}
                >
                  {copiedCode ? 'Copied' : 'Copy'}
                </button>
              </div>

              {/* Code content */}
              <pre
                className="landing-code-content"
                role="tabpanel"
                id={`tabpanel-${activeTab}`}
                aria-labelledby={`tab-${activeTab}`}
              >
                <code>
                  {CODE_EXAMPLES[activeTab]}
                </code>
              </pre>
            </div>

            <p className="landing-code-footer">
              Full documentation at{' '}
              <a
                href={`${API_BASE_URL}/api/docs/`}
                target="_blank"
                rel="noopener noreferrer"
              >
                /api/docs
              </a>
            </p>
          </div>
        </div>
      </section>

      {/* PAGE 3: FEATURES - Bento Grid */}
      <section
        className="observe-me landing-section landing-section-light landing-padding-lg"
        id="features"
        aria-label="Features"
      >
        <div className="landing-container">
          <div className="landing-features-header">
            <h2 className="landing-h2 landing-h2-light">
              Built for{' '}
              <span className="landing-gradient-text-dark">Enterprise Scale</span>
            </h2>
            <p className="landing-lead landing-lead-dark landing-lead-narrow">
              Vector search + Graph relationships + Sub-30s processing.
              Everything you need, nothing you don't.
            </p>
          </div>

          {/* Bento Grid */}
          <div className="landing-bento-grid">
            {FEATURES.map((feature, idx) => (
              <div
                key={feature.title}
                className={`landing-bento-card animation-delay-${idx + 1} ${visibleSections.has('features') ? 'fade-in' : 'opacity-0'} ${feature.wide ? 'landing-bento-card-wide' : ''} ${feature.tall ? 'landing-bento-card-tall' : ''}`}
                tabIndex={0}
                role="article"
                aria-labelledby={`feature-${idx}`}
              >
                <h3
                  id={`feature-${idx}`}
                  className={`landing-h3 ${feature.small ? 'landing-h3-sm' : ''}`}
                >
                  {feature.title}
                </h3>
                <p className="landing-bento-text">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PAGE 4: CTA */}
      <section
        className="observe-me landing-section landing-section-cta landing-padding-lg"
        id="cta"
        aria-label="Call to action"
      >
        <div className="landing-deco-shape landing-deco-shape-1" aria-hidden="true" />
        <div className="landing-deco-shape landing-deco-shape-2" aria-hidden="true" />

        <div className="landing-container">
          <div className="landing-content-narrow text-center">
            <h2 className="landing-h2 landing-h2-dark landing-h2-cta">
              Stop Losing Candidates to{' '}
              <span className="landing-gradient-text-red">Bad Parsing</span>
            </h2>

            <p className="landing-lead landing-lead-light">
              Deploy with Docker Compose in 5 minutes. Process your first resume in 30 seconds.
            </p>

            <div className="landing-cta-center">
              <Link to="/upload" className="landing-btn-white">
                Start Processing Now
                <ArrowRight size={20} aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
