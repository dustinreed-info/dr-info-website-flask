# Build the Astro static site, then serve it with nginx.
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG PUBLIC_LAMBDA_ENDPOINT
ENV PUBLIC_LAMBDA_ENDPOINT=$PUBLIC_LAMBDA_ENDPOINT
RUN npm run build

# Run Playwright e2e tests (Debian base — browsers pre-installed; Alpine is unreliable).
FROM mcr.microsoft.com/playwright:v1.61.1-jammy AS test
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ENV CI=true
RUN npm test

# Export only dist/ for CI S3 sync (BuildKit: -o type=local,dest=./dist).
FROM scratch AS export
COPY --from=build /app/dist /

FROM nginx:alpine AS prod
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
