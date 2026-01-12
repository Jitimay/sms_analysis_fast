# RouteX Hackathon Submission

## Inspiration
Sending money globally is broken. Traditional banks charge ~7% and take days to settle. Even "modern" fintech apps often hide fees in exchange rate markups. We were inspired by the **Euro Coin (MNEE)** ecosystem and the speed of the Celo blockchain to create a solution that makes remittance **instant, transparent, and virtually free**. We wanted to prove that an **AI Agent** could navigate the complex web of bridges and swaps better than a human ever could.

## What it does
**RouteX** is an AI-powered remittance router. It:
1.  **Analyzes Real-Time Data**: Fetches live gas prices (via RPC) and token prices (CoinGecko).
2.  **Optimizes Routes**: An AI agent calculates the cheapest and fastest path for your money, comparing traditional banking vs. crypto rails in milliseconds.
3.  **Executes Safely**: Uses MNEE stablecoins to transfer value instantly without volatility risk.
4.  **Verifies on Chain**: All transactions are executable via smart contracts (simulated on Anvil for this demo), ensuring trustlessness.

## How we built it
We built RouteX using a modern "Agentic" tech stack:
*   **Frontend**: React + Vite for a high-performance, glassmorphism UI. We used `ethers.js` for deep wallet integration.
*   **Backend**: Python (FastAPI) acts as the "Brain". It aggregates market data and runs the routing logic.
*   **Blockchain**: Solidity smart contracts (Router & Oracle) developed with **Foundry**. We deployed to a local **Anvil** fork to simulate mainnet conditions cost-effectively.
*   **AI Integration**: The backend logic acts as an autonomous agent, making decisions based on live network conditions rather than static rules.

## Challenges we ran into
*   **Live Data Synchronization**: harmonizing off-chain API data (CoinGecko) with on-chain state (Gas Prices) was tricky to get right in real-time.
*   **Wallet UX**: Making a Web3 app feel like a Web2 fintech app is hard. We spent a lot of time ensuring MetaMask interactions felt smooth and errors were handled gracefully.
*   **Local Dev Environment**: integrating a local blockchain (Anvil) with a browser wallet required careful configuration of chain IDs and RPC endpoints.

## Accomplishments that we're proud of
*   **Fully Functional "Intent" UI**: Users just say "Send $100 to Kenya", and the AI handles the crypto complexity.
*   **Real Wallet Integration**: It connects to a real MetaMask wallet and triggers actual `ERC20.transfer` functions.
*   **Live Price Feeds**: The dashboard is alive, reacting to real market changes, not just static mock data.
*   **Vibe Coding**: We built this utilizing advanced AI coding assistants, logging our prompts and iteration history to showcase the future of software development.

## What we learned
*   **Stablecoins are King**: For remittance, volatility is the enemy. MNEE is perfect for this use case.
*   **User Experience is Key**: The technology doesn't matter if the user is confused. Abstracting the "bridge/swap" complexity is essential for adoption.
*   **Agentic Workflows**: Building *with* AI (using it as a pair programmer) exponentially increased our velocity.

## What's next for RouteX
*   **Mainnet Deployment**: Deploying our Router contracts to Celo Mainnet.
*   **More Corridors**: Expanding beyond EUR/MNEE to other global stablecoins.
*   **Mobile App**: Building a React Native version for on-the-go payments.
*   **Account Abstraction**: Implementing ERC-4337 to remove the need for users to hold gas tokens completely.
