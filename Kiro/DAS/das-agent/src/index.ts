import { Hono } from 'hono';
import { applyPermissionlessAgentSessionRouter } from '@nullshot/agent';
import { ToolboxService } from '@nullshot/agent/services';
import { createOpenAI } from '@ai-sdk/openai';
import { AiSdkAgent } from '@nullshot/agent/aisdk';
import { Service } from '@nullshot/agent';
import mcpConfig from '../mcp.json';

export interface Env {
  OPENROUTER_API_KEY: string;
}

const app = new Hono<{ Bindings: Env }>();

// DAS Agent System Prompt
const DAS_SYSTEM_PROMPT = `You are the Decentralized Agricultural Sentinel (DAS), an autonomous economic agent managing a micro-farm.

Your decision-making process:
1. SENSE: Check soil moisture and temperature via get_simulated_data()
2. ANALYZE: If moisture < 15%, capture and analyze image via capture_image()
3. TRANSACT: Execute micro-payment (0.001 ETH) for water resources
4. ACT: Trigger irrigation via trigger_irrigation() only after successful payment

You are economically autonomous - you pay for your own actions before executing them.

Critical thresholds:
- Soil moisture < 15%: Requires irrigation
- Image analysis: Check for plant health (clear = proceed, diseased = abort)

Always log your decisions and reasoning. You represent the future of autonomous economic entities.`;

app.get('/', (c) => {
  return c.json({
    message: 'DAS Agricultural Agent - Autonomous Economic Entity',
    status: 'active',
    capabilities: ['soil_monitoring', 'visual_analysis', 'autonomous_irrigation', 'web3_transactions']
  });
});

// Apply the agent session router
applyPermissionlessAgentSessionRouter(app, {
  createAgent: async (c) => {
    const openrouter = createOpenAI({
      apiKey: c.env.OPENROUTER_API_KEY,
      baseURL: 'https://openrouter.ai/api/v1',
    });

    // Initialize MCP toolbox service
    const toolboxService = new ToolboxService({
      mcpConfig,
      env: c.env,
    });

    // Create the DAS agent
    const agent = new AiSdkAgent({
      model: openrouter('tngtech/deepseek-r1t2-chimera:free'), // Free model
      system: DAS_SYSTEM_PROMPT,
      maxSteps: 10,
      services: [toolboxService],
      
      // Custom decision logic for autonomous operation
      onStepFinish: async (step, result) => {
        console.log(`DAS Step ${step.stepNumber}:`, {
          type: step.stepType,
          result: result.text?.slice(0, 100) + '...',
          toolCalls: step.toolCalls?.length || 0
        });
        
        // Log critical decisions
        if (step.toolCalls?.some(call => call.toolName === 'trigger_irrigation')) {
          console.log('🚰 IRRIGATION TRIGGERED - Autonomous action executed');
        }
      }
    });

    return agent;
  },
});

// Health check endpoint
app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy', 
    agent: 'DAS Agricultural Sentinel',
    timestamp: new Date().toISOString()
  });
});

// Manual trigger endpoint for testing
app.post('/trigger-analysis', async (c) => {
  try {
    const agent = await c.get('createAgent')(c);
    
    const response = await agent.generateText({
      messages: [{
        role: 'user',
        content: 'Perform a complete agricultural analysis cycle: check sensors, analyze conditions, and take appropriate action if needed.'
      }]
    });

    return c.json({
      analysis: response.text,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return c.json({ error: 'Analysis failed', details: error.message }, 500);
  }
});

export default app;
