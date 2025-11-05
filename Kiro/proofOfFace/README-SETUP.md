# 🚀 ProofOfFace Development Setup Guide

**Complete step-by-step instructions for setting up the ProofOfFace development environment**

## 📋 Prerequisites

Before starting, ensure you have the following software installed on your system:

### Required Software Versions
- **Rust**: 1.70.0 or later
- **Node.js**: 16.0.0 or later  
- **Python**: 3.8 or later
- **Git**: 2.30 or later
- **Docker**: 20.10 or later (optional, for containerized setup)
- **Docker Compose**: 2.0 or later (optional)

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 10GB free space
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11 with WSL2

---

## 🛠️ Installation Instructions

### Step 1: Install Rust and Cargo

#### Linux/macOS:
```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Reload your shell
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version

# Add WebAssembly target (required for Substrate)
rustup target add wasm32-unknown-unknown

# Update to latest stable
rustup update stable
```

#### Windows:
```powershell
# Download and run rustup-init.exe from https://rustup.rs/
# Or use chocolatey:
choco install rust

# Add WebAssembly target
rustup target add wasm32-unknown-unknown
```

### Step 2: Install Node.js and npm

#### Using Node Version Manager (Recommended):

**Linux/macOS:**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell or restart terminal
source ~/.bashrc

# Install and use Node.js 18
nvm install 18
nvm use 18
nvm alias default 18

# Verify installation
node --version
npm --version
```

**Windows:**
```powershell
# Install nvm-windows from: https://github.com/coreybutler/nvm-windows
# Then run:
nvm install 18.17.0
nvm use 18.17.0
```

#### Direct Installation:
Download from [nodejs.org](https://nodejs.org/) and install the LTS version.

### Step 3: Install Python

#### Linux (Ubuntu/Debian):
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv python3-dev

# Install system dependencies for face_recognition
sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev

# Verify installation
python3 --version
pip3 --version
```

#### macOS:
```bash
# Using Homebrew (install from https://brew.sh if needed)
brew install python3

# Install system dependencies
brew install cmake

# Verify installation
python3 --version
pip3 --version
```

#### Windows:
```powershell
# Download from python.org or use chocolatey:
choco install python3

# Install Visual Studio Build Tools (required for face_recognition)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Step 4: Install Additional Tools

#### Install cargo-contract (for Ink! smart contracts):
```bash
cargo install --force --locked cargo-contract --version 2.2.1
```

#### Install Docker (Optional but Recommended):

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again, then verify
docker --version
docker-compose --version
```

**macOS/Windows:**
Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)

---

## 📁 Project Setup

### Step 1: Clone the Repository
```bash
# Clone the project
git clone https://github.com/your-org/proofofface.git
cd proofofface

# Verify project structure
ls -la
```

### Step 2: Automated Setup (Recommended)
```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run automated setup
./scripts/setup.sh

# This will:
# - Install all Rust dependencies
# - Set up Python virtual environment
# - Install Node.js dependencies  
# - Build smart contracts
# - Create environment files
```

### Step 3: Manual Setup (Alternative)

If the automated setup fails, follow these manual steps:

#### Install Root Dependencies:
```bash
# Install workspace dependencies
npm install
```

#### Setup Substrate Node:
```bash
cd substrate-node

# Build the node (this takes 15-30 minutes)
cargo build --release

# Verify build
ls -la target/release/

cd ..
```

#### Setup AI Service:
```bash
cd ai-service

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=1
IPFS_NODE_URL=http://localhost:5001
POSTGRES_URL=postgresql://postgres:password@localhost:5432/proofofface
FACE_RECOGNITION_TOLERANCE=0.6
PORT=5000
EOF

cd ..
```

#### Setup Frontend:
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env << EOF
REACT_APP_SUBSTRATE_WS_URL=ws://localhost:9944
REACT_APP_AI_SERVICE_URL=http://localhost:5000
REACT_APP_IPFS_GATEWAY=http://localhost:8080/ipfs/
EOF

cd ..
```

#### Setup Smart Contracts:
```bash
cd contracts

# Build contracts
cargo contract build

# Verify build
ls -la target/ink/

cd ..
```

---

## 🚀 Running the Application

### Option 1: Docker Compose (Easiest)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop all services
docker-compose down
```

**Service URLs:**
- Frontend: http://localhost:3000
- AI Service: http://localhost:5000
- Substrate Node: ws://localhost:9944
- IPFS Gateway: http://localhost:8080
- PostgreSQL: localhost:5432

### Option 2: Manual Startup (Development)

You'll need **4 terminal windows**:

#### Terminal 1 - Substrate Node:
```bash
cd substrate-node
./target/release/proofofface-node --dev --tmp --ws-external --rpc-external --rpc-cors all
```

#### Terminal 2 - AI Service:
```bash
cd ai-service
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

python app.py
```

