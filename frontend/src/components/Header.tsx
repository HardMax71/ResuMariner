import { Link, NavLink, useLocation } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { Upload, Search as SearchIcon, FileSearch, Sparkles, Users, MessageCircle, ChevronDown } from "lucide-react";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [ragDropdownOpen, setRagDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setRagDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const mainNavItems = [
    { path: "/upload", label: "Upload", icon: Upload },
    { path: "/search", label: "Search", icon: SearchIcon },
  ];

  const ragItems = [
    { path: "/rag/explain-match", label: "Match", icon: Sparkles },
    { path: "/rag/compare", label: "Compare", icon: Users },
    { path: "/rag/interview", label: "Interview", icon: MessageCircle },
  ];

  const isRagActive = location.pathname.startsWith("/rag");

  return (
    <>
      <header
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          background: "rgba(12, 10, 9, 0.95)",
          backdropFilter: "blur(16px)",
          WebkitBackdropFilter: "blur(16px)",
          borderBottom: "1px solid rgba(129, 140, 248, 0.15)",
          boxShadow: "0 4px 24px rgba(0, 0, 0, 0.4), 0 1px 3px rgba(0, 0, 0, 0.2)",
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        <div
          style={{
            maxWidth: "1280px",
            margin: "0 auto",
            padding: "16px 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Link
            to="/"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "20px",
              fontWeight: 800,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              transition: "opacity 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.8")}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
          >
            <img
              src="/icons/icon.png"
              alt="ResuMariner"
              style={{
                width: "40px",
                height: "40px",
                flexShrink: 0
              }}
            />
            <span style={{
              display: "flex",
              whiteSpace: "nowrap"
            }}>
              <span style={{ color: "#818cf8" }}>Resu</span>
              <span style={{ color: "#ffffff" }}>Mariner</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav
            style={{
              display: "none",
              gap: "4px",
              alignItems: "center",
              flex: 1,
              marginLeft: "clamp(24px, 5vw, 64px)",
            }}
            className="desktop-nav"
          >
            {/* Left: Main actions */}
            <div style={{ display: "flex", gap: "4px", alignItems: "center" }}>
              {mainNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    style={({ isActive }) => ({
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "8px 14px",
                      fontFamily: "var(--font-body)",
                      fontSize: "14px",
                      fontWeight: 600,
                      color: "#ffffff",
                      background: isActive
                        ? "rgba(129, 140, 248, 0.15)"
                        : "transparent",
                      border: "1px solid transparent",
                      borderRadius: "2px",
                      textDecoration: "none",
                      transition: "all 0.2s",
                    })}
                    onMouseEnter={(e) => {
                      const isActive = e.currentTarget.getAttribute('aria-current') === 'page';
                      if (!isActive) {
                        e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      const isActive = e.currentTarget.getAttribute('aria-current') === 'page';
                      if (!isActive) {
                        e.currentTarget.style.background = "transparent";
                      }
                    }}
                  >
                    <Icon size={16} />
                    {item.label}
                  </NavLink>
                );
              })}

              {/* RAG Dropdown */}
              <div ref={dropdownRef} style={{ position: "relative" }}>
                <button
                  onClick={() => setRagDropdownOpen(!ragDropdownOpen)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "8px 14px",
                    fontFamily: "var(--font-body)",
                    fontSize: "14px",
                    fontWeight: 600,
                    color: "#ffffff",
                    background: isRagActive ? "rgba(129, 140, 248, 0.15)" : "transparent",
                    border: "1px solid transparent",
                    borderRadius: "2px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    if (!isRagActive) {
                      e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isRagActive) {
                      e.currentTarget.style.background = "transparent";
                    }
                  }}
                >
                  <FileSearch size={16} />
                  RAG
                  <ChevronDown size={14} style={{
                    transform: ragDropdownOpen ? "rotate(180deg)" : "rotate(0deg)",
                    transition: "transform 0.2s"
                  }} />
                </button>

                {ragDropdownOpen && (
                  <div
                    style={{
                      position: "absolute",
                      top: "calc(100% + 8px)",
                      left: 0,
                      minWidth: "180px",
                      background: "rgba(12, 10, 9, 0.98)",
                      backdropFilter: "blur(16px)",
                      WebkitBackdropFilter: "blur(16px)",
                      border: "1px solid rgba(129, 140, 248, 0.15)",
                      borderRadius: "4px",
                      boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
                      padding: "8px",
                      zIndex: 1001,
                    }}
                  >
                    {ragItems.map((item) => {
                      const Icon = item.icon;
                      const isActive = location.pathname === item.path;
                      return (
                        <NavLink
                          key={item.path}
                          to={item.path}
                          onClick={() => setRagDropdownOpen(false)}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            padding: "10px 12px",
                            fontFamily: "var(--font-body)",
                            fontSize: "14px",
                            fontWeight: 600,
                            color: "#ffffff",
                            background: isActive ? "rgba(129, 140, 248, 0.15)" : "transparent",
                            borderRadius: "2px",
                            textDecoration: "none",
                            transition: "all 0.2s",
                          }}
                          onMouseEnter={(e) => {
                            if (!isActive) {
                              e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!isActive) {
                              e.currentTarget.style.background = "transparent";
                            }
                          }}
                        >
                          <Icon size={16} />
                          {item.label}
                        </NavLink>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

          </nav>
        </div>
      </header>

      {/* Mobile Navigation (Bottom) */}
      <nav
        className="mobile-nav-bottom"
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          display: "none",
          background: "rgba(12, 10, 9, 0.98)",
          backdropFilter: "blur(16px)",
          WebkitBackdropFilter: "blur(16px)",
          borderTop: "1px solid rgba(68, 64, 60, 0.3)",
          padding: "8px",
        }}
      >
        <div
          className="mobile-nav-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            maxWidth: "100%",
            margin: "0 auto",
            gap: "8px",
            padding: "0 4px",
          }}
        >
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                style={({ isActive }) => ({
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "2px",
                  padding: "6px 4px",
                  fontFamily: "var(--font-body)",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: isActive ? "#818cf8" : "#a8a29e",
                  textDecoration: "none",
                  transition: "all 0.2s",
                })}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
          {ragItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                style={({ isActive }) => ({
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "2px",
                  padding: "6px 4px",
                  fontFamily: "var(--font-body)",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: isActive ? "#818cf8" : "#a8a29e",
                  textDecoration: "none",
                  transition: "all 0.2s",
                })}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      </nav>

      <style>{`
        @media (min-width: 768px) {
          .desktop-nav {
            display: flex !important;
          }
        }

        @media (max-width: 767px) {
          .mobile-nav-bottom {
            display: block !important;
          }
        }

        /* Mobile grid adaptive layout - 5 items total */
        @media (max-width: 767px) and (min-width: 500px) {
          .mobile-nav-grid {
            grid-template-columns: repeat(5, 1fr) !important;
          }
        }

        @media (max-width: 499px) {
          .mobile-nav-grid {
            grid-template-columns: repeat(3, 1fr) !important;
          }
        }
      `}</style>
    </>
  );
}