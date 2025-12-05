import { useLocation, Link } from "react-router-dom";
import { Home, AlertTriangle, RefreshCw } from "lucide-react";
import { PageWrapper, PageContainer } from "../components/styled";

interface ErrorDetails {
  message?: string;
  status?: number;
  statusText?: string;
  stack?: string;
  data?: any;
  timestamp?: string;
}

function parseError(error: any): ErrorDetails {
  const timestamp = new Date().toISOString();

  if (error?.status !== undefined) {
    return {
      message: error.message || error.statusText || "Unknown error",
      status: error.status,
      statusText: error.statusText,
      data: error.data,
      timestamp
    };
  }

  if (error?.statusCode !== undefined) {
    return {
      message: error.message || "API request failed",
      status: error.statusCode,
      data: error.response,
      stack: error.stack,
      timestamp
    };
  }

  if (error?.name === 'NetworkError') {
    return {
      message: error.message || "Network request failed",
      status: 0,
      statusText: "Network Error",
      stack: error.stack,
      timestamp
    };
  }

  if (error instanceof Error) {
    const e = error as Error;
    return {
      message: e.message,
      stack: e.stack,
      statusText: e.name,
      timestamp
    };
  }

  return {
    message: String(error) || "An unexpected error occurred",
    data: error,
    timestamp
  };
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

  return (
    <PageWrapper>
      <PageContainer>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "calc(100vh - 200px)",
          paddingTop: "var(--space-8)"
        }}>
          <div className="glass-card" style={{
            maxWidth: "900px",
            width: "100%",
            padding: "var(--space-8)",
            textAlign: "center"
          }}>
            <div style={{
              width: "80px",
              height: "80px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "linear-gradient(135deg, rgba(225, 29, 72, 0.15) 0%, rgba(225, 29, 72, 0.05) 100%)",
              border: "1px solid rgba(225, 29, 72, 0.2)",
              borderRadius: "var(--radius-sm)",
              margin: "0 auto var(--space-4)"
            }}>
              <AlertTriangle size={40} strokeWidth={2} color="var(--accent2-600)" />
            </div>

            {errorDetails.status && (
              <div style={{
                fontFamily: "var(--font-display)",
                fontSize: "clamp(3rem, 10vw, 5rem)",
                fontWeight: 800,
                lineHeight: 1,
                color: "var(--accent2-600)",
                marginBottom: "var(--space-3)",
                letterSpacing: "var(--tracking-tight)"
              }}>
                {errorDetails.status}
              </div>
            )}

            <h1 style={{
              fontFamily: "var(--font-display)",
              fontSize: "clamp(1.75rem, 4vw, 2.5rem)",
              fontWeight: 700,
              color: "var(--neutral-900)",
              marginBottom: "var(--space-3)",
              letterSpacing: "var(--tracking-tight)"
            }}>
              {errorDetails.statusText ||
               (isNotFound ? "Page Not Found" : isServerError ? "Server Error" : "Something Went Wrong")}
            </h1>

            <p style={{
              fontSize: "var(--text-lg)",
              color: "var(--neutral-600)",
              lineHeight: "var(--leading-relaxed)",
              marginBottom: "var(--space-5)",
              maxWidth: "600px",
              margin: "0 auto var(--space-5)"
            }}>
              {errorDetails.message}
            </p>

            <pre style={{
              background: "var(--neutral-50)",
              border: "1px solid var(--neutral-200)",
              borderRadius: "var(--radius-sm)",
              padding: "var(--space-4)",
              margin: "var(--space-4) 0",
              fontFamily: "var(--font-mono)",
              fontSize: "var(--text-xs)",
              color: "var(--neutral-700)",
              overflow: "auto",
              textAlign: "left",
              lineHeight: "var(--leading-relaxed)",
              maxHeight: "400px"
            }}>
{`Error Details:

Type: ${errorDetails.statusText || 'Unknown'}
${errorDetails.status ? `Status Code: ${errorDetails.status}\n` : ''}Message: ${errorDetails.message}
Timestamp: ${errorDetails.timestamp}

Location:
  Path: ${location.pathname}
  Search: ${location.search || '(none)'}
  Hash: ${location.hash || '(none)'}

${errorDetails.data ? `Response Data:
${JSON.stringify(errorDetails.data, null, 2)}

` : ''}${errorDetails.stack ? `Stack Trace:
${errorDetails.stack}` : 'Stack trace not available'}`}
            </pre>

            <div style={{
              display: "flex",
              gap: "var(--space-2)",
              justifyContent: "center",
              flexWrap: "wrap",
              marginTop: "var(--space-5)"
            }}>
              <button
                onClick={() => window.location.reload()}
                className="btn"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "var(--space-1)"
                }}
              >
                <RefreshCw size={16} />
                Reload Page
              </button>
              <Link
                to="/"
                className="btn ghost"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "var(--space-1)"
                }}
              >
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
