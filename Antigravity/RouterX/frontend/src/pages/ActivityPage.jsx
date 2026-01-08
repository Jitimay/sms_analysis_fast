import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useWallet } from '../contexts/WalletContext'

export default function ActivityPage() {
    const { account } = useWallet()
    const [transactions, setTransactions] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (account) {
            fetchTransactions()
        } else {
            setLoading(false)
            setError('Please connect your wallet to view transaction history')
        }
    }, [account])

    const fetchTransactions = async () => {
        try {
            const response = await fetch(`http://localhost:8000/transactions/${account}`)
            if (!response.ok) {
                throw new Error(`Failed to fetch transactions: ${response.status}`)
            }
            const data = await response.json()
            setTransactions(data.transactions || [])
        } catch (err) {
            console.error('Failed to fetch transactions:', err)
            setError(`Unable to load transaction history: ${err.message}`)
        } finally {
            setLoading(false)
        }
    }

    const totalSavings = transactions.reduce((sum, tx) => sum + (tx.savings || 0), 0)

    if (loading) {
        return (
            <div className="dashboard-container">
                <div className="glass-card">
                    <div className="loader"></div>
                    <h3>Loading transactions...</h3>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="dashboard-container">
                <div className="glass-card" style={{ maxWidth: '600px', borderColor: '#ef4444' }}>
                    <h2 style={{ color: '#ef4444' }}>Transaction History Unavailable</h2>
                    <p style={{ opacity: 0.8, marginBottom: '2rem' }}>{error}</p>
                    <Link to="/send">
                        <button className="primary-btn">Send New Payment</button>
                    </Link>
                </div>
            </div>
        )
    }

    if (transactions.length === 0) {
        return (
            <div className="dashboard-container">
                <header>
                    <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
                    <p style={{ marginTop: '-0.5rem', opacity: 0.7 }}>Transaction History</p>
                </header>
                <div className="glass-card" style={{ maxWidth: '600px' }}>
                    <h2>No Transactions Yet</h2>
                    <p style={{ opacity: 0.8, marginBottom: '2rem' }}>
                        Start using RouteX to see your transaction history and savings.
                    </p>
                    <Link to="/send">
                        <button className="primary-btn">Send Your First Payment</button>
                    </Link>
                </div>
            </div>
        )
    }

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
