import { PrismaClient, User as PrismaUser } from '@prisma/client';

export interface User {
  userId: string;
  email: string;
  fullName: string;
  passwordHash: string;
}

export class UserRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async create(data: { email: string; passwordHash: string; fullName: string }): Promise<User> {
    const row = await this.prisma.user.create({ data });
    return this.toModel(row);
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.prisma.user.findUnique({ where: { email } });
    return row ? this.toModel(row) : null;
  }

  async findById(userId: string): Promise<User | null> {
    const row = await this.prisma.user.findUnique({ where: { id: userId } });
    return row ? this.toModel(row) : null;
  }

  private toModel(row: PrismaUser): User {
    return {
      userId: row.id,
      email: row.email,
      fullName: row.fullName,
      passwordHash: row.passwordHash,
    };
  }
}
