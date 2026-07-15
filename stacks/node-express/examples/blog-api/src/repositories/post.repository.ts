import { PrismaClient, Post as PrismaPost } from '@prisma/client';
import { Post } from '../schemas/post.schema';

export class PostRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async create(data: { title: string; content: string; authorId: string }): Promise<Post> {
    const row = await this.prisma.post.create({ data });
    return this.toModel(row);
  }

  async getById(postId: string): Promise<Post | null> {
    const row = await this.prisma.post.findUnique({ where: { id: postId } });
    return row ? this.toModel(row) : null;
  }

  async getAll(limit = 20, offset = 0): Promise<{ posts: Post[]; totalCount: number }> {
    const [rows, totalCount] = await Promise.all([
      this.prisma.post.findMany({
        take: limit,
        skip: offset,
        orderBy: { createdAt: 'desc' },
      }),
      this.prisma.post.count(),
    ]);
    return { posts: rows.map((row) => this.toModel(row)), totalCount };
  }

  async update(postId: string, data: { title?: string; content?: string }): Promise<Post> {
    const row = await this.prisma.post.update({ where: { id: postId }, data });
    return this.toModel(row);
  }

  async delete(postId: string): Promise<void> {
    await this.prisma.post.delete({ where: { id: postId } });
  }

  private toModel(row: PrismaPost): Post {
    return {
      postId: row.id,
      title: row.title,
      content: row.content,
      authorId: row.authorId,
      createdAt: row.createdAt.toISOString(),
      updatedAt: row.updatedAt.toISOString(),
    };
  }
}
