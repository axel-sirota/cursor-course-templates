# Architecture Vibe: Go gRPC

## When gRPC over REST
Use gRPC when:
- **Internal service-to-service communication** — no browser, no external clients
- **High throughput** — binary protocol is 5–10x more efficient than JSON for large volumes
- **Strongly typed contracts shared across teams** — proto generates client/server stubs in multiple languages; the contract is the source of truth
- **Streaming** — gRPC natively supports server-streaming, client-streaming, and bidirectional streaming

Use REST (go-gin stack) when:
- **External/browser-facing APIs** — browsers speak HTTP/1.1 + JSON natively
- **Webhook receivers** — inbound HTTP POST from third-party services
- **Public APIs** — REST + OpenAPI is the industry standard for external consumption
- **Rapid prototyping** — no proto compilation step

## Proto as Contract
The `.proto` file is the API contract. Treat it like a public interface in a library — once published, breaking it breaks all consumers.

Field numbers are sacred: **never reuse a field number**, even after deleting a field. Reserve deleted numbers with `reserved`:

```proto
message User {
  reserved 3, 5;           // formerly "phone", "address" — never reuse
  reserved "phone";        // also reserve the name
  string id   = 1;
  string name = 2;
  string email = 4;
}
```

Backwards-compatible additions:
- Adding a new field (new number)
- Adding a new RPC method
- Adding a new message type

Backwards-incompatible (never do after v1):
- Removing a field or RPC
- Changing a field type
- Renaming a field (field numbers matter in binary, names matter in JSON/text format)

## buf vs protoc
buf handles proto linting, breaking change detection, and plugin management in a single config file. It is strictly better than raw protoc for application development.

Use buf. Only fall back to raw protoc if buf is unavailable (e.g., legacy CI that cannot install buf).

buf benefits:
- `buf lint` — catches proto style issues (missing go_package, reserved field gaps, etc.)
- `buf breaking` — detects backwards-incompatible changes automatically
- `buf generate` — manages plugin versions and output paths declaratively
- `buf dep` — manages proto dependencies (like googleapis/common-protos)

## Streaming Patterns
- **Unary** (request/response): the default. Use for almost everything.
- **Server-streaming**: client sends one request, server streams many responses. Use for: large result sets, live event feeds, progress updates.
- **Client-streaming**: client streams many requests, server responds once. Use for: bulk uploads, batch processing.
- **Bidirectional streaming**: both sides stream concurrently. Use for: real-time chat, collaborative editing, telemetry. Complex to implement correctly — only when genuinely needed.

## Go gRPC vs connect-go
**Standard gRPC** (`google.golang.org/grpc`): pure gRPC protocol. Best for service-to-service where all clients are Go (or other gRPC-native languages).

**connect-go** (from Buf, `connectrpc.com/connect`): supports gRPC, gRPC-Web, and Connect protocols from one handler. Advantages: works with browsers and curl without a proxy, simpler interceptor API. Consider when you need browser compatibility from a Go service without running a separate Envoy/grpc-gateway proxy.

## Service Mesh Compatibility
gRPC with HTTP/2 works seamlessly with service meshes (Istio, Linkerd). If deploying in a mesh, you get mTLS, observability, and load balancing without code changes. The health check proto (`grpc_health_v1`) is the standard probe for mesh sidecars.
