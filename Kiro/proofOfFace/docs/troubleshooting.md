# ProofOfFace Troubleshooting Guide

Common issues and their solutions for the ProofOfFace development environment.

## 🔧 Build Issues

### Rust/Substrate Build Errors

#### Error: `linker 'cc' not found`
**Solution:**
```bash
# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install build-essential

# Linux (CentOS/RHEL)
sudo yum groupinstall "Development Tools"

# macOS
xcode-select --install
```

#### Error: `wasm32-unknown-unknown target not found`
**Solution:**
```bash
rustup target add wasm32-unknown-unknown
```

#### Error: `cargo-contract not found`
**Solution:**
```bash
cargo install --force --locked cargo-contract --version 2.2.1
```

#### Error: Substrate build takes too long
**Solution:**
```bash
# Use more CPU cores
export CARGO_BUILD_JOBS=$(nproc)

# Use faster linker (Linux only)
sudo apt install lld
export RUSTFLAGS="-C link-arg=-fuse-ld=lld"

# Enable incremental compilation
export CARGO_INCREMENTAL=1
```

### Python/AI Service Issues

#### Error: `No module named 'face_recognition'`
**Solution:**
```bash
# Ensure virtual environment is activated
cd ai-service
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Error: `Microsoft Visual C++ 14.0 is required` (Windows)
**Solution:**
1. Download Visual Studio Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install with C++ build tools workload
3. Restart terminal and try again

#### Error: `cmake not found`
**Solution:**
```bash
# Linux
sudo apt install cmake

# macOS
brew install cmake

# Windows
choco install cmake
```

#### Error: `dlib installation failed`
**Solution:**
```bash
# Linux - install system dependencies first
sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev

# macOS
brew install cmake boost

# Then reinstall dlib
pip install --upgrade dlib
```

### Node.js/Frontend Issues

#### Error: `EACCES: permission denied` (npm)
**Solution:**
```bash
# Linux/macOS - fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### Error: `Module not found` or dependency issues
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Error: `Port 3000 already in use`
**Solution:**
```bash
# Find and kill process using port 3000
sudo lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start
```

## 🐳 Docker Issues

### Docker Daemon Issues

#### Error: `Cannot connect to Docker daemon`
**Solution:**
```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

#### Error: `Port already in use`
**Solution:**
```bash
# Stop all containers
docker-compose down

# Kill processes using ports
sudo lsof -ti:3000,5000,9944,9933 | xargs kill -9

# Start fresh
docker-compose up -d
```

#### Error: `No space left on device`
**Solution:**
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Remove unused images
docker image prune -a
```

### Docker Compose Issues

#### Error: `Service 'substrate-node' failed to build`
**Solution:**
```bash
# Build with no cache
docker-compose build --no-cache substrate-node

# Check Dockerfile syntax
docker build -t test-substrate ./substrate-node
```

#### Error: `Health check failed`
**Solution:**
```bash
# Check service logs
docker-compose logs substrate-node

# Restart specific service
docker-compose restart substrate-node
```

## 🌐 Network & Connectivity Issues

### Substrate Node Connection Issues

#### Error: `Connection refused` to ws://localhost:9944
**Solution:**
```bash
# Check if node is running
curl http://localhost:9933/health

# Restart with correct flags
./target/release/proofofface-node --dev --tmp --ws-external --rpc-external --rpc-cors all

# Check firewall settings
sudo ufw allow 9944
sudo ufw allow 9933
```

#### Error: `RPC methods not available`
**Solution:**
```bash
# Start node with unsafe methods (development only)
./target/release/proofofface-node --dev --rpc-methods unsafe --rpc-cors all
```

### AI Service Connection Issues

#### Error: `AI service not responding`
**Solution:**
```bash
# Check if service is running
curl http://localhost:5000/health

# Check Python virtual environment
cd ai-service
source venv/bin/activate
python app.py

# Check logs for errors
tail -f app.log
```

### IPFS Connection Issues

