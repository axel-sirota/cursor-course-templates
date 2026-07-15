import { z } from 'zod';

export const CommentBaseSchema = z.object({
  postId: z.string(),
  content: z.string().min(1).max(1000),
  authorId: z.string(),
});

export const CommentSchema = CommentBaseSchema.extend({
  commentId: z.string(),
  createdAt: z.string(),
});
export type Comment = z.infer<typeof CommentSchema>;

export const CreateCommentRequestSchema = z.object({
  content: z.string().min(1).max(1000),
});
export type CreateCommentRequest = z.infer<typeof CreateCommentRequestSchema>;

export const CommentResponseSchema = CommentSchema;
export type CommentResponse = z.infer<typeof CommentResponseSchema>;

export const CommentListResponseSchema = z.object({
  comments: z.array(CommentResponseSchema),
  totalCount: z.number(),
});
export type CommentListResponse = z.infer<typeof CommentListResponseSchema>;
