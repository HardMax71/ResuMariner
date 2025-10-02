import { ReactNode } from "react";
import { FlexRow } from "./styled";
import { IconWrapper } from "./styled/Card";
import styled from "@emotion/styled";

const PageHeaderIcon = styled(IconWrapper)`
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
  box-shadow: 0 4px 12px rgba(67, 56, 202, 0.25);
`;

const PageHeaderTitle = styled.h1`
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: 800;
  letter-spacing: var(--tracking-tight);
  color: var(--neutral-900);
`;

const PageHeaderSubtitle = styled.p`
  margin: 0;
  font-size: var(--text-sm);
  color: var(--neutral-600);
`;

interface PageHeaderProps {
  icon?: ReactNode;
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export default function PageHeader({ icon, title, subtitle, actions }: PageHeaderProps) {
  return (
    <FlexRow justify="space-between" align="center" style={{ marginBottom: "var(--space-5)" }}>
      <FlexRow gap="var(--space-3)" align="center">
        {icon && (
          <PageHeaderIcon>
            {icon}
          </PageHeaderIcon>
        )}
        <div>
          <PageHeaderTitle>{title}</PageHeaderTitle>
          {subtitle && <PageHeaderSubtitle>{subtitle}</PageHeaderSubtitle>}
        </div>
      </FlexRow>
      {actions && <div>{actions}</div>}
    </FlexRow>
  );
}
