import { ReactNode } from "react";
import { ChevronDown } from "lucide-react";

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
          <ChevronDown
            size={20}
            strokeWidth={2}
            style={{
              flexShrink: 0,
              display: "block",
              transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
              transition: "transform 0.2s ease"
            }}
          />
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
        <ChevronDown
          size={16}
          strokeWidth={2}
          className="chevron"
          style={{ flexShrink: 0, display: "block" }}
        />
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
