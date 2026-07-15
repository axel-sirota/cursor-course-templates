import { PrismaClient, Comment as PrismaComment } from '@prisma/client';
import { Comment } from '../schemas/comment.schema';

export class CommentRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async create(data: { postId: string; content: string; authorId: string }): Promise<Comment> {
    const row = await this.prisma.comment.create({ data });
    return this.toModel(row);
  }

  async getByPostId(postId: string): Promise<{ comments: Comment[]; totalCount: number }> {
    const [rows, totalCount] = await Promise.all([
      this.prisma.comment.findMany({
        where: { postId },
        orderBy: { createdAt: 'asc' },
      }),
      this.prisma.comment.count({ where: { postId } }),
    ]);
    return { comments: rows.map((row) => this.toModel(row)), totalCount };
  }

  private toModel(row: PrismaComment): Comment {
    return {
      commentId: row.id,
      postId: row.postId,
      content: row.content,
      authorId: row.authorId,
      createdAt: row.createdAt.toISOString(),
    };
  }
}
