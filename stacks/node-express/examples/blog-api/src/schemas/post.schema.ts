import { z } from 'zod';

// Base: business fields only
export const PostBaseSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1).max(10000),
  authorId: z.string(),
});

// Full: includes generated/database fields
export const PostSchema = PostBaseSchema.extend({
  postId: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Create request (authorId is derived from the authenticated user, not the body)
export const CreatePostRequestSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1).max(10000),
});
export type CreatePostRequest = z.infer<typeof CreatePostRequestSchema>;

// Update request: all fields optional
export const UpdatePostRequestSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  content: z.string().min(1).max(10000).optional(),
});
export type UpdatePostRequest = z.infer<typeof UpdatePostRequestSchema>;

export type Post = z.infer<typeof PostSchema>;

export const PostResponseSchema = PostSchema;
export type PostResponse = z.infer<typeof PostResponseSchema>;

export const PostListResponseSchema = z.object({
  posts: z.array(PostResponseSchema),
  totalCount: z.number(),
  hasMore: z.boolean(),
});
export type PostListResponse = z.infer<typeof PostListResponseSchema>;