#### Error: `IPFS daemon not running`
**Solution:**
```bash
# Initialize IPFS (first time only)
ipfs init

# Start daemon
ipfs daemon

# Check status
ipfs id
```

#### Error: `CORS issues with IPFS`
**Solution:**
```bash
# Configure IPFS for web access
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "POST", "GET"]'

# Restart daemon
ipfs shutdown
ipfs daemon
```

## 💾 Database Issues

### PostgreSQL Connection Issues

#### Error: `Connection refused` to PostgreSQL
**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check connection
psql -h localhost -U postgres -d proofofface
```

#### Error: `Database does not exist`
**Solution:**
```bash
# Create database
sudo -u postgres createdb proofofface

# Run initialization script
psql -h localhost -U postgres -d proofofface -f ai-service/init.sql
```

## 🔐 Permission Issues

### File Permission Errors

#### Error: `Permission denied` when running scripts
**Solution:**
```bash
# Make scripts executable
chmod +x scripts/setup.sh
chmod +x scripts/deploy.sh

# Fix ownership if needed
sudo chown -R $USER:$USER .
```

### Docker Permission Issues

#### Error: `Permission denied` in Docker containers
**Solution:**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./ai-service
sudo chown -R 1000:1000 ./substrate-node
```

## 🚀 Performance Issues

### Slow Build Times

**Solution:**
```bash
# Use parallel builds
export CARGO_BUILD_JOBS=$(nproc)

# Use faster linker (Linux)
export RUSTFLAGS="-C link-arg=-fuse-ld=lld"

# Enable incremental compilation
export CARGO_INCREMENTAL=1
```

### High Memory Usage

**Solution:**
```bash
# Limit Rust compilation jobs
export CARGO_BUILD_JOBS=2

# Use swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow Face Recognition

**Solution:**
```bash
# Install optimized OpenCV
pip uninstall opencv-python
pip install opencv-contrib-python

# Use GPU acceleration (if available)
pip install opencv-python-headless[gpu]
```

## 🔍 Debugging Tips

### Enable Debug Logging

#### Substrate Node:
```bash
RUST_LOG=debug ./target/release/proofofface-node --dev
```

#### AI Service:
```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
python app.py
```

#### Frontend:
```bash
REACT_APP_DEBUG=true npm start
```

### Check Service Status

```bash
# All services health check
npm run health

# Individual service checks
curl http://localhost:9933/health    # Substrate
curl http://localhost:5000/health    # AI Service
curl http://localhost:3000           # Frontend
curl http://localhost:5001/api/v0/id # IPFS
```

### View Logs

```bash
# Docker logs
docker-compose logs -f [service-name]

# System logs
journalctl -u docker
tail -f /var/log/syslog

# Application logs
tail -f ai-service/app.log
tail -f frontend/build/static/js/*.js.map
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Verify all prerequisites are installed**
3. **Try the clean setup process**:
   ```bash
   npm run clean
   ./scripts/setup.sh
   ```
4. **Check service logs for error messages**
5. **Verify network connectivity between services**

### Information to Include

When reporting issues, please include:

- Operating system and version
- Software versions (Rust, Node.js, Python, Docker)
- Complete error messages
- Steps to reproduce the issue
- Relevant log outputs
- Output of `npm run health`

### Community Support

- **GitHub Issues**: Create detailed bug reports
- **Documentation**: Check [docs/](../docs/) folder
- **Setup Guide**: Review [README-SETUP.md](../README-SETUP.md)

### Emergency Reset

If everything is broken, try this complete reset:

```bash
# Stop all services
docker-compose down -v
pkill -f "proofofface-node"
pkill -f "python.*app.py"

# Clean everything
npm run clean
docker system prune -a
rm -rf ai-service/venv
rm -rf frontend/node_modules

# Fresh setup
./scripts/setup.sh
npm run start
```

---

**Remember**: Most issues are environment-related. When in doubt, try the automated setup script first!