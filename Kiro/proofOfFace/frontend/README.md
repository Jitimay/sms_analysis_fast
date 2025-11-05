# ProofOfFace Frontend

React + TypeScript application for decentralized identity verification.

## Features

- Identity Registration Interface
- Photo Upload with Preview
- Verification Dashboard
- Dispute Management System
- Wallet Integration (Polkadot.js)
- Real-time Verification Status

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Tech Stack

- React 18 + TypeScript
- TailwindCSS for styling
- Polkadot.js API for blockchain interaction
- React Query for state management
- React Router for navigation
- Framer Motion for animations

## Environment Variables

Create a `.env` file:

```
REACT_APP_SUBSTRATE_WS_URL=ws://localhost:9944
REACT_APP_AI_SERVICE_URL=http://localhost:5000
REACT_APP_IPFS_GATEWAY=https://ipfs.io/ipfs/
```

## Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API and blockchain services
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── styles/             # Global styles and Tailwind config
```