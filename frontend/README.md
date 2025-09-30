# ResuMariner Frontend

React + Vite + TypeScript UI for uploading CVs, tracking processing jobs, running semantic/structured/hybrid search, viewing health, and triggering cleanup.

- Node: 20.17.0 (see .nvmrc)
- Dev server: http://app.localhost (via Traefik)
- API base (CORS): `VITE_API_BASE_URL` defaults to `http://api.localhost`

## Scripts

- `npm ci` – install deps (preferred)
- `npm run dev` – start Vite dev server on 0.0.0.0:5173
- `npm run build` – type-check + build
- `npm run preview` – preview production build

## Env

- `VITE_API_BASE_URL` – API origin, default `http://api.localhost` (Traefik route to backend). Example:

```bash
VITE_API_BASE_URL=http://api.localhost npm run dev
```

## Pages

- Upload – drag & drop single file (PDF/JPG/PNG), validates size: 10MB (PDF), 5MB (images)
- Job – polls status and shows structured result; toggle to view raw JSON
- Search – semantic/structured/hybrid with filters; toggle to view raw JSON
- Health – status and queue summary; toggle to view raw JSON
- Admin – trigger jobs cleanup

## Styling

- Clean, white background. Slightly rounded elements. Accessible contrast.
- Inter font via Google Fonts with system fallbacks.

## Docker

This repo’s docker-compose adds a `frontend` service routed by Traefik at `http://app.localhost` (web entrypoint). Backend is routed at `http://api.localhost` (web entrypoint) and `http://localhost:8000` (backend entrypoint). Direct port 5173 is not published; access via Traefik.
