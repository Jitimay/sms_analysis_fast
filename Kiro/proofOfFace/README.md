# ProofOfFace - Decentralized Identity Verification

**Polkadot Cloud Hackathon Submission**

A decentralized identity verification system that prevents deepfake impersonation using blockchain technology and AI-powered face recognition.

## 🎯 Problem Statement

With the rise of deepfakes and AI-generated content, verifying authentic human identity has become critical. ProofOfFace creates an immutable, decentralized record of verified identities to combat impersonation.

## 🏗️ Architecture

```
ProofOfFace System
├── Substrate Node (Polkadot/Substrate)
│   ├── Identity Registration Pallet
│   └── FaceProof NFT Management
├── AI Service (Python Flask)
│   ├── Face Recognition Engine
│   └── Verification API
├── Frontend (React + TypeScript)
│   ├── Identity Registration UI
│   ├── Verification Dashboard
│   └── Dispute Management
└── IPFS Storage
    ├── Encrypted Face Embeddings
    └── Metadata Storage
```

## 🚀 Core Features

### 1. Identity Registration
- Upload selfie photo
- Generate unique face embedding
- Mint FaceProof NFT on Polkadot
- Store encrypted data on IPFS

### 2. Verification API
- Compare submitted photo against registered identities
- Return verification score and confidence level
- Prevent unauthorized impersonation

### 3. Dispute Mechanism
- Flag suspicious verification attempts
- Community-driven dispute resolution
- Reputation scoring system

## 🛠️ Tech Stack

- **Blockchain**: Polkadot/Substrate
- **Smart Contracts**: Ink! (Rust)
- **Storage**: IPFS
- **Frontend**: React + TypeScript + TailwindCSS
- **AI**: Python Flask + face_recognition library
- **Database**: PostgreSQL (for caching)

## 📁 Project Structure

```
proofofface/
├── substrate-node/          # Blockchain backend
├── contracts/              # Ink! smart contracts
├── ai-service/             # Python face recognition API
├── frontend/               # React application
├── docs/                   # Documentation
└── scripts/                # Deployment & utility scripts
```

## 🚦 Getting Started

1. **Setup Substrate Node**
   ```bash
   cd substrate-node
   cargo build --release
   ./target/release/node-template --dev
   ```

2. **Start AI Service**
   ```bash
   cd ai-service
   pip install -r requirements.txt
   python app.py
   ```

3. **Launch Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 🔐 Security Features

- End-to-end encryption of biometric data
- Zero-knowledge proofs for privacy
- Decentralized storage prevents single points of failure
- Multi-signature dispute resolution

## 🎯 Hackathon Goals

- [ ] MVP with basic identity registration
- [ ] Face verification API integration
- [ ] Simple dispute mechanism
- [ ] Polkadot parachain deployment
- [ ] Demo application

## 📄 License

MIT License - Built for Polkadot Cloud Hackathon

---

**Team**: [Your Team Name]  
**Contact**: [Your Contact Info]  
**Demo**: [Demo URL when available]