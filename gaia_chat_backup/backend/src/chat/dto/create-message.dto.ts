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
