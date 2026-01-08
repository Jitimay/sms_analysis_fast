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

    const MNEE_ADDRESS = '0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF'

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
            throw new Error('Wallet not connected')
        }

        // RouteX Router Contract ABI
        const routerABI = [
            'function executeRoute(uint256 amount, address recipient, string calldata routeId, uint256 simulatedSavings) external'
        ]

        // For demo purposes, we'll use a mock contract address
        // In production, this would be the deployed RouteXRouter
        const ROUTER_ADDRESS = '0x0000000000000000000000000000000000000001' // Mock

        const contract = new ethers.Contract(ROUTER_ADDRESS, routerABI, signer)

        try {
            // Convert amount to Wei (assuming MNEE has 18 decimals like standard ERC20)
            const amountWei = ethers.utils.parseEther(amount.toString())
            const savingsWei = ethers.utils.parseEther('6.49') // Mock savings

            const tx = await contract.executeRoute(
                amountWei,
                recipient,
                routeId,
                savingsWei
            )

            return tx
        } catch (error) {
            console.error('Transaction failed:', error)
            throw error
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
            MNEE_ADDRESS
        }}>
            {children}
        </WalletContext.Provider>
    )
}
