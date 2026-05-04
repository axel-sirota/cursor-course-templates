import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException, ConflictException } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { User } from './entities/user.entity';

// ── Mock factory ─────────────────────────────────────────────────────────────

const mockUser = (): User =>
  ({
    id: 'uuid-1',
    name: 'Alice Smith',
    email: 'alice@example.com',
    passwordHash: '$2b$12$hashed',
    refreshToken: null,
    role: 'user',
    isActive: true,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
  } as User);

const mockUsersService = () => ({
  findAll: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  remove: jest.fn(),
});

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('UsersController', () => {
  let controller: UsersController;
  let usersService: jest.Mocked<ReturnType<typeof mockUsersService>>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [
        {
          provide: UsersService,
          useValue: mockUsersService(),
        },
      ],
    }).compile();

    controller = module.get<UsersController>(UsersController);
    usersService = module.get(UsersService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // ── findAll ────────────────────────────────────────────────────────────────

  describe('findAll', () => {
    it('should return an array of users', async () => {
      const users = [mockUser()];
      usersService.findAll.mockResolvedValue(users);

      const result = await controller.findAll();

      expect(result).toEqual(users);
      expect(usersService.findAll).toHaveBeenCalledTimes(1);
    });

    it('should return an empty array when no users exist', async () => {
      usersService.findAll.mockResolvedValue([]);

      const result = await controller.findAll();

      expect(result).toEqual([]);
    });
  });

  // ── findOne ────────────────────────────────────────────────────────────────

  describe('findOne', () => {
    it('should return a user when found', async () => {
      const user = mockUser();
      usersService.findOne.mockResolvedValue(user);

      const result = await controller.findOne('uuid-1');

      expect(result).toEqual(user);
      expect(usersService.findOne).toHaveBeenCalledWith('uuid-1');
    });

    it('should propagate NotFoundException when user does not exist', async () => {
      usersService.findOne.mockRejectedValue(
        new NotFoundException('User with id "uuid-missing" not found'),
      );

      await expect(controller.findOne('uuid-missing')).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  // ── create ─────────────────────────────────────────────────────────────────

  describe('create', () => {
    const dto: CreateUserDto = {
      name: 'Alice Smith',
      email: 'alice@example.com',
      password: 'secure1234',
    };

    it('should return the created user', async () => {
      const user = mockUser();
      usersService.create.mockResolvedValue(user);

      const result = await controller.create(dto);

      expect(result).toEqual(user);
      expect(usersService.create).toHaveBeenCalledWith(dto);
    });

    it('should propagate ConflictException when email already in use', async () => {
      usersService.create.mockRejectedValue(
        new ConflictException('Email "alice@example.com" is already in use'),
      );

      await expect(controller.create(dto)).rejects.toThrow(ConflictException);
    });
  });

  // ── remove ─────────────────────────────────────────────────────────────────

  describe('remove', () => {
    it('should call service.remove with the given id', async () => {
      usersService.remove.mockResolvedValue(undefined);

      await controller.remove('uuid-1');

      expect(usersService.remove).toHaveBeenCalledWith('uuid-1');
    });

    it('should propagate NotFoundException when user does not exist', async () => {
      usersService.remove.mockRejectedValue(
        new NotFoundException('User with id "uuid-missing" not found'),
      );

      await expect(controller.remove('uuid-missing')).rejects.toThrow(
        NotFoundException,
      );
    });
  });
});
