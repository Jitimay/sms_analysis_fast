// Simple test for MCP server functions
const { spawn } = require('child_process');

async function testMCP() {
  console.log('🌱 Testing DAS MCP Server...\n');
  
  const mcp = spawn('node', ['mcp-server.js'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // Test get_simulated_data
  const testRequest = {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/call',
    params: {
      name: 'get_simulated_data',
      arguments: {}
    }
  };

  mcp.stdin.write(JSON.stringify(testRequest) + '\n');

  mcp.stdout.on('data', (data) => {
    try {
      const response = JSON.parse(data.toString());
      console.log('📊 Sensor Data:', JSON.parse(response.result.content[0].text));
    } catch (e) {
      console.log('Raw response:', data.toString());
    }
  });

  // Test trigger_irrigation
  setTimeout(() => {
    const irrigationTest = {
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/call',
      params: {
        name: 'trigger_irrigation',
        arguments: { duration_s: 3 }
      }
    };
    
    mcp.stdin.write(JSON.stringify(irrigationTest) + '\n');
    console.log('🚰 Testing irrigation trigger...');
  }, 1000);

  setTimeout(() => {
    mcp.kill();
    console.log('\n✅ MCP Server test complete');
  }, 3000);
}

testMCP();
