import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function ConfirmationPage() {
    const navigate = useNavigate()
    const [paymentIntent, setPaymentIntent] = useState(null)
    const [route, setRoute] = useState(null)
    const [traditionalFee, setTraditionalFee] = useState(0)

    useEffect(() => {
        const intent = JSON.parse(sessionStorage.getItem('paymentIntent') || '{}')
        const selectedRoute = JSON.parse(sessionStorage.getItem('selectedRoute') || '{}')

        if (!intent.amount || !selectedRoute.id) {
            navigate('/send')
            return
        }

        setPaymentIntent(intent)
        setRoute(selectedRoute)
        setTraditionalFee(intent.amount * 0.07) // 7% traditional fee
    }, [navigate])

    if (!paymentIntent || !route) return null

    const savingsPercent = ((traditionalFee - route.cost) / traditionalFee * 100).toFixed(0)

    return (
        <div className="dashboard-container">
            <header>
                <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
            </header>

            <div className="glass-card" style={{ maxWidth: '600px', borderColor: '#10b981' }}>
                <div className="success-icon">🎉</div>
                <h2 style={{ color: '#10b981' }}>Payment Successful!</h2>
                <p style={{ opacity: 0.8 }}>Your money is on its way</p>

                <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', textAlign: 'left' }}>
                        <div>
                            <div style={{ fontSize: '0.85rem', opacity: 0.7, marginBottom: '0.25rem' }}>Amount Sent</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>${paymentIntent.amount}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.85rem', opacity: 0.7, marginBottom: '0.25rem' }}>Destination</div>
                            <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{paymentIntent.destination}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.85rem', opacity: 0.7, marginBottom: '0.25rem' }}>RouteX Fee</div>
                            <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#10b981' }}>${route.cost.toFixed(2)}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.85rem', opacity: 0.7, marginBottom: '0.25rem' }}>Delivery Time</div>
                            <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{route.time}</div>
                        </div>
                    </div>
                </div>

                <div style={{
                    marginTop: '2rem',
                    padding: '1.5rem',
                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05))',
                    border: '2px solid #10b981',
                    borderRadius: '12px'
                }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem' }}>💰 You Saved Money!</div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                        <span style={{ opacity: 0.8 }}>Traditional Bank Fee:</span>
                        <span style={{ fontWeight: 600, textDecoration: 'line-through', opacity: 0.6 }}>${traditionalFee.toFixed(2)}</span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                        <span style={{ opacity: 0.8 }}>RouteX Fee:</span>
                        <span style={{ fontWeight: 700, color: '#10b981' }}>${route.cost.toFixed(2)}</span>
                    </div>

                    <div style={{
                        height: '1px',
                        background: 'rgba(255,255,255,0.2)',
                        margin: '1rem 0'
                    }}></div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.2rem', fontWeight: 600 }}>Total Savings:</span>
                        <span style={{ fontSize: '1.8rem', fontWeight: 800, color: '#10b981' }}>
                            ${(traditionalFee - route.cost).toFixed(2)}
                        </span>
                    </div>

                    <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '1.1rem', fontWeight: 700, color: '#34d399' }}>
                        You saved {savingsPercent}%! 🚀
                    </div>
                </div>

                <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '8px', fontSize: '0.9rem' }}>
                    <div style={{ opacity: 0.7, marginBottom: '0.5rem' }}>Route Taken:</div>
                    <div style={{ fontWeight: 500 }}>{route.steps.join(' → ')}</div>
                </div>

                <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
                    <Link to="/activity" style={{ flex: 1 }}>
                        <button className="primary-btn" style={{ width: '100%', background: 'transparent', border: '2px solid #6366f1' }}>
                            View History
                        </button>
                    </Link>
                    <Link to="/send" style={{ flex: 1 }}>
                        <button className="primary-btn" style={{ width: '100%' }}>
                            Send Another
                        </button>
                    </Link>
                </div>
            </div>
        </div >
    )
}
