import React, { useState, useEffect, useRef } from 'react';
import { Conversation, Message } from '../types/types';
import MessageItem from './MessageItem';
import io, { Socket } from 'socket.io-client';

interface ChatAreaProps {
  conversation: Conversation | null;
  onConversationUpdate: (conversation: Conversation) => void;
}

const ChatArea: React.FC<ChatAreaProps> = ({ conversation, onConversationUpdate }) => {
  const [message, setMessage] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize socket connection
  useEffect(() => {
    const newSocket = io('http://localhost:3055', {
      withCredentials: true,
    });
    
    setSocket(newSocket);
    
    return () => {
      newSocket.disconnect();
    };
  }, []);

  // Join conversation room when conversation changes
  useEffect(() => {
    if (socket && conversation) {
      socket.emit('joinConversation', conversation.id);
      
      // Listen for new messages
      socket.on('newMessage', (newMessage: Message) => {
        if (newMessage.conversationId === conversation.id) {
          onConversationUpdate({
            ...conversation,
            messages: [...conversation.messages, newMessage],
          });
        }
      });
      
      // Listen for typing indicators
      socket.on('userTyping', (data: { userId: string; isTyping: boolean }) => {
        setIsTyping(data.isTyping);
      });
      
      return () => {
        socket.emit('leaveConversation', conversation.id);
        socket.off('newMessage');
        socket.off('userTyping');
      };
    }
  }, [socket, conversation]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages]);

  const handleSendMessage = async () => {
    if (!message.trim() || !conversation) return;
    
    try {
      const response = await fetch('http://localhost:3055/api/chat/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: message,
          conversationId: conversation.id,
        }),
      });
      
      if (response.ok) {
        setMessage('');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!conversation) {
    return (
      <div className="chat-area">
        <div className="no-conversation">
          <h3>대화를 선택하거나 새 대화를 시작하세요</h3>
          <p>왼쪽 사이드바에서 기존 대화를 선택하거나 "새 대화" 버튼을 클릭하여 시작하세요.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-area">
      <div className="chat-header">
        <h3 className="chat-title">{conversation.title}</h3>
      </div>
      
      <div className="message-list">
        {conversation.messages.map((msg) => (
          <MessageItem key={msg.id} message={msg} />
        ))}
        {isTyping && (
          <div className="message assistant">
            <div className="typing-indicator">입력 중...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="message-input-container">
        <textarea
          className="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="메시지를 입력하세요..."
          rows={1}
        />
        <button className="send-button" onClick={handleSendMessage}>
          전송
        </button>
      </div>
    </div>
  );
};

export default ChatArea;
