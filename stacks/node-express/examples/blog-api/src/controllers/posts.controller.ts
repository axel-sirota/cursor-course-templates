import { Request, Response } from 'express';
import { CreatePostRequestSchema, UpdatePostRequestSchema } from '../schemas/post.schema';
import { postService } from './deps';

/** POST /api/posts */
export async function createPost(req: Request, res: Response): Promise<void> {
  const parsed = CreatePostRequestSchema.parse(req.body);
  const post = await postService.createPost(parsed.title, parsed.content, req.user!.userId);
  res.status(201).json(post);
}

/** GET /api/posts */
export async function listPosts(req: Request, res: Response): Promise<void> {
  const limit = req.query.limit ? Number(req.query.limit) : 20;
  const offset = req.query.offset ? Number(req.query.offset) : 0;
  const result = await postService.listPosts(limit, offset);
  res.status(200).json(result);
}

/** GET /api/posts/:postId */
export async function getPost(req: Request, res: Response): Promise<void> {
  const post = await postService.getPostById(req.params.postId);
  res.status(200).json(post);
}

/** PUT /api/posts/:postId */
export async function updatePost(req: Request, res: Response): Promise<void> {
  const parsed = UpdatePostRequestSchema.parse(req.body);
  const post = await postService.updatePost(req.params.postId, req.user!.userId, parsed);
  res.status(200).json(post);
}

/** DELETE /api/posts/:postId */
export async function deletePost(req: Request, res: Response): Promise<void> {
  await postService.deletePost(req.params.postId, req.user!.userId);
  res.status(204).send();
}
