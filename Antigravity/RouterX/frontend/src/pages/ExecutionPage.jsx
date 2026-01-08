import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function ExecutionPage() {
    const navigate = useNavigate()
    const [status, setStatus] = useState('pending') // pending, executing, completed, failed
    const [currentStep, setCurrentStep] = useState(0)
    const [txHash, setTxHash] = useState('')
    const [route, setRoute] = useState(null)

    const steps = [
        { label: 'Converting USD to MNEE', status: 'completed' },
        { label: 'Routing through Celo Bridge', status: 'executing' },
        { label: 'Converting to Local Currency (KES)', status: 'pending' },
        { label: 'Delivering to M-Pesa Wallet', status: 'pending' }
    ]

    useEffect(() => {
        const selectedRoute = JSON.parse(sessionStorage.getItem('selectedRoute') || '{}')
        if (!selectedRoute.id) {
            navigate('/send')
            return
        }
        setRoute(selectedRoute)

        // Simulate transaction execution
        const executionSteps = [
            { time: 1000, step: 0, hash: '0x8cce...' },
            { time: 2000, step: 1, hash: '0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF' },
            { time: 3000, step: 2, hash: '0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF' },
            { time: 4000, step: 3, status: 'completed' }
        ]

        executionSteps.forEach(({ time, step, hash, status: st }) => {
            setTimeout(() => {
                if (step !== undefined) setCurrentStep(step + 1)
                if (hash) setTxHash(hash)
                if (st) setStatus(st)
            }, time)
        })
    }, [navigate])

    useEffect(() => {
        if (status === 'completed') {
            setTimeout(() => navigate('/confirmation'), 1500)
        }
    }, [status, navigate])

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
                            {route.steps.join(' → ')}
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
                            opacity: idx < currentStep ? 1 : 0.5
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
                                {idx === currentStep && (
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
                                {idx === currentStep && (
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
