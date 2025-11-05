import React, { useState } from 'react';

export const RegisterPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleRegister = async () => {
    if (!selectedFile) return;
    
    setIsRegistering(true);
    // TODO: Implement registration logic
    setTimeout(() => {
      setIsRegistering(false);
      alert('Identity registered successfully!');
    }, 2000);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Register Your Identity</h1>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Your Selfie
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {preview ? (
                <div className="space-y-4">
                  <img 
                    src={preview} 
                    alt="Preview" 
                    className="mx-auto h-48 w-48 object-cover rounded-lg"
                  />
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setPreview(null);
                    }}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Change Photo
                  </button>
                </div>
              ) : (
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="photo-upload"
                  />
                  <label
                    htmlFor="photo-upload"
                    className="cursor-pointer inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Choose Photo
                  </label>
                  <p className="mt-2 text-sm text-gray-500">
                    PNG, JPG up to 10MB
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-medium text-yellow-800 mb-2">Important Guidelines:</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Use a clear, well-lit photo of your face</li>
              <li>• Look directly at the camera</li>
              <li>• Ensure your face is clearly visible</li>
              <li>• Avoid sunglasses or face coverings</li>
            </ul>
          </div>

          <button
            onClick={handleRegister}
            disabled={!selectedFile || isRegistering}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isRegistering ? 'Registering...' : 'Register Identity'}
          </button>
        </div>
      </div>
    </div>
  );
};