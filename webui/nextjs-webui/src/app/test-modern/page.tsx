'use client';

import { useState } from 'react';

export default function TestModernPage() {
  const [mounted, setMounted] = useState(false);

  useState(() => {
    setMounted(true);
  });

  if (!mounted) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Test Modern Page</h1>
      <p>This is a test page to check if the basic setup works.</p>
      <div className="mt-4 p-4 bg-blue-100 rounded-lg">
        <p>If you can see this with styling, Tailwind is working.</p>
      </div>
    </div>
  );
}