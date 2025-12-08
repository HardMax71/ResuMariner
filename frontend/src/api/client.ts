// Configure the Hey API client with the base URL
import { client } from './generated';

// Runtime config from window.APP_CONFIG (set by /config.js loaded before React)
declare global {
  interface Window {
    APP_CONFIG?: {
      API_BASE_URL?: string;
      GRAFANA_URL?: string;
    };
  }
}

// Base URL for API requests (generated client paths already include /api prefix)
export const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000";

// Configure the global client with our base URL
client.setConfig({
  baseUrl: API_BASE_URL,
});

// Re-export the configured client
export { client };

// Re-export all generated SDK functions and types
export * from './generated';
