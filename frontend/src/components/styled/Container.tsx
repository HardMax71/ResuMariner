import styled from '@emotion/styled';

export const PageWrapper = styled.div`
  position: absolute;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  background-attachment: fixed;
  padding-top: 40px;
  padding-bottom: var(--space-6);
  overflow-y: auto;
  overflow-x: hidden;
`;

export const PageContainer = styled.div`
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--container-padding);
  position: relative;
  z-index: 1;
`;

export const GlassCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(67, 56, 202, 0.15);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
`;

export const FlexRow = styled.div<{ gap?: string; justify?: string; align?: string }>`
  display: flex;
  gap: ${props => props.gap || 'var(--space-2)'};
  justify-content: ${props => props.justify || 'flex-start'};
  align-items: ${props => props.align || 'center'};
`;

export const FlexColumn = styled.div<{ gap?: string; align?: string; justify?: string }>`
  display: flex;
  flex-direction: column;
  gap: ${props => props.gap || 'var(--space-2)'};
  align-items: ${props => props.align || 'stretch'};
  justify-content: ${props => props.justify || 'flex-start'};
`;

export const ErrorCard = styled(GlassCard)`
  background: var(--accent2-50);
  border: 1px solid var(--accent2-200);
  padding: var(--space-4);
  margin-bottom: var(--space-3);
`;

export const EmptyStateCard = styled(GlassCard)`
  text-align: center;
  padding: var(--space-8) var(--space-4);
`;

export const DecorativeBlur = styled.div<{ position?: 'top-right' | 'bottom-left' }>`
  position: absolute;
  ${props => props.position === 'bottom-left' ? 'bottom: 20%; left: -5%;' : 'top: 10%; right: -5%;'}
  width: ${props => props.position === 'bottom-left' ? '400px' : '500px'};
  height: ${props => props.position === 'bottom-left' ? '400px' : '500px'};
  background: ${props => props.position === 'bottom-left'
    ? 'radial-gradient(circle, rgba(245, 158, 11, 0.06) 0%, transparent 70%)'
    : 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)'};
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
`;

export const Spinner = styled.div`
  width: 48px;
  height: 48px;
  border: 3px solid var(--primary-100);
  border-top-color: var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
