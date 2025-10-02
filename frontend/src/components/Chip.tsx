import { ReactNode, CSSProperties } from "react";

interface ChipProps {
  children: ReactNode;
  selected?: boolean;
  selectable?: boolean;
  count?: number;
  onClick?: (e: React.MouseEvent) => void;
  onRemove?: () => void;
  title?: string;
  style?: CSSProperties;
}

export default function Chip({
  children,
  selected = false,
  selectable = false,
  count,
  onClick,
  onRemove,
  title,
  style = {}
}: ChipProps) {
  const classes = [
    "chip",
    selectable && "selectable",
    selected && "selected"
  ].filter(Boolean).join(" ");

  const content = (
    <>
      {children}
      {count !== undefined && (
        <span style={{ opacity: 0.6, marginLeft: "4px" }}>
          {count}
        </span>
      )}
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          style={{
            marginLeft: "4px",
            background: "none",
            border: "none",
            cursor: "pointer",
            padding: 0,
          }}
        >
          ×
        </button>
      )}
    </>
  );

  if (selectable || onClick) {
    return (
      <button
        type="button"
        className={classes}
        onClick={onClick}
        title={title}
        style={style}
      >
        {content}
      </button>
    );
  }

  return (
    <span className={classes} title={title} style={style}>
      {content}
    </span>
  );
}
