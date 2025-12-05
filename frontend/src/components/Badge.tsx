import { ReactNode, CSSProperties } from "react";

export interface BadgeProps {
  children: ReactNode;
  variant?: "primary" | "success" | "warning" | "error";
  style?: CSSProperties;
  title?: string;
}

export default function Badge({
  children,
  variant = "primary",
  style = {},
  title
}: BadgeProps) {
  const className = `badge badge-${variant}`;

  return (
    <span className={className} style={style} title={title}>
      {children}
    </span>
  );
}
