import io, { Socket } from 'socket.io-client';
import { Message } from '../types/types';

interface SocketEvents {
  onNewMessage?: (message: Message) => void;
  onUserTyping?: (data: { userId: string; isTyping: boolean }) => void;
}

class SocketService {
  private socket: Socket | null = null;
  private events: SocketEvents = {};

  connect(): Promise<Socket> {
    return new Promise((resolve, reject) => {
      this.socket = io('http://localhost:3055', {
        withCredentials: true,
      });

      this.socket.on('connect', () => {
        console.log('Socket connected');
        resolve(this.socket as Socket);
      });

      this.socket.on('connect_error', (error: any) => {
        console.error('Socket connection error:', error);
        reject(error);
      });

      this.socket.on('newMessage', (message: Message) => {
        if (this.events.onNewMessage) {
          this.events.onNewMessage(message);
        }
      });

      this.socket.on('userTyping', (data: { userId: string; isTyping: boolean }) => {
        if (this.events.onUserTyping) {
          this.events.onUserTyping(data);
        }
      });
    });
  }

  joinConversation(conversationId: string): void {
    if (this.socket) {
      this.socket.emit('joinConversation', conversationId);
    }
  }

  leaveConversation(conversationId: string): void {
    if (this.socket) {
      this.socket.emit('leaveConversation', conversationId);
    }
  }

  sendMessage(message: { content: string; conversationId: string }): void {
    if (this.socket) {
      this.socket.emit('sendMessage', message);
    }
  }

  sendTypingStatus(data: { conversationId: string; isTyping: boolean }): void {
    if (this.socket) {
      this.socket.emit('typing', data);
    }
  }

  registerEvents(events: SocketEvents): void {
    this.events = { ...this.events, ...events };
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export default new SocketService();
