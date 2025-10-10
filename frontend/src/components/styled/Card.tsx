import styled from '@emotion/styled';

export const MetricCard = styled.div<{ color?: string; bgColor?: string }>`
  border-top: 3px solid ${props => props.color || 'var(--primary-600)'};
  padding: var(--space-3);
  transition: all 0.2s;
  cursor: default;
  background: ${props => props.bgColor
    ? `linear-gradient(135deg, ${props.bgColor} 0%, rgba(255, 255, 255, 0.95) 100%)`
    : 'rgba(255, 255, 255, 0.95)'};
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(67, 56, 202, 0.15);
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  }
`;

export const MetricLabel = styled.div`
  font-size: 11px;
  color: var(--neutral-700);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-1);
`;

export const MetricValue = styled.div<{ color?: string }>`
  font-size: 1.5rem;
  font-weight: 800;
  color: ${props => props.color || 'var(--neutral-900)'};
  line-height: 1;
`;

export const IconWrapper = styled.div<{ color?: string; bgColor?: string }>`
  padding: 12px;
  background: ${props => props.bgColor || 'linear-gradient(135deg, rgba(67, 56, 202, 0.15) 0%, rgba(67, 56, 202, 0.05) 100%)'};
  border-radius: var(--radius-sm);
  border: 1px solid ${props => props.color || 'rgba(67, 56, 202, 0.2)'};
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

export const StatusBadge = styled.span<{ variant?: 'success' | 'warning' | 'error' }>`
  padding: 6px 12px;
  background: ${props => {
    switch (props.variant) {
      case 'success': return 'rgba(34, 197, 94, 0.15)';
      case 'warning': return 'rgba(245, 158, 11, 0.15)';
      case 'error': return 'rgba(239, 68, 68, 0.15)';
      default: return 'rgba(67, 56, 202, 0.15)';
    }
  }};
  border: 1px solid ${props => {
    switch (props.variant) {
      case 'success': return 'rgba(34, 197, 94, 0.3)';
      case 'warning': return 'rgba(245, 158, 11, 0.3)';
      case 'error': return 'rgba(239, 68, 68, 0.3)';
      default: return 'rgba(67, 56, 202, 0.3)';
    }
  }};
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  color: ${props => {
    switch (props.variant) {
      case 'success': return '#15803d';
      case 'warning': return '#b45309';
      case 'error': return '#b91c1c';
      default: return '#4338ca';
    }
  }};
  letter-spacing: 0.025em;
  text-transform: uppercase;
`;

export const Grid = styled.div<{ columns?: number; gap?: string }>`
  display: grid;
  grid-template-columns: repeat(${props => props.columns || 6}, 1fr);
  gap: ${props => props.gap || 'var(--space-2)'};

  @media (max-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const ScoreHero = styled.div`
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
  margin-bottom: var(--space-5);
  box-shadow: 0 8px 24px rgba(67, 56, 202, 0.2);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    pointer-events: none;
  }
`;

export const ScoreValue = styled.div`
  font-size: 64px;
  font-weight: 800;
  font-family: var(--font-display);
  color: white;
  line-height: 1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);

  span {
    font-size: 32px;
    font-weight: 700;
    opacity: 0.8;
  }
`;

export const FeedbackSection = styled.div<{ isExpanded?: boolean; priorityColor?: string; priorityBg?: string }>`
  padding: 0;
  overflow: hidden;
  transition: all var(--transition-base);
  cursor: pointer;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(67, 56, 202, 0.15);
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
`;

export const SectionHeader = styled.div<{ isExpanded?: boolean; priorityColor?: string; priorityBg?: string }>`
  padding: var(--space-3) var(--space-4);
  background: ${props => props.priorityBg || 'var(--primary-50)'};
  border-bottom: ${props => props.isExpanded ? `1px solid ${props.priorityColor}20` : 'none'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  user-select: none;
  transition: background var(--transition-fast);

  &:hover {
    background: ${props => !props.isExpanded ? `${props.priorityColor}15` : props.priorityBg};
  }
`;

export const PriorityIndicator = styled.div<{ color?: string }>`
  width: 4px;
  height: 32px;
  background: ${props => props.color || 'var(--primary-600)'};
  border-radius: var(--radius-full);
`;

export const FeedbackBadge = styled.span<{ variant?: 'critical' | 'important' | 'tip' }>`
  padding: 2px 8px;
  background: ${props => {
    switch (props.variant) {
      case 'critical': return 'var(--accent2-100)';
      case 'important': return 'var(--accent1-100)';
      case 'tip': return 'var(--primary-100)';
      default: return 'var(--primary-100)';
    }
  }};
  color: ${props => {
    switch (props.variant) {
      case 'critical': return 'var(--accent2-700)';
      case 'important': return 'var(--accent1-700)';
      case 'tip': return 'var(--primary-700)';
      default: return 'var(--primary-700)';
    }
  }};
  font-size: var(--text-xs);
  font-weight: 600;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  gap: 4px;
`;

export const FeedbackDot = styled.span<{ variant?: 'critical' | 'important' | 'tip' }>`
  width: 6px;
  height: 6px;
  background: ${props => {
    switch (props.variant) {
      case 'critical': return 'var(--accent2-600)';
      case 'important': return 'var(--accent1-600)';
      case 'tip': return 'var(--primary-600)';
      default: return 'var(--primary-600)';
    }
  }};
  border-radius: 50%;
`;

export const FeedbackItem = styled.div<{
  variant?: 'critical' | 'important' | 'tip';
  bgColor?: string;
  borderColor?: string;
  dotColor?: string;
}>`
  padding: 0;
  background: transparent;
  border: none;
  display: flex;
  gap: 8px;

  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${props => props.dotColor || 'var(--neutral-400)'};
    margin-top: 6px;
    margin-left: 6px;
    flex-shrink: 0;
  }
`;

export const ConfigGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
`;

export const ConfigRow = styled.div<{ bgColor?: string; borderColor?: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2);
  background: ${props => props.bgColor || 'rgba(67, 56, 202, 0.03)'};
  border-radius: var(--radius-sm);
  border: 1px solid ${props => props.borderColor || 'rgba(67, 56, 202, 0.1)'};
`;

export const ConfigLabel = styled.span`
  font-size: 12px;
  color: var(--neutral-600);
  font-weight: 500;
`;

export const ConfigTag = styled.span<{ emphasis?: boolean }>`
  padding: 2px 6px;
  background: ${props => props.emphasis ? 'rgba(67, 56, 202, 0.15)' : 'rgba(67, 56, 202, 0.1)'};
  border: 1px solid ${props => props.emphasis ? 'rgba(67, 56, 202, 0.25)' : 'rgba(67, 56, 202, 0.2)'};
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
  color: #4338ca;
  font-family: var(--font-mono);
`;

export const ToggleBadge = styled.span<{ isOn?: boolean }>`
  padding: 3px 8px;
  background: ${props => props.isOn ? 'rgba(34, 197, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)'};
  border: 1px solid ${props => props.isOn ? 'rgba(34, 197, 94, 0.3)' : 'rgba(245, 158, 11, 0.3)'};
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 700;
  color: ${props => props.isOn ? '#15803d' : '#b45309'};
  letter-spacing: 0.025em;
`;

export const SectionTitle = styled.h3`
  font-size: 14px;
  font-weight: 700;
  color: var(--neutral-900);
  margin-bottom: var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

export const SubsectionTitle = styled.h4<{ color?: string }>`
  font-size: 13px;
  font-weight: 600;
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
  display: flex;
  align-items: center;
  gap: 6px;
`;
