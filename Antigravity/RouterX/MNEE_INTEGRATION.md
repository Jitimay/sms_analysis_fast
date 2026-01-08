# MNEE Integration Documentation

## Contract Address
RouterX integrates with MNEE stablecoin at: `0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF`

## AI Agent Payment Flow
1. Agent fetches live market data (CoinGecko API, Celo gas prices)
2. Calculates optimal route using MNEE pricing
3. Executes payment through RouteXRouter contract
4. Validates transaction with Chainlink oracle

## Programmable Money Features
- Automated route selection based on cost/speed preferences
- Real-time fee calculation using live MNEE price feeds
- Smart contract execution with slippage protection
- Event-driven transaction tracking

## Economic Coordination
- Eliminates manual routing decisions
- Transparent cost comparison across payment rails
- Automated settlement in 3 seconds vs days
- 90%+ cost savings through intelligent routing
