import { Link, NavLink, useLocation } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { Upload, Search as SearchIcon, FileSearch, Sparkles, Users, MessageCircle, ChevronDown } from "lucide-react";

// Navigation items defined outside component to avoid recreation
const MAIN_NAV_ITEMS = [
  { path: "/upload", label: "Upload", icon: Upload },
  { path: "/search", label: "Search", icon: SearchIcon },
] as const;

const RAG_NAV_ITEMS = [
  { path: "/rag/explain-match", label: "Match", icon: Sparkles },
  { path: "/rag/compare", label: "Compare", icon: Users },
  { path: "/rag/interview", label: "Interview", icon: MessageCircle },
] as const;

export default function Header() {
  const [ragDropdownOpen, setRagDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setRagDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const isRagActive = location.pathname.startsWith("/rag");

  return (
    <>
      <header className="site-header">
        <div className="site-header-inner">
          <Link to="/" className="header-logo">
            <img
              src="/icons/icon.png"
              alt="ResuMariner"
              className="header-logo-icon"
            />
            <span className="header-logo-text">
              <span className="header-logo-text-primary">Resu</span>
              <span className="header-logo-text-secondary">Mariner</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="header-nav-desktop">
            <div className="header-nav-group">
              {MAIN_NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `header-nav-link ${isActive ? 'active' : ''}`
                    }
                  >
                    <Icon size={16} />
                    {item.label}
                  </NavLink>
                );
              })}

              {/* RAG Dropdown */}
              <div ref={dropdownRef} className="header-dropdown">
                <button
                  onClick={() => setRagDropdownOpen(!ragDropdownOpen)}
                  className={`header-nav-link ${isRagActive ? 'active' : ''}`}
                >
                  <FileSearch size={16} />
                  RAG
                  <ChevronDown
                    size={14}
                    className={`header-dropdown-chevron ${ragDropdownOpen ? 'open' : ''}`}
                  />
                </button>

                {ragDropdownOpen && (
                  <div className="header-dropdown-menu">
                    {RAG_NAV_ITEMS.map((item) => {
                      const Icon = item.icon;
                      const isActive = location.pathname === item.path;
                      return (
                        <NavLink
                          key={item.path}
                          to={item.path}
                          onClick={() => setRagDropdownOpen(false)}
                          className={`header-dropdown-item ${isActive ? 'active' : ''}`}
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
      <nav className="header-nav-mobile">
        <div className="header-nav-mobile-grid">
          {MAIN_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `header-mobile-link ${isActive ? 'active' : ''}`
                }
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
          {RAG_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `header-mobile-link ${isActive ? 'active' : ''}`
                }
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      </nav>
    </>
  );
}
