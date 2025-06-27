// src/components/ClientProviders.tsx
'use client';

import React from 'react';
import { SimpleChatProvider } from '@/contexts/SimpleChatContext';

interface ClientProvidersProps {
  children: React.ReactNode;
}

const ClientProviders: React.FC<ClientProvidersProps> = ({ children }) => {
  return <SimpleChatProvider>{children}</SimpleChatProvider>;
};

export default ClientProviders;
