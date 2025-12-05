# Default: production (nginx). Dev mode: docker build --target dev
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

FROM base AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

FROM base AS builder
ARG VITE_API_BASE_URL
ARG VITE_GRAFANA_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_GRAFANA_URL=$VITE_GRAFANA_URL
COPY . .
RUN npm run build

FROM nginx:alpine AS prod
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
