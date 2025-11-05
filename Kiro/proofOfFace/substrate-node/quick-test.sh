#!/bin/bash

# Quick test to check if we can build a minimal Substrate node
echo "🚀 Testing minimal Substrate build..."

# Try to clone the official node template for comparison
cd /tmp
git clone https://github.com/substrate-developer-hub/substrate-node-template.git test-template
cd test-template

echo "📋 Checking official template structure..."
ls -la

echo "🔧 Testing official template build..."
cargo check --release

echo "✅ Official template works!"
echo "Now let's compare with our structure..."