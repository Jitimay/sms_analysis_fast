const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

const server = new Server(
  {
    name: "das-agricultural-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Simulated sensor data
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;
  
  switch (name) {
    case 'get_simulated_data':
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            soil_moisture: Math.random() * 30, // 0-30%
            temperature: 20 + Math.random() * 15 // 20-35°C
          })
        }]
      };
      
    case 'capture_image':
      return {
        content: [{
          type: "text", 
          text: JSON.stringify({
            image_url: "https://placeholder.com/farm-image.jpg",
            status: "clear"
          })
        }]
      };
      
    case 'trigger_irrigation':
      const duration = args?.duration_s || 5;
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            action: "irrigation_triggered",
            duration: duration,
            timestamp: new Date().toISOString()
          })
        }]
      };
  }
});

server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: "get_simulated_data",
      description: "Get current soil moisture and temperature readings",
      inputSchema: { type: "object", properties: {} }
    },
    {
      name: "capture_image", 
      description: "Capture image from ESP-CAM for visual analysis",
      inputSchema: { type: "object", properties: {} }
    },
    {
      name: "trigger_irrigation",
      description: "Activate irrigation pump for specified duration",
      inputSchema: {
        type: "object",
        properties: {
          duration_s: { type: "number", description: "Duration in seconds" }
        }
      }
    }
  ]
}));

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
