import { Component, ErrorInfo, ReactNode } from 'react';
import styled from '@emotion/styled';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

const ErrorContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--neutral-50) 0%, var(--neutral-200) 50%, var(--neutral-300) 100%);
  padding: var(--space-4);
`;

const ErrorCard = styled.div`
  width: 100%;
  max-width: 90%;
  background: rgba(var(--neutral-0-rgb), 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid var(--accent2-200);
  border-radius: var(--radius-sm);
  padding: var(--space-6);
  box-shadow: 0 8px 32px rgba(var(--accent2-600-rgb), 0.12);

  @media (min-width: 768px) {
    max-width: 50%;
  }
`;

const ErrorIcon = styled.div`
  width: 64px;
  height: 64px;
  margin: 0 auto var(--space-4);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent2-100);
  border-radius: var(--radius-sm);
  color: var(--accent2-600);
`;

const ErrorTitle = styled.h1`
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--neutral-900);
  text-align: center;
  margin-bottom: var(--space-2);
`;

const ErrorMessage = styled.p`
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--neutral-600);
  text-align: center;
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-4);
`;

const ErrorDetails = styled.details`
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: var(--neutral-50);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--neutral-700);
  cursor: pointer;

  summary {
    font-family: var(--font-body);
    font-weight: 600;
    color: var(--neutral-800);
    margin-bottom: var(--space-2);
    user-select: none;
  }

  pre {
    margin-top: var(--space-2);
    white-space: pre-wrap;
    word-break: break-word;
    line-height: var(--leading-relaxed);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-5);
  flex-wrap: wrap;

  @media (max-width: 640px) {
    flex-direction: column;
  }
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 600;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);

  ${props => props.variant === 'primary' ? `
    background: var(--primary-600);
    color: white;

    &:hover:not(:disabled) {
      background: var(--primary-700);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(var(--primary-600-rgb), 0.3);
    }
  ` : `
    background: white;
    color: var(--neutral-700);
    border: 1px solid var(--neutral-300);

    &:hover:not(:disabled) {
      background: var(--neutral-50);
      border-color: var(--neutral-400);
    }
  `}

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

interface Props {
  children: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });

    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Call optional error handler
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  handleGoHome = (): void => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo } = this.state;

      return (
        <ErrorContainer>
          <ErrorCard>
            <ErrorIcon>
              <AlertTriangle size={32} strokeWidth={2} />
            </ErrorIcon>

            <ErrorTitle>Something went wrong</ErrorTitle>

            <ErrorMessage>
              We're sorry, but something unexpected happened. The error has been logged
              and we'll look into it. You can try refreshing the page or return to the
              homepage.
            </ErrorMessage>

            {import.meta.env.DEV && error && (
              <ErrorDetails>
                <summary>Error Details (Development Only)</summary>
                <pre>
                  <strong>Error:</strong> {error.toString()}
                  {errorInfo?.componentStack && (
                    <>
                      {'\n\n'}
                      <strong>Component Stack:</strong>
                      {errorInfo.componentStack}
                    </>
                  )}
                </pre>
              </ErrorDetails>
            )}

            <ButtonGroup>
              <Button variant="primary" onClick={this.handleReset}>
                <RefreshCw size={16} />
                Try Again
              </Button>
              <Button variant="secondary" onClick={this.handleGoHome}>
                <Home size={16} />
                Go to Homepage
              </Button>
            </ButtonGroup>
          </ErrorCard>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}
