# GAIAGPT 프로젝트 파일 구조

## 프로젝트 디렉토리 구조
```
gaiagpt-project/
├── backend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── nest-cli.json
│   └── src/
│       ├── main.ts
│       ├── app.module.ts
│       ├── chat/
│       │   ├── chat.module.ts
│       │   ├── chat.controller.ts
│       │   ├── chat.service.ts
│       │   ├── chat.gateway.ts
│       │   └── dto/
│       │       └── create-message.dto.ts
│       └── common/
│           └── interfaces/
│               └── message.interface.ts
│
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.tsx
        ├── App.css
        ├── index.tsx
        ├── index.css
        ├── types/
        │   └── index.ts
        ├── services/
        │   └── api.ts
        └── components/
            ├── Sidebar.tsx
            ├── Sidebar.css
            ├── ConversationList.tsx
            ├── ConversationList.css
            ├── ChatArea.tsx
            └── ChatArea.css
```

## 백엔드 파일들

### backend/package.json
```json
{
  "name": "gaiagpt-backend",
  "version": "1.0.0",
  "description": "GAIAGPT Chat Backend",
  "main": "dist/main.js",
  "scripts": {
    "prebuild": "rimraf dist",
    "build": "nest build",
    "format": "prettier --write \"src/**/*.ts\" \"test/**/*.ts\"",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:debug": "nest start --debug --watch",
    "start:prod": "node dist/main",
    "lint": "eslint \"{src,apps,libs,test}/**/*.ts\" --fix"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/platform-socket.io": "^10.0.0",
    "@nestjs/websockets": "^10.0.0",
    "class-transformer": "^0.5.1",
    "class-validator": "^0.14.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1",
    "socket.io": "^4.6.1",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/schematics": "^10.0.0",
    "@types/express": "^4.17.17",
    "@types/node": "^20.3.1",
    "@types/uuid": "^9.0.0",
    "@typescript-eslint/eslint-plugin": "^5.59.11",
    "@typescript-eslint/parser": "^5.59.11",
    "eslint": "^8.42.0",
    "prettier": "^2.8.8",
    "rimraf": "^5.0.1",
    "typescript": "^5.1.3"
  }
}
```

### backend/tsconfig.json
```json
{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "skipLibCheck": true,
    "strictNullChecks": false,
    "noImplicitAny": false,
    "strictBindCallApply": false,
    "forceConsistentCasingInFileNames": false,
    "noFallthroughCasesInSwitch": false
  }
}
```

### backend/nest-cli.json
```json
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "compilerOptions": {
    "deleteOutDir": true
  }
}
```

### backend/src/main.ts
```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.enableCors({
    origin: 'http://localhost:3000',
    credentials: true,
  });
  
  app.useGlobalPipes(new ValidationPipe());
  
  await app.listen(3055);
  console.log('Server is running on http://localhost:3055');
}
bootstrap();
```

### backend/src/app.module.ts
```typescript
import { Module } from '@nestjs/common';
import { ChatModule } from './chat/chat.module';

@Module({
  imports: [ChatModule],
})
export class AppModule {}
```

### backend/src/chat/chat.module.ts
```typescript
import { Module } from '@nestjs/common';
import { ChatController } from './chat.controller';
import { ChatService } from './chat.service';
import { ChatGateway } from './chat.gateway';

@Module({
  controllers: [ChatController],
  providers: [ChatService, ChatGateway],
})
export class ChatModule {}
```

### backend/src/common/interfaces/message.interface.ts
```typescript
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  conversationId: string;
  attachments?: string[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}
```

### backend/src/chat/dto/create-message.dto.ts
```typescript
import { IsString, IsNotEmpty, IsOptional, IsArray } from 'class-validator';

export class CreateMessageDto {
  @IsString()
  @IsNotEmpty()
  content: string;

  @IsString()
  @IsNotEmpty()
  conversationId: string;

  @IsArray()
  @IsOptional()
  attachments?: string[];
}
```

### backend/src/chat/chat.service.ts
```typescript
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
```

### backend/src/chat/chat.controller.ts
```typescript
import { Controller, Get, Post, Body, Param } from '@nestjs/common';
import { ChatService } from './chat.service';
import { CreateMessageDto } from './dto/create-message.dto';

@Controller('api/chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  @Post('messages')
  async createMessage(@Body() createMessageDto: CreateMessageDto) {
    return this.chatService.createMessage(createMessageDto);
  }

  @Get('conversations')
  getConversations() {
    return this.chatService.getConversations();
  }

  @Get('conversations/:id')
  getConversation(@Param('id') id: string) {
    return this.chatService.getConversation(id);
  }

  @Post('conversations')
  createConversation(@Body() body: { title: string }) {
    return this.chatService.createConversation(body.title);
  }
}
```

### backend/src/chat/chat.gateway.ts
```typescript
import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
  OnGatewayConnection,
  OnGatewayDisconnect,
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
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
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
}
```

## 프론트엔드 파일들

### frontend/package.json
```json
{
  "name": "gaiagpt-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@types/node": "^16.18.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "lucide-react": "^0.288.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "socket.io-client": "^4.6.1",
    "typescript": "^4.9.5"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@types/socket.io-client": "^3.0.0"
  }
}
```

### frontend/public/index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="GAIAGPT - Your AI Assistant"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <title>GAIAGPT</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

### frontend/src/index.tsx
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### frontend/src/index.css
```css
body {
  margin: 0;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI',
    'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
    'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

## 프로젝트 설정 및 실행 명령어

### 1. 프로젝트 초기화
```bash
# 루트 디렉토리 생성
mkdir gaiagpt-project
cd gaiagpt-project

# 백엔드 및 프론트엔드 디렉토리 생성
mkdir backend frontend
```

### 2. 백엔드 설정
```bash
cd backend

# Nest.js 프로젝트 초기화
npm init -y
npm install @nestjs/common @nestjs/core @nestjs/platform-express @nestjs/platform-socket.io @nestjs/websockets class-transformer class-validator reflect-metadata rxjs socket.io uuid
npm install -D @nestjs/cli @nestjs/schematics @types/express @types/node @types/uuid @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint prettier rimraf typescript

# 위의 파일들을 모두 생성한 후
npm run start:dev
```

### 3. 프론트엔드 설정
```bash
cd ../frontend

# React 프로젝트 초기화
npx create-react-app . --template typescript

# 추가 의존성 설치
npm install lucide-react socket.io-client
npm install -D @types/socket.io-client

# 위의 파일들을 모두 생성한 후
npm start
```

### 4. 동시 실행
```bash
# 터미널 1 (백엔드)
cd backend && npm run start:dev

# 터미널 2 (프론트엔드)
cd frontend && npm start
```

백엔드는 http://localhost:3055에서, 프론트엔드는 http://localhost:3000에서 실행됩니다.