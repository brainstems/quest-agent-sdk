/**
 * Quest Agent Client (TypeScript/JavaScript)
 * 
 * Client library for calling Quest agents from TypeScript/JavaScript applications.
 * This is the CLIENT side - for BUILDING agents, use the Python SDK.
 * 
 * Use Cases:
 * - Call Quest agents from your Node.js/TypeScript backend
 * - Call Quest agents from React/Vue/Angular frontends
 * - Orchestrate multiple agents
 * - Build agent workflows
 */

import axios, { AxiosInstance } from 'axios';
import Redis from 'ioredis';
import { v4 as uuidv4 } from 'uuid';
import crypto from 'crypto';

// ============================================================================
// Types
// ============================================================================

export interface QuestClientConfig {
  apiUrl?: string;
  apiKey?: string;
  redisUrl?: string;
  timeout?: number;
}

export interface AgentManifest {
  name: string;
  version?: string;
  owner?: string;
  description?: string;
  capabilities: string[];
  intents?: string[];
  enabled?: boolean;
  manifest?: Record<string, any>;
}

export interface AgentExecuteParams {
  agentName: string;
  capability: string;
  parameters: Record<string, any>;
  context?: Record<string, any>;
}

export interface AgentExecuteResult {
  status: 'pending_approval' | 'approved' | 'denied' | 'completed' | 'failed';
  result?: any;
  error?: string;
  actionId?: string;
  approvalRequired?: boolean;
}

export interface MeshEnvelope<T = any> {
  envelope_version: '1.0';
  event_type?: string;
  command_type?: string;
  trace_id: string;
  span_id: string;
  correlation_id: string;
  timestamp: string;
  producer: {
    service: string;
    agent_id?: string;
    agent_version?: string;
  };
  subject: {
    type: string;
    id: string;
  };
  rights: {
    classification: 'public' | 'internal' | 'restricted' | 'confidential';
    pii: boolean;
    retention_days: number;
    shareable: boolean;
  };
  idempotency_key: string;
  tags: string[];
  payload: T;
}

export interface ActionPayload {
  action: {
    id: string;
    type: string;
    requiredCapabilities: string[];
    inputs: Record<string, any>;
    priority?: 'low' | 'medium' | 'high';
    cost?: number;
    risk?: 'low' | 'medium' | 'high';
    metadata?: Record<string, any>;
  };
}

// ============================================================================
// Quest Agent Client
// ============================================================================

export class QuestAgentClient {
  private http: AxiosInstance;
  private redis?: Redis;
  private config: Required<QuestClientConfig>;

