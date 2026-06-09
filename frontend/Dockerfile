FROM oven/bun:latest AS base

WORKDIR /app

ENV NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install

# Copy the rest of the application
COPY . .

EXPOSE 3000

# Run in dev mode with hot reload
CMD ["bun", "run", "dev"]
