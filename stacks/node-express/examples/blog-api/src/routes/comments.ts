import { Router } from 'express';
import { createComment, listComments } from '../controllers/comments.controller';
import { requireAuth } from '../middleware/auth';
import { asyncHandler } from '../middleware/asyncHandler';

// mergeParams: true is required to read :postId from the parent router (src/routes/posts.ts)
const router = Router({ mergeParams: true });

router.post('', requireAuth, asyncHandler(createComment));
router.get('', asyncHandler(listComments));

export default router;
