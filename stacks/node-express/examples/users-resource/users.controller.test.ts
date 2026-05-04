import { Request, Response, NextFunction } from 'express';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { NotFoundError } from './users.service';

// Helper to create a typed partial mock of express Request
const mockReq = (overrides: Partial<Request> = {}): Request =>
  ({ body: {}, params: {}, query: {}, ...overrides } as unknown as Request);

const mockRes = (): Response => {
  const res = {} as Response;
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

const mockNext: NextFunction = jest.fn();

// Create a mock UsersService
const mockUsersService = {
  listUsers: jest.fn(),
  getUserById: jest.fn(),
  createUser: jest.fn(),
} as unknown as UsersService;

describe('UsersController', () => {
  let controller: UsersController;

  beforeEach(() => {
    jest.clearAllMocks();
    controller = new UsersController(mockUsersService);
  });

  describe('list', () => {
    it('should return an array of users with status 200', async () => {
      const users = [{ id: '1', name: 'Alice', email: 'alice@example.com' }];
      (mockUsersService.listUsers as jest.Mock).mockResolvedValue(users);

      const req = mockReq({ query: { page: 1, limit: 20 } as unknown as Request['query'] });
      const res = mockRes();

      await controller.list(req, res, mockNext);

      expect(mockUsersService.listUsers).toHaveBeenCalledWith({ page: 1, limit: 20 });
      expect(res.json).toHaveBeenCalledWith(users);
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('should call next with error when service throws', async () => {
      const error = new Error('DB error');
      (mockUsersService.listUsers as jest.Mock).mockRejectedValue(error);

      const req = mockReq({ query: {} as Request['query'] });
      const res = mockRes();

      await controller.list(req, res, mockNext);

      expect(mockNext).toHaveBeenCalledWith(error);
      expect(res.json).not.toHaveBeenCalled();
    });
  });

  describe('getById', () => {
    it('should return a user by id', async () => {
      const user = { id: 'abc-123', name: 'Bob', email: 'bob@example.com' };
      (mockUsersService.getUserById as jest.Mock).mockResolvedValue(user);

      const req = mockReq({ params: { id: 'abc-123' } as Request['params'] });
      const res = mockRes();

      await controller.getById(req, res, mockNext);

      expect(mockUsersService.getUserById).toHaveBeenCalledWith('abc-123');
      expect(res.json).toHaveBeenCalledWith(user);
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('should call next with NotFoundError when user does not exist', async () => {
      const error = new NotFoundError('User with id abc-123 not found');
      (mockUsersService.getUserById as jest.Mock).mockRejectedValue(error);

      const req = mockReq({ params: { id: 'abc-123' } as Request['params'] });
      const res = mockRes();

      await controller.getById(req, res, mockNext);

      expect(mockNext).toHaveBeenCalledWith(error);
      expect(res.json).not.toHaveBeenCalled();
    });
  });

  describe('create', () => {
    it('should create a user and return 201', async () => {
      const dto = { name: 'Carol', email: 'carol@example.com' };
      const created = { id: 'xyz-789', ...dto };
      (mockUsersService.createUser as jest.Mock).mockResolvedValue(created);

      const req = mockReq({ body: dto });
      const res = mockRes();

      await controller.create(req, res, mockNext);

      expect(mockUsersService.createUser).toHaveBeenCalledWith(dto);
      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith(created);
      expect(mockNext).not.toHaveBeenCalled();
    });

    it('should call next with error when service throws', async () => {
      const error = new Error('Conflict');
      (mockUsersService.createUser as jest.Mock).mockRejectedValue(error);

      const req = mockReq({ body: { name: 'Dave', email: 'dave@example.com' } });
      const res = mockRes();

      await controller.create(req, res, mockNext);

      expect(mockNext).toHaveBeenCalledWith(error);
      expect(res.json).not.toHaveBeenCalled();
    });
  });
});
