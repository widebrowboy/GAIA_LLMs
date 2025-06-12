/**
 * Sequential Thinking Engine
 * Core logic for managing and processing thought sequences
 */

import { ThoughtStep, ThinkingProcess, ThinkingRequest, ThinkRequest } from './types.js';

export class SequentialThinkingEngine {
  private processes: Map<string, ThinkingProcess> = new Map();
  private maxProcesses = 100; // Limit concurrent processes

  /**
   * Start a new thinking process
   */
  startThinking(request: ThinkingRequest): string {
    // Clean up old processes if needed
    if (this.processes.size >= this.maxProcesses) {
      this.cleanupOldProcesses();
    }

    const processId = this.generateProcessId();
    const process: ThinkingProcess = {
      id: processId,
      problem: request.problem,
      thoughts: [],
      currentStep: 0,
      completed: false,
      metadata: {
        startTime: new Date(),
        totalSteps: 0,
        confidence: 0,
      },
    };

    this.processes.set(processId, process);
    return processId;
  }

  /**
   * Add a thought step to an existing process
   */
  addThought(processId: string, request: ThinkRequest): ThoughtStep {
    const process = this.processes.get(processId);
    if (!process) {
      throw new Error(`Process ${processId} not found`);
    }

    if (process.completed) {
      throw new Error(`Process ${processId} is already completed`);
    }

    const thoughtStep: ThoughtStep = {
      thoughtNumber: request.thoughtNumber,
      thought: request.thought,
      nextThoughtNeeded: request.nextThoughtNeeded,
      totalThoughts: request.totalThoughts,
      confidence: request.confidence || 0.5,
      reasoning: this.generateReasoning(request, process),
    };

    // Handle branching
    if (request.branchAlternative && request.parentThoughtNumber !== undefined) {
      thoughtStep.alternatives = this.generateAlternatives(request, process);
    }

    // Handle revision
    if (request.revision && request.parentThoughtNumber !== undefined) {
      this.reviseThought(process, request.parentThoughtNumber, thoughtStep);
    } else {
      process.thoughts.push(thoughtStep);
    }

    process.currentStep = process.thoughts.length;
    process.metadata!.totalSteps = process.currentStep;

    return thoughtStep;
  }

  /**
   * Complete a thinking process
   */
  completeThinking(processId: string, forceSolution = false): ThinkingProcess {
    const process = this.processes.get(processId);
    if (!process) {
      throw new Error(`Process ${processId} not found`);
    }

    if (!forceSolution && process.thoughts.length === 0) {
      throw new Error('Cannot complete process with no thoughts');
    }

    process.completed = true;
    process.metadata!.endTime = new Date();
    process.solution = this.synthesizeSolution(process);
    process.metadata!.confidence = this.calculateOverallConfidence(process);

    return process;
  }

  /**
   * Get a thinking process by ID
   */
  getProcess(processId: string): ThinkingProcess | undefined {
    return this.processes.get(processId);
  }

  /**
   * Get all active processes
   */
  getAllProcesses(): ThinkingProcess[] {
    return Array.from(this.processes.values());
  }

  /**
   * Delete a process
   */
  deleteProcess(processId: string): boolean {
    return this.processes.delete(processId);
  }

  private generateProcessId(): string {
    return `thinking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateReasoning(request: ThinkRequest, process: ThinkingProcess): string {
    const previousThoughts = process.thoughts.slice(-2);
    const context = previousThoughts.length > 0 
      ? `Building on previous thoughts: ${previousThoughts.map(t => t.thought).join(' → ')}`
      : 'Starting fresh analysis';

    return `${context}. Current reasoning: Analyzing step ${request.thoughtNumber} of ${request.totalThoughts}.`;
  }

  private generateAlternatives(request: ThinkRequest, process: ThinkingProcess): string[] {
    // Generate alternative thinking paths
    const baseThought = request.thought;
    return [
      `Alternative approach: ${baseThought.replace(/^/, 'Instead of that, consider ')}`,
      `Different perspective: ${baseThought.replace(/^/, 'From another angle, ')}`,
      `Simplified version: ${baseThought.replace(/complex|complicated/gi, 'simple')}`,
    ];
  }

  private reviseThought(process: ThinkingProcess, parentNumber: number, newThought: ThoughtStep): void {
    const parentIndex = process.thoughts.findIndex(t => t.thoughtNumber === parentNumber);
    if (parentIndex !== -1) {
      // Insert revised thought after parent
      process.thoughts.splice(parentIndex + 1, 0, {
        ...newThought,
        thoughtNumber: parentNumber + 0.1, // Fractional numbering for revisions
        thought: `[REVISION] ${newThought.thought}`,
      });
    }
  }

  private synthesizeSolution(process: ThinkingProcess): string {
    const thoughts = process.thoughts;
    if (thoughts.length === 0) {
      return 'No solution could be generated from the thinking process.';
    }

    const keyInsights = thoughts
      .filter(t => t.confidence && t.confidence > 0.7)
      .map(t => t.thought)
      .slice(-3); // Take last 3 high-confidence thoughts

    const solution = keyInsights.length > 0
      ? `Based on the sequential thinking process, the solution is: ${keyInsights.join(' Furthermore, ')}`
      : `Solution derived from ${thoughts.length} thinking steps: ${thoughts[thoughts.length - 1].thought}`;

    return solution;
  }

  private calculateOverallConfidence(process: ThinkingProcess): number {
    if (process.thoughts.length === 0) return 0;

    const confidences = process.thoughts
      .map(t => t.confidence || 0.5)
      .filter(c => c > 0);

    if (confidences.length === 0) return 0.5;

    // Weighted average with recent thoughts having more weight
    const weights = confidences.map((_, i) => Math.pow(1.1, i));
    const weightedSum = confidences.reduce((sum, conf, i) => sum + conf * weights[i], 0);
    const weightSum = weights.reduce((sum, weight) => sum + weight, 0);

    return Math.min(weightedSum / weightSum, 1.0);
  }

  private cleanupOldProcesses(): void {
    const cutoffTime = new Date();
    cutoffTime.setHours(cutoffTime.getHours() - 1); // Remove processes older than 1 hour

    for (const [id, process] of this.processes.entries()) {
      if (process.metadata!.startTime < cutoffTime || process.completed) {
        this.processes.delete(id);
      }
    }
  }
}