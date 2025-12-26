// Test DAS Agent with OpenRouter API
import { createOpenAI } from '@ai-sdk/openai';
import { generateText } from 'ai';

async function testDASAgent() {
  console.log('🤖 Testing DAS Agent with OpenRouter...\n');
  
  try {
    const openrouter = createOpenAI({
      apiKey: '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',
      baseURL: 'https://openrouter.ai/api/v1',
    });

    const DAS_PROMPT = `You are the Decentralized Agricultural Sentinel (DAS). 
    
Current sensor data:
- Soil moisture: 12%
- Temperature: 28°C
- Image status: clear

Your threshold: irrigate if moisture < 15%.

Decide: Should you execute autonomous irrigation? Answer briefly.`;

    const result = await generateText({
      model: openrouter('tngtech/deepseek-r1t2-chimera:free'),
      prompt: DAS_PROMPT,
    });

    console.log('🌱 DAS Agent Decision:', result.text);
    console.log('\n✅ DAS Agent + OpenRouter integration working!');
    
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
}

testDASAgent();
