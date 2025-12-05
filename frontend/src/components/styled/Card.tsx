import styled from '@emotion/styled';

export const MetricCard = styled.div<{ color?: string; bgColor?: string }>`
  border-top: 3px solid ${props => props.color || 'var(--primary-600)'};
  padding: var(--space-3);
  transition: all 0.2s;
  cursor: default;
  background: ${props => props.bgColor
    ? `linear-gradient(135deg, ${props.bgColor} 0%, rgba(var(--neutral-0-rgb), 0.95) 100%)`
    : 'rgba(var(--neutral-0-rgb), 0.95)'};
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(var(--primary-700-rgb), 0.15);
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
  background: ${props => props.bgColor || 'linear-gradient(135deg, rgba(var(--primary-700-rgb), 0.15) 0%, rgba(var(--primary-700-rgb), 0.05) 100%)'};
  border-radius: var(--radius-sm);
  border: 1px solid ${props => props.color || 'rgba(var(--primary-700-rgb), 0.2)'};
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;

export const StatusBadge = styled.span<{ variant?: 'success' | 'warning' | 'error' }>`
  padding: 6px 12px;
  background: ${props => {
    switch (props.variant) {
      case 'success': return 'rgba(var(--green-500-rgb), 0.15)';
      case 'warning': return 'rgba(var(--accent1-500-rgb), 0.15)';
      case 'error': return 'rgba(var(--red-500-rgb), 0.15)';
      default: return 'rgba(var(--primary-700-rgb), 0.15)';
    }
  }};
  border: 1px solid ${props => {
    switch (props.variant) {
      case 'success': return 'rgba(var(--green-500-rgb), 0.3)';
      case 'warning': return 'rgba(var(--accent1-500-rgb), 0.3)';
      case 'error': return 'rgba(var(--red-500-rgb), 0.3)';
      default: return 'rgba(var(--primary-700-rgb), 0.3)';
    }
  }};
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  color: ${props => {
    switch (props.variant) {
      case 'success': return 'var(--accent3-700)';
      case 'warning': return 'var(--accent1-700)';
      case 'error': return 'var(--accent2-700)';
      default: return 'var(--primary-700)';
    }
  }};
  letter-spacing: 0.025em;
  text-transform: uppercase;
`;

export const Grid = styled.div<{ columns?: number; gap?: string }>`
  display: grid;
  grid-template-columns: repeat(${props => props.columns || 6}, 1fr);
  gap: ${props => props.gap || 'var(--space-2)'};

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

export const ScoreHero = styled.div`
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
  margin-bottom: var(--space-5);
  box-shadow: 0 8px 24px rgba(var(--primary-700-rgb), 0.2);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 30vw;
    height: 30vw;
    background: radial-gradient(circle, rgba(var(--neutral-0-rgb), 0.1) 0%, transparent 70%);
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
  background: rgba(var(--neutral-0-rgb), 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(var(--primary-700-rgb), 0.15);
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
`;

export const SectionHeader = styled.div<{ isExpanded?: boolean; priorityColor?: string; priorityBg?: string }>`
  padding: var(--space-3) var(--space-4);
  background: ${props => props.priorityBg || 'var(--primary-50)'};
  border-bottom: ${props => props.isExpanded ? `1px solid ${props.priorityColor}20` : '1px solid transparent'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  user-select: none;
  transition: all var(--transition-base);

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
  align-items: flex-start;

  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${props => props.dotColor || 'var(--neutral-400)'};
    margin-top: 6px;
    flex-shrink: 0;
  }
`;

export const ConfigGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr));
  gap: var(--space-4);
`;

export const ConfigRow = styled.div<{ bgColor?: string; borderColor?: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2);
  background: ${props => props.bgColor || 'rgba(var(--primary-700-rgb), 0.03)'};
  border-radius: var(--radius-sm);
  border: 1px solid ${props => props.borderColor || 'rgba(var(--primary-700-rgb), 0.1)'};
`;

export const ConfigLabel = styled.span`
  font-size: 12px;
  color: var(--neutral-600);
  font-weight: 500;
`;

export const ConfigTag = styled.span<{ emphasis?: boolean }>`
  padding: 2px 6px;
  background: ${props => props.emphasis ? 'rgba(var(--primary-700-rgb), 0.15)' : 'rgba(var(--primary-700-rgb), 0.1)'};
  border: 1px solid ${props => props.emphasis ? 'rgba(var(--primary-700-rgb), 0.25)' : 'rgba(var(--primary-700-rgb), 0.2)'};
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
  color: var(--primary-700);
  font-family: var(--font-mono);
`;

export const ToggleBadge = styled.span<{ isOn?: boolean }>`
  padding: 3px 8px;
  background: ${props => props.isOn ? 'rgba(var(--green-500-rgb), 0.15)' : 'rgba(var(--accent1-500-rgb), 0.15)'};
  border: 1px solid ${props => props.isOn ? 'rgba(var(--green-500-rgb), 0.3)' : 'rgba(var(--accent1-500-rgb), 0.3)'};
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 700;
  color: ${props => props.isOn ? 'var(--accent3-700)' : 'var(--accent1-700)'};
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
