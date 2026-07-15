import { z } from 'zod';

export const RegisterRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  fullName: z.string().min(1),
});
export type RegisterRequest = z.infer<typeof RegisterRequestSchema>;

export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});
export type LoginRequest = z.infer<typeof LoginRequestSchema>;

export const AuthResponseSchema = z.object({
  message: z.string(),
  accessToken: z.string(),
  user: z.object({
    userId: z.string(),
    email: z.string(),
    fullName: z.string(),
  }),
});
export type AuthResponse = z.infer<typeof AuthResponseSchema>;
