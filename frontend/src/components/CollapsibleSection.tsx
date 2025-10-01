import { ReactNode } from "react";

interface CollapsibleSectionProps {
  title: string;
  badge?: number | string;
  children: ReactNode;
  // Controlled mode
  isExpanded?: boolean;
  onToggle?: () => void;
  // Uncontrolled mode (native details)
  defaultOpen?: boolean;
  // Optional custom styles
  headerStyle?: React.CSSProperties;
  containerStyle?: React.CSSProperties;
  containerClassName?: string;
}

export default function CollapsibleSection({
  title,
  badge,
  children,
  isExpanded,
  onToggle,
  defaultOpen = false,
  headerStyle = {},
  containerStyle = {},
  containerClassName = ""
}: CollapsibleSectionProps) {
  const isControlled = isExpanded !== undefined && onToggle !== undefined;

  // Controlled mode
  if (isControlled) {
    return (
      <div className={containerClassName} style={containerStyle}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            cursor: "pointer",
            userSelect: "none",
            ...headerStyle
          }}
          onClick={onToggle}
        >
          <h3 className="title" style={{ margin: 0, lineHeight: 1, display: "flex", alignItems: "center" }}>
            {title}
            {badge !== undefined && badge !== null && (
              <span className="badge badge-primary" style={{ marginLeft: "var(--space-1)" }}>
                {badge}
              </span>
            )}
          </h3>
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            style={{
              flexShrink: 0,
              display: "block",
              transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.2s ease"
            }}
          >
            <path d="M7 10l5 5 5-5" />
          </svg>
        </div>
        {isExpanded && children}
      </div>
    );
  }

  // Uncontrolled mode using native details
  return (
    <details open={defaultOpen} className={containerClassName} style={containerStyle}>
      <summary
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          cursor: "pointer",
          userSelect: "none",
          listStyle: "none",
          ...headerStyle
        }}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="chevron"
          style={{ flexShrink: 0, display: "block" }}
        >
          <path d="M7 10l5 5 5-5" />
        </svg>
        <span className="title" style={{ margin: 0, lineHeight: 1, display: "flex", alignItems: "center" }}>
          {title}
          {badge !== undefined && badge !== null && (
            <span className="badge badge-primary" style={{ marginLeft: "var(--space-1)" }}>
              {badge}
            </span>
          )}
        </span>
      </summary>
      {children}
    </details>
  );
}
