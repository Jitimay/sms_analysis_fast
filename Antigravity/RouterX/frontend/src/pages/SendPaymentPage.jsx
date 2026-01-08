import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function SendPaymentPage() {
    const navigate = useNavigate()
    const [amount, setAmount] = useState(100)
    const [currency, setCurrency] = useState('USD')
    const [destination, setDestination] = useState('KE-MPESA')
    const [priority, setPriority] = useState('cheapest')

    const handleSubmit = (e) => {
        e.preventDefault()
        // Store payment details in sessionStorage for next pages
        sessionStorage.setItem('paymentIntent', JSON.stringify({
            amount,
            currency,
            destination,
            priority
        }))
        navigate('/routes')
    }

    return (
        <div className="dashboard-container">
            <header>
                <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
                <p style={{ marginTop: '-0.5rem', opacity: 0.7 }}>Send Money Smarter</p>
            </header>

            <div className="glass-card">
                <h2>Where do you want to send money?</h2>
                <p style={{ opacity: 0.7, marginTop: '0.5rem' }}>Just tell us what you want — we'll handle the rest</p>

                <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
                    <div className="input-group">
                        <div style={{ flex: 2 }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', opacity: 0.8 }}>Amount</label>
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(Number(e.target.value))}
                                placeholder="100"
                                required
                            />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', opacity: 0.8 }}>Currency</label>
                            <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                                <option value="USD">USD</option>
                                <option value="EUR">EUR</option>
                                <option value="GBP">GBP</option>
                            </select>
                        </div>
                    </div>

                    <div style={{ marginTop: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', opacity: 0.8 }}>Destination</label>
                        <select value={destination} onChange={(e) => setDestination(e.target.value)}>
                            <option value="KE-MPESA">Kenya — M-Pesa Mobile Money</option>
                            <option value="NG-BANK">Nigeria — Bank Transfer</option>
                            <option value="BR-PIX">Brazil — PIX Instant Payment</option>
                            <option value="WALLET">Crypto Wallet (Any Chain)</option>
                        </select>
                    </div>

                    <div style={{ marginTop: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', opacity: 0.8 }}>Priority</label>
                        <div style={{ display: 'flex', gap: '0.75rem' }}>
                            {['cheapest', 'fastest', 'reliable'].map(p => (
                                <button
                                    key={p}
                                    type="button"
                                    onClick={() => setPriority(p)}
                                    className={`priority-btn ${priority === p ? 'active' : ''}`}
                                    style={{
                                        flex: 1,
                                        padding: '0.75rem',
                                        background: priority === p ? 'rgba(99, 102, 241, 0.2)' : 'rgba(10, 14, 39, 0.5)',
                                        border: `2px solid ${priority === p ? '#6366f1' : 'rgba(99, 102, 241, 0.3)'}`,
                                        borderRadius: '8px',
                                        color: 'inherit',
                                        cursor: 'pointer',
                                        fontWeight: priority === p ? 600 : 400,
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    {p === 'cheapest' && '💰'} {p === 'fastest' && '⚡'} {p === 'reliable' && '🛡️'}
                                    <div style={{ marginTop: '0.25rem', fontSize: '0.9rem' }}>
                                        {p.charAt(0).toUpperCase() + p.slice(1)}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div style={{ marginTop: '2.5rem' }}>
                        <button type="submit" className="primary-btn" style={{ width: '100%', padding: '1.25rem' }}>
                            Find Best Route
                        </button>
                    </div>
                </form>
            </div>

            <p style={{ marginTop: '2rem', opacity: 0.6, fontSize: '0.9rem' }}>
                ℹ️ No wallet connection needed — RouteX handles everything
            </p>
        </div>
    )
}
