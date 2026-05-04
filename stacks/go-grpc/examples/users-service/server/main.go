package main

import (
	"context"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	"google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"

	pb "github.com/example/users-service/gen/users/v1"
	"github.com/example/users-service/internal/service"
)

func main() {
	addr := os.Getenv("GRPC_ADDR")
	if addr == "" {
		addr = ":50051"
	}

	lis, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatalf("failed to listen on %s: %v", addr, err)
	}

	// Build dependencies
	// In a real service, wire in a real repository (e.g. postgres):
	//   repo, err := repository.NewPostgres(os.Getenv("DB_URL"))
	repo := service.NewInMemoryUserRepository()
	userSvc := service.NewUserService(repo)

	// Create gRPC server with interceptors
	s := grpc.NewServer(
		grpc.ChainUnaryInterceptor(
			loggingInterceptor,
		),
	)

	// Register UserService
	pb.RegisterUserServiceServer(s, userSvc)

	// Health check (required for Kubernetes probes)
	healthSrv := health.NewServer()
	healthSrv.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
	healthSrv.SetServingStatus("users.v1.UserService", grpc_health_v1.HealthCheckResponse_SERVING)
	grpc_health_v1.RegisterHealthServer(s, healthSrv)

	// Server reflection — enabled only in non-production for grpcurl debugging
	if os.Getenv("GRPC_REFLECTION") == "true" {
		reflection.Register(s)
		log.Println("gRPC reflection enabled")
	}

	// Graceful shutdown on SIGINT / SIGTERM
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	go func() {
		log.Printf("gRPC server listening on %s", addr)
		if err := s.Serve(lis); err != nil {
			log.Fatalf("server exited with error: %v", err)
		}
	}()

	<-ctx.Done()
	log.Println("shutdown signal received — stopping gRPC server gracefully")
	s.GracefulStop()
	log.Println("server stopped")
}

// loggingInterceptor logs each unary RPC call with method and error (if any).
func loggingInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {
	resp, err := handler(ctx, req)
	if err != nil {
		log.Printf("RPC error: method=%s err=%v", info.FullMethod, err)
	} else {
		log.Printf("RPC ok: method=%s", info.FullMethod)
	}
	return resp, err
}