  constructor(config: QuestClientConfig = {}) {
    this.config = {
      apiUrl: config.apiUrl || process.env.API_URL || 'http://localhost:3000',
      apiKey: config.apiKey || process.env.API_KEY || '',
      redisUrl: config.redisUrl || process.env.REDIS_URL || 'redis://localhost:6379',
      timeout: config.timeout || 30000
    };

    // Setup HTTP client
    this.http = axios.create({
      baseURL: this.config.apiUrl,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` })
      }
    });

    // Setup Redis client (optional, for event streaming)
    if (config.redisUrl !== null) {
      try {
        this.redis = new Redis(this.config.redisUrl);
      } catch (error) {
        console.warn('[QuestAgentClient] Redis connection failed, using HTTP only:', error);
      }
    }
  }

  // ==========================================================================
  // REST API Methods
  // ==========================================================================

  /**
   * List all available agents
   */
  async listAgents(filters?: {
    intent?: string;
    capability?: string;
    limit?: number;
  }): Promise<AgentManifest[]> {
    const response = await this.http.get('/api/agents', { params: filters });
    return response.data.agents || [];
  }

  /**
   * Discover agents by semantic search
   */
  async searchAgents(query: string, limit: number = 10): Promise<AgentManifest[]> {
    const response = await this.http.get('/api/agents', {
      params: { q: query, limit }
    });
    return response.data.agents || [];
  }

  /**
   * Execute an agent capability
   */
  async executeAgent(params: AgentExecuteParams): Promise<AgentExecuteResult> {
    const response = await this.http.post('/api/agents/execute', params);
    return response.data;
  }

  /**
   * Register an agent (typically only used by agent builders)
   */
  async registerAgent(manifest: AgentManifest): Promise<AgentManifest> {
    const response = await this.http.post('/api/agents', manifest);
    return response.data.agent;
  }

  // ==========================================================================
  // Redis Streams Methods (Advanced)
  // ==========================================================================

  /**
   * Publish command to Redis stream
   */
  async publishCommand(
    commandType: string,
    payload: Record<string, any>,
    options?: {
      stream?: string;
      traceId?: string;
      correlationId?: string;
    }
  ): Promise<string> {
    if (!this.redis) {
      throw new Error('Redis client not initialized');
    }

    const envelope = this.createEnvelope({
      command_type: commandType,
      payload,
      trace_id: options?.traceId,
      correlation_id: options?.correlationId
    });

    const stream = options?.stream || 'mesh:commands';
    const messageId = await this.redis.xadd(
      stream,
      'MAXLEN',
      '~',
      '100000',
      '*',
      'json',
      JSON.stringify(envelope)
    );

    return messageId;
  }

  /**
   * Publish action execution command
   */
  async publishActionCommand(action: {
    id?: string;
    type: string;
    requiredCapabilities: string[];
    inputs: Record<string, any>;
    priority?: 'low' | 'medium' | 'high';
  }): Promise<string> {
    const actionId = action.id || `action_${uuidv4()}`;
    
    return this.publishCommand('action.execution.requested', {
      action: {
        ...action,
        id: actionId
      }
    });
  }

  /**
   * Subscribe to events from a Redis stream
   */
  async subscribeToEvents(
    callback: (event: MeshEnvelope) => void | Promise<void>,
    options?: {
      stream?: string;
      group?: string;
      consumer?: string;
      count?: number;
      blockMs?: number;
    }
  ): Promise<() => void> {
    if (!this.redis) {
      throw new Error('Redis client not initialized');
    }

    const stream = options?.stream || 'mesh:events';
    const group = options?.group || 'typescript-client';
    const consumer = options?.consumer || `consumer-${uuidv4().substring(0, 8)}`;
    const count = options?.count || 10;
    const blockMs = options?.blockMs || 5000;

    // Ensure consumer group exists
    try {
      await this.redis.xgroup('CREATE', stream, group, '$', 'MKSTREAM');
    } catch (error: any) {
      if (!error.message.includes('BUSYGROUP')) {
        throw error;
      }
    }

    let running = true;

    // Start polling loop
    const poll = async () => {
      while (running) {
        try {
          const results = await this.redis!.xreadgroup(
            'GROUP',
            group,
            consumer,
            'COUNT',
            count,
            'BLOCK',
            blockMs,
            'STREAMS',
            stream,
            '>'
          );

          if (results && results.length > 0) {
            for (const [, entries] of results) {
              for (const [id, fields] of entries as any[]) {
                try {
                  const envelope = JSON.parse(fields[1]); // fields is ['json', '{...}']
                  await callback(envelope);
                  
                  // Acknowledge
                  await this.redis!.xack(stream, group, id);
                } catch (error) {
                  console.error('[QuestAgentClient] Error processing event:', error);
                }
              }
            }
          }
        } catch (error) {
          if (running) {
            console.error('[QuestAgentClient] Error reading stream:', error);
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      }
    };

    poll();

    // Return unsubscribe function
    return () => {
      running = false;
    };
  }

  // ==========================================================================
  // Utility Methods
  // ==========================================================================

  /**
   * Create a mesh envelope
   */
  private createEnvelope(options: {
    event_type?: string;
    command_type?: string;
    payload: any;
    trace_id?: string;
    span_id?: string;
    correlation_id?: string;
    producer?: any;
    subject?: any;
  }): MeshEnvelope {
    const envelope: MeshEnvelope = {
      envelope_version: '1.0',
      event_type: options.event_type,
      command_type: options.command_type,
      trace_id: options.trace_id || uuidv4(),
      span_id: options.span_id || uuidv4(),
      correlation_id: options.correlation_id || uuidv4(),
      timestamp: new Date().toISOString(),
      producer: options.producer || {
        service: 'typescript-client',
        agent_id: 'client',
        agent_version: '1.0.0'
      },
      subject: options.subject || {
        type: 'client',
        id: 'client'
      },
      rights: {
        classification: 'internal',
        pii: false,
        retention_days: 14,
        shareable: true
      },
      idempotency_key: '',
      tags: [],
      payload: options.payload
    };

    // Compute idempotency key
    envelope.idempotency_key = this.computeIdempotencyKey(envelope);

    return envelope;
  }

  /**
   * Compute SHA-256 idempotency key
   */
  private computeIdempotencyKey(envelope: MeshEnvelope): string {
    const content = {
      type: envelope.event_type || envelope.command_type,
      producer: envelope.producer,
      subject: envelope.subject,
      payload: envelope.payload,
      timestamp: envelope.timestamp
    };

    return crypto
      .createHash('sha256')
      .update(JSON.stringify(content))
      .digest('hex');
  }

  /**
   * Close connections
   */
  async close(): Promise<void> {
    if (this.redis) {
      await this.redis.quit();
    }
  }
}

// ============================================================================
// Convenience Functions
// ============================================================================

/**
 * Create a Quest agent client
 */
export function createQuestClient(config?: QuestClientConfig): QuestAgentClient {
  return new QuestAgentClient(config);
}

/**
 * Execute an agent and wait for result
 */
export async function executeAgent(
  agentName: string,
  capability: string,
  parameters: Record<string, any>,
  config?: QuestClientConfig
): Promise<AgentExecuteResult> {
  const client = createQuestClient(config);
  return client.executeAgent({ agentName, capability, parameters });
}

/**
 * Discover agents by capability
 */
export async function discoverAgents(
  capability: string,
  config?: QuestClientConfig
): Promise<AgentManifest[]> {
  const client = createQuestClient(config);
  return client.listAgents({ capability });
}

// ============================================================================
// Export
// ============================================================================

export default QuestAgentClient;
