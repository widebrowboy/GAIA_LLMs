#!/bin/bash

# GAIA MCP Build Script
# Builds all MCP servers (Docker and NPM)

set -e

echo "🔨 Building GAIA MCP Servers..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ to continue."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Skipping Docker builds."
    SKIP_DOCKER=true
else
    SKIP_DOCKER=false
fi

# Build Sequential Thinking MCP Server (TypeScript)
print_status "Building Sequential Thinking MCP Server..."
cd mcp/sequential-thinking

if [ ! -f "package.json" ]; then
    print_error "package.json not found in sequential-thinking directory"
    exit 1
fi

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

# Build TypeScript
print_status "Building TypeScript..."
npm run build

# Run tests if available
if npm run test --dry-run &> /dev/null; then
    print_status "Running tests..."
    npm test
fi

print_success "Sequential Thinking MCP Server built successfully"

# Go back to root directory
cd ../..

# Build Docker images if Docker is available
if [ "$SKIP_DOCKER" = false ]; then
    print_status "Building Docker images..."
    
    # Build Sequential Thinking Docker image
    print_status "Building Sequential Thinking Docker image..."
    docker build -f mcp/sequential-thinking/Dockerfile -t mcp/sequentialthinking:latest mcp/sequential-thinking/
    
    # Build Research MCP Docker image
    print_status "Building Research MCP Docker image..."
    docker build -f mcp/Dockerfile.research -t mcp/gaia-research:latest .
    
    # Build WebSocket MCP Docker image
    print_status "Building WebSocket MCP Docker image..."
    docker build -f mcp/Dockerfile.websocket -t mcp/gaia-websocket:latest .
    
    # Build BiomCP Docker image
    print_status "Building BiomCP Docker image..."
    docker build -f mcp/biomcp/Dockerfile -t biomcp/server:latest mcp/biomcp/
    
    print_success "All Docker images built successfully"
    
    # List built images
    print_status "Built Docker images:"
    docker images | grep -E "(mcp/sequentialthinking|mcp/gaia-research|mcp/gaia-websocket|biomcp/server)"
else
    print_warning "Skipping Docker builds (Docker not available)"
fi

# Create npm link for local development (optional)
if [ "$1" = "--link" ]; then
    print_status "Creating npm link for local development..."
    cd mcp/sequential-thinking
    npm link
    cd ../..
    print_success "npm link created. You can now use 'gaia-sequential-thinking' command globally"
fi

# Validate mcp.json
if [ -f "mcp.json" ]; then
    print_status "Validating mcp.json..."
    if command -v jq &> /dev/null; then
        if jq empty mcp.json; then
            print_success "mcp.json is valid"
        else
            print_error "mcp.json contains syntax errors"
            exit 1
        fi
    else
        print_warning "jq not installed, skipping mcp.json validation"
    fi
fi

print_success "🎉 All MCP servers built successfully!"
echo ""
echo "Usage:"
echo "  NPX:    npx @gaia/mcp-server-sequential-thinking"
echo "  Docker: docker run --rm -i mcp/sequentialthinking"
echo "  Compose: docker-compose -f docker-compose.mcp.yml up"
echo ""
echo "Configuration: mcp.json"