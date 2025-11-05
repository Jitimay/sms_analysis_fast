import React from 'react';

export const DashboardPage: React.FC = () => {
  // Mock data for demonstration
  const mockData = {
    identity: {
      id: '0x1234...5678',
      registered: '2024-01-15',
      verified: true,
      reputation: 95
    },
    recentVerifications: [
      { id: 1, timestamp: '2024-01-20 14:30', result: 'Success', confidence: 94.2 },
      { id: 2, timestamp: '2024-01-19 09:15', result: 'Success', confidence: 91.8 },
      { id: 3, timestamp: '2024-01-18 16:45', result: 'Failed', confidence: 45.3 }
    ]
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Identity Dashboard</h1>
      
      {/* Identity Overview */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Your Identity</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{mockData.identity.id}</div>
            <div className="text-sm text-blue-600">Identity ID</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {mockData.identity.verified ? 'Verified' : 'Pending'}
            </div>
            <div className="text-sm text-green-600">Status</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{mockData.identity.reputation}</div>
            <div className="text-sm text-purple-600">Reputation Score</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-gray-600">{mockData.identity.registered}</div>
            <div className="text-sm text-gray-600">Registered</div>
          </div>
        </div>
      </div>

      {/* Recent Verifications */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Verifications</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Timestamp</th>
                <th className="text-left py-2">Result</th>
                <th className="text-left py-2">Confidence</th>
                <th className="text-left py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockData.recentVerifications.map((verification) => (
                <tr key={verification.id} className="border-b">
                  <td className="py-2">{verification.timestamp}</td>
                  <td className="py-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      verification.result === 'Success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {verification.result}
                    </span>
                  </td>
                  <td className="py-2">{verification.confidence}%</td>
                  <td className="py-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
            <div className="font-semibold">Update Identity</div>
            <div className="text-sm text-gray-600">Refresh your identity data</div>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
            <div className="font-semibold">Export Data</div>
            <div className="text-sm text-gray-600">Download your verification history</div>
          </button>
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
            <div className="font-semibold">Report Issue</div>
            <div className="text-sm text-gray-600">Flag suspicious activity</div>
          </button>
        </div>
      </div>
    </div>
  );
};