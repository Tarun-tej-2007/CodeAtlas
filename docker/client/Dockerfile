# Stage 1: Base image with libc6-compat for Next.js on Alpine
FROM node:22-alpine AS base
WORKDIR /app
RUN apk add --no-cache libc6-compat

# Stage 2: Install dependencies (both prod and dev dependencies)
FROM base AS deps
COPY client/package.json client/package-lock.json ./
RUN npm ci

# Stage 3: Development environment
FROM base AS development
COPY client/package.json client/package-lock.json ./
RUN npm ci
COPY client/ .
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Stage 4: Production builder
FROM deps AS builder
COPY client/ .
# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 5: Minimal Production runner
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NEXT_TELEMETRY_DISABLED=1

# Create a non-root system user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built code and dependencies
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Adjust permissions for non-root user
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

CMD ["npm", "run", "start"]
