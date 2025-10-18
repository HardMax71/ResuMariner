import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { SelectionProvider } from "./contexts/SelectionContext";
import "./styles.css";

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2, // Retry failed queries 2 times
      refetchOnWindowFocus: false, // Don't refetch on window focus
    },
  },
});

const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
  // Log to external error tracking service (e.g., Sentry, LogRocket)
  // For now, just log to console in production
  if (!import.meta.env.DEV) {
    console.error('Application Error:', error);
    console.error('Error Info:', errorInfo);
    // TODO: Send to error tracking service
    // Example: Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
  }
};

const rootEl = document.getElementById("root")!;
createRoot(rootEl).render(
  <React.StrictMode>
    <ErrorBoundary onError={handleError}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SelectionProvider>
            <App />
          </SelectionProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);

