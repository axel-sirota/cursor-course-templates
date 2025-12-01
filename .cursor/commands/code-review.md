# Code Review Command

Perform comprehensive code review checking security standards, Python Google Style Guide compliance, and code complexity. This command identifies issues for manual review without modifying code.

## Prerequisites

Before starting code review, read:
- @.cursor/rules/000-core-workflow.mdc - Core workflow and style guidelines
- @.cursor/rules/500-implementation.mdc - Implementation patterns and code style
- @.cursor/rules/400-testing-first.mdc - Testing patterns and standards
- @vibe/vibe_fastapi_boilerplate.md - Project structure and security patterns
- @vibe/vibe_database.md - Database security patterns

## Review Scope

Review the following areas:
- Python files in app/ directory
- Test files in tests/ directory
- Configuration files (.env.example, docker-compose.yml)
- API endpoints and authentication
- Database operations and repositories

## Review Checklist

### 1. Security Standards Review

Following @.cursor/rules/000-core-workflow.mdc secrets management and security rules:

#### Secrets Management
Check the following locations for potential security issues:

**Configuration Files:**
- [ ] Check all `.py` files for hardcoded secrets (API keys, passwords, tokens)
- [ ] Verify `.env` files are in `.gitignore`
- [ ] Check `.env.example` exists with placeholder values
- [ ] Verify `docker-compose.yml` uses environment variables, not hardcoded secrets
- [ ] Check `app/core/config.py` for proper secret handling

**Search Patterns:**
```python
# Look for potential hardcoded secrets
grep -r "password\s*=\s*['\"]" app/
grep -r "api_key\s*=\s*['\"]" app/
grep -r "secret\s*=\s*['\"]" app/
grep -r "token\s*=\s*['\"]" app/
grep -r "API_KEY\s*=\s*['\"]" app/
```

**Logging Security:**
- [ ] Check all `logger.` calls to ensure no sensitive data is logged
- [ ] Verify password/token fields are not in log statements
- [ ] Check exception handlers don't expose secrets in error messages

**Search Patterns:**
```python
# Look for potential secret logging
grep -r "logger.*password" app/
grep -r "logger.*token" app/
grep -r "logger.*secret" app/
grep -r "logger.*api_key" app/
```

#### Authentication & Authorization
Check authentication implementation in API endpoints:

**JWT Token Security:**
- [ ] Check `app/core/security.py` for proper JWT secret handling
- [ ] Verify JWT tokens have expiration
- [ ] Check token validation in authentication dependencies
- [ ] Verify refresh token implementation if present

**Endpoint Protection:**
- [ ] Check all API endpoints in `app/api/` for proper authentication
- [ ] Verify sensitive endpoints use `Depends(require_auth)`
- [ ] Check authorization logic for resource ownership
- [ ] Verify admin-only endpoints have proper role checks

**Search Patterns:**
```python
# Look for unprotected endpoints
grep -r "@router\.(get|post|put|delete)" app/api/
# Then verify each has authentication dependency
```

#### SQL Injection Prevention
Following @vibe/vibe_database.md patterns:

- [ ] Check repository methods use parameterized queries
- [ ] Verify no raw SQL string concatenation
- [ ] Check SQLAlchemy models use proper column types
- [ ] Verify input validation on all database operations

**Search Patterns:**
```python
# Look for potential SQL injection
grep -r "execute.*f\"" app/
grep -r "execute.*%s" app/
grep -r "execute.*\+" app/
```

#### Input Validation
Check Pydantic models and validators:

- [ ] Verify all API request models have proper validation
- [ ] Check Field() constraints (min_length, max_length, regex)
- [ ] Verify custom validators for business rules
- [ ] Check file upload size limits if applicable

**Locations to Review:**
- `app/api/*/schemas.py` - API request/response models
- `app/modules/*/models/` - Domain models

#### CORS Configuration
- [ ] Check `app/main.py` for CORS middleware configuration
- [ ] Verify allowed origins are not set to `["*"]` in production
- [ ] Check allowed methods and headers are appropriate

#### Error Handling
- [ ] Verify error responses don't expose internal implementation details
- [ ] Check exception handlers return safe error messages
- [ ] Verify stack traces are not exposed to clients
- [ ] Check 500 errors return generic messages

---

### 2. Python Google Style Guide Compliance

Following @.cursor/rules/000-core-workflow.mdc and @.cursor/rules/500-implementation.mdc code style guidelines:

#### Type Hints
Check all Python files for proper type hints:

**Function Signatures:**
- [ ] All function parameters have type hints
- [ ] All function return types are annotated
- [ ] Async functions use proper return types (Coroutine, Awaitable)
- [ ] Complex types use proper typing imports (List, Dict, Optional, Union)

