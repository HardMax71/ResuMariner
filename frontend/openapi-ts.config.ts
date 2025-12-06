import { defineConfig } from '@hey-api/openapi-ts';

// Use OPENAPI_URL env var, or default to localhost:8000 (backend via traefik)
// For container generation: OPENAPI_URL=http://backend:8000/api/schema/
const inputUrl = process.env.OPENAPI_URL || 'http://localhost:8000/api/schema/';

export default defineConfig({
  client: '@hey-api/client-fetch',
  input: inputUrl,
  output: {
    path: 'src/api/generated',
  },
  plugins: [
    '@hey-api/typescript',  // Generate TypeScript types
    '@hey-api/sdk',         // Generate SDK client
  ],
});
