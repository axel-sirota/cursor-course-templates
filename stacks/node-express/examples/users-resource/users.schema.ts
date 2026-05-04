import { z } from 'zod';

export const CreateUserSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
});

export const UserParamsSchema = z.object({
  id: z.string().uuid('Invalid user ID format'),
});

export const ListUsersQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
});

export type CreateUserDto = z.infer<typeof CreateUserSchema>;
export type UserParams = z.infer<typeof UserParamsSchema>;
export type ListUsersQuery = z.infer<typeof ListUsersQuerySchema>;