**Search Patterns:**
```python
# Look for functions without type hints
grep -r "^def \|^async def " app/ | grep -v " -> "
grep -r "^    def \|^    async def " app/ | grep -v " -> "
```

**Locations to Review:**
- `app/api/` - All endpoint functions
- `app/modules/*/services/` - All service methods
- `app/modules/*/repository/` - All repository methods
- `app/core/` - All utility functions

#### Docstrings
Following @.cursor/rules/500-implementation.mdc docstring patterns:

**Public Functions and Classes:**
- [ ] All public functions have Google-style docstrings
- [ ] Docstrings include: description, Args, Returns, Raises
- [ ] Class docstrings describe purpose and usage
- [ ] Module-level docstrings for public modules

**Example Expected Format:**
```python
def create_post(self, post_data: PostCreate) -> Post:
    """Create a new blog post.
    
    Args:
        post_data: Post creation data containing title, content, and author ID
        
    Returns:
        Created post with generated ID and timestamps
        
    Raises:
        ValueError: If post data is invalid
        DatabaseError: If database operation fails
    """
```

**Locations to Review:**
- `app/api/` - All endpoint functions
- `app/modules/*/services/` - All service classes and methods
- `app/modules/*/repository/` - All repository classes and methods

**Search Patterns:**
```python
# Look for functions without docstrings
# This requires manual review of function definitions
```

#### Naming Conventions
Following @.cursor/rules/500-implementation.mdc naming patterns:

**Variable and Function Names:**
- [ ] All variables use snake_case
- [ ] All functions use snake_case
- [ ] Names are descriptive (no single letters except iterators)
- [ ] No abbreviations (use `request` not `req`, `response` not `res`)

**Class Names:**
- [ ] All classes use PascalCase
- [ ] Service classes end with `Service`
- [ ] Repository classes end with `Repository`
- [ ] Model classes are singular nouns

**Constants:**
- [ ] All constants use UPPER_CASE_WITH_UNDERSCORES
- [ ] Constants are defined at module level
- [ ] Magic numbers are replaced with named constants

**Locations to Review:**
- All Python files in `app/` directory

#### Line Length and Formatting
- [ ] Lines are maximum 88 characters (Black formatter default)
- [ ] Code is formatted with Black
- [ ] Imports are organized (stdlib, third-party, local)
- [ ] No trailing whitespace

**Commands to Run:**
```bash
# Check if Black formatting is needed
.venv/bin/python3 -m black --check app/

# Check line length violations
grep -r ".\{89,\}" app/ --include="*.py"
```

#### Function Length and Complexity
Following @.cursor/rules/500-implementation.mdc function guidelines:

- [ ] Functions are maximum 50 lines
- [ ] Each function has single responsibility
- [ ] Complex logic is extracted to helper functions
- [ ] Deep nesting (>3 levels) is refactored

**Manual Review Required:**
Review each function in:
- `app/api/` - API endpoint handlers
- `app/modules/*/services/` - Service methods
- `app/modules/*/repository/` - Repository methods

---

### 3. Code Complexity and Improvement Suggestions

Check for unnecessary complexity and identify improvement opportunities:

#### Complex Logic Patterns

**Nested Conditionals:**
- [ ] Search for deeply nested if statements (>3 levels)
- [ ] Look for complex boolean expressions
- [ ] Check for duplicate conditional logic

**Search Locations:**
```python
# Manually review these files for nested conditionals
app/modules/*/services/*.py
app/api/*.py
```

**Improvement Strategy:**
- Extract conditions to named variables
- Use early returns to reduce nesting
- Consider strategy pattern for complex branching

#### Long Functions
- [ ] Identify functions longer than 50 lines
- [ ] Check for functions doing multiple things
- [ ] Look for repeated code blocks

**Manual Review:**
Review function length in all service and repository files.

**Improvement Strategy:**
- Extract helper methods
- Use composition over long procedures
- Consider splitting into multiple specialized classes

#### Duplicate Code
- [ ] Search for similar code patterns across files
- [ ] Check for copy-pasted logic
- [ ] Look for similar validation logic

**Common Duplicate Patterns:**
- Authentication checks
- Input validation
- Error handling
- Data transformation

**Improvement Strategy:**
- Extract to shared utilities in `app/core/`
- Create base classes for common patterns
- Use decorators for cross-cutting concerns

#### Database Query Optimization
Following @vibe/vibe_database.md patterns:

**N+1 Query Problems:**
- [ ] Check repository methods for loops with queries
- [ ] Look for `get_by_id` calls inside loops
- [ ] Verify relationships use proper loading strategies

**Locations to Review:**
```python
app/modules/*/repository/*.py
app/modules/*/services/*.py
```

**Improvement Strategy:**
- Use JOIN queries instead of multiple queries
- Implement batch loading
- Use eager loading for relationships

