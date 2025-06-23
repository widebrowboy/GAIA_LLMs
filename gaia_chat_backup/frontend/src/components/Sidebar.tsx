import React from 'react';
import { Conversation } from '../types/types';

interface SidebarProps {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  onSelectConversation: (conversation: Conversation) => void;
  onNewConversation: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  conversations, 
  activeConversation, 
  onSelectConversation, 
  onNewConversation 
}) => {
  const formatDate = (dateString: Date) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', { 
      month: 'short', 
      day: 'numeric'
    });
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="app-title">GAIAGPT</h2>
      </div>
      
      <button className="new-chat-button" onClick={onNewConversation}>
        새 대화
      </button>
      
      <div className="conversation-list">
        {conversations.map(conversation => (
          <div
            key={conversation.id}
            className={`conversation-item ${activeConversation?.id === conversation.id ? 'active' : ''}`}
            onClick={() => onSelectConversation(conversation)}
          >
            <div className="conversation-title">{conversation.title}</div>
            <div className="conversation-date">
              {formatDate(conversation.createdAt)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