#### Terminal 3 - Frontend:
```bash
cd frontend
npm start
```

#### Terminal 4 - IPFS (Optional):
```bash
# Install IPFS if not using Docker
# Linux/macOS:
wget https://dist.ipfs.io/go-ipfs/v0.17.0/go-ipfs_v0.17.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.17.0_linux-amd64.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/

# Initialize and start
ipfs init
ipfs daemon
```

### Option 3: Using NPM Scripts

```bash
# Start all services concurrently
npm run start

# Or start individual services
npm run start:substrate
npm run start:ai  
npm run start:frontend
```

---

## 🔍 Verification & Testing

### Check Service Health:
```bash
# Check all services
npm run health

# Or check individually:
curl http://localhost:9933/health    # Substrate
curl http://localhost:5000/health    # AI Service  
curl http://localhost:3000           # Frontend
```

### Test the Application:

1. **Open Frontend**: Navigate to http://localhost:3000
2. **Register Identity**: Upload a selfie photo
3. **Verify Identity**: Test face verification
4. **Check Dashboard**: View your identity status

### Run Tests:
```bash
# Run all tests
npm run test

# Or run individual test suites
npm run test:contracts
npm run test:ai
npm run test:frontend
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Rust/Cargo Build Errors

**Error**: `error: linker 'cc' not found`
```bash
# Linux
sudo apt install build-essential

# macOS  
xcode-select --install
```

**Error**: `wasm32-unknown-unknown target not found`
```bash
rustup target add wasm32-unknown-unknown
```

#### 2. Python Face Recognition Issues

**Error**: `No module named 'face_recognition'`
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall with verbose output
pip install --verbose face_recognition
```

**Error**: `Microsoft Visual C++ 14.0 is required` (Windows)
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Error**: `cmake not found`
```bash
# Linux
sudo apt install cmake

# macOS
brew install cmake

# Windows
choco install cmake
```

#### 3. Node.js/NPM Issues

**Error**: `EACCES: permission denied`
```bash
# Fix npm permissions (Linux/macOS)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

**Error**: `Module not found`
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 4. Substrate Node Issues

**Error**: `Address already in use (port 9944)`
```bash
# Kill existing processes
sudo lsof -ti:9944 | xargs kill -9
sudo lsof -ti:9933 | xargs kill -9
```

**Error**: `Database error`
```bash
# Clear chain data
rm -rf /tmp/substrate*
```

#### 5. Docker Issues

**Error**: `Cannot connect to Docker daemon`
```bash
# Start Docker service
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

**Error**: `Port already in use`
```bash
# Stop conflicting services
docker-compose down
sudo lsof -ti:3000,5000,9944 | xargs kill -9
```

#### 6. IPFS Issues

**Error**: `IPFS daemon not running`
```bash
# Initialize IPFS (first time only)
ipfs init

# Start daemon
ipfs daemon
```

### Performance Optimization

#### For Slow Builds:
```bash
# Use more CPU cores for Rust compilation
export CARGO_BUILD_JOBS=4

# Use faster linker (Linux)
sudo apt install lld
export RUSTFLAGS="-C link-arg=-fuse-ld=lld"
```

#### For Memory Issues:
```bash
# Limit Rust compilation memory usage
export CARGO_BUILD_JOBS=2
```

### Getting Help

1. **Check Logs**:
   ```bash
   # Docker logs
   docker-compose logs -f [service-name]
   
   # Application logs
   tail -f ai-service/app.log
   ```

2. **Verify Versions**:
   ```bash
   rustc --version
   node --version  
   python3 --version
   docker --version
   ```

3. **Clean and Rebuild**:
   ```bash
   npm run clean
   npm run setup
   npm run build
   ```

---

## 🎯 Next Steps

Once everything is running:

1. **Deploy Smart Contracts**: 
   ```bash
   npm run deploy:local
   ```

2. **Test Face Recognition**:
   - Upload test images via the frontend
   - Check AI service logs for processing details

3. **Explore the Code**:
   - Review `contracts/src/` for smart contract logic
   - Check `ai-service/app.py` for face recognition API
   - Examine `frontend/src/` for React components

4. **Customize for Hackathon**:
   - Add your team branding
   - Implement additional features
   - Prepare demo scenarios

---

## 📞 Support

If you encounter issues not covered here:

1. Check the [troubleshooting guide](./docs/troubleshooting.md)
2. Review [architecture documentation](./docs/architecture.md)  
3. Create an issue in the GitHub repository
4. Join the community Discord/Telegram

---

**🎉 Congratulations! Your ProofOfFace development environment is ready!**

Access your application at:
- **Frontend**: http://localhost:3000
- **AI API**: http://localhost:5000/health
- **Substrate RPC**: http://localhost:9933/health

Happy hacking! 🚀