import React from 'react';
import { Link } from 'react-router-dom';

export const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">PF</span>
            </div>
            <span className="text-xl font-bold text-gray-900">ProofOfFace</span>
          </Link>
          
          <nav className="flex items-center space-x-6">
            <Link 
              to="/register" 
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Register
            </Link>
            <Link 
              to="/verify" 
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Verify
            </Link>
            <Link 
              to="/dashboard" 
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              Dashboard
            </Link>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Connect Wallet
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};