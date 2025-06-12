# GAIA Sequential Thinking MCP Server

A Model Context Protocol (MCP) server that provides dynamic and reflective problem-solving through structured thinking processes. This server enables AI agents to break down complex problems into manageable steps, revise and refine thoughts dynamically, and explore alternative reasoning paths.

## Features

- **Sequential Problem Solving**: Break complex problems into step-by-step thought processes
- **Dynamic Revision**: Revise and refine previous thoughts as new insights emerge
- **Alternative Branching**: Explore multiple reasoning paths for comprehensive analysis
- **Confidence Tracking**: Monitor confidence levels throughout the thinking process
- **Process Management**: Start, manage, and complete multiple thinking processes

## Installation

### Using npx (Recommended)

```bash
npx @gaia/mcp-server-sequential-thinking
```

### Using npm

```bash
npm install -g @gaia/mcp-server-sequential-thinking
gaia-sequential-thinking
```

### From Source

```bash
git clone <repository-url>
cd mcp/sequential-thinking
npm install
npm run build
npm start
```

## Usage

### MCP Configuration

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "gaia-sequential-thinking": {
      "command": "npx",
      "args": ["@gaia/mcp-server-sequential-thinking"],
      "description": "Sequential thinking for complex problem solving"
    }
  }
}
```

### Available Tools

#### 1. `start_thinking`

Start a new sequential thinking process.

**Parameters:**
- `problem` (required): The problem or question to analyze
- `maxSteps` (optional): Maximum thinking steps (default: 10)
- `enableBranching` (optional): Enable alternative paths (default: true)
- `enableRevision` (optional): Enable thought revision (default: true)
- `thoughtSeed` (optional): Initial thought to seed the process

**Example:**
```json
{
  "problem": "How can we reduce carbon emissions in urban transportation?",
  "maxSteps": 8,
  "enableBranching": true
}
```

#### 2. `think`

Add a thought step to an existing process.

**Parameters:**
- `processId` (required): Process identifier
- `thought` (required): Current thought or reasoning
- `nextThoughtNeeded` (required): Whether to continue thinking
- `thoughtNumber` (required): Current step number
- `totalThoughts` (required): Estimated total steps
- `confidence` (optional): Confidence level (0.0-1.0)
- `revision` (optional): Mark as revision of previous thought
- `branchAlternative` (optional): Explore alternative path

#### 3. `complete_thinking`

Complete a thinking process and generate solution.

**Parameters:**
- `processId` (required): Process to complete
- `forceSolution` (optional): Force completion even if incomplete

#### 4. `get_thinking_status`

Get current status of a thinking process.

**Parameters:**
- `processId` (required): Process identifier

#### 5. `list_thinking_processes`

List all active thinking processes.

## Example Workflow

1. **Start thinking process:**
```json
{
  "tool": "start_thinking",
  "args": {
    "problem": "Design a sustainable energy system for a small city"
  }
}
```

2. **Add thought steps:**
```json
{
  "tool": "think",
  "args": {
    "processId": "thinking_1234567890_abc123",
    "thought": "First, analyze current energy consumption patterns",
    "nextThoughtNeeded": true,
    "thoughtNumber": 1,
    "totalThoughts": 6,
    "confidence": 0.8
  }
}
```

3. **Complete the process:**
```json
{
  "tool": "complete_thinking",
  "args": {
    "processId": "thinking_1234567890_abc123"
  }
}
```

## Development

### Prerequisites

- Node.js 18+
- TypeScript 5+

### Building

```bash
npm run build
```

### Development Mode

```bash
npm run dev
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
npm run format
```

## Integration with GAIA System

This MCP server integrates seamlessly with the GAIA LLMs ecosystem:

- **Research Integration**: Combine with GAIA research tools for evidence-based thinking
- **Chatbot Integration**: Use through GAIA chatbot's `/mcp` commands
- **Analysis Pipeline**: Part of comprehensive analysis and reasoning pipeline

## Configuration Profiles

The server supports multiple configuration profiles via `mcp.json`:

- **development**: Debug mode with extended timeouts
- **production**: Optimized for production use
- **thinking-only**: Standalone sequential thinking server

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]
- Community: [community-url]