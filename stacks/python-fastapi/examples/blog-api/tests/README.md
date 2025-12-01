# Test Documentation

## Overview
This folder contains comprehensive E2E tests demonstrating the test-driven development approach used in the session-based workflow.

## Test Files

### `conftest.py`
- Pytest configuration and fixtures
- Sets up test database (SQLite in-memory)
- Provides `client` fixture for API testing
- Provides `db_session` fixture for database testing

### `test_api.py`
- Basic E2E tests for all endpoints
- Quick smoke tests
- Use these for quick validation

### `test_scenarios.py` ⭐ **MAIN TEACHING REFERENCE**
- Complete test scenarios with detailed documentation
- Each test includes:
  - **Scenario description**: What we're testing
  - **Input**: Exact request format with example data
  - **Expected Output**: Exact response format with status codes
- Organized by feature area:
  - `TestUserAuthenticationScenarios`
  - `TestBlogPostScenarios`
  - `TestCommentScenarios`
  - `TestCompleteUserFlow`

## Running Tests

### Run all tests
```bash
cd solutions/blog-api
source .venv/bin/activate
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_scenarios.py -v
```

### Run specific test class
```bash
pytest tests/test_scenarios.py::TestBlogPostScenarios -v
```

### Run specific test
```bash
pytest tests/test_scenarios.py::TestBlogPostScenarios::test_create_post_success -v
```

### Run with output
```bash
pytest tests/ -v -s
```

## Test Structure Best Practices

### 1. Arrange-Act-Assert Pattern
Every test follows this pattern:
```python
def test_example(client):
    # Arrange: Set up test data
    user = create_user(client)
    
    # Act: Perform the action
    response = client.post("/api/posts", json={...})
    
    # Assert: Verify the result
    assert response.status_code == 201
```

### 2. Clear Test Names
Test names describe the scenario:
- `test_create_post_success` - Happy path
- `test_create_post_empty_title` - Validation error
- `test_get_nonexistent_post` - Not found error

### 3. Documented Inputs/Outputs
Each test documents:
```python
"""
Scenario: What we're testing

Input:
    <exact request format>

Expected Output:
    <exact response format>
"""
```

### 4. Independent Tests
Each test:
- Sets up its own data
- Doesn't depend on other tests
- Can run in any order
- Cleans up after itself (handled by fixture)

## Teaching with These Tests

### Session 1: Show Students
1. **conftest.py** - How test fixtures work
2. **test_scenarios.py** - Pick 2-3 examples:
   - `test_register_new_user_success` (simple)
   - `test_create_post_success` (with setup)
   - `test_complete_blog_workflow` (full flow)

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
3. Write similar test for new feature
4. Run test and see it fail
5. Implement feature to make it pass

## Test Coverage

### User Authentication
- ✅ Register new user
- ✅ Duplicate username handling
- ✅ Login success
- ✅ Login with wrong password

### Blog Posts
- ✅ Create post
- ✅ Empty title validation
- ✅ Title length validation
- ✅ Get post by ID
- ✅ Get nonexistent post

### Comments
- ✅ Create comment
- ✅ Empty content validation
- ✅ Comment on nonexistent post
- ✅ List comments
- ✅ List empty comments

### Complete Flows
- ✅ Full user workflow
- ✅ Multiple users interaction

## Common Test Patterns

### Pattern 1: Simple Success Case
```python
def test_action_success(client):
    response = client.post("/endpoint", json={...})
    assert response.status_code == 201
    assert "id" in response.json()
```

### Pattern 2: Validation Error
```python
def test_action_validation_error(client):
    response = client.post("/endpoint", json={"invalid": "data"})
    assert response.status_code == 400
    assert "error message" in response.json()["detail"]
```

### Pattern 3: Not Found
```python
def test_get_nonexistent(client):
    response = client.get("/endpoint/fake-id")
    assert response.status_code == 404
```

### Pattern 4: With Setup
```python
def test_action_with_setup(client):
    # Setup
    user = create_user(client)
    post = create_post(client, user["userId"])
    
    # Action
    response = client.post(f"/posts/{post['postId']}/comments", ...)
    
    # Assert
    assert response.status_code == 201
```

## Debugging Failed Tests

### View detailed output
```bash
pytest tests/test_scenarios.py::test_name -v -s
```

### Use print statements
```python
def test_something(client):
    response = client.post(...)
    print(f"Response: {response.json()}")  # Will show with -s flag
    assert response.status_code == 200
```

### Check database state
Tests use SQLite in-memory, which is reset after each test.
Use the `db_session` fixture to inspect database directly.

## Next Steps
After understanding these tests:
1. Use them as templates for new features
2. Adapt patterns to your specific needs
3. Keep documentation updated
4. Add edge cases as you find them

