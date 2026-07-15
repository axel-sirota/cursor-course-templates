import { Router } from 'express';
import { createPost, listPosts, getPost, updatePost, deletePost } from '../controllers/posts.controller';
import { requireAuth } from '../middleware/auth';
import { asyncHandler } from '../middleware/asyncHandler';
import commentsRouter from './comments';

const router = Router();

router.post('', requireAuth, asyncHandler(createPost));
router.get('', asyncHandler(listPosts));
router.get('/:postId', asyncHandler(getPost));
router.put('/:postId', requireAuth, asyncHandler(updatePost));
router.delete('/:postId', requireAuth, asyncHandler(deletePost));

// Nested resource: /api/posts/:postId/comments
router.use('/:postId/comments', commentsRouter);

export default router;
