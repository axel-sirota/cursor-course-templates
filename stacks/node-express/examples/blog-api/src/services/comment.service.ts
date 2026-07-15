import { CommentRepository } from '../repositories/comment.repository';
import { PostRepository } from '../repositories/post.repository';
import { Comment } from '../schemas/comment.schema';
import { NotFoundError } from '../errors';
import { logger } from '../config/logger';

export class CommentService {
  constructor(
    private readonly commentRepo: CommentRepository,
    private readonly postRepo: PostRepository
  ) {}

  /**
   * Create a comment on a post.
   * @throws {NotFoundError} If the parent post does not exist.
   */
  async createComment(postId: string, content: string, authorId: string): Promise<Comment> {
    const post = await this.postRepo.getById(postId);
    if (!post) {
      throw new NotFoundError('Post not found');
    }
    const comment = await this.commentRepo.create({ postId, content, authorId });
    logger.info({ commentId: comment.commentId, postId }, 'Comment created');
    return comment;
  }

  /**
   * List all comments for a post.
   * @throws {NotFoundError} If the parent post does not exist.
   */
  async listComments(postId: string): Promise<{ comments: Comment[]; totalCount: number }> {
    const post = await this.postRepo.getById(postId);
    if (!post) {
      throw new NotFoundError('Post not found');
    }
    return this.commentRepo.getByPostId(postId);
  }
}
