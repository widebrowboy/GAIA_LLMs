import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { Conversation } from './types/types';

function App() {
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const fetchConversations = async () => {
    try {
      const response = await fetch('http://localhost:3055/api/chat/conversations');
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    }
  };

  // Load conversations on component mount
  React.useEffect(() => {
    fetchConversations();
  }, []);

  const handleCreateConversation = async () => {
    try {
      const response = await fetch('http://localhost:3055/api/chat/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: 'New Conversation' }),
      });
      const newConversation = await response.json();
      setConversations([...conversations, newConversation]);
      setActiveConversation(newConversation);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  return (
    <div className="app">
      <Sidebar 
        conversations={conversations}
        activeConversation={activeConversation}
        onSelectConversation={setActiveConversation}
        onNewConversation={handleCreateConversation}
      />
      <ChatArea 
        conversation={activeConversation}
        onConversationUpdate={(updatedConversation) => {
          setConversations(conversations.map(conv => 
            conv.id === updatedConversation.id ? updatedConversation : conv
          ));
          setActiveConversation(updatedConversation);
        }}
      />
    </div>
  );
}

export default App;
