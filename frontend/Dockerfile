# Dev-time container running Vite on port 5173
FROM node:20.17.0-alpine

WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* bun.lockb* .npmrc* ./
RUN npm ci || npm i

COPY . .

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://api.localhost}

EXPOSE 5173
CMD ["npm", "run", "dev"]

