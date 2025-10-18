import { Link } from 'react-router-dom';
import { LogOut, Home, Wallet, BarChart3, User } from 'lucide-react';

export default function Navbar({ user, onLogout }) {
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-primary-600">
              EconoBridge
            </Link>
          </div>
          
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex items-center space-x-1 text-gray-700 hover:text-primary-600">
              <Home size={20} />
              <span>Home</span>
            </Link>
            <Link to="/admin" className="flex items-center space-x-1 text-gray-700 hover:text-primary-600">
              <BarChart3 size={20} />
              <span>Analytics</span>
            </Link>
            <div className="flex items-center space-x-2 text-gray-700">
              <User size={20} />
              <span>{user.name}</span>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-1 text-gray-700 hover:text-red-600"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
