import { ApiProperty } from '@nestjs/swagger';
import {
  IsEmail,
  IsNotEmpty,
  IsString,
  MinLength,
  MaxLength,
  IsOptional,
  IsIn,
} from 'class-validator';

export class CreateUserDto {
  @ApiProperty({
    description: 'Full display name of the user',
    example: 'Alice Smith',
  })
  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  name: string;

  @ApiProperty({
    description: 'Unique email address used for login',
    example: 'alice@example.com',
  })
  @IsEmail()
  @MaxLength(255)
  email: string;

  @ApiProperty({
    description: 'Password (minimum 8 characters)',
    example: 'secure1234',
  })
  @IsString()
  @MinLength(8)
  @MaxLength(72)           // bcrypt hard limit
  password: string;

  @ApiProperty({
    description: 'User role',
    example: 'user',
    enum: ['user', 'admin'],
    required: false,
  })
  @IsOptional()
  @IsString()
  @IsIn(['user', 'admin'])
  role?: string;
}
