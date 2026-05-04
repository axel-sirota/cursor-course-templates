# gRPC Service Starter

This is the canonical scaffold for a new gRPC service using buf for code generation.

## Directory Layout

```
proto/
    {service}.proto          # service + message definitions (source of truth)
    buf.yaml                 # buf module config
    buf.gen.yaml             # generation config: go + grpc plugins
gen/
    {package}/v1/
        {service}.pb.go      # generated message types — never hand-edit
        {service}_grpc.pb.go # generated server/client interfaces — never hand-edit
internal/
    service/
        {service}.go         # implements generated {Service}Server interface
        {service}_test.go    # unit tests (no gRPC, direct method calls)
    repository/
        {service}.go         # repository interface
        postgres.go          # postgres implementation
    mocks/
        mock_{service}.go    # generated mocks (mockery)
cmd/server/
    main.go                  # wire deps, register services, start with graceful shutdown
buf.yaml                     # top-level buf config (if proto is a subdirectory)
buf.gen.yaml                 # generation config
go.mod
go.sum
```

## buf.yaml (module config)

```yaml
version: v1
modules:
  - path: proto
lint:
  use:
    - DEFAULT
breaking:
  use:
    - FILE
```

## buf.gen.yaml (code generation config)

```yaml
version: v1
plugins:
  - plugin: go
    out: gen
    opt: paths=source_relative
  - plugin: go-grpc
    out: gen
    opt: paths=source_relative,require_unimplemented_servers=false
```

## Setup Commands

```bash
# Install buf
brew install bufbuild/buf/buf

# Install Go protoc plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Lint proto
buf lint

# Generate Go code from proto
buf generate

# Check for breaking changes against main
buf breaking --against '.git#branch=main'
```

## Required Go Dependencies

```bash
go get google.golang.org/grpc@latest
go get google.golang.org/protobuf@latest
go get google.golang.org/grpc@latest  # health package is part of the main grpc module; import as "google.golang.org/grpc/health" and "google.golang.org/grpc/health/grpc_health_v1"
go get github.com/testify/assert@latest
go get github.com/testify/require@latest
go get go.uber.org/mock/gomock@latest
go get google.golang.org/grpc/test/bufconn@latest
```

## cmd/server/main.go Skeleton

```go
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

    pb "{module}/gen/{service}/v1"
    "{module}/internal/service"
)

func main() {
    addr := os.Getenv("GRPC_ADDR")
    if addr == "" {
        addr = ":50051"
    }

    lis, err := net.Listen("tcp", addr)
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }

    s := grpc.NewServer(
        grpc.ChainUnaryInterceptor(
        // add interceptors here: logging, auth, etc.
        ),
    )

    // Register business service
    svc := service.New{Service}Service( /* inject deps */ )
    pb.Register{Service}ServiceServer(s, svc)

    // Health check (required)
    healthSrv := health.NewServer()
    healthSrv.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
    grpc_health_v1.RegisterHealthServer(s, healthSrv)

    // Reflection (non-production only)
    if os.Getenv("GRPC_REFLECTION") == "true" {
        reflection.Register(s)
    }

    // Graceful shutdown
    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    go func() {
        log.Printf("gRPC server listening on %s", addr)
        if err := s.Serve(lis); err != nil {
            log.Fatalf("failed to serve: %v", err)
        }
    }()

    <-ctx.Done()
    log.Println("shutting down gRPC server...")
    s.GracefulStop()
}
```
