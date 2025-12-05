import { useLocation, Link } from "react-router-dom";
import { Home, AlertTriangle, RefreshCw } from "lucide-react";
import { PageWrapper, PageContainer } from "../components/styled";

interface ErrorDetails {
  message?: string;
  status?: number;
  statusText?: string;
  stack?: string;
  data?: unknown;
  timestamp?: string;
}

function parseError(error: unknown): ErrorDetails {
  const timestamp = new Date().toISOString();

  if (typeof error === 'object' && error !== null) {
    const err = error as Record<string, unknown>;

    if (err.status !== undefined) {
      return {
        message: String(err.message || err.statusText || "Unknown error"),
        status: Number(err.status),
        statusText: err.statusText as string | undefined,
        data: err.data,
        timestamp
      };
    }

    if (err.statusCode !== undefined) {
      return {
        message: String(err.message || "API request failed"),
        status: Number(err.statusCode),
        data: err.response,
        stack: err.stack as string | undefined,
        timestamp
      };
    }

    if (err.name === 'NetworkError') {
      return {
        message: String(err.message || "Network request failed"),
        status: 0,
        statusText: "Network Error",
        stack: err.stack as string | undefined,
        timestamp
      };
    }

    if (error instanceof Error) {
      return {
        message: error.message,
        stack: error.stack,
        statusText: error.name,
        timestamp
      };
    }
  }

  return {
    message: String(error) || "An unexpected error occurred",
    data: error,
    timestamp
  };
}

function formatErrorDetails(
  errorDetails: ErrorDetails,
  location: ReturnType<typeof useLocation>
): string {
  let output = `Error Details:

Type: ${errorDetails.statusText || 'Unknown'}
`;

  if (errorDetails.status) {
    output += `Status Code: ${errorDetails.status}\n`;
  }

  output += `Message: ${errorDetails.message}
Timestamp: ${errorDetails.timestamp}

Location:
  Path: ${location.pathname}
  Search: ${location.search || '(none)'}
  Hash: ${location.hash || '(none)'}

`;

  if (errorDetails.data) {
    output += `Response Data:
${JSON.stringify(errorDetails.data, null, 2)}

`;
  }

  output += errorDetails.stack
    ? `Stack Trace:\n${errorDetails.stack}`
    : 'Stack trace not available';

  return output;
}

export default function Error() {
  const location = useLocation();

  const error = location.state?.error || {
    status: 404,
    statusText: "Not Found",
    message: `The page "${location.pathname}" does not exist.`
  };
  const errorDetails = parseError(error);

  const isNotFound = errorDetails.status === 404;
  const isServerError = errorDetails.status && errorDetails.status >= 500;

  const title = errorDetails.statusText ||
    (isNotFound ? "Page Not Found" : isServerError ? "Server Error" : "Something Went Wrong");

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
