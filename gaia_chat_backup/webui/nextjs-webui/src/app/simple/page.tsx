'use client';

import { useState, useEffect } from 'react';

export default function SimplePage() {
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      console.log('Simple page mounting...');
      setMounted(true);
      console.log('Simple page mounted successfully');
    } catch (err) {
      console.error('Error in Simple page:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, []);

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Error</h1>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (!mounted) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Simple Test Page</h1>
      <div className="space-y-4">
        <p>✅ Basic Next.js setup is working</p>
        <p>✅ React state management is working</p>
        <p>✅ Tailwind CSS is working</p>
        <p>Current time: {new Date().toLocaleString()}</p>
        
        <div className="mt-8 space-y-2">
          <h2 className="text-lg font-semibold">Test Links:</h2>
          <div className="space-x-4">
            <a href="/debug" className="text-blue-600 hover:underline">Debug Page</a>
            <a href="/test-modern" className="text-blue-600 hover:underline">Test Modern</a>
            <a href="/modern" className="text-blue-600 hover:underline">Modern Chat (Problematic)</a>
          </div>
        </div>
      </div>
    </div>
  );
}