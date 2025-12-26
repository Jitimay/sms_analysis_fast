// Test OpenRouter API
async function testOpenRouterAPI() {
  console.log('🔑 Testing OpenRouter API...\n');
  
  try {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "messages": [
          {
            "role": "user",
            "content": "You are a DAS agricultural agent. Check soil moisture: 8%. Should you irrigate?"
          }
        ]
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ API Response:', data.choices[0].message.content);
      console.log('\n🎯 OpenRouter API is working!');
    } else {
      console.log('❌ API Error:', response.status, response.statusText);
      const error = await response.text();
      console.log('Error details:', error);
    }
  } catch (error) {
    console.log('❌ Network Error:', error.message);
  }
}

testOpenRouterAPI();
