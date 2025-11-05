# ProofOfFace Documentation

Comprehensive documentation for the ProofOfFace decentralized identity verification system.

## 📚 Documentation Structure

### Architecture
- [System Architecture](./architecture.md) - High-level system design
- [Data Flow](./data-flow.md) - How data moves through the system
- [Security Model](./security.md) - Security considerations and implementations

### Development
- [Setup Guide](./setup.md) - Complete development environment setup
- [API Reference](./api-reference.md) - AI Service API documentation
- [Smart Contracts](./contracts.md) - Ink! contract documentation
- [Frontend Guide](./frontend.md) - React application development

### Deployment
- [Local Deployment](./deployment-local.md) - Running locally for development
- [Testnet Deployment](./deployment-testnet.md) - Deploying to Polkadot testnet
- [Production Deployment](./deployment-production.md) - Production deployment guide

### User Guides
- [User Manual](./user-manual.md) - End-user documentation
- [Integration Guide](./integration.md) - How to integrate ProofOfFace
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/proofofface
   cd proofofface
   ```

2. **Follow the setup guide**
   See [Setup Guide](./setup.md) for detailed instructions

3. **Run the demo**
   ```bash
   # Terminal 1: Start Substrate node
   cd substrate-node && cargo run --release -- --dev

   # Terminal 2: Start AI service
   cd ai-service && python app.py

   # Terminal 3: Start frontend
   cd frontend && npm start
   ```

## 🎯 Hackathon Deliverables

- [ ] Working MVP with core features
- [ ] Smart contract deployment on testnet
- [ ] AI service integration
- [ ] Frontend demo application
- [ ] Documentation and presentation

## 📞 Support

For questions or issues:
- Create an issue in the GitHub repository
- Contact the development team
- Check the troubleshooting guide

---

Built for Polkadot Cloud Hackathon 2024