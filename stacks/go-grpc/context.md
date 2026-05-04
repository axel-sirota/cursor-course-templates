# Project Context: Go gRPC

## Tech Stack
- Language: Go 1.22+
- Transport: gRPC (google.golang.org/grpc v1.6x)
- Schema: Protocol Buffers v3 (google.golang.org/protobuf)
- Proto tooling: buf (preferred over raw protoc)
- Database: PostgreSQL (sqlx or pgx/v5)
- Testing: testing + testify + gomock (for interface mocks)
- Linting: golangci-lint

## Architecture Shape
gRPC Service — contract-first via .proto files. Binary transport. Not REST.
Use for: internal service-to-service communication, high-throughput APIs, streaming data.
Use REST (go-gin stack) for: external-facing APIs, browser clients, webhook receivers.

## Vibe & Style
- Coding Style: gofmt. Short idiomatic names.
- Architecture: proto first → generate → implement. Never write gRPC boilerplate by hand.
- Pattern: proto defines the contract; Go implements the server interface generated from proto.

## Key Rules
- Proto file is the source of truth. Never modify generated code.
- Use buf for proto linting and code generation (not raw protoc).
- Implement grpc_health_v1 health check on every service.
- Use interceptors (not middleware) for cross-cutting concerns (logging, auth, tracing).
- Always propagate context.Context as first argument.

## Active Phase
- Current: Phase 0 (Skeleton)
