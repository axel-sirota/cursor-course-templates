# Blog API Tests

Black-box E2E tests exercising the full stack (Gin handler -> service -> GORM repository -> real
PostgreSQL) through the HTTP interface only, using `net/http/httptest`.

## Test Files

1. **helpers_test.go** — `TestMain` (sets `gin.TestMode`), `setupTestDB` (opens a transaction that
   always rolls back for isolation), `setupRouter` (wires a real router against the test DB)
2. **test_api_test.go** — straightforward smoke tests, one per endpoint, plus shared fixture helpers
   (`registerTestUser`, `createTestPost`)
3. **test_scenarios_test.go** — detailed scenarios with documented input/output in the doc comments,
   used for teaching E2E testing concepts (duplicate detection, partial updates, 404 handling,
   chronological ordering, etc.)

## Running the Tests

### Prerequisites
```bash
# Start PostgreSQL
docker compose up -d

# Create the test database (separate from the dev database)
docker compose exec postgres psql -U postgres -c "CREATE DATABASE blog_db_test;"
```

### Run All Tests
```bash
go test ./tests/... -v
```

### Run With Coverage
```bash
go test ./tests/... -cover
```

### Run a Single Test
```bash
go test ./tests/... -run TestCreatePostThenRetrieve -v
```

### Run With Race Detector
```bash
go test ./tests/... -race -v
```

## Test Isolation

Every test opens its own database transaction via `setupTestDB` and rolls it back in `t.Cleanup`.
This means:
- Tests never leave residue in the database
- Tests can run in any order, including in parallel (`go test -parallel`)
- No manual cleanup or `TRUNCATE` statements are needed between test runs

## Key Patterns Demonstrated

### 1. Black-Box HTTP Testing with httptest
```go
req := httptest.NewRequest(http.MethodPost, "/api/posts", bytes.NewBuffer(body))
req.Header.Set("Content-Type", "application/json")
w := httptest.NewRecorder()
router.ServeHTTP(w, req)
```
No real network socket is opened — `httptest.NewRecorder()` captures the response in memory, which is
both faster and more deterministic than spinning up a real server per test.

### 2. Transaction-Per-Test Isolation
```go
tx := db.Begin()
t.Cleanup(func() { tx.Rollback() })
```
Every repository in the router under test uses this same transaction, so all writes made during the
test are automatically undone afterward.

### 3. Fixture Helpers Reduce Duplication
`registerTestUser` and `createTestPost` are shared across both test files — each test that needs a
"some user exists" or "some post exists" precondition calls the helper instead of duplicating the
registration/creation boilerplate.

### 4. Doc-Comment Scenarios
Each scenario test's doc comment documents the exact input and expected output, making the test
readable as a specification, not just an assertion — useful both for teaching and as living
documentation of the API contract.

## Common Issues & Solutions

**"connect: connection refused"**
```bash
docker compose ps        # confirm postgres is running and healthy
docker compose logs postgres
```

**"database blog_db_test does not exist"**
```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE blog_db_test;"
```

**Tests hang or time out**
- Check for an unclosed transaction from a previous failed run holding a lock — restart the postgres
  container: `docker compose restart postgres`
