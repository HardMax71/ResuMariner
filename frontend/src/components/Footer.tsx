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
        background: "rgba(var(--neutral-950-rgb), 0.95)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderTop: "1px solid rgba(var(--primary-400-rgb), 0.15)",
        padding: "var(--space-1) var(--space-2)",
      }}
    >
      <div
        className="footer-content"
        style={{
          maxWidth: "var(--container-max-width)",
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "var(--space-2)",
        }}
      >
        {/* Left: Copyright */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "var(--text-xs)",
            color: "var(--neutral-500)",
            fontFamily: "var(--font-body)",
            fontWeight: 500,
            whiteSpace: "nowrap",
          }}
        >
          <span style={{ color: "var(--primary-400)", fontWeight: 700 }}>ResuMariner</span>
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
          <Link to="/privacy" className="footer-link">
            Privacy
          </Link>
          <span className="footer-separator">·</span>
          <Link to="/terms" className="footer-link">
            Terms
          </Link>
          <span className="footer-separator">·</span>
          <Link to="/data-policy" className="footer-link">
            Data
          </Link>
          <span className="footer-separator">·</span>
          <a
            href="https://github.com/HardMax71/ResuMariner"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
            style={{ display: "inline-flex", alignItems: "center" }}
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
