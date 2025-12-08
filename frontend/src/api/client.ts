// Configure the Hey API client with the base URL
import { client } from './generated';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// Configure the global client with our base URL
client.setConfig({
  baseUrl: API_BASE_URL,
});

// Re-export the configured client
export { client };

// Re-export all generated SDK functions and types
export * from './generated';
