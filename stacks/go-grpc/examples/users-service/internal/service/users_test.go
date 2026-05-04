package service_test

import (
	"context"
	"net"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/status"
	"google.golang.org/grpc/test/bufconn"

	pb "github.com/example/users-service/gen/users/v1"
	"github.com/example/users-service/internal/service"
)

// ---- Unit tests (no gRPC, direct method calls) ----

func TestUserService_CreateUser(t *testing.T) {
	tests := []struct {
		name    string
		req     *pb.CreateUserRequest
		wantErr codes.Code
	}{
		{
			name:    "success",
			req:     &pb.CreateUserRequest{Name: "Alice", Email: "alice@example.com"},
			wantErr: codes.OK,
		},
		{
			name:    "missing name",
			req:     &pb.CreateUserRequest{Name: "", Email: "alice@example.com"},
			wantErr: codes.InvalidArgument,
		},
		{
			name:    "missing email",
			req:     &pb.CreateUserRequest{Name: "Alice", Email: ""},
			wantErr: codes.InvalidArgument,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			repo := service.NewInMemoryUserRepository()
			svc := service.NewUserService(repo)

			resp, err := svc.CreateUser(context.Background(), tt.req)

			if tt.wantErr == codes.OK {
				require.NoError(t, err)
				require.NotNil(t, resp.User)
				assert.NotEmpty(t, resp.User.Id)
				assert.Equal(t, tt.req.Name, resp.User.Name)
				assert.Equal(t, tt.req.Email, resp.User.Email)
			} else {
				require.Error(t, err)
				st, ok := status.FromError(err)
				require.True(t, ok)
				assert.Equal(t, tt.wantErr, st.Code())
			}
		})
	}
}

func TestUserService_GetUser(t *testing.T) {
	repo := service.NewInMemoryUserRepository()
	svc := service.NewUserService(repo)

	// Seed a user
	createResp, err := svc.CreateUser(context.Background(), &pb.CreateUserRequest{
		Name:  "Bob",
		Email: "bob@example.com",
	})
	require.NoError(t, err)
	createdID := createResp.User.Id

	tests := []struct {
		name    string
		req     *pb.GetUserRequest
		wantErr codes.Code
	}{
		{
			name:    "found",
			req:     &pb.GetUserRequest{Id: createdID},
			wantErr: codes.OK,
		},
		{
			name:    "not found",
			req:     &pb.GetUserRequest{Id: "does-not-exist"},
			wantErr: codes.NotFound,
		},
		{
			name:    "empty id",
			req:     &pb.GetUserRequest{Id: ""},
			wantErr: codes.InvalidArgument,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			resp, err := svc.GetUser(context.Background(), tt.req)

			if tt.wantErr == codes.OK {
				require.NoError(t, err)
				assert.Equal(t, createdID, resp.User.Id)
				assert.Equal(t, "Bob", resp.User.Name)
			} else {
				require.Error(t, err)
				st, ok := status.FromError(err)
				require.True(t, ok)
				assert.Equal(t, tt.wantErr, st.Code())
			}
		})
	}
}

func TestUserService_ListUsers(t *testing.T) {
	repo := service.NewInMemoryUserRepository()
	svc := service.NewUserService(repo)

	// Seed users
	for i, name := range []string{"Alice", "Bob", "Carol"} {
		_, err := svc.CreateUser(context.Background(), &pb.CreateUserRequest{
			Name:  name,
			Email: name + "@example.com",
		})
		require.NoError(t, err, "seed user %d", i)
	}

	tests := []struct {
		name      string
		req       *pb.ListUsersRequest
		wantCount int
		wantErr   codes.Code
	}{
		{
			name:      "default page size",
			req:       &pb.ListUsersRequest{},
			wantCount: 3,
			wantErr:   codes.OK,
		},
		{
			name:      "page size 2",
			req:       &pb.ListUsersRequest{PageSize: 2},
			wantCount: 2,
			wantErr:   codes.OK,
		},
		{
			name:      "page size clamped to 100",
			req:       &pb.ListUsersRequest{PageSize: 9999},
			wantCount: 3,
			wantErr:   codes.OK,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			resp, err := svc.ListUsers(context.Background(), tt.req)

			if tt.wantErr == codes.OK {
				require.NoError(t, err)
				assert.Len(t, resp.Users, tt.wantCount)
			} else {
				require.Error(t, err)
				st, ok := status.FromError(err)
				require.True(t, ok)
				assert.Equal(t, tt.wantErr, st.Code())
			}
		})
	}
}

// ---- Integration tests using bufconn in-memory gRPC server ----
//
// These tests exercise the full gRPC stack (serialization, interceptors, etc.)
// without a real network. Build tag "integration" keeps them out of the default
// `go test ./...` run; they run with `go test -tags integration ./...`.
//
// Note: The generated pb package is not available in this example (would require
// running buf generate), so the bufconn tests are shown as runnable skeletons.

func newTestServer(t *testing.T) (pb.UserServiceClient, func()) {
	t.Helper()

	lis := bufconn.Listen(1024 * 1024)
	s := grpc.NewServer()
	repo := service.NewInMemoryUserRepository()
	pb.RegisterUserServiceServer(s, service.NewUserService(repo))

	go func() {
		if err := s.Serve(lis); err != nil && err != grpc.ErrServerStopped {
			t.Logf("bufconn server error: %v", err)
		}
	}()

	dialer := func(ctx context.Context, _ string) (net.Conn, error) {
		return lis.DialContext(ctx)
	}

	conn, err := grpc.DialContext(
		context.Background(),
		"bufnet",
		grpc.WithContextDialer(dialer),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	require.NoError(t, err)

	client := pb.NewUserServiceClient(conn)
	cleanup := func() {
		conn.Close()
		s.Stop()
	}

	return client, cleanup
}

func TestIntegration_CreateAndGetUser(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	client, cleanup := newTestServer(t)
	defer cleanup()

	// Create
	createResp, err := client.CreateUser(context.Background(), &pb.CreateUserRequest{
		Name:  "Dave",
		Email: "dave@example.com",
	})
	require.NoError(t, err)
	require.NotNil(t, createResp.User)
	userID := createResp.User.Id
	assert.NotEmpty(t, userID)

	// Get back
	getResp, err := client.GetUser(context.Background(), &pb.GetUserRequest{Id: userID})
	require.NoError(t, err)
	assert.Equal(t, "Dave", getResp.User.Name)
	assert.Equal(t, "dave@example.com", getResp.User.Email)
}

func TestIntegration_GetUser_NotFound(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test in short mode")
	}

	client, cleanup := newTestServer(t)
	defer cleanup()

	_, err := client.GetUser(context.Background(), &pb.GetUserRequest{Id: "no-such-id"})
	require.Error(t, err)

	st, ok := status.FromError(err)
	require.True(t, ok)
	assert.Equal(t, codes.NotFound, st.Code())
}
