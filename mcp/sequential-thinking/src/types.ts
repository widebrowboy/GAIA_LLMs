/**
 * Types for Sequential Thinking MCP Server
 */

export interface ThoughtStep {
  thoughtNumber: number;
  thought: string;
  nextThoughtNeeded: boolean;
  totalThoughts: number;
  confidence?: number;
  alternatives?: string[];
  reasoning?: string;
}

export interface ThinkingProcess {
  id: string;
  problem: string;
  thoughts: ThoughtStep[];
  currentStep: number;
  completed: boolean;
  solution?: string;
  metadata?: {
    startTime: Date;
    endTime?: Date;
    totalSteps: number;
    confidence: number;
  };
}

export interface ThinkingRequest {
  problem: string;
  maxSteps?: number;
  enableBranching?: boolean;
  enableRevision?: boolean;
  thoughtSeed?: string;
}

export interface ThinkRequest {
  thought: string;
  nextThoughtNeeded: boolean;
  thoughtNumber: number;
  totalThoughts: number;
  revision?: boolean;
  branchAlternative?: boolean;
  parentThoughtNumber?: number;
  confidence?: number;
}

export interface ThinkResponse {
  processId: string;
  currentThought: ThoughtStep;
  nextStepSuggestion?: string;
  canContinue: boolean;
  summary?: string;
  insights?: string[];
}

export interface CompleteThinkingRequest {
  processId: string;
  forceSolution?: boolean;
}

export interface CompleteThinkingResponse {
  processId: string;
  solution: string;
  confidence: number;
  totalSteps: number;
  insights: string[];
  thoughtProcess: ThoughtStep[];
}