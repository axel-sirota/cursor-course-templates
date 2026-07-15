import { Request, Response } from 'express';
import { RegisterRequestSchema, LoginRequestSchema } from '../schemas/auth.schema';
import { authService } from './deps';

export async function register(req: Request, res: Response): Promise<void> {
  const parsed = RegisterRequestSchema.parse(req.body);
  const { user, token } = await authService.register(parsed.email, parsed.password, parsed.fullName);
  res.status(201).json({
    message: 'Registration successful',
    accessToken: token,
    user: { userId: user.userId, email: user.email, fullName: user.fullName },
  });
}

export async function login(req: Request, res: Response): Promise<void> {
  const parsed = LoginRequestSchema.parse(req.body);
  const { user, token } = await authService.login(parsed.email, parsed.password);
  res.status(200).json({
    message: 'Login successful',
    accessToken: token,
    user: { userId: user.userId, email: user.email, fullName: user.fullName },
  });
}
