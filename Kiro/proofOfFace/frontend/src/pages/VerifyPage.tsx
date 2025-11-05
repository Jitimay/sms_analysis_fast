import React, { useState } from 'react';

export const VerifyPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [identityId, setIdentityId] = useState('');
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const handleVerify = async () => {
    if (!selectedFile || !identityId) return;
    
    setIsVerifying(true);
    // TODO: Implement verification logic
    setTimeout(() => {
      setVerificationResult({
        verified: true,
        confidence: 92.5,
        timestamp: new Date().toISOString()
      });
      setIsVerifying(false);
    }, 1500);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Verify Identity</h1>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Identity ID or Wallet Address
            </label>
            <input
              type="text"
              value={identityId}
              onChange={(e) => setIdentityId(e.target.value)}
              placeholder="Enter identity ID or wallet address"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Photo to Verify
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <button
            onClick={handleVerify}
            disabled={!selectedFile || !identityId || isVerifying}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-300"
          >
            {isVerifying ? 'Verifying...' : 'Verify Identity'}
          </button>

          {verificationResult && (
            <div className={`p-4 rounded-lg ${verificationResult.verified ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <h3 className={`font-semibold ${verificationResult.verified ? 'text-green-800' : 'text-red-800'}`}>
                {verificationResult.verified ? '✅ Verification Successful' : '❌ Verification Failed'}
              </h3>
              <p className={`text-sm ${verificationResult.verified ? 'text-green-600' : 'text-red-600'}`}>
                Confidence: {verificationResult.confidence}%
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};