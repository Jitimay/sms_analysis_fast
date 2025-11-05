#!/bin/bash

# ProofOfFace Deployment Script
# Deploy to testnet or production

set -e

NETWORK=${1:-"local"}

echo "🚀 Deploying ProofOfFace to $NETWORK network..."

case $NETWORK in
    "local")
        echo "📍 Deploying to local development network..."
        
        # Start local Substrate node
        echo "Starting Substrate node..."
        cd substrate-node
        ./target/release/proofofface-node --dev --tmp &
        SUBSTRATE_PID=$!
        cd ..
        
        # Wait for node to start
        sleep 10
        
        # Deploy contracts
        echo "Deploying smart contracts..."
        cd contracts
        cargo contract instantiate --constructor new --suri //Alice
        cd ..
        
        echo "✅ Local deployment complete!"
        echo "Substrate node PID: $SUBSTRATE_PID"
        ;;
        
    "testnet")
        echo "📍 Deploying to Polkadot testnet..."
        
        # Deploy to testnet
        cd contracts
        cargo contract instantiate --constructor new --url wss://rococo-contracts-rpc.polkadot.io
        cd ..
        
        echo "✅ Testnet deployment complete!"
        ;;
        
    "production")
        echo "📍 Deploying to production..."
        echo "⚠️  Production deployment not implemented yet"
        exit 1
        ;;
        
    *)
        echo "❌ Unknown network: $NETWORK"
        echo "Usage: ./deploy.sh [local|testnet|production]"
        exit 1
        ;;
esac

echo "🎉 Deployment finished!"