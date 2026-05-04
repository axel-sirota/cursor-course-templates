import { User } from '@prisma/client';
import { UsersRepository } from './users.repository';
import { CreateUserDto, ListUsersQuery } from './users.schema';

export class NotFoundError extends Error {
  readonly status = 404;

  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class ConflictError extends Error {
  readonly status = 409;

  constructor(message: string) {
    super(message);
    this.name = 'ConflictError';
  }
}

export class UsersService {
  constructor(private readonly usersRepository: UsersRepository) {}

  async listUsers(query: ListUsersQuery): Promise<User[]> {
    return this.usersRepository.findAll(query.page, query.limit);
  }

  async getUserById(id: string): Promise<User> {
    const user = await this.usersRepository.findById(id);
    if (!user) {
      throw new NotFoundError(`User with id ${id} not found`);
    }
    return user;
  }

  async createUser(data: CreateUserDto): Promise<User> {
    const existing = await this.usersRepository.findByEmail(data.email);
    if (existing) {
      throw new ConflictError(`A user with email ${data.email} already exists`);
    }
    return this.usersRepository.create(data);
  }
}
