import { Link } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { API_BASE_URL } from "../lib/api";
import { ArrowRight } from 'lucide-react';
import AnimatedTerminal from '../components/AnimatedTerminal';

export default function Landing() {
  const [visibleSections, setVisibleSections] = useState(new Set<string>());
  const [activeTab, setActiveTab] = useState<'curl' | 'python' | 'node'>('curl');
  const [copiedCode, setCopiedCode] = useState(false);
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 1024);

  // Window resize handler
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Intersection observer for scroll animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisibleSections(prev => new Set(prev).add(entry.target.id));
          } else {
            // Remove from visible sections when scrolling away
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

  const copyCode = () => {
    const code = activeTab === 'curl' ? curlExample :
                 activeTab === 'python' ? pythonExample : nodeExample;
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const curlExample = `curl -X POST ${API_BASE_URL}/api/v1/resumes/ \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@resume.pdf"`;

  const pythonExample = `import requests

response = requests.post(
    '${API_BASE_URL}/api/v1/resumes/',
    files={'file': open('resume.pdf', 'rb')}
)
print(response.json())`;

  const nodeExample = `const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('resume.pdf'));

fetch('${API_BASE_URL}/api/v1/resumes/', {
  method: 'POST',
  body: form
}).then(r => r.json()).then(console.log);`;

  return (
    <div style={{
      position: 'absolute',
      top: 'var(--space-8)',
      left: 0,
      right: 0,
      bottom: 0,
      overflowY: 'auto',
      overflowX: 'hidden'
    }}>
      {/* PAGE 1: HERO - Dark with Diagonal Gradient */}
      <section
        className="observe-me"
        id="hero"
        style={{
          minHeight: '100vh',
          position: 'relative',
          background: 'linear-gradient(135deg, var(--neutral-950) 0%, var(--neutral-900) 50%, var(--primary-950) 100%)',
          padding: '100px 0',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        {/* Diagonal gradient overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, transparent 0%, var(--primary-950) 100%)',
          opacity: 0.3,
          pointerEvents: 'none'
        }} />

        {/* Grid pattern overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `linear-gradient(var(--neutral-800) 1px, transparent 1px),
                           linear-gradient(90deg, var(--neutral-800) 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
          opacity: 0.05,
          pointerEvents: 'none'
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1, width: '100%' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: windowWidth < 968 ? '1fr' : '1fr 1fr',
            gap: 'var(--space-10)',
            alignItems: 'stretch',
            marginBottom: 'var(--space-10)'
          }}>
            {/* Left: Text Content */}
            <div
              className={visibleSections.has('hero') ? 'fade-in' : 'opacity-0'}
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: '100%'
              }}
            >
              {/* Main Heading */}
              <h1 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
                fontWeight: 800,
                lineHeight: 1.1,
                marginBottom: 'var(--space-4)',
                color: 'var(--neutral-0)',
                letterSpacing: '-0.03em'
              }}>
                The Resume Parser
                <br />
                <span style={{
                  background: 'linear-gradient(135deg, var(--primary-400) 0%, var(--accent1-400) 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  Built for Scale
                </span>
              </h1>

              <p style={{
                fontSize: 'var(--text-xl)',
                color: 'var(--neutral-300)',
                marginBottom: 'var(--space-6)',
                lineHeight: 1.7
              }}>
                Vector search, graph relationships, and LLM extraction.
                Process thousands of resumes with enterprise-grade accuracy.
              </p>

              {/* Tech Stack Pills */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 'var(--space-2)',
                marginBottom: 'var(--space-6)'
              }}>
                {[
                  'Vector Search',
                  'Graph DB',
                  'AI Reviews'
                ].map((label, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '12px 16px',
                      background: 'rgba(255, 255, 255, 0.08)',
                      border: '1px solid rgba(255, 255, 255, 0.15)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: 'var(--text-sm)',
                      fontWeight: 600,
                      color: 'var(--neutral-100)',
                      transition: 'all 0.3s',
                      letterSpacing: '0.02em'
                    }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background = 'rgba(67, 56, 202, 0.25)';
                      e.currentTarget.style.borderColor = 'var(--primary-500)';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.color = 'var(--neutral-0)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.color = 'var(--neutral-100)';
                    }}
                  >
                    {label}
                  </div>
                ))}
              </div>

              {/* CTAs */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: 'var(--space-3)'
              }}>
                <Link
                  to="/upload"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    padding: '16px 24px',
                    fontSize: 'var(--text-base)',
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, var(--primary-700) 0%, var(--primary-600) 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    textDecoration: 'none',
                    transition: 'all 0.3s',
                    boxShadow: '0 8px 24px rgba(67, 56, 202, 0.4)'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 12px 32px rgba(67, 56, 202, 0.5)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(67, 56, 202, 0.4)';
                  }}
                >
                  Start Processing
                  <ArrowRight size={20} />
                </Link>

                <Link
                  to="/search"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    padding: '16px 24px',
                    fontSize: 'var(--text-base)',
                    fontWeight: 700,
                    background: 'transparent',
                    color: 'var(--neutral-0)',
                    border: '1.5px solid var(--neutral-600)',
                    borderRadius: 'var(--radius-sm)',
                    textDecoration: 'none',
                    transition: 'all 0.3s'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'var(--neutral-0)';
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'var(--neutral-600)';
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  Search Demo
                </Link>
              </div>
            </div>

            {/* Right: Terminal Mockup */}
            <div
              className={visibleSections.has('hero') ? 'fade-in' : 'opacity-0'}
              style={{
                animationDelay: '0.2s'
              }}
            >
              <AnimatedTerminal isVisible={visibleSections.has('hero')} />
            </div>
          </div>

          {/* Stats Bar - now flows with content */}
          <div
            className={visibleSections.has('hero') ? 'fade-in' : 'opacity-0'}
            style={{
              animationDelay: '0.4s'
            }}
          >
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: 'var(--space-6)',
              padding: 'var(--space-6)',
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 'var(--radius-sm)',
              backdropFilter: 'blur(12px)'
            }}>
                {[
                  { value: '<30s', label: 'Processing' },
                  { value: '768D', label: 'Embeddings' },
                  { value: 'MIT', label: 'License' }
                ].map((stat, idx) => (
                  <div
                    key={idx}
                    style={{
                      textAlign: 'center',
                      padding: 'var(--space-2)'
                    }}
                  >
                    <div style={{
                      fontSize: 'var(--text-4xl)',
                      fontWeight: 800,
                      color: 'var(--neutral-0)',
                      marginBottom: 'var(--space-1)',
                      fontFamily: 'var(--font-display)',
                      lineHeight: '1',
                      letterSpacing: '-0.03em'
                    }}>
                      {stat.value}
                    </div>
                    <div style={{
                      fontSize: 'var(--text-sm)',
                      color: 'var(--neutral-400)',
                      fontWeight: 500,
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em'
                    }}>
                      {stat.label}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </section>

      {/* PAGE 2: PROBLEM / SOLUTION - Diagonal Dividers */}
      <section
        className="observe-me"
        id="problem-solution"
        style={{
          position: 'relative',
          background: 'var(--neutral-0)'
        }}
      >
        {/* Problem Section */}
        <div style={{
          background: 'linear-gradient(135deg, #fecaca 0%, #fca5a5 50%, #f87171 100%)',
          padding: '80px 0',
          clipPath: 'polygon(0 0, 100% 0, 100% 95%, 0 100%)',
          marginBottom: '-40px'
        }}>
          <div className="container">
            <div style={{
              maxWidth: '900px',
              margin: '0 auto',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '6px 12px',
                background: '#dc2626',
                borderRadius: 'var(--radius-sm)',
                marginBottom: 'var(--space-3)'
              }}>
                <span style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 700,
                  color: '#ffffff',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  The Problem
                </span>
              </div>

              <h2 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'clamp(2rem, 5vw, 3.5rem)',
                fontWeight: 800,
                color: '#7f1d1d',
                marginBottom: 'var(--space-4)',
                lineHeight: 1.2
              }}>
                88% of Qualified Candidates
                <br />
                Lost to Rigid ATS Matching
                <sup style={{
                  fontSize: '0.4em',
                  verticalAlign: 'super',
                  marginLeft: '0.25em'
                }}>
                  <a
                    href="https://www.hbs.edu/managing-the-future-of-work/Documents/research/hiddenworkers09032021.pdf"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      color: '#7f1d1d',
                      textDecoration: 'none',
                      fontWeight: 700
                    }}
                  >
                    1
                  </a>
                </sup>
              </h2>

              <p style={{
                fontSize: 'var(--text-xl)',
                color: '#991b1b',
                lineHeight: 1.7,
                marginBottom: 'var(--space-5)'
              }}>
                Regex patterns miss context. Keyword matching fails on synonyms.
                Your perfect candidate gets filtered out because they wrote
                "Python" instead of "python".
              </p>

              <div style={{
                display: 'inline-block',
                padding: 'var(--space-3) var(--space-4)',
                background: 'white',
                border: '2px solid #dc2626',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-lg)',
                color: '#991b1b',
                fontWeight: 600
              }}>
                "Python" !== "python" !== "Python3"
              </div>
            </div>
          </div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%)',
          padding: '80px 0',
          clipPath: 'polygon(0 5%, 100% 0, 100% 100%, 0 100%)'
        }}>
          <div className="container">
            <div style={{
              maxWidth: '900px',
              margin: '0 auto',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '6px 12px',
                background: '#059669',
                borderRadius: 'var(--radius-sm)',
                marginBottom: 'var(--space-3)'
              }}>
                <span style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 700,
                  color: '#ffffff',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  Our Solution
                </span>
              </div>

              <h2 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'clamp(2rem, 5vw, 3.5rem)',
                fontWeight: 800,
                color: '#065f46',
                marginBottom: 'var(--space-4)',
                lineHeight: 1.2
              }}>
                LLM-Powered Semantic
                <br />
                Understanding
              </h2>

              <p style={{
                fontSize: 'var(--text-xl)',
                color: '#047857',
                lineHeight: 1.7,
                marginBottom: 'var(--space-5)'
              }}>
                Vector embeddings understand meaning. Graph databases map relationships.
                Find "ML engineer" when they wrote "deep learning specialist".
              </p>

              <div style={{
                display: 'inline-block',
                padding: 'var(--space-3) var(--space-4)',
                background: 'white',
                border: '2px solid #059669',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-lg)',
                color: '#047857',
                fontWeight: 600
              }}>
                Python ≈ python ≈ Python3 ≈ py
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PAGE 2.5: CODE INTEGRATION - Dark Section */}
      <section
        className="observe-me"
        id="code"
        style={{
          background: 'linear-gradient(135deg, var(--neutral-900) 0%, var(--neutral-950) 100%)',
          padding: '80px 0',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Grid overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `linear-gradient(var(--neutral-800) 1px, transparent 1px),
                           linear-gradient(90deg, var(--neutral-800) 1px, transparent 1px)`,
          backgroundSize: '40px 40px',
          opacity: 0.05
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '8px 16px',
              background: 'rgba(245, 158, 11, 0.15)',
              border: '1.5px solid var(--accent1-600)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 'var(--space-4)'
            }}>
              <span style={{
                fontSize: 'var(--text-sm)',
                fontWeight: 700,
                color: 'var(--accent1-400)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Developer First
              </span>
            </div>

            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2rem, 5vw, 3.5rem)',
              fontWeight: 800,
              color: 'var(--neutral-0)',
              marginBottom: 'var(--space-3)',
              lineHeight: 1.2
            }}>
              Deploy in 30 Seconds
            </h2>

            <p style={{
              fontSize: 'var(--text-lg)',
              color: 'var(--neutral-400)',
              marginBottom: 'var(--space-6)',
              lineHeight: 1.7
            }}>
              Simple REST API. Your backend dev can integrate it before lunch.
            </p>

            {/* Code tabs and content */}
            <div style={{
              background: 'var(--neutral-800)',
              border: '1px solid var(--neutral-700)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
              textAlign: 'left',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
            }}>
              {/* Tabs */}
              <div style={{
                display: 'flex',
                borderBottom: '1px solid var(--neutral-700)',
                background: 'var(--neutral-900)'
              }}>
                {(['curl', 'python', 'node'] as const).map(lang => (
                  <button
                    key={lang}
                    onClick={() => setActiveTab(lang)}
                    style={{
                      padding: '12px 24px',
                      background: activeTab === lang ? 'var(--neutral-800)' : 'transparent',
                      color: activeTab === lang ? 'var(--neutral-0)' : 'var(--neutral-500)',
                      border: 'none',
                      borderBottom: activeTab === lang ? '2px solid var(--primary-600)' : '2px solid transparent',
                      fontSize: 'var(--text-sm)',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      fontFamily: 'var(--font-body)',
                      textTransform: 'capitalize'
                    }}
                  >
                    {lang === 'node' ? 'NodeJS' : lang}
                  </button>
                ))}
                <button
                  onClick={copyCode}
                  style={{
                    marginLeft: 'auto',
                    padding: '12px 24px',
                    background: copiedCode ? 'rgba(67, 56, 202, 0.2)' : 'transparent',
                    color: copiedCode ? 'var(--primary-400)' : 'var(--neutral-500)',
                    border: 'none',
                    fontSize: 'var(--text-sm)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    fontFamily: 'var(--font-body)'
                  }}
                >
                  {copiedCode ? 'Copied' : 'Copy'}
                </button>
              </div>

              {/* Code content */}
              <pre style={{
                margin: 0,
                padding: 'var(--space-4)',
                fontSize: 'var(--text-sm)',
                fontFamily: 'var(--font-mono)',
                color: 'var(--neutral-200)',
                lineHeight: 1.8,
                overflowX: 'auto'
              }}>
                <code>
                  {activeTab === 'curl' && curlExample}
                  {activeTab === 'python' && pythonExample}
                  {activeTab === 'node' && nodeExample}
                </code>
              </pre>
            </div>

            <p style={{
              textAlign: 'center',
              marginTop: 'var(--space-4)',
              color: 'var(--neutral-500)',
              fontSize: 'var(--text-base)'
            }}>
              Full documentation at{' '}
              <a
                href={`${API_BASE_URL}/api/docs/`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: 'var(--primary-400)',
                  textDecoration: 'none',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 600
                }}
              >
                /api/docs
              </a>
            </p>
          </div>
        </div>
      </section>

      {/* PAGE 3: FEATURES - Bento Grid */}
      <section
        className="observe-me"
        id="features"
        style={{
          padding: '80px 0',
          background: 'var(--neutral-0)',
          position: 'relative'
        }}
      >
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2rem, 5vw, 3.5rem)',
              fontWeight: 800,
              color: 'var(--neutral-900)',
              marginBottom: 'var(--space-3)',
              lineHeight: 1.2
            }}>
              Built for{' '}
              <span style={{
                background: 'linear-gradient(135deg, var(--primary-700) 0%, var(--accent1-500) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                Enterprise Scale
              </span>
            </h2>
            <p style={{
              fontSize: 'var(--text-xl)',
              color: 'var(--neutral-600)',
              maxWidth: '700px',
              margin: '0 auto'
            }}>
              Vector search + Graph relationships + Sub-30s processing.
              Everything you need, nothing you don't.
            </p>
          </div>

          {/* Bento Grid - Unequal Sizes */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: windowWidth < 768 ? '1fr' : 'repeat(3, 1fr)',
            gridTemplateRows: windowWidth < 768 ? 'auto' : 'repeat(2, 240px)',
            gap: 'var(--space-4)'
          }}>
            {/* Large Feature 1 - Spans 2 columns */}
            <div
              className={visibleSections.has('features') ? 'fade-in' : 'opacity-0'}
              style={{
                gridColumn: windowWidth < 768 ? 'span 1' : 'span 2',
                gridRow: 'span 1',
                background: 'white',
                border: '1.5px solid var(--neutral-200)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                animationDelay: '0.1s',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'var(--primary-300)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--neutral-200)';
              }}
            >
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-xl)',
                fontWeight: 700,
                color: 'var(--neutral-900)',
                marginBottom: 'var(--space-2)'
              }}>
                Vector Search
              </h3>
              <p style={{
                fontSize: 'var(--text-base)',
                color: 'var(--neutral-600)',
                lineHeight: 1.6
              }}>
                Qdrant-powered semantic search. Find candidates by meaning, not keywords.
                768-dimensional embeddings capture context.
              </p>
            </div>

            {/* Feature 2 - Now spans 2 rows */}
            <div
              className={visibleSections.has('features') ? 'fade-in' : 'opacity-0'}
              style={{
                gridRow: windowWidth < 768 ? 'span 1' : 'span 2',
                background: 'white',
                border: '1.5px solid var(--neutral-200)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                transition: 'all 0.3s',
                animationDelay: '0.2s',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                cursor: 'pointer'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'var(--primary-300)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--neutral-200)';
              }}
            >
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-xl)',
                fontWeight: 700,
                color: 'var(--neutral-900)',
                marginBottom: 'var(--space-2)'
              }}>
                Sub-30s Processing
              </h3>
              <p style={{
                fontSize: 'var(--text-base)',
                color: 'var(--neutral-600)',
                lineHeight: 1.6
              }}>
                Async workers with Redis queue. Process thousands of resumes concurrently with automatic retry logic.
              </p>
            </div>

            {/* Feature 3 */}
            <div
              className={visibleSections.has('features') ? 'fade-in' : 'opacity-0'}
              style={{
                background: 'white',
                border: '1.5px solid var(--neutral-200)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-4)',
                transition: 'all 0.3s',
                animationDelay: '0.3s',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'var(--primary-300)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--neutral-200)';
              }}
            >
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-lg)',
                fontWeight: 700,
                color: 'var(--neutral-900)',
                marginBottom: 'var(--space-2)'
              }}>
                Graph Relations
              </h3>
              <p style={{
                fontSize: 'var(--text-base)',
                color: 'var(--neutral-600)',
                lineHeight: 1.6
              }}>
                Neo4j maps skills → companies → roles. Unlimited relationships.
              </p>
            </div>

            {/* Large Feature 4 - Spans 2 rows */}
            <div
              className={visibleSections.has('features') ? 'fade-in' : 'opacity-0'}
              style={{
                gridRow: windowWidth < 768 ? 'span 1' : 'span 2',
                background: 'white',
                border: '1.5px solid var(--neutral-200)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                animationDelay: '0.4s',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'var(--primary-300)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--neutral-200)';
              }}
            >
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-xl)',
                fontWeight: 700,
                color: 'var(--neutral-900)',
                marginBottom: 'var(--space-2)'
              }}>
                LLM Extraction
              </h3>
              <p style={{
                fontSize: 'var(--text-base)',
                color: 'var(--neutral-600)',
                lineHeight: 1.6
              }}>
                Structured Pydantic models. Claude/GPT-4 parse with context awareness.
              </p>
            </div>

            {/* Feature 5 & 6 */}
            <div
              className={visibleSections.has('features') ? 'fade-in' : 'opacity-0'}
              style={{
                background: 'white',
                border: '1.5px solid var(--neutral-200)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-4)',
                transition: 'all 0.3s',
                animationDelay: '0.5s',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'var(--primary-300)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--neutral-200)';
              }}
            >
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-lg)',
                fontWeight: 700,
                color: 'var(--neutral-900)',
                marginBottom: 'var(--space-2)'
              }}>
                Self-Hosted
              </h3>
              <p style={{
                fontSize: 'var(--text-base)',
                color: 'var(--neutral-600)',
                lineHeight: 1.6
              }}>
                Your data never leaves your infrastructure. Full control.
              </p>
            </div>

            <div
              className={visibleSections.has('features') ? 'fade-in' : 'opacity-0'}
              style={{
                background: 'white',
                border: '1.5px solid var(--neutral-200)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-4)',
                transition: 'all 0.3s',
                animationDelay: '0.6s',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.borderColor = 'var(--primary-300)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = 'var(--neutral-200)';
              }}
            >
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-lg)',
                fontWeight: 700,
                color: 'var(--neutral-900)',
                marginBottom: 'var(--space-2)'
              }}>
                Open Source
              </h3>
              <p style={{
                fontSize: 'var(--text-base)',
                color: 'var(--neutral-600)',
                lineHeight: 1.6
              }}>
                MIT licensed. Inspect, modify, contribute. Zero vendor lock-in.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* PAGE 4: CTA - Full-Width Band */}
      <section
        className="observe-me"
        id="cta"
        style={{
          position: 'relative',
          background: 'linear-gradient(135deg, var(--primary-950) 0%, var(--neutral-950) 100%)',
          padding: '100px 0',
          overflow: 'hidden'
        }}
      >
        {/* Geometric shapes background */}
        <div style={{
          position: 'absolute',
          top: '10%',
          left: '5%',
          width: '300px',
          height: '300px',
          border: '2px solid var(--primary-800)',
          borderRadius: 'var(--radius-sm)',
          transform: 'rotate(45deg)',
          opacity: 0.1
        }} />
        <div style={{
          position: 'absolute',
          bottom: '15%',
          right: '8%',
          width: '200px',
          height: '200px',
          border: '2px solid var(--accent1-700)',
          borderRadius: 'var(--radius-sm)',
          transform: 'rotate(30deg)',
          opacity: 0.1
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
            <h2 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2rem, 5vw, 3.5rem)',
              fontWeight: 800,
              color: 'var(--neutral-0)',
              marginBottom: 'var(--space-4)',
              lineHeight: 1.15
            }}>
              Stop Losing Candidates to{' '}
              <span style={{
                background: 'linear-gradient(135deg, #f87171 0%, #dc2626 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                Bad Parsing
              </span>
            </h2>

            <p style={{
              fontSize: 'var(--text-xl)',
              color: 'var(--neutral-300)',
              marginBottom: 'var(--space-6)',
              lineHeight: 1.7
            }}>
              Deploy with Docker Compose in 5 minutes. Process your first resume in 30 seconds.
            </p>

            <div style={{
              display: 'flex',
              justifyContent: 'center',
              marginBottom: 'var(--space-8)'
            }}>
              <Link
                to="/upload"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '16px 32px',
                  fontSize: 'var(--text-xl)',
                  fontWeight: 700,
                  background: 'white',
                  color: 'var(--neutral-900)',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  textDecoration: 'none',
                  transition: 'all 0.3s',
                  boxShadow: '0 8px 24px rgba(255, 255, 255, 0.2)'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-3px) scale(1.02)';
                  e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 255, 255, 0.3)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0) scale(1)';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(255, 255, 255, 0.2)';
                }}
              >
                Start Processing Now
                <ArrowRight size={20} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Animations */}
      <style>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes cursor-blink {
          0%, 50% {
            opacity: 1;
          }
          51%, 100% {
            opacity: 0;
          }
        }

        .fade-in {
          animation: fade-in 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        .opacity-0 {
          opacity: 0;
        }
      `}</style>
    </div>
  );
}