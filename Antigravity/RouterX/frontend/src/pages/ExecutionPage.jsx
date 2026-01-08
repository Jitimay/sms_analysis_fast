import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWallet } from '../contexts/WalletContext'

export default function ExecutionPage() {
    const navigate = useNavigate()
    const { executeRoute } = useWallet()

    // Status: pending -> executing -> completed (or failed)
    const [status, setStatus] = useState('pending')
    const [currentStep, setCurrentStep] = useState(0)
    const [txHash, setTxHash] = useState('')
    const [route, setRoute] = useState(null)
    const [error, setError] = useState(null)

    const steps = [
        { label: 'Converting USD to MNEE', status: 'completed' },
        { label: 'Routing through Celo Bridge', status: 'executing' },
        { label: 'Converting to Local Currency (KES)', status: 'pending' },
        { label: 'Delivering to M-Pesa Wallet', status: 'pending' }
    ]

    useEffect(() => {
        // 1. Load Route Data
        try {
            const storedRoute = sessionStorage.getItem('selectedRoute')
            if (!storedRoute) {
                navigate('/send')
                return
            }
            const selectedRoute = JSON.parse(storedRoute)
            if (!selectedRoute.id) {
                navigate('/send')
                return
            }
            setRoute(selectedRoute)

            // 2. Execute Transaction
            handleExecution(selectedRoute)
        } catch (err) {
            console.error("Failed to load route:", err)
            navigate('/send')
        }
    }, []) // Run once on mount

    const handleExecution = async (selectedRoute) => {
        try {
            setStatus('executing')
            setCurrentStep(0)
            await new Promise(r => setTimeout(r, 1000))

            setCurrentStep(1)

            // Get payment intent for amount
            const paymentIntent = JSON.parse(sessionStorage.getItem('paymentIntent') || '{}')
            const amount = paymentIntent.amount || 100
            const recipient = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"

            console.log("Initiating real MNEE transaction:", { amount, recipient, routeId: selectedRoute.id })
            
            const tx = await executeRoute(amount, recipient, selectedRoute.id)

            if (tx && tx.hash) {
                setTxHash(tx.hash)
                console.log("Transaction successful:", tx.hash)
            } else {
                throw new Error('Transaction returned invalid response')
            }

            setCurrentStep(2)
            await new Promise(r => setTimeout(r, 2000))

            setCurrentStep(3)
            setStatus('completed')

            setTimeout(() => {
                navigate('/confirmation')
            }, 2000)

        } catch (err) {
            console.error("Transaction execution failed:", err)
            setError(err.message || 'Transaction failed')
            setStatus('failed')
        }
    }

    if (error) {
        return (
            <div className="dashboard-container">
                <div className="glass-card" style={{ maxWidth: '700px', textAlign: 'center', borderColor: '#ef4444' }}>
                    <h2 style={{ color: '#ef4444' }}>Execution Failed</h2>
                    <p style={{ opacity: 0.8, marginBottom: '2rem' }}>{error}</p>
                    <button className="primary-btn" onClick={() => navigate('/send')}>Try Again</button>
                    <button className="secondary-btn" onClick={() => navigate('/')} style={{ marginLeft: '1rem' }}>Home</button>
                </div>
            </div>
        )
    }

    return (
        <div className="dashboard-container">
            <header>
                <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
                <p style={{ marginTop: '-0.5rem', opacity: 0.7 }}>Transaction in Progress</p>
            </header>

            <div className="glass-card" style={{ maxWidth: '700px' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div className="loader" style={{ margin: '0 auto 1rem' }}></div>
                    <h2>Executing Payment</h2>
                    <p style={{ opacity: 0.7 }}>Your transaction is being processed securely</p>
                </div>

                {route && (
                    <div style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '0.5rem' }}>Selected Route:</div>
                        <div style={{ fontWeight: 600 }}>{route.name}</div>
                        <div style={{ fontSize: '0.9rem', opacity: 0.7, marginTop: '0.25rem' }}>
                            {route.steps ? route.steps.join(' → ') : 'Direct Transfer'}
                        </div>
                    </div>
                )}

                <div style={{ marginTop: '2rem' }}>
                    <div style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '1rem' }}>Transaction Progress:</div>

                    {steps.map((step, idx) => (
                        <div key={idx} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '1rem',
                            marginBottom: '1.5rem',
                            opacity: idx < currentStep ? 1 : idx === currentStep ? 1 : 0.5
                        }}>
                            <div style={{
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                background: idx < currentStep ? '#10b981' : idx === currentStep ? '#6366f1' : 'rgba(99, 102, 241, 0.2)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexShrink: 0,
                                position: 'relative'
                            }}>
                                {idx < currentStep && <span>✓</span>}
                                {idx === currentStep && status !== 'failed' && (
                                    <div style={{
                                        width: '12px',
                                        height: '12px',
                                        borderRadius: '50%',
                                        background: '#fff',
                                        animation: 'pulse-dot 1.5s ease-in-out infinite'
                                    }}></div>
                                )}
                            </div>

                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 500 }}>{step.label}</div>
                                {idx === currentStep && status !== 'failed' && (
                                    <div style={{ fontSize: '0.85rem', opacity: 0.7, marginTop: '0.25rem' }}>
                                        Processing...
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {txHash && (
                    <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '0.5rem' }}>Transaction Hash:</div>
                        <div style={{ fontFamily: 'monospace', fontSize: '0.9rem', wordBreak: 'break-all' }}>
                            {txHash}
                        </div>
                    </div>
                )}

                {status === 'completed' && (
                    <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✓</div>
                        <div style={{ color: '#10b981', fontWeight: 600 }}>Transaction Completed!</div>
                        <div style={{ fontSize: '0.9rem', opacity: 0.8, marginTop: '0.25rem' }}>Redirecting...</div>
                    </div>
                )}
            </div>
        </div>
    )
}
