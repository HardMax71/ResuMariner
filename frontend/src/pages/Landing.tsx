import { Link } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { API_BASE_URL } from "../lib/api";
import {
  SiDjango,
  SiRedis,
  SiReact,
  SiPostgresql,
  SiDocker
} from 'react-icons/si';
import { TbVectorTriangle } from 'react-icons/tb';
import { BiNetworkChart } from 'react-icons/bi';
import { GrGraphQl } from 'react-icons/gr';

export default function Landing() {
  const [visibleSections, setVisibleSections] = useState(new Set<string>());
  const [activeTab, setActiveTab] = useState<'curl' | 'python' | 'node'>('curl');
  const [copiedCode, setCopiedCode] = useState(false);
  const heroRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [windowWidth, setWindowWidth] = useState(typeof window !== 'undefined' ? window.innerWidth : 1024);
  const [currentPage, setCurrentPage] = useState(0);

  // Window resize handler
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Track current page for scroll indicator
  useEffect(() => {
    const handleScroll = () => {
      const scrollContainer = document.querySelector('div[style*="scroll-snap-type"]');
      if (scrollContainer) {
        const scrollTop = scrollContainer.scrollTop;
        const pageHeight = window.innerHeight - 64; // minus header height
        const page = Math.round(scrollTop / pageHeight);
        setCurrentPage(page);
      }
    };

    const scrollContainer = document.querySelector('div[style*="scroll-snap-type"]');
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      return () => scrollContainer.removeEventListener('scroll', handleScroll);
    }
  }, []);

  // Intersection observer for scroll animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisibleSections(prev => new Set(prev).add(entry.target.id));
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('.observe-me').forEach(el => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  // Mouse tracking for hero gradient
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (heroRef.current) {
        const rect = heroRef.current.getBoundingClientRect();
        setMousePosition({
          x: ((e.clientX - rect.left) / rect.width) * 100,
          y: ((e.clientY - rect.top) / rect.height) * 100
        });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const copyCode = () => {
    const code = activeTab === 'curl' ? curlExample :
                 activeTab === 'python' ? pythonExample : nodeExample;
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const curlExample = `curl -X POST http://localhost:8000/api/v1/upload/ \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@resume.pdf"`;

  const pythonExample = `import requests

response = requests.post(
    'http://localhost:8000/api/v1/upload/',
    files={'file': open('resume.pdf', 'rb')}
)
print(response.json())`;

  const nodeExample = `const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('resume.pdf'));

fetch('http://localhost:8000/api/v1/upload/', {
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
      scrollSnapType: 'y mandatory',
      scrollBehavior: 'smooth'
    }}>
      {/* Fixed scroll indicator - hidden on last page */}
      {currentPage < 3 && (
        <div style={{
          position: 'fixed',
          bottom: '40px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
          cursor: 'pointer',
          zIndex: 1000,
          opacity: currentPage === 3 ? 0 : 1,
          transition: 'opacity 0.3s ease'
        }}
        onClick={() => {
          const scrollContainer = document.querySelector('div[style*="scroll-snap-type"]');
          if (scrollContainer) {
            const currentScroll = scrollContainer.scrollTop;
            const pageHeight = window.innerHeight - 64; // minus header height
            const currentPage = Math.round(currentScroll / pageHeight);
            const nextPage = currentPage < 3 ? currentPage + 1 : 0;
            scrollContainer.scrollTo({ top: nextPage * pageHeight, behavior: 'smooth' });
          }
        }}>
        <span style={{
          fontSize: 'var(--text-xs)',
          color: 'var(--gray-600)',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          fontWeight: 500
        }}>Scroll</span>
        <div style={{
          width: '24px',
          height: '40px',
          border: '2px solid var(--gray-400)',
          borderRadius: '12px',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{
            width: '4px',
            height: '8px',
            background: 'var(--gray-600)',
            borderRadius: '2px',
            position: 'absolute',
            left: '50%',
            transform: 'translateX(-50%)',
            animation: 'scroll-down 2s ease-in-out infinite'
          }} />
        </div>
      </div>
      )}

      {/* Page 1: Hero Section with Dynamic Gradient */}
      <section
        ref={heroRef}
        className="observe-me fullpage-section"
        id="hero"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%,
            rgba(59, 130, 246, 0.08) 0%,
            transparent 50%),
            var(--gray-50)`,
          height: 'calc(100vh - var(--space-8))',
          display: 'flex',
          alignItems: 'center',
          position: 'relative',
          overflow: 'hidden',
          transition: 'background 0.3s ease',
          scrollSnapAlign: 'start',
          scrollSnapStop: 'always'
        }}
      >
        <div className="container" style={{ position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'center' }}>
          <div style={{ maxWidth: '800px', width: '100%', textAlign: 'center' }}>
            {/* Dev-focused tagline */}
            <div
              className={`${visibleSections.has('hero') ? 'fade-in-up' : 'opacity-0'}`}
              style={{
                marginBottom: 'var(--space-3)',
                animationDelay: '0.1s'
              }}
            >
              <span style={{
                fontSize: 'var(--text-sm)',
                fontWeight: 500,
                color: 'var(--blue-600)',
                background: 'var(--blue-50)',
                padding: '6px 12px',
                borderRadius: 'var(--radius-full)',
                display: 'inline-block'
              }}>
                🚀 v2.0 - Now 3x faster with Django monolith
              </span>
            </div>

            <h1
              className={`${visibleSections.has('hero') ? 'fade-in-up' : 'opacity-0'}`}
              style={{
                fontSize: 'clamp(2.5rem, 8vw, 4.5rem)',
                fontWeight: 800,
                lineHeight: 1.1,
                marginBottom: 'var(--space-3)',
                background: 'linear-gradient(135deg, var(--gray-900) 0%, var(--gray-700) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                animationDelay: '0.2s'
              }}
            >
              CV Processing
              <br />
              <span style={{
                background: 'linear-gradient(135deg, var(--blue-600) 0%, var(--blue-500) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                That Actually Works
              </span>
            </h1>

            <p
              className={`${visibleSections.has('hero') ? 'fade-in-up' : 'opacity-0'}`}
              style={{
                fontSize: 'var(--text-lg)',
                color: 'var(--gray-600)',
                marginBottom: 'var(--space-4)',
                maxWidth: '600px',
                margin: '0 auto var(--space-4)',
                lineHeight: 1.7,
                animationDelay: '0.3s'
              }}
            >
              Stop regex-ing through PDFs like it's 2010.
              Let LLMs handle the messy parts while Neo4j and Qdrant do what they do best -
              finding connections and semantic meaning in your candidate data.
            </p>

            <div
              className={`flex gap-3 flex-wrap ${visibleSections.has('hero') ? 'fade-in-up' : 'opacity-0'}`}
              style={{ animationDelay: '0.4s', justifyContent: 'center' }}
            >
              <Link
                to="/upload"
                className="btn"
                style={{
                  padding: '14px 28px',
                  fontSize: 'var(--text-base)',
                  fontWeight: 600,
                  background: 'var(--blue-600)',
                  color: 'white',
                  border: 'none',
                  position: 'relative',
                  overflow: 'hidden',
                  transition: 'transform 0.2s, box-shadow 0.2s'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 10px 20px rgba(59, 130, 246, 0.3)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Upload Your First CV
                <span style={{
                  position: 'absolute',
                  top: 0,
                  left: '-100%',
                  width: '100%',
                  height: '100%',
                  background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                  animation: 'shimmer 3s infinite'
                }} />
              </Link>

              <Link
                to="/search"
                className="btn ghost"
                style={{
                  padding: '14px 28px',
                  fontSize: 'var(--text-base)',
                  fontWeight: 600,
                  border: '2px solid var(--gray-300)',
                  background: 'white',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = 'var(--blue-600)';
                  e.currentTarget.style.color = 'var(--blue-600)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = 'var(--gray-300)';
                  e.currentTarget.style.color = '';
                }}
              >
                Try Search Demo
              </Link>

              <a
                href="https://github.com/HardMax71/ResuMariner"
                target="_blank"
                rel="noopener noreferrer"
                className="btn ghost"
                style={{
                  padding: windowWidth < 480 ? '12px 20px' : '14px 28px',
                  fontSize: windowWidth < 480 ? 'var(--text-sm)' : 'var(--text-base)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.2s'
                }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                Star on GitHub
              </a>
            </div>
          </div>
        </div>

        {/* Animated background elements */}
        <div style={{
          position: 'absolute',
          top: '20%',
          right: '-100px',
          width: '400px',
          height: '400px',
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 20s ease-in-out infinite'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '10%',
          left: '-150px',
          width: '500px',
          height: '500px',
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 25s ease-in-out infinite reverse'
        }} />
      </section>

      {/* Page 2: Problem/Solution + Code Integration */}
      <div
        id="page2"
        className="fullpage-section"
        style={{
          height: 'calc(100vh - var(--space-8))',
          scrollSnapAlign: 'start',
          scrollSnapStop: 'always',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Problem/Solution Section */}
        <section className="observe-me" id="problem" style={{ padding: '40px 0', flex: '0 0 50%', display: 'flex', alignItems: 'center', background: 'white' }}>
          <div className="container">
          <div className="grid grid-2" style={{ gap: windowWidth < 768 ? 'var(--space-4)' : 'var(--space-6)', alignItems: 'stretch' }}>
            <div style={{ animation: 'fade-in-right 0.6s ease-out', animationFillMode: 'both', display: 'flex', flexDirection: 'column', height: '100%' }}>
              <div style={{ height: '20px', marginBottom: 'var(--space-2)' }}>
                <span style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  color: 'var(--red-600)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}>
                  The Problem
                </span>
              </div>
              <div style={{ height: '72px', marginBottom: 'var(--space-6)' }}>
                <h2 style={{
                  fontSize: 'var(--text-3xl)',
                  fontWeight: 700,
                  color: 'var(--gray-900)',
                  margin: 0,
                  lineHeight: 1.2
                }}>
                  Your ATS thinks "Python" and "python" are different skills
                </h2>
              </div>
              <div style={{ flex: 1, marginBottom: 'var(--space-3)' }}>
                <p style={{
                  fontSize: 'var(--text-base)',
                  color: 'var(--gray-600)',
                  lineHeight: 1.7,
                  margin: 0
                }}>
                  Traditional resume parsers use regex patterns from the stone age.
                  They miss context, can't handle variations, and definitely can't understand
                  that "10 years building distributed systems" is more valuable than listing "Kafka" as a keyword.
                </p>
              </div>
              <div style={{
                padding: 'var(--space-3)',
                background: 'var(--red-50)',
                borderLeft: '3px solid var(--red-500)',
                borderRadius: 'var(--radius-sm)'
              }}>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--red-800)', margin: 0 }}>
                  <strong>Fun fact:</strong> Most ATS systems would reject their own developers' resumes.
                </p>
              </div>
            </div>

            <div style={{ animation: 'fade-in-left 0.6s ease-out', animationDelay: '0.2s', animationFillMode: 'both', display: 'flex', flexDirection: 'column', height: '100%' }}>
              <div style={{ height: '20px', marginBottom: 'var(--space-2)' }}>
                <span style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  color: 'var(--green-600)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}>
                  Our Solution
                </span>
              </div>
              <div style={{ height: '72px', marginBottom: 'var(--space-6)' }}>
                <h2 style={{
                  fontSize: 'var(--text-3xl)',
                  fontWeight: 700,
                  color: 'var(--gray-900)',
                  margin: 0,
                  lineHeight: 1.2
                }}>
                  LLMs that understand context + Graph DB that maps relationships
                </h2>
              </div>
              <div style={{ flex: 1, marginBottom: 'var(--space-3)' }}>
                <p style={{
                  fontSize: 'var(--text-base)',
                  color: 'var(--gray-600)',
                  lineHeight: 1.7,
                  margin: 0
                }}>
                  We let GPT-4 handle the messy parsing (it's good at that),
                  store relationships in Neo4j (because skills are connected),
                  and use vector embeddings for semantic search (because "Python developer"
                  should match "Django expert").
                </p>
              </div>
              <div style={{
                padding: 'var(--space-3)',
                background: 'var(--green-50)',
                borderLeft: '3px solid var(--green-500)',
                borderRadius: 'var(--radius-sm)'
              }}>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--green-800)', margin: 0 }}>
                  <strong>Result:</strong> Find the senior backend engineer who never wrote "senior backend engineer" on their resume.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Code Example */}
      <section
        className="observe-me"
        id="code"
        style={{
          background: 'var(--gray-900)',
          padding: '40px 0',
          position: 'relative',
          overflow: 'hidden',
          flex: '0 0 50%',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <div className="container">
          <div className={visibleSections.has('code') ? 'fade-in-up' : 'opacity-0'}>
            <h2 style={{
              fontSize: 'var(--text-3xl)',
              fontWeight: 700,
              marginBottom: 'var(--space-2)',
              color: 'white',
              textAlign: 'center'
            }}>
              Integration in 30 seconds
            </h2>
            <p style={{
              fontSize: 'var(--text-base)',
              color: 'var(--gray-400)',
              textAlign: 'center',
              marginBottom: 'var(--space-4)'
            }}>
              RESTful API that your intern can integrate. Promise.
            </p>

            <div style={{
              maxWidth: '800px',
              margin: '0 auto',
              background: 'var(--gray-800)',
              borderRadius: 'var(--radius-md)',
              overflow: 'hidden',
              border: '1px solid var(--gray-700)'
            }}>
              {/* Code editor tabs */}
              <div style={{
                display: 'flex',
                background: 'var(--gray-900)',
                borderBottom: '1px solid var(--gray-700)',
                padding: 0
              }}>
                {(['curl', 'python', 'node'] as const).map((lang, idx) => (
                  <button
                    key={lang}
                    onClick={() => setActiveTab(lang)}
                    style={{
                      padding: 'var(--space-2) var(--space-3)',
                      paddingLeft: idx === 0 ? 'var(--space-2)' : 'var(--space-3)',
                      background: activeTab === lang ? 'var(--gray-800)' : 'transparent',
                      color: activeTab === lang ? 'white' : 'var(--gray-500)',
                      border: 'none',
                      borderBottom: activeTab === lang ? '2px solid var(--blue-500)' : '2px solid transparent',
                      fontSize: 'var(--text-sm)',
                      fontWeight: 500,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      textTransform: 'capitalize'
                    }}
                  >
                    {lang === 'node' ? 'Node.js' : lang}
                  </button>
                ))}
                <button
                  onClick={copyCode}
                  style={{
                    marginLeft: 'auto',
                    marginRight: 0,
                    padding: 'var(--space-2)',
                    background: copiedCode ? 'rgba(255,255,255,0.1)' : 'transparent',
                    color: copiedCode ? 'white' : 'var(--gray-500)',
                    border: copiedCode ? '1px solid rgba(255,255,255,0.2)' : '1px solid transparent',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-sm)',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {copiedCode ? (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Copied
                    </>
                  ) : (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                        <rect x="2" y="2" width="13" height="13" rx="2" ry="2" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              </div>

              {/* Code content */}
              <pre style={{
                margin: 0,
                padding: 'var(--space-3)',
                fontSize: 'var(--text-sm)',
                fontFamily: 'var(--font-mono)',
                color: 'var(--gray-100)',
                lineHeight: 1.6,
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
              marginTop: 'var(--space-3)',
              color: 'var(--gray-500)',
              fontSize: 'var(--text-sm)',
              position: 'relative',
              zIndex: 1
            }}>
              Full API docs at{' '}
              <a
                href={`${API_BASE_URL}/api/docs/`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: 'var(--blue-400)',
                  textDecoration: 'none',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.9em',
                  padding: '2px 4px',
                  background: 'rgba(59, 130, 246, 0.1)',
                  borderRadius: 'var(--radius-sm)',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                  e.currentTarget.style.textDecoration = 'underline';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                  e.currentTarget.style.textDecoration = 'none';
                }}
              >
                /api/docs
              </a>{' '}•
              <span style={{ display: 'inline-block', paddingBottom: '60px' }}>
                OpenAPI spec available •
                Postman collection on request
              </span>
            </p>
          </div>
        </div>

        {/* Animated code lines in background */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.05,
          pointerEvents: 'none',
          fontSize: '10px',
          fontFamily: 'var(--font-mono)',
          color: 'white',
          lineHeight: 1.4,
          whiteSpace: 'pre',
          overflow: 'hidden'
        }}>
          {`const processResume = async (file) => {
  const embeddings = await generateEmbeddings(file);
  const entities = await extractEntities(file);
  await neo4j.save(entities);
  await qdrant.index(embeddings);
  return { success: true };
}`}
        </div>
      </section>
      </div>

      {/* Page 3: Features Bento Box */}
      <section
        className="observe-me fullpage-section"
        id="features"
        style={{
          height: 'calc(100vh - var(--space-8))',
          padding: '60px 0',
          scrollSnapAlign: 'start',
          scrollSnapStop: 'always',
          display: 'flex',
          alignItems: 'center',
          overflow: 'auto'
        }}
      >
        <div className="container">
          <h2 style={{
            fontSize: 'var(--text-4xl)',
            fontWeight: 700,
            marginBottom: 'var(--space-2)',
            textAlign: 'center',
            color: 'var(--gray-900)'
          }}>
            Built for scale, designed for humans
          </h2>
          <p style={{
            fontSize: 'var(--text-lg)',
            color: 'var(--gray-600)',
            textAlign: 'center',
            marginBottom: 'var(--space-6)',
            maxWidth: '600px',
            margin: '0 auto var(--space-6)'
          }}>
            Every feature solves a real problem you've actually had with resume processing.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: windowWidth < 768 ? '1fr' : 'repeat(3, 1fr)',
            gap: 'var(--space-4)',
            marginBottom: 'var(--space-4)'
          }}>
            {/* Large feature - spans full width */}
            <div
              className={`${visibleSections.has('features') ? 'scale-in' : 'opacity-0'}`}
              style={{
                gridColumn: windowWidth < 768 ? 'span 1' : 'span 3',
                padding: 'var(--space-4)',
                background: 'linear-gradient(135deg, var(--blue-50) 0%, var(--purple-50) 100%)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--blue-100)',
                position: 'relative',
                overflow: 'hidden',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer',
                animationDelay: '0.1s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'scale(1.02)';
                e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = 'none';
              }}
              onMouseMove={e => {
                // 3D tilt effect on hover
                const rect = e.currentTarget.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width - 0.5) * 10;
                const y = ((e.clientY - rect.top) / rect.height - 0.5) * -10;
                e.currentTarget.style.transform = `scale(1.02) perspective(1000px) rotateY(${x}deg) rotateX(${y}deg)`;
              }}
            >
              <div style={{ position: 'relative', zIndex: 1, pointerEvents: 'none' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-2)' }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    background: 'white',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--blue-600)" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" />
                      <path d="M2 17l10 5 10-5" />
                      <path d="M2 12l10 5 10-5" />
                    </svg>
                  </div>
                  <h3 style={{
                    fontSize: 'var(--text-xl)',
                    fontWeight: 700,
                    color: 'var(--gray-900)',
                    margin: 0
                  }}>
                    Multi-vector embedding strategy
                  </h3>
                </div>
                <p style={{
                  fontSize: 'var(--text-sm)',
                  color: 'var(--gray-700)',
                  lineHeight: 1.5,
                  marginBottom: 'var(--space-3)'
                }}>
                  Each section of a resume gets its own embedding. Skills, experience, and education
                  are indexed separately. This means searching for "React developer" actually finds React
                  developers, not just people who mentioned React once in their hobbies section.
                </p>
                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: 'var(--space-2)',
                  flexWrap: 'wrap'
                }}>
                  <div style={{
                    padding: '8px 12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue-600)" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="9" y1="9" x2="21" y2="9"/>
                      <line x1="9" y1="15" x2="21" y2="15"/>
                    </svg>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--blue-700)', fontWeight: 500 }}>
                      15-30 vectors/resume
                    </span>
                  </div>
                  <div style={{
                    padding: '8px 12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue-600)" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M12 6v6l4 2"/>
                    </svg>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--blue-700)', fontWeight: 500 }}>
                      384 dimensions
                    </span>
                  </div>
                  <div style={{
                    padding: '8px 12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--blue-600)" strokeWidth="2">
                      <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                    </svg>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--blue-700)', fontWeight: 500 }}>
                      Cosine similarity
                    </span>
                  </div>
                </div>
              </div>
              <div style={{
                position: 'absolute',
                top: '-50px',
                right: '-50px',
                width: '200px',
                height: '200px',
                background: 'radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 70%)',
                borderRadius: '50%'
              }} />
            </div>

            {/* Medium features */}
            <div
              className={`${visibleSections.has('features') ? 'scale-in' : 'opacity-0'}`}
              style={{
                padding: 'var(--space-3)',
                background: 'white',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--gray-200)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer',
                animationDelay: '0.2s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  background: 'var(--green-50)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--green-600)" strokeWidth="2">
                    <circle cx="12" cy="12" r="3" />
                    <circle cx="12" cy="12" r="10" />
                    <circle cx="12" cy="4" r="2" />
                    <circle cx="20" cy="12" r="2" />
                    <circle cx="12" cy="20" r="2" />
                    <circle cx="4" cy="12" r="2" />
                  </svg>
                </div>
                <h4 style={{
                  fontSize: 'var(--text-lg)',
                  fontWeight: 600,
                  color: 'var(--gray-900)',
                  margin: 0
                }}>
                  Graph relationships
                </h4>
              </div>
              <p style={{
                fontSize: 'var(--text-sm)',
                color: 'var(--gray-600)',
                lineHeight: 1.5
              }}>
                Skills → Companies → Roles → Technologies all connected in Neo4j.
                Find everyone who worked at a FAANG and then joined a startup.
              </p>
            </div>

            <div
              className={`${visibleSections.has('features') ? 'scale-in' : 'opacity-0'}`}
              style={{
                padding: 'var(--space-3)',
                background: 'white',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--gray-200)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer',
                animationDelay: '0.3s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  background: 'var(--purple-50)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--purple-600)" strokeWidth="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                    <line x1="12" y1="22.08" x2="12" y2="12" />
                  </svg>
                </div>
                <h4 style={{
                  fontSize: 'var(--text-lg)',
                  fontWeight: 600,
                  color: 'var(--gray-900)',
                  margin: 0
                }}>
                  Smart deduplication
                </h4>
              </div>
              <p style={{
                fontSize: 'var(--text-sm)',
                color: 'var(--gray-600)',
                lineHeight: 1.5
              }}>
                Upload the same resume 10 times? We'll recognize it.
                John Smith and John M. Smith with same email? Same person.
              </p>
            </div>

            <div
              className={`${visibleSections.has('features') ? 'scale-in' : 'opacity-0'}`}
              style={{
                padding: 'var(--space-3)',
                background: 'white',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--gray-200)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer',
                animationDelay: '0.4s'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  background: 'var(--orange-50)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--orange-600)" strokeWidth="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                </div>
                <h4 style={{
                  fontSize: 'var(--text-lg)',
                  fontWeight: 600,
                  color: 'var(--gray-900)',
                  margin: 0
                }}>
                  Batch processing
                </h4>
              </div>
              <p style={{
                fontSize: 'var(--text-sm)',
                color: 'var(--gray-600)',
                lineHeight: 1.5
              }}>
                Process thousands of resumes in parallel. Automatic queuing, retry on failures, and real-time progress tracking.
              </p>
            </div>
          </div>

          {/* Small features grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: windowWidth < 768 ? 'repeat(2, 1fr)' : 'repeat(3, 1fr)',
            gap: 'var(--space-3)'
          }}>
            {[
              {
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                  </svg>
                ),
                text: 'Cost effective - $0.002/resume'
              },
              {
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                ),
                text: 'Your data never leaves your servers'
              },
              {
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="20" x2="12" y2="10" />
                    <line x1="18" y1="20" x2="18" y2="4" />
                    <line x1="6" y1="20" x2="6" y2="16" />
                  </svg>
                ),
                text: 'Real-time processing metrics'
              },
              {
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                ),
                text: 'Hybrid search (vector + graph)'
              },
              {
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </svg>
                ),
                text: 'Sub-30s processing time'
              },
              {
                icon: (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="9" y1="15" x2="15" y2="15" />
                  </svg>
                ),
                text: 'AI-powered resume review'
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className={`${visibleSections.has('features') ? 'fade-in-up' : 'opacity-0'}`}
                style={{
                  padding: 'var(--space-2)',
                  background: 'var(--gray-50)',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  transition: 'all 0.2s',
                  cursor: 'pointer',
                  animationDelay: `${0.5 + idx * 0.1}s`
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'white';
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'var(--gray-50)';
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <span style={{ color: 'var(--gray-700)', display: 'flex', alignItems: 'center' }}>{item.icon}</span>
                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--gray-700)' }}>{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Page 4: Tech Stack + CTA */}
      <div
        id="page4"
        className="fullpage-section"
        style={{
          height: 'calc(100vh - var(--space-8))',
          scrollSnapAlign: 'start',
          scrollSnapStop: 'always',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Tech Stack Showcase */}
        <section className="observe-me" id="stack" style={{ padding: '30px 0', flex: '0 0 50%', display: 'flex', alignItems: 'center', background: 'white' }}>
        <div className="container">
          <h2 style={{
            fontSize: 'var(--text-2xl)',
            fontWeight: 700,
            marginBottom: 'var(--space-1)',
            textAlign: 'center',
            color: 'var(--gray-900)'
          }}>
            Modern stack, boring reliability
          </h2>
          <p style={{
            fontSize: 'var(--text-sm)',
            color: 'var(--gray-600)',
            textAlign: 'center',
            marginBottom: 'var(--space-3)'
          }}>
            We chose proven technologies that actually work in production.
          </p>

          <div
            className={`${visibleSections.has('stack') ? 'scale-in' : 'opacity-0'}`}
            style={{
              display: 'grid',
              gridTemplateColumns: windowWidth < 480 ? 'repeat(2, 1fr)' : windowWidth < 768 ? 'repeat(3, 1fr)' : 'repeat(4, 1fr)',
              gap: 'var(--space-3)',
              maxWidth: '800px',
              margin: '0 auto'
            }}
          >
            {[
              {
                name: 'Django',
                icon: <SiDjango />,
                color: '#092E20',
                desc: 'Python Backend Framework'
              },
              {
                name: 'Neo4j',
                icon: <GrGraphQl />,
                color: '#008CC1',
                desc: 'Graph Database'
              },
              {
                name: 'Qdrant',
                icon: <TbVectorTriangle />,
                color: '#8B5CF6',
                desc: 'Vector Search Engine'
              },
              {
                name: 'Redis',
                icon: <SiRedis />,
                color: '#DC382D',
                desc: 'In-Memory Cache'
              },
              {
                name: 'React',
                icon: <SiReact />,
                color: '#61DAFB',
                desc: 'UI Framework'
              },
              {
                name: 'PostgreSQL',
                icon: <SiPostgresql />,
                color: '#336791',
                desc: 'Relational Database'
              },
              {
                name: 'Docker',
                icon: <SiDocker />,
                color: '#2496ED',
                desc: 'Containerization'
              },
              {
                name: 'Traefik',
                icon: <BiNetworkChart />,
                color: '#24A1C1',
                desc: 'Reverse Proxy'
              },
            ].map((tech, idx) => (
              <div
                key={tech.name}
                style={{
                  padding: 'var(--space-3)',
                  background: 'white',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--gray-200)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: '120px',
                  transition: 'all 0.2s',
                  cursor: 'pointer',
                  animationDelay: `${idx * 0.05}s`,
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-4px) scale(1.02)';
                  e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.12)';
                  e.currentTarget.style.borderColor = tech.color;
                  e.currentTarget.querySelector('.tech-icon').style.transform = 'scale(1.1)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0) scale(1)';
                  e.currentTarget.style.boxShadow = 'none';
                  e.currentTarget.style.borderColor = 'var(--gray-200)';
                  e.currentTarget.querySelector('.tech-icon').style.transform = 'scale(1)';
                }}
              >
                <div
                  className="tech-icon"
                  style={{
                    fontSize: windowWidth < 480 ? '36px' : '42px',
                    color: tech.color,
                    marginBottom: 'var(--space-2)',
                    transition: 'transform 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                  {tech.icon}
                </div>
                <div style={{
                  fontSize: windowWidth < 480 ? 'var(--text-base)' : 'var(--text-lg)',
                  fontWeight: 600,
                  color: 'var(--gray-900)',
                  marginBottom: '4px'
                }}>
                  {tech.name}
                </div>
                <div style={{
                  fontSize: windowWidth < 480 ? 'var(--text-xs)' : 'var(--text-sm)',
                  color: 'var(--gray-600)',
                  textAlign: 'center'
                }}>
                  {tech.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section
        className="observe-me"
        id="cta"
        style={{
          background: 'var(--gray-900)',
          padding: '40px 0',
          position: 'relative',
          overflow: 'hidden',
          flex: '0 0 50%',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div
            className={`${visibleSections.has('cta') ? 'fade-in-up' : 'opacity-0'}`}
            style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto' }}
          >
            <h2 style={{
              fontSize: 'clamp(2rem, 6vw, 3.5rem)',
              fontWeight: 800,
              marginBottom: 'var(--space-3)',
              color: 'white',
              lineHeight: 1.2
            }}>
              Stop losing great candidates to bad parsing
            </h2>
            <p style={{
              fontSize: 'var(--text-lg)',
              color: 'var(--gray-400)',
              marginBottom: 'var(--space-4)',
              lineHeight: 1.6
            }}>
              Deploy in 5 minutes with Docker Compose. Process your first resume in 30 seconds.
              Find that perfect candidate who's been hiding in plain sight.
            </p>
            <div className="flex gap-3 justify-center flex-wrap">
              <Link
                to="/upload"
                className="btn"
                style={{
                  padding: windowWidth < 480 ? '14px 24px' : '16px 32px',
                  fontSize: windowWidth < 480 ? 'var(--text-sm)' : 'var(--text-base)',
                  fontWeight: 600,
                  background: 'white',
                  color: 'var(--gray-900)',
                  border: 'none'
                }}
              >
                Start Processing CVs
              </Link>
              <a
                href="https://github.com/HardMax71/ResuMariner"
                target="_blank"
                rel="noopener noreferrer"
                className="btn"
                style={{
                  padding: windowWidth < 480 ? '14px 24px' : '16px 32px',
                  fontSize: windowWidth < 480 ? 'var(--text-sm)' : 'var(--text-base)',
                  fontWeight: 600,
                  background: 'transparent',
                  color: 'white',
                  border: '2px solid white'
                }}
              >
                View Documentation
              </a>
            </div>

            {/* Trust indicators */}
            <div style={{
              marginTop: 'var(--space-6)',
              padding: 'var(--space-3)',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: 'var(--radius-md)',
              display: 'inline-flex',
              gap: 'var(--space-4)',
              alignItems: 'center',
              flexWrap: 'wrap'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--green-400)" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                <span style={{ fontSize: 'var(--text-sm)', color: 'white' }}>Open Source</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--green-400)" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                <span style={{ fontSize: 'var(--text-sm)', color: 'white' }}>Self-hosted</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--green-400)" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
                <span style={{ fontSize: 'var(--text-sm)', color: 'white' }}>No vendor lock-in</span>
              </div>
            </div>
          </div>
        </div>

        {/* Background decoration */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '150%',
          height: '150%',
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 50%)',
          animation: 'pulse 4s ease-in-out infinite'
        }} />
      </section>
      </div>

      <style>{`
        @keyframes scroll-down {
          0% {
            top: 6px;
            opacity: 0;
          }
          30% {
            opacity: 1;
          }
          100% {
            top: 24px;
            opacity: 0;
          }
        }
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fade-in-left {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes fade-in-right {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0) rotate(0deg);
          }
          25% {
            transform: translateY(-20px) rotate(1deg);
          }
          75% {
            transform: translateY(20px) rotate(-1deg);
          }
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 0.6;
          }
          50% {
            opacity: 1;
          }
        }

        @keyframes shimmer {
          0% {
            left: -100%;
          }
          100% {
            left: 200%;
          }
        }

        .fade-in-up {
          animation: fade-in-up 0.6s ease-out forwards;
        }

        .fade-in-left {
          animation: fade-in-left 0.6s ease-out forwards;
        }

        .fade-in-right {
          animation: fade-in-right 0.6s ease-out forwards;
        }

        .scale-in {
          animation: scale-in 0.6s ease-out forwards;
        }

        .opacity-0 {
          opacity: 0;
        }

        @media (max-width: 768px) {
          .grid-2 {
            grid-template-columns: 1fr;
          }
        }

        .fullpage-section {
          width: 100%;
        }

        /* Hide scrollbar for cleaner look */
        div[style*="scroll-snap-type"] {
          scrollbar-width: none;
          -ms-overflow-style: none;
        }
        div[style*="scroll-snap-type"]::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
}