import { prisma } from '../config/prisma';
import { UserRepository } from '../repositories/user.repository';
import { PostRepository } from '../repositories/post.repository';
import { CommentRepository } from '../repositories/comment.repository';
import { AuthService } from '../services/auth.service';
import { PostService } from '../services/post.service';
import { CommentService } from '../services/comment.service';

/**
 * Manual dependency wiring. No DI container needed at this scale — one
 * module owns constructing the layered graph, everything else imports from here.
 */
const userRepo = new UserRepository(prisma);
const postRepo = new PostRepository(prisma);
const commentRepo = new CommentRepository(prisma);

export const authService = new AuthService(userRepo);
export const postService = new PostService(postRepo);
export const commentService = new CommentService(commentRepo, postRepo);