**Search Pattern:**
```python
# Look for potential N+1 queries
grep -r "for.*in.*:" app/modules/*/services/*.py
grep -r "await.*get_by_id" app/modules/*/services/*.py
```

#### Missing Pagination
- [ ] Check list endpoints return all records
- [ ] Verify large collections use pagination
- [ ] Check for limit/offset parameters

**Locations to Review:**
- All GET endpoints returning lists
- Repository methods returning collections

**Improvement Strategy:**
- Add limit/offset parameters
- Implement cursor-based pagination for large datasets
- Add total count to responses

#### Error Handling Improvements
- [ ] Check for bare `except:` clauses
- [ ] Look for swallowed exceptions
- [ ] Verify specific exception types are caught

**Search Patterns:**
```python
# Look for problematic error handling
grep -r "except:" app/ --include="*.py"
grep -r "except Exception:" app/ --include="*.py"
grep -r "pass$" app/ --include="*.py"
```

**Improvement Strategy:**
- Catch specific exception types
- Log exceptions before re-raising
- Add context to exception messages

#### Performance Anti-Patterns

**Synchronous Operations in Async Code:**
- [ ] Check for blocking I/O in async functions
- [ ] Look for synchronous database calls
- [ ] Verify file operations are async

**Improvement Strategy:**
- Use async libraries (aiofiles, httpx)
- Use `asyncio.to_thread()` for CPU-bound tasks
- Implement proper async/await patterns

**Missing Caching:**
- [ ] Check for repeated expensive calculations
- [ ] Look for frequently accessed static data
- [ ] Verify external API calls are cached

**Improvement Strategy:**
- Add caching with TTL for static data
- Use Redis for distributed caching
- Implement memoization for pure functions

---

## Web Search for Best Practices

For complex issues found during review, perform web searches to find modern solutions:

### When to Search

Perform web search when finding:
1. **Complex authentication patterns** - Search: "FastAPI JWT authentication best practices 2024"
2. **Performance bottlenecks** - Search: "FastAPI database query optimization patterns"
3. **Security vulnerabilities** - Search: "Python FastAPI security checklist 2024"
4. **Complex async patterns** - Search: "Python asyncio best practices error handling"
5. **Testing complex scenarios** - Search: "FastAPI testing async database operations"
6. **Modern Python patterns** - Search: "Python 3.11 type hints best practices"

### Search Strategy

For each complex issue:
1. Identify the specific problem or pattern
2. Formulate search query with: technology + problem + "best practices" + year
3. Review top 3-5 results
4. Document findings and recommendations
5. Provide specific code examples from research

---

## Review Output Format

For each issue found, provide:

### Issue Template

**Issue Type:** [Security | Style | Complexity]

**Severity:** [Critical | High | Medium | Low]

**Location:** `file/path.py:line_number` or `file/path.py:function_name`

**Current Code:**
```python
# Show problematic code snippet
```

**Issue Description:**
Clear explanation of what's wrong and why it matters.

**Recommendation:**
Specific fix or improvement with example.

**Reference:**
- Rule: @.cursor/rules/XXX-name.mdc
- Pattern: @vibe/vibe_xxx.md
- Documentation: [URL if web search performed]

---

## Review Execution Steps

1. **Read Prerequisites**
   - Load all rule files listed in Prerequisites section
   - Review current codebase structure

2. **Security Review**
   - Run grep patterns for secrets
   - Check authentication on all endpoints
   - Review database query patterns
   - Check CORS and error handling

3. **Style Review**
   - Check type hints on all functions
   - Verify docstrings on public APIs
   - Review naming conventions
   - Check line length and formatting

4. **Complexity Review**
   - Identify long or complex functions
   - Check for duplicate code
   - Review database query patterns
   - Look for performance anti-patterns

5. **Web Research**
   - For critical or complex issues, perform web search
   - Document modern best practices
   - Provide specific recommendations with examples

6. **Generate Report**
   - Group issues by severity
   - Provide specific file locations
   - Include actionable recommendations
   - Reference relevant rules and documentation

---

## Success Criteria

Review is complete when:
- [ ] All Python files in app/ reviewed for security
- [ ] All functions checked for type hints
- [ ] All public APIs checked for docstrings
- [ ] Complex functions identified
- [ ] Performance issues documented
- [ ] Web research performed for critical issues
- [ ] Comprehensive report generated
- [ ] Each issue includes specific location
- [ ] Each issue includes recommendation
- [ ] Each issue references relevant rules

---

## Anti-Patterns

Do NOT:
- Modify code automatically
- Skip web research for complex issues
- Provide generic recommendations
- Miss file location references
- Forget to check test files
- Skip configuration files
- Only report critical issues (report all severity levels)
- Provide recommendations without examples

