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

        // Standard ERC20 ABI for transfer
        const erc20ABI = [
            'function transfer(address to, uint256 amount) returns (bool)',
            'function decimals() view returns (uint8)'
        ]

        // Use the MNEE Token Contract directly
        const contract = new ethers.Contract(MNEE_ADDRESS, erc20ABI, signer)

        try {
            // Get decimals (usually 18, but safer to check or assume 18 for hackathon speed)
            // For now, assume 18 to save a network call, or use parseUnits if we want to be safe
            // const decimals = await contract.decimals() 
            const amountWei = ethers.utils.parseUnits(amount.toString(), 18)

            // Execute Direct Transfer
            // This ensures MetaMask shows "Transfer <Amount> MNEE" instead of "0 ETH"
            const tx = await contract.transfer(recipient, amountWei)

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
