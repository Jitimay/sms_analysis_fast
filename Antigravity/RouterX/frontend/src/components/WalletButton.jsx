import { useWallet } from '../contexts/WalletContext'

export default function WalletButton() {
    const { account, connecting, connectWallet, disconnectWallet } = useWallet()

    if (account) {
        return (
            <div style={{
                position: 'fixed',
                top: '1.5rem',
                right: '1.5rem',
                zIndex: 1000
            }}>
                <button
                    onClick={disconnectWallet}
                    className="wallet-btn"
                    style={{
                        background: 'rgba(10, 14, 39, 0.8)',
                        backdropFilter: 'blur(10px)',
                        border: '2px solid #10b981',
                        borderRadius: '12px',
                        padding: '0.75rem 1.25rem',
                        color: '#f8fafc',
                        cursor: 'pointer',
                        fontFamily: 'monospace',
                        fontSize: '0.9rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        transition: 'all 0.2s'
                    }}
                >
                    <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#10b981',
                        boxShadow: '0 0 8px #10b981'
                    }}></div>
                    {account.slice(0, 6)}...{account.slice(-4)}
                </button>
            </div>
        )
    }

    return (
        <div style={{
            position: 'fixed',
            top: '1.5rem',
            right: '1.5rem',
            zIndex: 1000
        }}>
            <button
                onClick={connectWallet}
                disabled={connecting}
                className="primary-btn"
                style={{
                    padding: '0.75rem 1.5rem',
                    fontSize: '0.9rem'
                }}
            >
                {connecting ? 'Connecting...' : '🦊 Connect Wallet'}
            </button>
        </div>
    )
}
