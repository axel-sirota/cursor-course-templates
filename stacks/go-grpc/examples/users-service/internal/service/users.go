package service

import (
	"context"
	"errors"
	"sync"
	"time"

	"github.com/google/uuid"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"

	pb "github.com/example/users-service/gen/users/v1"
)

// Sentinel domain errors — mapped to gRPC status codes in toGRPCError.
var (
	ErrUserNotFound    = errors.New("user not found")
	ErrUserExists      = errors.New("user already exists")
	ErrInvalidArgument = errors.New("invalid argument")
)

// User is the internal domain type. Separate from the proto type.
type User struct {
	ID        string
	Name      string
	Email     string
	CreatedAt time.Time
}

// UserRepository is the data access interface. Implemented by postgres (prod) or in-memory (test).
type UserRepository interface {
	Create(ctx context.Context, u *User) error
	FindByID(ctx context.Context, id string) (*User, error)
	List(ctx context.Context, pageSize int, pageToken string) ([]*User, string, error)
}

// UserService implements pb.UserServiceServer.
type UserService struct {
	pb.UnimplementedUserServiceServer
	repo UserRepository
}

// NewUserService constructs a UserService with the given repository.
func NewUserService(repo UserRepository) *UserService {
	return &UserService{repo: repo}
}

// CreateUser creates a new user.
func (s *UserService) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	if req.Name == "" {
		return nil, status.Errorf(codes.InvalidArgument, "name is required")
	}
	if req.Email == "" {
		return nil, status.Errorf(codes.InvalidArgument, "email is required")
	}

	u := &User{
		ID:        uuid.NewString(),
		Name:      req.Name,
		Email:     req.Email,
		CreatedAt: time.Now().UTC(),
	}

	if err := s.repo.Create(ctx, u); err != nil {
		if ctx.Err() != nil {
			return nil, status.FromContextError(ctx.Err()).Err()
		}
		return nil, toGRPCError(err)
	}

	return &pb.CreateUserResponse{User: toProto(u)}, nil
}

// GetUser retrieves a user by ID.
func (s *UserService) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
	if req.Id == "" {
		return nil, status.Errorf(codes.InvalidArgument, "id is required")
	}

	u, err := s.repo.FindByID(ctx, req.Id)
	if err != nil {
		if ctx.Err() != nil {
			return nil, status.FromContextError(ctx.Err()).Err()
		}
		return nil, toGRPCError(err)
	}

	return &pb.GetUserResponse{User: toProto(u)}, nil
}

// ListUsers returns a paginated list of users.
func (s *UserService) ListUsers(ctx context.Context, req *pb.ListUsersRequest) (*pb.ListUsersResponse, error) {
	pageSize := int(req.PageSize)
	if pageSize <= 0 {
		pageSize = 20
	}
	if pageSize > 100 {
		pageSize = 100
	}

	users, nextToken, err := s.repo.List(ctx, pageSize, req.PageToken)
	if err != nil {
		if ctx.Err() != nil {
			return nil, status.FromContextError(ctx.Err()).Err()
		}
		return nil, toGRPCError(err)
	}

	protoUsers := make([]*pb.User, len(users))
	for i, u := range users {
		protoUsers[i] = toProto(u)
	}

	return &pb.ListUsersResponse{
		Users:         protoUsers,
		NextPageToken: nextToken,
	}, nil
}

// toProto converts a domain User to a proto User.
func toProto(u *User) *pb.User {
	return &pb.User{
		Id:        u.ID,
		Name:      u.Name,
		Email:     u.Email,
		CreatedAt: timestamppb.New(u.CreatedAt),
	}
}

// toGRPCError maps domain errors to gRPC status errors.
func toGRPCError(err error) error {
	switch {
	case errors.Is(err, ErrUserNotFound):
		return status.Errorf(codes.NotFound, "%v", err)
	case errors.Is(err, ErrUserExists):
		return status.Errorf(codes.AlreadyExists, "%v", err)
	case errors.Is(err, ErrInvalidArgument):
		return status.Errorf(codes.InvalidArgument, "%v", err)
	default:
		// Never expose internal error detail to callers.
		return status.Errorf(codes.Internal, "internal error")
	}
}

// InMemoryUserRepository is a simple in-memory repository for local development and unit tests.
type InMemoryUserRepository struct {
	mu    sync.RWMutex
	users map[string]*User
}

// NewInMemoryUserRepository creates an empty in-memory repository.
func NewInMemoryUserRepository() *InMemoryUserRepository {
	return &InMemoryUserRepository{users: make(map[string]*User)}
}

func (r *InMemoryUserRepository) Create(_ context.Context, u *User) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	for _, existing := range r.users {
		if existing.Email == u.Email {
			return ErrUserExists
		}
	}
	r.users[u.ID] = u
	return nil
}

func (r *InMemoryUserRepository) FindByID(_ context.Context, id string) (*User, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	u, ok := r.users[id]
	if !ok {
		return nil, ErrUserNotFound
	}
	return u, nil
}

func (r *InMemoryUserRepository) List(_ context.Context, pageSize int, _ string) ([]*User, string, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	result := make([]*User, 0, len(r.users))
	for _, u := range r.users {
		result = append(result, u)
		if len(result) >= pageSize {
			break
		}
	}
	return result, "", nil
}
