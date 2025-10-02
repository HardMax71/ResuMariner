import { ReactNode, CSSProperties } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "primary";
  style?: CSSProperties;
}

export default function Badge({
  children,
  variant = "primary",
  style = {}
}: BadgeProps) {
  const className = variant === "primary" ? "badge badge-primary" : "badge";

  return (
    <span className={className} style={style}>
      {children}
    </span>
  );
}
