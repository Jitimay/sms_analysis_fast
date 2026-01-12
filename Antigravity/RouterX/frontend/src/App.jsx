import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { WalletProvider } from './contexts/WalletContext'
import ErrorBoundary from './components/ErrorBoundary'
import WalletButton from './components/WalletButton'
import LivePriceDisplay from './components/LivePriceDisplay'
import LandingPage from './pages/LandingPage'
import SendPaymentPage from './pages/SendPaymentPage'
import RouteComparisonPage from './pages/RouteComparisonPage'
import ExecutionPage from './pages/ExecutionPage'
import ConfirmationPage from './pages/ConfirmationPage'
import ActivityPage from './pages/ActivityPage'

function App() {
  return (
    <ErrorBoundary>
      <WalletProvider>
        <BrowserRouter>
          <WalletButton />
          <LivePriceDisplay />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/send" element={<SendPaymentPage />} />
            <Route path="/routes" element={<RouteComparisonPage />} />
            <Route path="/execute" element={<ExecutionPage />} />
            <Route path="/confirmation" element={<ConfirmationPage />} />
            <Route path="/activity" element={<ActivityPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </WalletProvider>
    </ErrorBoundary>
  )
}

export default App
