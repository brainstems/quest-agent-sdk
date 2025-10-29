# TypeScript/JavaScript Client

TypeScript/JavaScript client library for calling Quest agents.

**Note:** This is the CLIENT side. For BUILDING agents, use the Python SDK.

## Files

### `quest-agent-client.ts`

Complete TypeScript client for Quest Agent Forge.

**Features:**
- REST API client (list, search, execute agents)
- Redis Streams pub/sub
- TypeScript type definitions
- Convenience functions

**Usage:**

```typescript
import { QuestAgentClient } from './quest-agent-client';

const client = new QuestAgentClient({
    apiUrl: 'http://localhost:3000'
});

// List agents
const agents = await client.listAgents({ capability: 'pricing' });

// Execute agent
const result = await client.executeAgent({
    agentName: 'Pricing Agent',
    capability: 'pricing_optimization',
    parameters: { price: 99.99 }
});

// Close connections
await client.close();
```

---

### `example-usage.ts`

Complete examples showing all client patterns.

**Includes:**
- Simple agent execution
- Agent discovery
- Semantic search
- Multi-agent orchestration
- Event streaming (Redis)
- Convenience functions

**Run Examples:**

```typescript
import { runExamples } from './example-usage';

runExamples();
```

---

## Installation

```bash
npm install @types/redis ioredis axios uuid
# or
yarn add @types/redis ioredis axios uuid
```

---

## Use Cases

### 1. Call Quest Agents from Node.js Backend

```typescript
// In your Express/Fastify API
app.post('/optimize-price', async (req, res) => {
    const result = await client.executeAgent({
        agentName: 'Pricing Agent',
        capability: 'pricing_optimization',
        parameters: req.body
    });
    
    res.json(result);
});
```

### 2. Call Quest Agents from React Frontend

```typescript
// In your React component
const optimizePrice = async (productId: string) => {
    const result = await client.executeAgent({
        agentName: 'Pricing Agent',
        capability: 'pricing_optimization',
        parameters: { productId }
    });
    
    setOptimizedPrice(result.result.recommended_price);
};
```

### 3. Agent Discovery

```typescript
// Find agents that can help
const pricingAgents = await client.listAgents({ 
    capability: 'pricing_optimization' 
});

// Semantic search
const agents = await client.searchAgents(
    'agents that can optimize inventory and pricing together'
);
```

### 4. Multi-Agent Coordination

```typescript
// Orchestrate multiple agents
const inventory = await client.executeAgent({
    agentName: 'Inventory Agent',
    capability: 'inventory_check',
    parameters: { productId: '123' }
});

const price = await client.executeAgent({
    agentName: 'Pricing Agent',
    capability: 'pricing_optimization',
    parameters: { 
        productId: '123',
        inventoryLevel: inventory.result.level
    }
});
```

---

## API Reference

### Constructor

```typescript
new QuestAgentClient({
    apiUrl?: string;        // Default: http://localhost:3000
    apiKey?: string;        // Optional API key
    redisUrl?: string;      // Optional Redis URL
    timeout?: number;       // Request timeout (ms)
})
```

### Methods

```typescript
// List agents
listAgents(filters?: {
    intent?: string;
    capability?: string;
    limit?: number;
}): Promise<AgentManifest[]>

// Semantic search
searchAgents(query: string, limit?: number): Promise<AgentManifest[]>

// Execute agent
executeAgent(params: {
    agentName: string;
    capability: string;
    parameters: Record<string, any>;
    context?: Record<string, any>;
}): Promise<AgentExecuteResult>

// Register agent
registerAgent(manifest: AgentManifest): Promise<AgentManifest>

// Publish command (Redis Streams)
publishCommand(
    commandType: string,
    payload: Record<string, any>,
    options?: {...}
): Promise<string>

// Subscribe to events
subscribeToEvents(
    callback: (event: MeshEnvelope) => void,
    options?: {...}
): Promise<() => void>

// Close connections
close(): Promise<void>
```

### Convenience Functions

```typescript
import { executeAgent, discoverAgents } from './quest-agent-client';

// Quick execute
const result = await executeAgent('Agent Name', 'capability', {...});

// Quick discover
const agents = await discoverAgents('pricing_optimization');
```

---

## Type Definitions

```typescript
interface AgentManifest {
    name: string;
    version?: string;
    description?: string;
    capabilities: string[];
    intents?: string[];
    enabled?: boolean;
}

interface AgentExecuteResult {
    status: 'pending_approval' | 'approved' | 'denied' | 'completed' | 'failed';
    result?: any;
    error?: string;
    actionId?: string;
}

interface MeshEnvelope<T = any> {
    envelope_version: '1.0';
    event_type?: string;
    command_type?: string;
    trace_id: string;
    // ... full CloudEvents structure
    payload: T;
}
```

---

## Examples

See `example-usage.ts` for complete working examples of all patterns.

---

## Documentation

- **Getting Started:** See [../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)
- **API Reference:** See [../docs/API_REFERENCE.md](../docs/API_REFERENCE.md)

---

**Perfect for calling Quest agents from your TypeScript/JavaScript applications!**
