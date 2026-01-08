import { Link } from 'react-router-dom'

export default function LandingPage() {
    return (
        <div className="dashboard-container">
            <header style={{ marginBottom: '3rem' }}>
                <h1>Route<span style={{ color: '#6366f1' }}>X</span></h1>
                <p style={{ fontSize: '1.8rem', fontWeight: 600, marginTop: '1rem', opacity: 0.9 }}>
                    Money chooses the best path automatically
                </p>
                <p style={{ opacity: 0.7, marginTop: '0.5rem' }}>
                    AI-powered routing saves you 85% on cross-border payments
                </p>
            </header>

            <div className="glass-card" style={{ maxWidth: '800px' }}>
                <h2 style={{ marginBottom: '2rem' }}>How It Works</h2>

                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', margin: '2rem 0' }}>
                    <div className="flow-step">
                        <div className="flow-icon">💭</div>
                        <div className="flow-label">Your Intent</div>
                        <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>Send $100 to Kenya</p>
                    </div>

                    <div style={{ fontSize: '2rem', opacity: 0.5 }}>→</div>

                    <div className="flow-step">
                        <div className="flow-icon">🤖</div>
                        <div className="flow-label">AI Agent</div>
                        <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>Analyzes 12+ routes</p>
                    </div>

                    <div style={{ fontSize: '2rem', opacity: 0.5 }}>→</div>

                    <div className="flow-step">
                        <div className="flow-icon">⚡</div>
                        <div className="flow-label">Best Route</div>
                        <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>Cheapest & fastest</p>
                    </div>

                    <div style={{ fontSize: '2rem', opacity: 0.5 }}>→</div>

                    <div className="flow-step">
                        <div className="flow-icon">✅</div>
                        <div className="flow-label">Recipient</div>
                        <p style={{ fontSize: '0.85rem', opacity: 0.7 }}>Gets money instantly</p>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem', marginTop: '3rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    <Link to="/send">
                        <button className="primary-btn" style={{ fontSize: '1.1rem', padding: '1.25rem 3rem' }}>
                            Send a Payment
                        </button>
                    </Link>
                    <Link to="/send">
                        <button className="primary-btn" style={{ background: 'transparent', border: '2px solid #6366f1' }}>
                            View Demo Route
                        </button>
                    </Link>
                </div>
            </div>

            <div className="stats-grid" style={{ marginTop: '3rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', maxWidth: '800px', width: '100%' }}>
                <div className="stat-card">
                    <div className="stat-value">85%</div>
                    <div className="stat-label">Average Savings</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">3 sec</div>
                    <div className="stat-label">Average Speed</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">12+</div>
                    <div className="stat-label">Routes Analyzed</div>
                </div>
            </div>
        </div>
    )
}
