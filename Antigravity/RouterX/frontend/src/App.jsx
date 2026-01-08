import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { WalletProvider } from './contexts/WalletContext'
import WalletButton from './components/WalletButton'
import LandingPage from './pages/LandingPage'
import SendPaymentPage from './pages/SendPaymentPage'
import RouteComparisonPage from './pages/RouteComparisonPage'
import ExecutionPage from './pages/ExecutionPage'
import ConfirmationPage from './pages/ConfirmationPage'
import ActivityPage from './pages/ActivityPage'

function App() {
  return (
    <WalletProvider>
      <BrowserRouter>
        <WalletButton />
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
  )
}

export default App
