import { Request, Response, NextFunction } from 'express';
import { UsersService } from './users.service';
import { CreateUserDto, ListUsersQuery, UserParams } from './users.schema';

export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  async create(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const dto = req.body as CreateUserDto;
      const user = await this.usersService.createUser(dto);
      res.status(201).json(user);
    } catch (err) {
      next(err);
    }
  }

  async getById(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const { id } = req.params as unknown as UserParams;
      const user = await this.usersService.getUserById(id);
      res.json(user);
    } catch (err) {
      next(err);
    }
  }

  async list(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      const query = req.query as unknown as ListUsersQuery;
      const users = await this.usersService.listUsers(query);
      res.json(users);
    } catch (err) {
      next(err);
    }
  }
}
