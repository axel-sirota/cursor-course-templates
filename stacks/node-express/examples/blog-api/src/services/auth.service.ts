import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { UserRepository, User } from '../repositories/user.repository';
import { env } from '../config/env';
import { ConflictError, UnauthorizedError } from '../errors';
import { logger } from '../config/logger';

export class AuthService {
  constructor(private readonly userRepo: UserRepository) {}

  /**
   * Register a new user, hashing the password with bcrypt before storage.
   * @throws {ConflictError} If the email is already registered.
   */
  async register(email: string, password: string, fullName: string): Promise<{ user: User; token: string }> {
    const existing = await this.userRepo.findByEmail(email);
    if (existing) {
      throw new ConflictError('User already registered');
    }

    const passwordHash = await bcrypt.hash(password, 10);
    const user = await this.userRepo.create({ email, passwordHash, fullName });
    logger.info({ userId: user.userId }, 'User registered');

    return { user, token: this.issueToken(user) };
  }

  /**
   * Authenticate a user by email/password.
   * @throws {UnauthorizedError} If credentials are invalid.
   */
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    const user = await this.userRepo.findByEmail(email);
    if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
      throw new UnauthorizedError('Invalid credentials');
    }
    logger.info({ userId: user.userId }, 'User logged in');
    return { user, token: this.issueToken(user) };
  }

  private issueToken(user: User): string {
    return jwt.sign({ userId: user.userId, email: user.email }, env.JWT_SECRET, {
      expiresIn: env.JWT_EXPIRES_IN,
    });
  }
}
