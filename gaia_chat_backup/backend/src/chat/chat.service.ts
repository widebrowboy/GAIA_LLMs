import { Injectable } from '@nestjs/common';
import { Message, Conversation } from '../common/interfaces/message.interface';
import { CreateMessageDto } from './dto/create-message.dto';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class ChatService {
  private conversations: Map<string, Conversation> = new Map();
  
  constructor() {
    // Initialize with sample data
    this.initializeSampleData();
  }

  private initializeSampleData() {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const conversations = [
      {
        id: 'conv1',
        title: 'How to be a better person?',
        createdAt: today,
      },
      {
        id: 'conv2',
        title: 'Hacking FBI server with linux',
        createdAt: today,
      },
      {
        id: 'conv3',
        title: 'How to get rich from youtube as an influencer',
        createdAt: today,
      },
      {
        id: 'conv4',
        title: 'Help me with web development tasks from client',
        createdAt: yesterday,
      },
      {
        id: 'conv5',
        title: 'REACT NEXTJS Tutorial',
        createdAt: yesterday,
      },
    ];

    conversations.forEach(conv => {
      this.conversations.set(conv.id, {
        ...conv,
        messages: [],
        updatedAt: conv.createdAt,
      });
    });
  }

  async createMessage(createMessageDto: CreateMessageDto): Promise<Message> {
    const message: Message = {
      id: uuidv4(),
      role: 'user',
      content: createMessageDto.content,
      timestamp: new Date(),
      conversationId: createMessageDto.conversationId,
      attachments: createMessageDto.attachments,
    };

    const conversation = this.conversations.get(createMessageDto.conversationId);
    if (conversation) {
      conversation.messages.push(message);
      conversation.updatedAt = new Date();
      
      // Simulate AI response
      const aiResponse = await this.generateAIResponse(message);
      conversation.messages.push(aiResponse);
    }

    return message;
  }

  private async generateAIResponse(userMessage: Message): Promise<Message> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000));

    const responses = [
      "I understand your question. Let me help you with that...",
      "That's an interesting topic! Here's what I think...",
      "Based on my analysis, I can suggest the following...",
      "Let me break this down for you step by step...",
    ];

    return {
      id: uuidv4(),
      role: 'assistant',
      content: responses[Math.floor(Math.random() * responses.length)],
      timestamp: new Date(),
      conversationId: userMessage.conversationId,
    };
  }

  getConversations(): Conversation[] {
    return Array.from(this.conversations.values());
  }

  getConversation(id: string): Conversation | undefined {
    return this.conversations.get(id);
  }

  createConversation(title: string): Conversation {
    const conversation: Conversation = {
      id: uuidv4(),
      title,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    this.conversations.set(conversation.id, conversation);
    return conversation;
  }
}
