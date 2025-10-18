import { useState, useEffect } from 'react';
import { Send, Wallet, TrendingUp, Clock } from 'lucide-react';
import CreditScore from './CreditScore';
import SendMoney from './SendMoney';

export default function Dashboard({ user, setUser }) {
  const [transactions, setTransactions] = useState([]);
  const [showSendMoney, setShowSendMoney] = useState(false);

  useEffect(() => {
    fetchTransactions();
    fetchProfile();
  }, []);

  const fetchTransactions = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/transactions', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setTransactions(data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:3001/api/profile', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setUser(data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleSendSuccess = () => {
    setShowSendMoney(false);
    fetchTransactions();
    fetchProfile();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user.name}</h1>
        <p className="text-gray-600">Wallet ID: {user.walletId}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Balance Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Wallet className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Balance</p>
              <p className="text-2xl font-bold text-gray-900">{user.balance?.toFixed(2)} EBT</p>
            </div>
          </div>
        </div>

        {/* Credit Score Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <CreditScore score={user.creditScore || 50} />
        </div>

        {/* Transactions Count */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-secondary-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Transactions</p>
              <p className="text-2xl font-bold text-gray-900">{transactions.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mb-8">
        <button
          onClick={() => setShowSendMoney(true)}
          className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 flex items-center space-x-2"
        >
          <Send size={20} />
          <span>Send Money</span>
        </button>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Transactions</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {transactions.length === 0 ? (
            <div className="px-6 py-4 text-gray-500 text-center">No transactions yet</div>
          ) : (
            transactions.slice(-10).reverse().map((tx) => (
              <div key={tx.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center">
                  <Clock className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {tx.from === user.walletId ? `To ${tx.to}` : `From ${tx.from}`}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(tx.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className={`text-sm font-medium ${
                  tx.from === user.walletId ? 'text-red-600' : 'text-green-600'
                }`}>
                  {tx.from === user.walletId ? '-' : '+'}{tx.amount.toFixed(2)} EBT
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showSendMoney && (
        <SendMoney
          onClose={() => setShowSendMoney(false)}
          onSuccess={handleSendSuccess}
        />
      )}
    </div>
  );
}
