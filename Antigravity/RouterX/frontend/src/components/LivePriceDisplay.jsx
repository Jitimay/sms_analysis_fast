import { useState, useEffect } from 'react'

export default function LivePriceDisplay() {
    const [priceData, setPriceData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchLivePrice()
        const interval = setInterval(fetchLivePrice, 30000) // Update every 30 seconds
        return () => clearInterval(interval)
    }, [])

    const fetchLivePrice = async () => {
        try {
            const response = await fetch('http://localhost:8000/optimize-route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: 100,
                    currency: 'USD',
                    destination: 'KE-MPESA',
                    priority: 'cheapest'
                })
            })
            
            if (response.ok) {
                const data = await response.json()
                setPriceData(data.market_data)
            }
        } catch (error) {
            console.error('Failed to fetch live price:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading || !priceData) return null

    return (
        <div style={{
            position: 'fixed',
            bottom: '1.5rem',
            right: '1.5rem',
            background: 'rgba(10, 14, 39, 0.9)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '12px',
            padding: '1rem',
            fontSize: '0.85rem',
            zIndex: 1000
        }}>
            <div style={{ opacity: 0.7, marginBottom: '0.5rem' }}>Live Market Data</div>
            <div>MNEE: ${priceData.mnee_price_usd?.toFixed(3)}</div>
            <div>Celo Gas: {priceData.celo_gas_gwei?.toFixed(1)} Gwei</div>
        </div>
    )
}
