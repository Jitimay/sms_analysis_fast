# RouterX - AI-Powered Programmable Money for Autonomous Agents

## 🎯 MNEE Hackathon Project
**Track: AI & Agent Payments**

RouterX demonstrates the future of programmable money where AI agents autonomously optimize and execute cross-border payments using MNEE stablecoin. This is true autonomous economic coordination - agents making financial decisions without human intervention.

## 🤖 Autonomous AI Agent Features
- **Self-Directed Market Analysis**: AI fetches live MNEE prices and Ethereum gas costs
- **Autonomous Route Selection**: Agent compares traditional banking vs blockchain routes
- **Automated Execution**: Smart contracts execute MNEE payments without human approval
- **Economic Coordination**: Demonstrates how agents can coordinate financial activities

## 💰 MNEE Integration
- **Contract**: `0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF` (Real MNEE on Ethereum)
- **Programmable Money**: MNEE enables autonomous agent transactions
- **Live Price Feeds**: Real-time MNEE pricing for cost calculations
- **Smart Contract Automation**: Oracle-validated MNEE transfers

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ and pip
- MetaMask browser extension

### One-Command Setup
```bash
./start.sh
```

This will:
- Install all dependencies
- Start backend API on http://localhost:8000
- Start frontend on http://localhost:5173
- Initialize the database

### Manual Setup
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 🤖 AI Agent Functionality
- **Autonomous Decision Making**: AI agent analyzes live market conditions
- **Real-Time Data Integration**: CoinGecko API + Celo network gas prices
- **Intelligent Routing**: Compares traditional banking vs blockchain routes
- **Automated Execution**: Smart contract payments without human intervention
- **Transaction Persistence**: Saves all transactions to local database

## 💰 MNEE Integration
- Contract: `0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF`
- Live price feeds for cost calculations
- Automated MNEE transfers through RouteXRouter
- Oracle validation for secure execution

## 🛠 Tech Stack
- **Backend**: Python/FastAPI (AI Agent) + SQLite Database
- **Smart Contracts**: Solidity with Chainlink oracles
- **Frontend**: React 19 with Web3 integration
- **Network**: Celo (MNEE native chain)

## 📊 Demo Flow
1. User inputs payment details
2. AI agent fetches live market data
3. Agent calculates optimal route using MNEE pricing
4. Smart contract executes payment automatically
5. Transaction saved to database
6. Real-time savings displayed to user

## 🏆 Production Features
- ✅ Real-time market data integration
- ✅ Database transaction persistence
- ✅ Error handling and recovery
- ✅ Environment configuration
- ✅ Smart contract testing
- ✅ Comprehensive logging

## 🔧 API Endpoints
- `POST /optimize-route` - Get optimal payment route
- `POST /save-transaction` - Save transaction to database
- `GET /transactions/{address}` - Get user transaction history
- `GET /docs` - Interactive API documentation

## 🧪 Testing
```bash
# Smart Contract Tests
cd contracts
forge test

# Backend Tests
cd backend
python -m pytest

# Frontend Tests
cd frontend
npm test
```

## 🌟 Impact
- **90%+ cost savings** vs traditional remittances
- **3-second settlement** vs 2-3 days
- **$700B+ market** addressable
- **Real-world utility** for cross-border payments
