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

    const MNEE_ADDRESS = '0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF' // Real MNEE on Ethereum

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

        const erc20ABI = [
            'function transfer(address to, uint256 amount) returns (bool)',
            'function balanceOf(address owner) view returns (uint256)',
            'function decimals() view returns (uint8)'
        ]

        const contract = new ethers.Contract(MNEE_ADDRESS, erc20ABI, signer)

        try {
            // Check MNEE balance first
            const balance = await contract.balanceOf(account)
            const amountWei = ethers.utils.parseUnits(amount.toString(), 18)
            
            if (balance.lt(amountWei)) {
                throw new Error(`Insufficient MNEE balance. Need ${amount} MNEE, have ${ethers.utils.formatEther(balance)}`)
            }

            // Execute transfer
            const tx = await contract.transfer(recipient, amountWei)
            
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
            })

            if (!saveResponse.ok) {
                console.warn('Failed to save transaction to database')
            }

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
