# Build stage
FROM node:25-alpine AS builder

WORKDIR /app

# Build-time environment for Vite
ARG VITE_API_URL
ARG VITE_WS_URL
ARG VITE_SIGNALK_HOST
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL
ENV VITE_SIGNALK_HOST=$VITE_SIGNALK_HOST

# Copy package files
COPY package*.json ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit --no-fund

# Copy source files
COPY . .

# Build application with production optimizations
RUN npm run build

# Runtime stage
FROM nginx:1.29-alpine

# Set labels for better container management
LABEL maintainer="aads-team" \
      version="1.0" \
      description="AADS Frontend served by nginx"

# Remove default nginx content and configs
RUN rm -rf /usr/share/nginx/html/* \
    && rm /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add security headers and hardening
RUN echo 'server_tokens off;' > /etc/nginx/conf.d/security.conf \
    && chown -R nginx:nginx /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown -R nginx:nginx /var/run/nginx.pid \
    && chmod -R 755 /usr/share/nginx/html

# Security: Remove unnecessary packages and clean up
RUN apk del --purge \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

USER nginx

EXPOSE 80

# Use exec form for proper signal handling
CMD ["nginx", "-g", "daemon off;"]
