# ProofOfFace Makefile
# Convenient commands for development and deployment

.PHONY: help setup build start stop clean test health deploy

# Default target
help:
	@echo "ProofOfFace Development Commands"
	@echo "==============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete development environment setup"
	@echo "  make setup-rust     - Install Rust dependencies"
	@echo "  make setup-python   - Setup Python virtual environment"
	@echo "  make setup-node     - Install Node.js dependencies"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build          - Build all components"
	@echo "  make build-substrate - Build Substrate node"
	@echo "  make build-contracts - Build smart contracts"
	@echo "  make build-frontend - Build React frontend"
	@echo ""
	@echo "Development:"
	@echo "  make start          - Start all services"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View service logs"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make health         - Check service health"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-local   - Deploy to local environment"
	@echo "  make deploy-testnet - Deploy to testnet"
	@echo "  make docker-up      - Start with Docker Compose"
	@echo "  make docker-down    - Stop Docker services"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make reset          - Complete environment reset"

# Setup commands
setup:
	@echo "🚀 Setting up ProofOfFace development environment..."
	chmod +x scripts/*.sh
	./scripts/setup.sh

setup-rust:
	@echo "🦀 Setting up Rust environment..."
	rustup target add wasm32-unknown-unknown
	cargo install --force --locked cargo-contract

setup-python:
	@echo "🐍 Setting up Python environment..."
	cd ai-service && python3 -m venv venv
	cd ai-service && source venv/bin/activate && pip install -r requirements.txt

setup-node:
	@echo "📦 Setting up Node.js environment..."
	npm install
	cd frontend && npm install

# Build commands
build: build-substrate build-contracts build-frontend

build-substrate:
	@echo "🔗 Building Substrate node..."
	cd substrate-node && cargo build --release

build-contracts:
	@echo "📜 Building smart contracts..."
	cd contracts && cargo contract build

build-frontend:
	@echo "🎨 Building frontend..."
	cd frontend && npm run build

# Development commands
start:
	@echo "🚀 Starting all services..."
	npm run start

stop:
	@echo "🛑 Stopping all services..."
	pkill -f "proofofface-node" || true
	pkill -f "python.*app.py" || true
	pkill -f "npm.*start" || true

restart: stop start

logs:
	@echo "📋 Viewing service logs..."
	docker-compose logs -f

# Testing commands
test:
	@echo "🧪 Running all tests..."
	npm run test

test-contracts:
	@echo "📜 Testing smart contracts..."
	cd contracts && cargo test

test-ai:
	@echo "🤖 Testing AI service..."
	cd ai-service && source venv/bin/activate && pytest

test-frontend:
	@echo "🎨 Testing frontend..."
	cd frontend && npm test -- --watchAll=false

# Health and quality commands
health:
	@echo "🏥 Checking service health..."
	chmod +x scripts/health-check.sh
	./scripts/health-check.sh

lint:
	@echo "🔍 Running code linting..."
	cd contracts && cargo clippy
	cd ai-service && source venv/bin/activate && flake8 .
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	cd contracts && cargo fmt
	cd ai-service && source venv/bin/activate && black .
	cd frontend && npm run format

# Deployment commands
deploy-local:
	@echo "🏠 Deploying to local environment..."
	./scripts/deploy.sh local

deploy-testnet:
	@echo "🌐 Deploying to testnet..."
	./scripts/deploy.sh testnet

# Docker commands
docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-logs:
	@echo "🐳 Viewing Docker logs..."
	docker-compose logs -f

# Maintenance commands
clean:
	@echo "🧹 Cleaning build artifacts..."
	cd substrate-node && cargo clean
	cd contracts && cargo clean
	cd frontend && rm -rf build node_modules
	rm -rf ai-service/__pycache__

clean-docker:
	@echo "🐳 Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

reset: clean
	@echo "🔄 Resetting environment..."
	rm -rf ai-service/venv
	rm -rf frontend/node_modules
	rm -rf target/
	make setup

# Development shortcuts
dev: start
up: docker-up
down: docker-down
check: health