import { Request, Response } from 'express';
import { CreateCommentRequestSchema } from '../schemas/comment.schema';
import { commentService } from './deps';

/** POST /api/posts/:postId/comments */
export async function createComment(req: Request, res: Response): Promise<void> {
  const parsed = CreateCommentRequestSchema.parse(req.body);
  const comment = await commentService.createComment(req.params.postId, parsed.content, req.user!.userId);
  res.status(201).json(comment);
}

/** GET /api/posts/:postId/comments */
export async function listComments(req: Request, res: Response): Promise<void> {
  const result = await commentService.listComments(req.params.postId);
  res.status(200).json(result);
}
