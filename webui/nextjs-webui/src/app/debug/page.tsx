'use client';

import { useState, useEffect } from 'react';

export default function DebugPage() {
  const [mounted, setMounted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      setMounted(true);
      console.log('Debug page mounted successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Debug page error:', err);
    }
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      <div className="space-y-4">
        <p>Mounted: {mounted ? 'Yes' : 'No'}</p>
        <p>Error: {error || 'None'}</p>
        <p>Current time: {new Date().toISOString()}</p>
        <div className="mt-4 p-4 bg-blue-100 rounded">
          <p>If you can see this, basic Next.js setup is working.</p>
        </div>
      </div>
    </div>
  );
}