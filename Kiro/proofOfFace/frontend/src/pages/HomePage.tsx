import React from 'react';
import { Link } from 'react-router-dom';

export const HomePage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto text-center">
      <div className="mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Decentralized Identity Verification
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Prevent deepfake impersonation with blockchain-powered face verification
        </p>
        
        <div className="flex justify-center space-x-4">
          <Link 
            to="/register"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Register Identity
          </Link>
          <Link 
            to="/verify"
            className="bg-gray-200 text-gray-900 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-300 transition-colors"
          >
            Verify Identity
          </Link>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mb-12">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
            <span className="text-blue-600 text-xl">🔒</span>
          </div>
          <h3 className="text-lg font-semibold mb-2">Secure Registration</h3>
          <p className="text-gray-600">
            Upload your selfie to create an immutable identity record on Polkadot
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
            <span className="text-green-600 text-xl">✓</span>
          </div>
          <h3 className="text-lg font-semibold mb-2">AI Verification</h3>
          <p className="text-gray-600">
            Advanced face recognition prevents unauthorized impersonation
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
            <span className="text-purple-600 text-xl">⚖️</span>
          </div>
          <h3 className="text-lg font-semibold mb-2">Dispute Resolution</h3>
          <p className="text-gray-600">
            Community-driven system to handle verification disputes
          </p>
        </div>
      </div>

      <div className="bg-gray-100 rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-4">Built for Polkadot Cloud Hackathon</h2>
        <p className="text-gray-600 mb-4">
          ProofOfFace combines cutting-edge AI with blockchain technology to create 
          a trustless identity verification system that protects against deepfakes.
        </p>
        <div className="flex justify-center space-x-6 text-sm text-gray-500">
          <span>Polkadot/Substrate</span>
          <span>•</span>
          <span>Ink! Smart Contracts</span>
          <span>•</span>
          <span>IPFS Storage</span>
          <span>•</span>
          <span>AI Face Recognition</span>
        </div>
      </div>
    </div>
  );
};