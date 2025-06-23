import React from 'react';
import { Message } from '../types/types';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const formatTimestamp = (timestamp: Date) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">{message.content}</div>
      <div className="message-time">{formatTimestamp(message.timestamp)}</div>
      {message.attachments && message.attachments.length > 0 && (
        <div className="message-attachments">
          {message.attachments.map((attachment, index) => (
            <div key={index} className="attachment-item">
              {attachment}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessageItem;
