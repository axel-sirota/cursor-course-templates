# Test Documentation

## Overview
This folder contains comprehensive E2E tests demonstrating the test-driven development approach used in the session-based workflow, using Jest + Supertest against a real PostgreSQL database (truncated between tests).

## Test Files

### `setup.ts`
- Jest global setup (`setupFilesAfterEnv`)
- Provides a shared `prisma` client
- Provides `createTestUser()` / `getAuthHeaders()` helpers
- Truncates all tables in `beforeEach` for test isolation
- Disconnects Prisma in `afterAll`

### `routes.test.ts`
- Basic E2E smoke tests for every endpoint
- Quick validation that the whole request/response chain works
- Use these for fast sanity checks

### `scenarios.test.ts` ⭐ **MAIN TEACHING REFERENCE**
- Complete test scenarios with detailed documentation
- Each test includes an inline comment block with:
  - **Scenario description**: What we're testing
  - **Input**: Exact request format with example data
  - **Expected Output**: Exact response format with status codes
- Organized by feature area (`describe` blocks):
  - `User authentication scenarios`
  - `Blog post scenarios`
  - `Comment scenarios`

## Running Tests

### Run all tests
```bash
cd examples/blog-api
npm install
docker compose up -d
npm run prisma:migrate
npm test
```

### Run a specific test file
```bash
npx jest tests/scenarios.test.ts
```

### Run a specific describe block
```bash
npx jest tests/scenarios.test.ts -t "Blog post scenarios"
```

### Run a specific test
```bash
npx jest tests/scenarios.test.ts -t "creates a post with all required fields"
```

### Run with verbose output
```bash
npx jest --verbose
```

## Test Structure Best Practices

### 1. Arrange-Act-Assert Pattern
Every test follows this pattern:
```typescript
it('creates a post', async () => {
  // Arrange: set up test data
  const user = await createTestUser();

  // Act: perform the action
  const response = await request(app).post('/api/posts').set('Authorization', `Bearer ${user.token}`).send({ ... });

  // Assert: verify the result
  expect(response.status).toBe(201);
});
```

### 2. Clear Test Names
Test names describe the scenario:
- `creates a post with all required fields` - Happy path
- `rejects a post with a title shorter than 3 characters` - Validation error
- `returns 404 for a nonexistent post` - Not found error

### 3. Documented Inputs/Outputs
Each scenario test documents:
```typescript
/**
 * Scenario: What we're testing
 *
 * Input:
 *   <exact request format>
 *
 * Expected Output:
 *   <exact response format>
 */
```

### 4. Independent Tests
Each test:
- Sets up its own data (via `createTestUser()`)
- Doesn't depend on other tests
- Can run in any order
- Starts from a clean database (handled by `beforeEach` truncation in `setup.ts`)

## Teaching with These Tests

### Session 1: Show Students
1. **setup.ts** - How shared fixtures work in Jest
2. **scenarios.test.ts** - Pick 2-3 examples:
   - `registers a new user successfully` (simple)
   - `creates a post with all required fields` (with setup)
   - The full auth → post → comment chain across a few tests (full flow)

### Key Points to Emphasize
- Tests document API behavior
- Input/output examples are the contract
- Tests fail first, then drive implementation
- Each test is self-contained
- Descriptive names tell the story

### Student Exercise
Have students:
1. Read a test scenario
2. Understand input/output format
3. Write a similar test for a new feature
4. Run the test and see it fail
5. Implement the feature to make it pass

## Test Coverage

### User Authentication
- ✅ Register new user
- ✅ Duplicate email handling (409 Conflict)
- ✅ Login success
- ✅ Login with wrong password (401)

### Blog Posts
- ✅ Create post
- ✅ Title length validation (business rule, not just Zod)
- ✅ Get post by ID
- ✅ Get nonexistent post (404)
- ✅ Update post (author-only)
- ✅ Update post rejected for non-author
- ✅ List posts with pagination
- ✅ Delete post

### Comments
- ✅ Create comment
- ✅ Empty content validation
- ✅ Comment on nonexistent post (404)
- ✅ Comment requires authentication
- ✅ List comments in chronological order

## Common Test Patterns

### Pattern 1: Simple Success Case
```typescript
it('succeeds', async () => {
  const response = await request(app).post('/endpoint').send({ ... });
  expect(response.status).toBe(201);
  expect(response.body).toHaveProperty('id');
});
```

### Pattern 2: Validation Error
```typescript
it('rejects invalid input', async () => {
  const response = await request(app).post('/endpoint').send({ invalid: 'data' });
  expect(response.status).toBe(400);
  expect(response.body.detail).toContain('error message');
});
```

### Pattern 3: Not Found
```typescript
it('returns 404 for a nonexistent resource', async () => {
  const response = await request(app).get('/endpoint/fake-id');
  expect(response.status).toBe(404);
});
```

### Pattern 4: With Setup
```typescript
it('performs an action with setup', async () => {
  // Setup
  const user = await createTestUser();
  const post = await request(app).post('/api/posts').set('Authorization', `Bearer ${user.token}`).send({ ... });

  // Action
  const response = await request(app)
    .post(`/api/posts/${post.body.postId}/comments`)
    .set('Authorization', `Bearer ${user.token}`)
    .send({ ... });

  // Assert
  expect(response.status).toBe(201);
});
```

## Debugging Failed Tests

### View detailed output
```bash
npx jest tests/scenarios.test.ts -t "test name" --verbose
```

### Inspect a response body
```typescript
it('debugs a response', async () => {
  const response = await request(app).post(...);
  // eslint-disable-next-line no-console
  console.log('Response:', response.body);
  expect(response.status).toBe(200);
});
```

### Check database state
Tests use the real PostgreSQL instance from `docker-compose.yml`, truncated between tests. Use `npx prisma studio` (with `DATABASE_URL` pointed at the test database) to inspect rows directly while debugging.

## Next Steps
After understanding these tests:
1. Use them as templates for new features
2. Adapt patterns to your specific needs
3. Keep documentation updated
4. Add edge cases as you find them
