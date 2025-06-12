FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci

# Copy source code
COPY src/ ./src/

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runtime

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S mcp -u 1001 -G nodejs

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Change ownership to non-root user
RUN chown -R mcp:nodejs /app
USER mcp

# Set environment variables
ENV NODE_ENV=production
ENV NODE_OPTIONS="--unhandled-rejections=strict"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "console.log('Server is healthy')" || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the server
CMD ["node", "dist/index.js"]

# Metadata
LABEL org.opencontainers.image.title="GAIA Sequential Thinking MCP Server"
LABEL org.opencontainers.image.description="Dynamic and reflective problem-solving through thought sequences"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.authors="GAIA Team"
LABEL org.opencontainers.image.source="https://github.com/your-org/GAIA_LLMs"
LABEL org.opencontainers.image.licenses="MIT"