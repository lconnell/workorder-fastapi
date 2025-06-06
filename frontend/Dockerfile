# Dockerfile for SvelteKit app on Fly.io

# ---- Build Stage ----
FROM oven/bun:1-alpine AS builder

# Set working directory
WORKDIR /app

# Accept build-time environment variables for Fly.io
ARG PUBLIC_API_BASE_URL
ARG PUBLIC_SUPABASE_URL
ARG PUBLIC_SUPABASE_ANON_KEY

ENV PUBLIC_API_BASE_URL=$PUBLIC_API_BASE_URL
ENV PUBLIC_SUPABASE_URL=$PUBLIC_SUPABASE_URL
ENV PUBLIC_SUPABASE_ANON_KEY=$PUBLIC_SUPABASE_ANON_KEY

# Copy package.json and lockfile
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy the frontend application code
COPY . .

# Build the application
RUN bun run build

# ---- Production Stage ----
FROM nginx:1.25-alpine

# Install Node.js for SvelteKit adapter-node (if needed)
RUN apk add --no-cache nodejs npm

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from the builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy start script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port 3000 for Fly.io
EXPOSE 3000

# Update nginx to listen on port 3000
RUN sed -i 's/listen       80;/listen       3000;/' /etc/nginx/conf.d/default.conf

# Start Nginx
CMD ["/docker-entrypoint.sh"]
