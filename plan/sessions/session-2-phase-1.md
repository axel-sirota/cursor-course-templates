# Session 2: Phase 1 - Authentication

## Goal
Implement real user authentication with database persistence, password hashing, and JWT token generation.

## Prerequisites
- Phase 0 skeleton complete
- PostgreSQL running via Docker Compose
- Alembic migrations configured

## Implementation Tasks

### 1. Database Models
Create `app/models/user.py`:
- User table with SQLAlchemy 2.0 async
- Fields: id, username, email, password_hash, created_at
- Indexes on email and username

### 2. Database Migrations
- Initialize Alembic: `alembic init alembic`
- Create migration: `alembic revision -m "Create users table"`
- Run migration: `alembic upgrade head`

### 3. Password Security
- Install: `passlib[bcrypt]`
- Create password hashing utilities in `app/core/security.py`
- Hash passwords on registration
- Verify passwords on login

### 4. JWT Token Generation
- Install: `python-jose[cryptography]`
- Create JWT utilities in `app/core/security.py`
- Token payload: { sub: user_id, username, exp }
- Token expiry: 7 days

### 5. Repository Layer
Create `app/repositories/user_repository.py`:
- `create_user(username, email, password_hash)` → User
- `get_user_by_email(email)` → User | None
- `get_user_by_id(user_id)` → User | None

### 6. Service Layer
Create `app/services/auth_service.py`:
- `register_user(username, email, password)` → AuthResponse
- `login_user(email, password)` → AuthResponse
- `get_current_user(user_id)` → UserResponse

### 7. Update API Routes
Replace mock implementations in `app/api/auth.py`:
- POST /api/auth/register → Call auth_service.register_user
- POST /api/auth/login → Call auth_service.login_user
- GET /api/auth/me → Call auth_service.get_current_user

### 8. Real Auth Dependency
Update `app/core/dependencies.py`:
```python
async def require_auth(authorization: str = Header(None), db = Depends(get_db)):
    token = extract_token(authorization)
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    # Verify user exists in database
    return {"user_id": user_id, "username": payload.get("username")}
```

### 9. E2E Tests
Create `tests/api/test_auth_real.py`:
- Test user registration flow
- Test login with correct credentials
- Test login with wrong credentials
- Test accessing protected endpoint with token
- Test accessing protected endpoint without token

## Verification Steps
1. Register new user: POST /api/auth/register
2. Login with credentials: POST /api/auth/login
3. Extract token from response
4. Get user profile: GET /api/auth/me (with token)
5. Verify token expiry handling

## Completion Checklist
- [ ] User model created with proper fields
- [ ] Alembic migration applied successfully
- [ ] Password hashing working (bcrypt)
- [ ] JWT token generation working
- [ ] User registration endpoint working
- [ ] Login endpoint returning valid tokens
- [ ] Auth dependency verifying tokens
- [ ] E2E tests passing for auth flow
- [ ] Database persisting users correctly

## Next Session
Session 3 will implement Phase 2 (Posts CRUD) with real database operations.

## Session Duration
Estimated: 60-90 minutes
