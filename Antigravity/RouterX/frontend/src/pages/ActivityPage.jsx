import { Link } from 'react-router-dom'

export default function ActivityPage() {
    // Mock transaction history
    const transactions = [
        {
            id: '1',
            amount: 500,
            destination: 'KE-MPESA',
            route: 'RouteX Optimized (MNEE)',
            fee: 2.51,
            savings: 32.49,
            status: 'completed',
            date: '2026-01-06 17:15',
            txHash: '0x8ccedbAe...2bFD6cF'
        },
        {
            id: '2',
            amount: 250,
            destination: 'NG-BANK',
            route: 'RouteX Optimized (MNEE)',
            fee: 1.26,
            savings: 16.24,
            status: 'completed',
            date: '2026-01-05 14:30',
            txHash: '0x7bbcdaAd...1aED5bE'
        },
        {
            id: '3',
            amount: 1000,
            destination: 'BR-PIX',
            route: 'RouteX Optimized (MNEE)',
            fee: 5.01,
            savings: 64.99,
            status: 'completed',
            date: '2026-01-04 09:45',
            txHash: '0x6aabcb9c...0bcC4aD'
        }
    ]

    const totalSavings = transactions.reduce((sum, tx) => sum + tx.savings, 0)

    return (
        <div className="dashboard-container">
            <header>
                <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
                <p style={{ marginTop: '-0.5rem', opacity: 0.7 }}>Transaction History</p>
            </header>

            <div className="glass-card" style={{ maxWidth: '900px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                        <h2 style={{ margin: 0 }}>Your Activity</h2>
                        <p style={{ margin: '0.25rem 0 0 0', opacity: 0.7 }}>{transactions.length} transactions</p>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>Total Savings</div>
                        <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981' }}>
                            ${totalSavings.toFixed(2)}
                        </div>
                    </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                    {transactions.map(tx => (
                        <div
                            key={tx.id}
                            className="route-item"
                            style={{
                                marginBottom: '1rem',
                                display: 'grid',
                                gridTemplateColumns: '1fr 1fr 1fr auto',
                                gap: '1rem',
                                alignItems: 'center'
                            }}
                        >
                            <div>
                                <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>${tx.amount}</div>
                                <div style={{ fontSize: '0.85rem', opacity: 0.7 }}>{tx.destination}</div>
                            </div>

                            <div>
                                <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>{tx.route}</div>
                                <div style={{ fontSize: '0.85rem', opacity: 0.6, marginTop: '0.25rem' }}>
                                    {tx.date}
                                </div>
                            </div>

                            <div>
                                <div style={{ fontSize: '0.85rem', opacity: 0.7 }}>Fee: ${tx.fee.toFixed(2)}</div>
                                <div style={{ fontSize: '0.9rem', color: '#10b981', fontWeight: 600, marginTop: '0.25rem' }}>
                                    Saved ${tx.savings.toFixed(2)}
                                </div>
                            </div>

                            <div>
                                <div className="badge" style={{ background: '#10b981', color: '#064e3b' }}>
                                    {tx.status}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                    <Link to="/send">
                        <button className="primary-btn">
                            Send New Payment
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    )
}
