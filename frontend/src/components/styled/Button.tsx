import styled from '@emotion/styled';

export const Button = styled.button<{ variant?: 'primary' | 'ghost'; disabled?: boolean }>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: 12px var(--space-4);
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 600;
  line-height: var(--leading-normal);
  color: ${props => props.variant === 'ghost' ? 'var(--neutral-700)' : 'var(--neutral-0)'};
  background-color: ${props => props.variant === 'ghost' ? 'transparent' : 'var(--primary-700)'};
  border: ${props => props.variant === 'ghost' ? '1.5px solid var(--neutral-300)' : 'none'};
  border-radius: var(--radius-sm);
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
  opacity: ${props => props.disabled ? 0.5 : 1};

  &:hover:not(:disabled) {
    background-color: ${props => props.variant === 'ghost' ? 'var(--neutral-50)' : 'var(--primary-800)'};
    border-color: ${props => props.variant === 'ghost' ? 'var(--neutral-400)' : 'transparent'};
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:focus-visible {
    outline: 2px solid var(--primary-500);
    outline-offset: 2px;
  }
`;

export const IconButton = styled.button<{ disabled?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(67, 56, 202, 0.15);
  border-radius: var(--radius-sm);
  color: #4338ca;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  opacity: ${props => props.disabled ? 0.5 : 1};

  &:hover:not(:disabled) {
    background: rgba(67, 56, 202, 0.1);
    transform: translateY(-2px);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;
