import { createContext, useContext, useState, useEffect } from 'react'
import { ethers } from 'ethers'

const WalletContext = createContext()

export const useWallet = () => {
    const context = useContext(WalletContext)
    if (!context) {
        throw new Error('useWallet must be used within WalletProvider')
    }
    return context
}

export const WalletProvider = ({ children }) => {
    const [account, setAccount] = useState(null)
    const [provider, setProvider] = useState(null)
    const [signer, setSigner] = useState(null)
    const [balance, setBalance] = useState('0')
    const [connecting, setConnecting] = useState(false)

    const DAI_ADDRESS = '0x6B175474E89094C44Da98b954EedeAC495271d0F' // Real DAI on Ethereum

    const connectWallet = async () => {
        if (typeof window.ethereum === 'undefined') {
            alert('Please install MetaMask to use RouteX!')
            return
        }

        try {
            setConnecting(true)
            const provider = new ethers.providers.Web3Provider(window.ethereum)
            const accounts = await provider.send('eth_requestAccounts', [])
            const signer = provider.getSigner()
            const address = accounts[0]

            setProvider(provider)
            setSigner(signer)
            setAccount(address)

            // Get ETH balance
            const balance = await provider.getBalance(address)
            setBalance(ethers.utils.formatEther(balance))

        } catch (error) {
            console.error('Failed to connect wallet:', error)
            alert('Failed to connect wallet. Please try again.')
        } finally {
            setConnecting(false)
        }
    }

    const disconnectWallet = () => {
        setAccount(null)
        setProvider(null)
        setSigner(null)
        setBalance('0')
    }

    // Listen for account changes
    useEffect(() => {
        if (typeof window.ethereum !== 'undefined') {
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length === 0) {
                    disconnectWallet()
                } else {
                    setAccount(accounts[0])
                }
            })

            window.ethereum.on('chainChanged', () => {
                window.location.reload()
            })
        }

        return () => {
            if (typeof window.ethereum !== 'undefined') {
                window.ethereum.removeAllListeners('accountsChanged')
                window.ethereum.removeAllListeners('chainChanged')
            }
        }
    }, [])

        const executeRoute = async (amount, recipient, routeId) => {
            if (!signer) {
                throw new Error('Wallet not connected');
            }
    
            // IMPORTANT: This address has been updated by the agent.
            const ROUTEX_ROUTER_ADDRESS = '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0';
    
            const mneeABI = [
                'function approve(address spender, uint256 amount) returns (bool)',
                'function allowance(address owner, address spender) view returns (uint256)',
                'function balanceOf(address owner) view returns (uint256)',
            ];
    
            const routeXRouterABI = [
                'function executeRoute(uint256 amount, address recipient, string calldata routeId, uint256 simulatedSavings)'
            ];
    
            const daiContract = new ethers.Contract(DAI_ADDRESS, mneeABI, signer);
            const routeXRouterContract = new ethers.Contract(ROUTEX_ROUTER_ADDRESS, routeXRouterABI, signer);
    
            const amountWei = ethers.utils.parseUnits(amount.toString(), 18);
    
            try {
                // Check MNEE balance first
                const balance = await daiContract.balanceOf(account);
                if (balance.lt(amountWei)) {
                    throw new Error(`Insufficient MNEE balance. Need ${amount} MNEE, have ${ethers.utils.formatEther(balance)}`);
                }
    
                // Check allowance and approve if necessary
                const currentAllowance = await mneeContract.allowance(account, ROUTEX_ROUTER_ADDRESS);
                if (currentAllowance.lt(amountWei)) {
                    console.log('Allowance is insufficient, requesting approval...');
                    const approvalTx = await mneeContract.approve(ROUTEX_ROUTER_ADDRESS, amountWei);
                    await approvalTx.wait(); // Wait for the approval transaction to be mined
                    console.log('Approval successful!');
                } else {
                    console.log('Sufficient allowance already granted.');
                }
    
                // Execute the route on the router contract
                console.log('Executing route via RouteXRouter contract...');
                const simulatedSavings = ethers.utils.parseUnits((amount * 0.065).toString(), 18); // Example savings
                const executeTx = await routeXRouterContract.executeRoute(amountWei, recipient, routeId, simulatedSavings);
    
                // Save transaction to backend
                const saveResponse = await fetch('http://localhost:8000/save-transaction', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_address: account,
                        amount: amount,
                        route_id: routeId,
                        route_name: 'RouteX Optimized (MNEE)',
                        fee: amount * 0.005,
                        savings: amount * 0.065,
                        destination: 'Cross-border Payment'
                    })
                });
    
                if (!saveResponse.ok) {
                    console.warn('Failed to save transaction to database');
                }
    
                return executeTx;
            } catch (error) {
                console.error('Transaction failed:', error);
                throw error;
            }
        }
    return (
        <WalletContext.Provider value={{
            account,
            provider,
            signer,
            balance,
            connecting,
            connectWallet,
            disconnectWallet,
            executeRoute,
            USDC_ADDRESS
        }}>
            {children}
        </WalletContext.Provider>
    )
}
