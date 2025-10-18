import { Link } from "react-router-dom";
import { Github } from "lucide-react";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className="footer-container"
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        background: "rgba(12, 10, 9, 0.95)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderTop: "1px solid rgba(129, 140, 248, 0.15)",
        padding: "10px 16px",
      }}
    >
      <div
        className="footer-content"
        style={{
          maxWidth: "1280px",
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
        }}
      >
        {/* Left: Copyright */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "var(--text-xs)",
            color: "#78716c",
            fontFamily: "var(--font-body)",
            fontWeight: 500,
            whiteSpace: "nowrap",
          }}
        >
          <span style={{ color: "#818cf8", fontWeight: 700 }}>ResuMariner</span>
          <span>© {currentYear}</span>
        </div>

        {/* Right: Links */}
        <div
          style={{
            display: "flex",
            gap: "6px",
            alignItems: "center",
            fontSize: "var(--text-xs)",
            fontFamily: "var(--font-body)",
          }}
        >
          <Link
            to="/privacy"
            style={{
              color: "#d6d3d1",
              textDecoration: "none",
              fontWeight: 500,
              transition: "color 0.2s",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#818cf8")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#d6d3d1")}
          >
            Privacy
          </Link>
          <span style={{ color: "#57534e" }}>·</span>
          <Link
            to="/terms"
            style={{
              color: "#d6d3d1",
              textDecoration: "none",
              fontWeight: 500,
              transition: "color 0.2s",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#818cf8")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#d6d3d1")}
          >
            Terms
          </Link>
          <span style={{ color: "#57534e" }}>·</span>
          <Link
            to="/data-policy"
            style={{
              color: "#d6d3d1",
              textDecoration: "none",
              fontWeight: 500,
              transition: "color 0.2s",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#818cf8")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#d6d3d1")}
          >
            Data
          </Link>
          <span style={{ color: "#57534e" }}>·</span>
          <a
            href="https://github.com/HardMax71/ResuMariner"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#d6d3d1",
              textDecoration: "none",
              fontWeight: 500,
              display: "inline-flex",
              alignItems: "center",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#818cf8")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#d6d3d1")}
          >
            <Github size={14} />
          </a>
        </div>
      </div>

      <style>{`
        /* Hide footer on mobile - bottom nav is sufficient */
        @media (max-width: 767px) {
          .footer-container {
            display: none !important;
          }
        }

        /* Hide footer when viewport height is small (zoomed in or small screens) */
        @media (max-height: 500px) {
          .footer-container {
            display: none !important;
          }
        }

        /* Tablets in landscape - reduce padding */
        @media (min-width: 768px) and (max-height: 600px) {
          .footer-container {
            padding: 6px 12px !important;
          }
        }
      `}</style>
    </footer>
  );
}
