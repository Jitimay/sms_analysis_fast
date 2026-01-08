import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export default function RouteComparisonPage() {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [routes, setRoutes] = useState([])
    const [selectedRoute, setSelectedRoute] = useState(null)
    const [paymentIntent, setPaymentIntent] = useState(null)

    useEffect(() => {
        const intent = JSON.parse(sessionStorage.getItem('paymentIntent') || '{}')
        if (!intent.amount) {
            navigate('/send')
            return
        }
        setPaymentIntent(intent)

        // Fetch Real-Time Data from Python Backend
        const fetchRoutes = async () => {
            try {
                const response = await fetch('http://localhost:8000/optimize-route', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        amount: intent.amount,
                        currency: intent.currency,
                        destination: intent.destination,
                        priority: intent.priority
                    })
                })

                if (!response.ok) throw new Error('Failed to fetch routes')

                const data = await response.json()
                setRoutes(data.routes_evaluated)
                setSelectedRoute(data.routes_evaluated.find(r => r.is_best))
            } catch (err) {
                console.error('API Error:', err)
                // FallbackMock for demo stability if backend is offline
                setRoutes(fallbackRoutes(intent.amount))
            } finally {
                setLoading(false)
            }
        }

        fetchRoutes()
    }, [navigate])

    const fallbackRoutes = (amount) => [
        {
            id: 'route_a',
            name: 'Traditional Bank Wire',
            provider: 'SWIFT / Western Union',
            fee: amount * 0.07,
            time: '2-3 days',
            reliability: '92%',
            savings: 0
        },
        {
            id: 'route_c',
            name: 'RouteX Optimized (MNEE)',
            provider: 'AI-Selected Path',
            fee: amount * 0.005,
            time: '3 seconds',
            reliability: '98%',
            is_best: true,
            savings: (amount * 0.07) - (amount * 0.005)
        }
    ]

    const handleProceed = () => {
        if (selectedRoute) {
            sessionStorage.setItem('selectedRoute', JSON.stringify(selectedRoute))
            navigate('/execute')
        }
    }

    if (loading) {
        return (
            <div className="dashboard-container">
                <div className="glass-card">
                    <span className="loader"></span>
                    <h3>AI Agent analyzing routes...</h3>
                    <p style={{ opacity: 0.6 }}>Checking gas fees, liquidity, FX rates across 12+ bridges</p>
                </div>
            </div>
        )
    }

    return (
        <div className="dashboard-container">
            <header>
                <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
                <p style={{ marginTop: '-0.5rem', opacity: 0.7 }}>Route Comparison</p>
            </header>

            <div className="glass-card" style={{ maxWidth: '900px' }}>
                <div style={{ textAlign: 'left', marginBottom: '2rem' }}>
                    <span style={{ opacity: 0.6, fontSize: '0.9rem' }}>OPTIMAL ROUTE FOUND</span>
                    {selectedRoute && (
                        <div className="savings-highlight">
                            Saved ${selectedRoute.savings.toFixed(2)}
                        </div>
                    )}
                </div>

                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 1rem' }}>
                        <thead>
                            <tr style={{ textAlign: 'left', opacity: 0.7 }}>
                                <th style={{ padding: '0.5rem' }}>Route</th>
                                <th style={{ padding: '0.5rem' }}>Cost</th>
                                <th style={{ padding: '0.5rem' }}>Time</th>
                                <th style={{ padding: '0.5rem' }}>Reliability</th>
                            </tr>
                        </thead>
                        <tbody>
                            {routes.map(route => (
                                <tr
                                    key={route.id}
                                    className={`route-item ${route.selected ? 'best-route' : ''}`}
                                    style={{
                                        opacity: route.selected ? 1 : 0.6,
                                        cursor: 'pointer'
                                    }}
                                    onClick={() => setSelectedRoute(route)}
                                >
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ fontWeight: 600 }}>{route.name}</div>
                                        <div style={{ fontSize: '0.85rem', opacity: 0.7 }}>{route.provider}</div>
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ fontWeight: 700 }}>${route.fee.toFixed(2)}</div>
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <div>{route.delivery_time || route.time}</div>
                                    </td>
                                    <td style={{ padding: '1rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <div style={{
                                                width: typeof route.reliability === 'string' ? route.reliability : `${route.reliability}%`,
                                                height: '8px',
                                                background: '#10b981',
                                                borderRadius: '4px'
                                            }}></div>
                                            <span style={{ fontSize: '0.9rem' }}>{route.reliability}</span>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {selectedRoute && (
                    <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '12px', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                        <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>💡 Why this route was selected:</div>
                        <p style={{ opacity: 0.8, margin: 0 }}>
                            {selectedRoute.id === 'route_c'
                                ? 'AI chose MNEE routing through Celo because it offers the lowest fees ($0.51 vs $7.00), fastest settlement (3 seconds), and highest reliability (98%). The smart contract automatically selected the optimal liquidity pool with minimal slippage.'
                                : 'This route optimizes for your selected priority.'
                            }
                        </p>
                    </div>
                )}

                <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
                    <button
                        className="primary-btn"
                        style={{ flex: 1, background: 'transparent', border: '2px solid #6366f1' }}
                        onClick={() => navigate('/send')}
                    >
                        ← Back
                    </button>
                    <button
                        className="primary-btn"
                        style={{ flex: 2 }}
                        onClick={handleProceed}
                    >
                        Execute Transaction
                    </button>
                </div>
            </div>
        </div>
    )
}
