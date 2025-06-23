import {
  WebSocketGateway,
  SubscribeMessage,
  MessageBody,
  WebSocketServer,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { ChatService } from './chat.service';
import { CreateMessageDto } from './dto/create-message.dto';

@WebSocketGateway({
  cors: {
    origin: 'http://localhost:3000',
    credentials: true,
  },
})
export class ChatGateway {
  @WebSocketServer()
  server: Server;

  constructor(private readonly chatService: ChatService) {}

  handleConnection(client: Socket) {
    console.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: Socket) {
    console.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage('sendMessage')
  async handleMessage(
    @MessageBody() createMessageDto: CreateMessageDto,
    @ConnectedSocket() client: Socket,
  ) {
    const message = await this.chatService.createMessage(createMessageDto);
    
    // Emit to all clients in the conversation room
    this.server.to(createMessageDto.conversationId).emit('newMessage', message);
    
    // Get AI response after a delay
    setTimeout(async () => {
      const conversation = this.chatService.getConversation(createMessageDto.conversationId);
      if (conversation && conversation.messages.length > 0) {
        const aiResponse = conversation.messages[conversation.messages.length - 1];
        this.server.to(createMessageDto.conversationId).emit('newMessage', aiResponse);
      }
    }, 1500);
    
    return message;
  }

  @SubscribeMessage('joinConversation')
  handleJoinConversation(
    @MessageBody() conversationId: string,
    @ConnectedSocket() client: Socket,
  ) {
    client.join(conversationId);
    console.log(`Client ${client.id} joined conversation ${conversationId}`);
  }

  @SubscribeMessage('leaveConversation')
  handleLeaveConversation(
    @MessageBody() conversationId: string,
    @ConnectedSocket() client: Socket,
  ) {
    client.leave(conversationId);
    console.log(`Client ${client.id} left conversation ${conversationId}`);
  }

  @SubscribeMessage('typing')
  handleTyping(
    @MessageBody() data: { conversationId: string; isTyping: boolean },
    @ConnectedSocket() client: Socket,
  ) {
    client.to(data.conversationId).emit('userTyping', {
      userId: client.id,
      isTyping: data.isTyping,
    });
  }

  afterInit(server: Server) {
    console.log('웹소켓 서버 초기화');
  }
}
