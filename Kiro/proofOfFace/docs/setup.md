# ProofOfFace Setup Guide

Complete development environment setup for the ProofOfFace decentralized identity verification system.

## Prerequisites

### Required Software
- **Rust** (latest stable) - For Substrate and Ink! contracts
- **Node.js** (v16+) - For frontend development
- **Python** (3.8+) - For AI service
- **Git** - Version control
- **Docker** (optional) - For containerized deployment

### Installation Commands

#### Rust & Substrate
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Add WebAssembly target
rustup target add wasm32-unknown-unknown

# Install Substrate node template (optional)
git clone https://github.com/substrate-developer-hub/substrate-node-template
```

#### Node.js
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or download from nodejs.org
```

#### Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS
brew install python3

# Windows
# Download from python.org
```

## Project Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/proofofface
cd proofofface
```

### 2. Automated Setup
```bash
# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Manual Setup (Alternative)

#### Substrate Node
```bash
cd substrate-node
cargo build --release
```

#### AI Service
```bash
cd ai-service
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

#### Smart Contracts
```bash
# Install cargo-contract
cargo install --force --locked cargo-contract

cd contracts
cargo contract build
```

## Configuration

### Environment Variables

#### AI Service (.env)
```bash
cd ai-service
cat > .env << EOF
FLASK_ENV=development
IPFS_NODE_URL=http://localhost:5001
POSTGRES_URL=postgresql://user:pass@localhost/proofofface
FACE_RECOGNITION_TOLERANCE=0.6
PORT=5000
EOF
```

#### Frontend (.env)
```bash
cd frontend
cat > .env << EOF
REACT_APP_SUBSTRATE_WS_URL=ws://localhost:9944
REACT_APP_AI_SERVICE_URL=http://localhost:5000
REACT_APP_IPFS_GATEWAY=https://ipfs.io/ipfs/
EOF
```

### Database Setup (Optional)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb proofofface
sudo -u postgres createuser proofofface_user
```

### IPFS Setup (Optional)
```bash
# Install IPFS
wget https://dist.ipfs.io/go-ipfs/v0.14.0/go-ipfs_v0.14.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.14.0_linux-amd64.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/

# Initialize and start
ipfs init
ipfs daemon
```

## Running the Application

### Development Mode

#### Terminal 1: Substrate Node
```bash
cd substrate-node
./target/release/proofofface-node --dev --tmp
```

#### Terminal 2: AI Service
```bash
cd ai-service
source venv/bin/activate
python app.py
```

#### Terminal 3: Frontend
```bash
cd frontend
npm start
```

### Access Points
- **Frontend**: http://localhost:3000
- **AI Service**: http://localhost:5000
- **Substrate Node**: ws://localhost:9944

## Verification

### Test the Setup
```bash
# Check Substrate node
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' http://localhost:9933

# Check AI service
curl http://localhost:5000/health

# Check frontend
curl http://localhost:3000
```

## Troubleshooting

### Common Issues

#### Rust/Cargo Issues
```bash
# Update Rust
rustup update

# Clear cargo cache
cargo clean
```

#### Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install system dependencies (Ubuntu)
sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Performance Optimization

#### Substrate Node
- Use `--release` flag for production builds
- Increase database cache: `--db-cache 1024`
- Use SSD storage for better performance

#### AI Service
- Install OpenCV with optimizations
- Use GPU acceleration if available
- Implement caching for face encodings

## Next Steps

1. **Deploy Smart Contracts**: See [contracts/README.md](../contracts/README.md)
2. **Configure IPFS**: Set up distributed storage
3. **Set up Monitoring**: Add logging and metrics
4. **Security Hardening**: Review security checklist

## Support

- Check [troubleshooting guide](./troubleshooting.md)
- Review [architecture documentation](./architecture.md)
- Create GitHub issues for bugs
- Join community discussions

---

Setup complete! You're ready to start developing with ProofOfFace.