#!/usr/bin/env node

/**
 * GAIA Sequential Thinking MCP Server
 * 
 * A Model Context Protocol server that provides dynamic and reflective 
 * problem-solving through structured thinking processes.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

import { SequentialThinkingEngine } from './thinking-engine.js';
import {
  ThinkingRequest,
  ThinkRequest,
  CompleteThinkingRequest,
  ThinkResponse,
  CompleteThinkingResponse,
} from './types.js';

class SequentialThinkingServer {
  private server: Server;
  private engine: SequentialThinkingEngine;

  constructor() {
    this.engine = new SequentialThinkingEngine();
    this.server = new Server(
      {
        name: 'gaia-sequential-thinking',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  private setupToolHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'start_thinking',
            description: 'Start a new sequential thinking process for complex problem solving',
            inputSchema: {
              type: 'object',
              properties: {
                problem: {
                  type: 'string',
                  description: 'The problem or question to think through systematically',
                },
                maxSteps: {
                  type: 'number',
                  description: 'Maximum number of thinking steps (default: 10)',
                  default: 10,
                },
                enableBranching: {
                  type: 'boolean',
                  description: 'Enable alternative thinking paths (default: true)',
                  default: true,
                },
                enableRevision: {
                  type: 'boolean',
                  description: 'Enable revision of previous thoughts (default: true)',
                  default: true,
                },
                thoughtSeed: {
                  type: 'string',
                  description: 'Initial thought or approach to seed the thinking process',
                },
              },
              required: ['problem'],
            },
          },
          {
            name: 'think',
            description: 'Add a thought step to an existing thinking process',
            inputSchema: {
              type: 'object',
              properties: {
                processId: {
                  type: 'string',
                  description: 'ID of the thinking process',
                },
                thought: {
                  type: 'string',
                  description: 'The current thought or reasoning step',
                },
                nextThoughtNeeded: {
                  type: 'boolean',
                  description: 'Whether another thinking step is needed',
                },
                thoughtNumber: {
                  type: 'number',
                  description: 'Current thought number in the sequence',
                },
                totalThoughts: {
                  type: 'number',
                  description: 'Estimated total thoughts needed',
                },
                revision: {
                  type: 'boolean',
                  description: 'Whether this is a revision of a previous thought',
                  default: false,
                },
                branchAlternative: {
                  type: 'boolean',
                  description: 'Whether this explores an alternative path',
                  default: false,
                },
                parentThoughtNumber: {
                  type: 'number',
                  description: 'Parent thought number for revisions/branches',
                },
                confidence: {
                  type: 'number',
                  description: 'Confidence level in this thought (0.0-1.0)',
                  minimum: 0,
                  maximum: 1,
                },
              },
              required: ['processId', 'thought', 'nextThoughtNeeded', 'thoughtNumber', 'totalThoughts'],
            },
          },
          {
            name: 'complete_thinking',
            description: 'Complete a thinking process and generate final solution',
            inputSchema: {
              type: 'object',
              properties: {
                processId: {
                  type: 'string',
                  description: 'ID of the thinking process to complete',
                },
                forceSolution: {
                  type: 'boolean',
                  description: 'Force completion even if process seems incomplete',
                  default: false,
                },
              },
              required: ['processId'],
            },
          },
          {
            name: 'get_thinking_status',
            description: 'Get the current status of a thinking process',
            inputSchema: {
              type: 'object',
              properties: {
                processId: {
                  type: 'string',
                  description: 'ID of the thinking process',
                },
              },
              required: ['processId'],
            },
          },
          {
            name: 'list_thinking_processes',
            description: 'List all active thinking processes',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'start_thinking':
            return await this.handleStartThinking(args as unknown as ThinkingRequest);

          case 'think':
            return await this.handleThink(args as unknown as ThinkRequest & { processId: string });

          case 'complete_thinking':
            return await this.handleCompleteThinking(args as unknown as CompleteThinkingRequest);

          case 'get_thinking_status':
            return await this.handleGetThinkingStatus(args as unknown as { processId: string });

          case 'list_thinking_processes':
            return await this.handleListThinkingProcesses();

          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        throw new McpError(
          ErrorCode.InternalError,
          `Error in ${name}: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    });
  }

  private async handleStartThinking(args: ThinkingRequest) {
    const processId = this.engine.startThinking(args);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            processId,
            message: 'Sequential thinking process started',
            problem: args.problem,
            nextStep: 'Use the "think" tool to add your first thought step',
            instructions: {
              thoughtNumber: 'Start with 1',
              totalThoughts: 'Estimate how many steps you think you\'ll need',
              nextThoughtNeeded: 'Set to true to continue the process',
            },
          }, null, 2),
        },
      ],
    };
  }

  private async handleThink(args: ThinkRequest & { processId: string }) {
    const { processId, ...thinkRequest } = args;
    const thoughtStep = this.engine.addThought(processId, thinkRequest);
    
    const process = this.engine.getProcess(processId);
    if (!process) {
      throw new McpError(ErrorCode.InvalidRequest, 'Process not found');
    }

    const response: ThinkResponse = {
      processId,
      currentThought: thoughtStep,
      canContinue: thinkRequest.nextThoughtNeeded,
      nextStepSuggestion: thinkRequest.nextThoughtNeeded 
        ? 'Continue with the next thought step or call complete_thinking if ready'
        : 'Process can be completed - call complete_thinking',
    };

    if (process.thoughts.length >= 3) {
      response.insights = this.generateInsights(process.thoughts.slice(-3));
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(response, null, 2),
        },
      ],
    };
  }

  private async handleCompleteThinking(args: CompleteThinkingRequest) {
    const process = this.engine.completeThinking(args.processId, args.forceSolution);
    
    const response: CompleteThinkingResponse = {
      processId: args.processId,
      solution: process.solution || 'No solution generated',
      confidence: process.metadata?.confidence || 0,
      totalSteps: process.metadata?.totalSteps || 0,
      insights: this.generateInsights(process.thoughts),
      thoughtProcess: process.thoughts,
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(response, null, 2),
        },
      ],
    };
  }

  private async handleGetThinkingStatus(args: { processId: string }) {
    const process = this.engine.getProcess(args.processId);
    
    if (!process) {
      throw new McpError(ErrorCode.InvalidRequest, 'Process not found');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            processId: process.id,
            problem: process.problem,
            currentStep: process.currentStep,
            totalSteps: process.metadata?.totalSteps || 0,
            completed: process.completed,
            confidence: process.metadata?.confidence || 0,
            thoughtsCount: process.thoughts.length,
            lastThought: process.thoughts[process.thoughts.length - 1]?.thought || 'No thoughts yet',
          }, null, 2),
        },
      ],
    };
  }

  private async handleListThinkingProcesses() {
    const processes = this.engine.getAllProcesses();
    
    const summary = processes.map(p => ({
      processId: p.id,
      problem: p.problem.substring(0, 100) + (p.problem.length > 100 ? '...' : ''),
      completed: p.completed,
      thoughtsCount: p.thoughts.length,
      confidence: p.metadata?.confidence || 0,
      startTime: p.metadata?.startTime,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            totalProcesses: processes.length,
            processes: summary,
          }, null, 2),
        },
      ],
    };
  }

  private generateInsights(thoughts: any[]): string[] {
    const insights: string[] = [];
    
    if (thoughts.length >= 2) {
      insights.push('Progress detected: Multiple thinking steps completed');
    }
    
    const highConfidenceThoughts = thoughts.filter(t => t.confidence && t.confidence > 0.7);
    if (highConfidenceThoughts.length > 0) {
      insights.push(`High confidence thoughts: ${highConfidenceThoughts.length}/${thoughts.length}`);
    }
    
    if (thoughts.some(t => t.alternatives && t.alternatives.length > 0)) {
      insights.push('Alternative approaches explored');
    }
    
    return insights;
  }

  private setupErrorHandling(): void {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('GAIA Sequential Thinking MCP server running on stdio');
  }
}

// Run the server
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new SequentialThinkingServer();
  server.run().catch((error) => {
    console.error('Failed to run server:', error);
    process.exit(1);
  });
}