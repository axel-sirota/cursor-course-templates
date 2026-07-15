import { PostRepository } from '../repositories/post.repository';
import { Post } from '../schemas/post.schema';
import { NotFoundError, ValidationError } from '../errors';
import { logger } from '../config/logger';

export class PostService {
  constructor(private readonly postRepo: PostRepository) {}

  /**
   * Create a new blog post.
   * @throws {ValidationError} If the title is too short for a meaningful post.
   */
  async createPost(title: string, content: string, authorId: string): Promise<Post> {
    if (title.trim().length < 3) {
      throw new ValidationError('Title must be at least 3 characters');
    }
    try {
      const post = await this.postRepo.create({ title: title.trim(), content, authorId });
      logger.info({ postId: post.postId, authorId }, 'Post created');
      return post;
    } catch (error) {
      logger.error({ err: error }, 'Error creating post');
      throw error;
    }
  }

  /**
   * Get a post by ID.
   * @throws {NotFoundError} If the post does not exist.
   */
  async getPostById(postId: string): Promise<Post> {
    const post = await this.postRepo.getById(postId);
    if (!post) {
      throw new NotFoundError('Post not found');
    }
    return post;
  }

  /** List posts with pagination. */
  async listPosts(limit: number, offset: number): Promise<{ posts: Post[]; totalCount: number; hasMore: boolean }> {
    const { posts, totalCount } = await this.postRepo.getAll(limit, offset);
    return { posts, totalCount, hasMore: offset + posts.length < totalCount };
  }

  /**
   * Update a post. Only the author may update their own post.
   * @throws {NotFoundError} If the post does not exist.
   */
  async updatePost(
    postId: string,
    authorId: string,
    data: { title?: string; content?: string }
  ): Promise<Post> {
    const existing = await this.getPostById(postId);
    if (existing.authorId !== authorId) {
      throw new NotFoundError('Post not found');
    }
    return this.postRepo.update(postId, data);
  }

  /**
   * Delete a post. Only the author may delete their own post.
   * @throws {NotFoundError} If the post does not exist or belongs to another author.
   */
  async deletePost(postId: string, authorId: string): Promise<void> {
    const existing = await this.getPostById(postId);
    if (existing.authorId !== authorId) {
      throw new NotFoundError('Post not found');
    }
    await this.postRepo.delete(postId);
    logger.info({ postId }, 'Post deleted');
  }
}
