import { useLocation, Link } from "react-router-dom";
import { Home, AlertTriangle, RefreshCw } from "lucide-react";
import { PageWrapper, PageContainer } from "../components/styled";

interface ErrorState {
  message?: string;
  status?: number;
  statusCode?: number;
  statusText?: string;
  name?: string;
  stack?: string;
  data?: unknown;
  response?: unknown;
}

interface LocationState {
  error?: ErrorState;
}

interface ErrorDetails {
  message: string;
  status?: number;
  statusText?: string;
  stack?: string;
  data?: unknown;
  timestamp: string;
}

function buildErrorDetails(error: ErrorState): ErrorDetails {
  return {
    message: error.message ?? error.statusText ?? "Unknown error",
    status: error.status ?? error.statusCode,
    statusText: error.statusText ?? error.name,
    stack: error.stack,
    data: error.data ?? error.response,
    timestamp: new Date().toISOString()
  };
}

function formatErrorDetails(
  errorDetails: ErrorDetails,
  location: ReturnType<typeof useLocation>
): string {
  const statusLine = errorDetails.status ? `Status Code: ${errorDetails.status}\n` : '';
  const dataBlock = errorDetails.data
    ? `Response Data:\n${JSON.stringify(errorDetails.data, null, 2)}\n\n`
    : '';
  const stackBlock = errorDetails.stack
    ? `Stack Trace:\n${errorDetails.stack}`
    : 'Stack trace not available';

  return `Error Details:

Type: ${errorDetails.statusText ?? 'Unknown'}
${statusLine}Message: ${errorDetails.message}
Timestamp: ${errorDetails.timestamp}

Location:
  Path: ${location.pathname}
  Search: ${location.search || '(none)'}
  Hash: ${location.hash || '(none)'}

${dataBlock}${stackBlock}`;
}

export default function Error() {
  const location = useLocation();
  const state = location.state as LocationState | null;

  const error: ErrorState = state?.error ?? {
    status: 404,
    statusText: "Not Found",
    message: `The page "${location.pathname}" does not exist.`
  };

  const errorDetails = buildErrorDetails(error);
  const isNotFound = errorDetails.status === 404;
  const isServerError = (errorDetails.status ?? 0) >= 500;

  const title = errorDetails.statusText
    ?? (isNotFound ? "Page Not Found" : isServerError ? "Server Error" : "Something Went Wrong");

  return (
    <PageWrapper>
      <PageContainer>
        <div className="error-page-container">
          <div className="glass-card error-card">
            <div className="error-icon-wrapper">
              <AlertTriangle size={40} strokeWidth={2} color="var(--accent2-600)" />
            </div>

            {errorDetails.status && (
              <div className="error-status-code">
                {errorDetails.status}
              </div>
            )}

            <h1 className="error-title">{title}</h1>

            <p className="error-message">{errorDetails.message}</p>

            <pre className="error-details">
              {formatErrorDetails(errorDetails, location)}
            </pre>

            <div className="error-actions">
              <button
                onClick={() => window.location.reload()}
                className="btn error-btn"
              >
                <RefreshCw size={16} />
                Reload Page
              </button>
              <Link to="/" className="btn ghost error-btn">
                <Home size={16} />
                Go Home
              </Link>
            </div>
          </div>
        </div>
      </PageContainer>
    </PageWrapper>
  );
}
