FROM oven/bun:latest AS base

WORKDIR /app

ENV NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Copy package files
COPY package.json bun.lock* ./

# Install all dependencies (including devDependencies for build)
RUN bun install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Build the Next.js application
RUN bun run build

FROM oven/bun:latest AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_TELEMETRY_DISABLED=1

# Copy built output from builder
COPY --from=base /app/.next ./.next
COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/package.json ./package.json
COPY --from=base /app/public ./public

EXPOSE 3000

# Run in production mode
CMD ["bun", "run", "start"]
