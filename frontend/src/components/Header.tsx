import { Link, NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { Upload, Search as SearchIcon, Activity, Github } from "lucide-react";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { path: "/upload", label: "Upload", icon: Upload },
    { path: "/search", label: "Search", icon: SearchIcon },
    { path: "/health", label: "Health", icon: Activity },
  ];

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
              fontFamily: "Manrope, sans-serif",
              fontSize: "20px",
              fontWeight: 800,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              transition: "opacity 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.8")}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
          >
            <span style={{ color: "#818cf8" }}>Resu</span>
            <span style={{ color: "#ffffff" }}>Mariner</span>
          </Link>

          {/* Desktop Navigation */}
          <nav
            style={{
              display: "none",
              gap: "4px",
              alignItems: "center",
            }}
            className="desktop-nav"
          >
            {navItems.map((item) => {
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
                    fontFamily: "Inter, sans-serif",
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

            {/* GitHub Link */}
            <a
              href="https://github.com/HardMax71/ResuMariner"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "8px",
                marginLeft: "8px",
                fontFamily: "Inter, sans-serif",
                fontSize: "14px",
                fontWeight: 600,
                color: "#ffffff",
                background: "transparent",
                border: "1px solid rgba(255, 255, 255, 0.15)",
                borderRadius: "2px",
                textDecoration: "none",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
                e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.25)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.15)";
              }}
            >
              <Github size={18} />
            </a>
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
          padding: "12px 0",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            maxWidth: "500px",
            margin: "0 auto",
          }}
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                style={({ isActive }) => ({
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "4px",
                  padding: "8px",
                  fontFamily: "Inter, sans-serif",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: isActive ? "#818cf8" : "#a8a29e",
                  textDecoration: "none",
                  transition: "all 0.2s",
                })}
              >
                <Icon size={20} />
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
      `}</style>
    </>
  );
}