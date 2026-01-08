import { Component } from 'react'

class ErrorBoundary extends Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error }
    }

    componentDidCatch(error, errorInfo) {
        console.error('RouterX Error:', error, errorInfo)
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="dashboard-container">
                    <div className="glass-card" style={{ maxWidth: '600px', borderColor: '#ef4444' }}>
                        <h2 style={{ color: '#ef4444' }}>Something went wrong</h2>
                        <p style={{ opacity: 0.8, marginBottom: '2rem' }}>
                            RouterX encountered an error. Please refresh and try again.
                        </p>
                        <button 
                            className="primary-btn" 
                            onClick={() => window.location.reload()}
                        >
                            Refresh Page
                        </button>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
