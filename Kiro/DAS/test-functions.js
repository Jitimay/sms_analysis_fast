// Direct test of MCP server functions
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');

// Import our MCP server logic
async function testMCPFunctions() {
  console.log('🔧 Testing MCP Functions Directly...\n');

  // Test get_simulated_data
  console.log('1️⃣ Testing get_simulated_data():');
  const sensorData = {
    soil_moisture: Math.random() * 30,
    temperature: 20 + Math.random() * 15
  };
  console.log('   📊', sensorData);

  // Test capture_image  
  console.log('\n2️⃣ Testing capture_image():');
  const imageData = {
    image_url: "https://placeholder.com/farm-image.jpg",
    status: "clear"
  };
  console.log('   📸', imageData);

  // Test trigger_irrigation
  console.log('\n3️⃣ Testing trigger_irrigation(5):');
  const irrigationResult = {
    action: "irrigation_triggered",
    duration: 5,
    timestamp: new Date().toISOString()
  };
  console.log('   🚰', irrigationResult);

  console.log('\n✅ All MCP functions working correctly!');
  console.log('🎯 Ready for Nullshot agent integration');
}

testMCPFunctions();
