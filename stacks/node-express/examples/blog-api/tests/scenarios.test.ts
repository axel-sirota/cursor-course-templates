/**
 * Test Scenarios with Expected Input/Output
 * Use these as examples when teaching students about E2E testing with Supertest.
 */
import request from 'supertest';
import app from '../src/app';
import { createTestUser, buildPostPayload } from './setup';

describe('User authentication scenarios', () => {
  it('registers a new user successfully', async () => {
    /**
     * Scenario: Register a new user successfully
     *
     * Input:
     *   POST /api/auth/register
     *   { "email": "johndoe@example.com", "password": "secure123", "fullName": "John Doe" }
     *
     * Expected Output:
     *   Status: 201
     *   {
     *     "message": "Registration successful",
     *     "accessToken": "<jwt>",
     *     "user": { "userId": "<uuid>", "email": "johndoe@example.com", "fullName": "John Doe" }
     *   }
     */
    const response = await request(app)
      .post('/api/auth/register')
      .send({ email: 'johndoe@example.com', password: 'secure123', fullName: 'John Doe' });

    expect(response.status).toBe(201);
    const data = response.body;
    expect(data.user).toHaveProperty('userId');
    expect(data.user.email).toBe('johndoe@example.com');
    expect(typeof data.accessToken).toBe('string');
  });

  it('rejects registering a duplicate email', async () => {
    /**
     * Scenario: Try to register with an already-registered email
     *
     * Input:
     *   First:  POST /api/auth/register { email: "dup@example.com", ... }
     *   Second: POST /api/auth/register { email: "dup@example.com", ... }
     *
     * Expected Output:
     *   First:  201 success
     *   Second: 409 error with detail mentioning the email is already registered
     */
    const payload = { email: 'dup@example.com', password: 'pass12345', fullName: 'Dup User' };

    const first = await request(app).post('/api/auth/register').send(payload);
    expect(first.status).toBe(201);

    const second = await request(app).post('/api/auth/register').send(payload);
    expect(second.status).toBe(409);
    expect(second.body.detail.toLowerCase()).toContain('already registered');
  });

  it('logs in with correct credentials', async () => {
    /**
     * Scenario: Login with correct credentials
     *
     * Input:
     *   Setup: Register user with email="alice@example.com", password="wonderland1"
     *   Then:  POST /api/auth/login { email: "alice@example.com", password: "wonderland1" }
     *
     * Expected Output:
     *   Status: 200
     *   { "message": "Login successful", "accessToken": "<jwt>", "user": { "userId": "<uuid>", ... } }
     */
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'alice@example.com', password: 'wonderland1', fullName: 'Alice' });

    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'alice@example.com', password: 'wonderland1' });

    expect(response.status).toBe(200);
    expect(response.body.message).toBe('Login successful');
  });

  it('rejects login with an incorrect password', async () => {
    /**
     * Scenario: Login with wrong password
     *
     * Expected Output:
     *   Status: 401
     *   { "detail": "Invalid credentials" }
     */
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'bob@example.com', password: 'correctpass1', fullName: 'Bob' });

    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'bob@example.com', password: 'wrongpass' });

    expect(response.status).toBe(401);
    expect(response.body.detail).toBe('Invalid credentials');
  });
});

describe('Blog post scenarios', () => {
  it('creates a post with all required fields', async () => {
    /**
     * Scenario: Create a post as an authenticated user
     *
     * Input:
     *   POST /api/posts (Authorization: Bearer <token>)
     *   { "title": "My First Post", "content": "This is the content of my first post." }
     *
     * Expected Output:
     *   Status: 201
     *   { "postId": "<uuid>", "title": "...", "content": "...", "authorId": "<uuid>", "createdAt": "<iso>", "updatedAt": "<iso>" }
     */
    const user = await createTestUser();

    const response = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload());

    expect(response.status).toBe(201);
    expect(response.body.authorId).toBe(user.userId);
    expect(response.body.createdAt).toBeDefined();
  });

  it('rejects a post with a title shorter than 3 characters', async () => {
    /**
     * Scenario: Business-rule validation in the service layer (not just Zod)
     *
     * Input: POST /api/posts { title: "Hi", content: "..." }
     * Expected Output: Status 400, detail mentions minimum title length
     */
    const user = await createTestUser();

    const response = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload({ title: 'Hi' }));

    expect(response.status).toBe(400);
    expect(response.body.detail.toLowerCase()).toContain('title');
  });

  it('rejects post creation without authentication', async () => {
    const response = await request(app).post('/api/posts').send(buildPostPayload());
    expect(response.status).toBe(401);
  });

  it('returns 404 for a nonexistent post', async () => {
    const response = await request(app).get('/api/posts/00000000-0000-0000-0000-000000000000');
    expect(response.status).toBe(404);
  });

  it('allows the author to update their own post', async () => {
    const user = await createTestUser();
    const created = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload());

    const response = await request(app)
      .put(`/api/posts/${created.body.postId}`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ title: 'Updated Title' });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated Title');
  });

  it('prevents a non-author from updating a post', async () => {
    const owner = await createTestUser();
    const intruder = await createTestUser();
    const created = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${owner.token}`)
      .send(buildPostPayload());

    const response = await request(app)
      .put(`/api/posts/${created.body.postId}`)
      .set('Authorization', `Bearer ${intruder.token}`)
      .send({ title: 'Hijacked Title' });

    expect(response.status).toBe(404); // not-found rather than 403: avoids leaking post existence to non-owners
  });

  it('lists posts with pagination metadata', async () => {
    const user = await createTestUser();
    for (let i = 0; i < 3; i += 1) {
      await request(app)
        .post('/api/posts')
        .set('Authorization', `Bearer ${user.token}`)
        .send(buildPostPayload({ title: `Post ${i}` }));
    }

    const response = await request(app).get('/api/posts?limit=2&offset=0');

    expect(response.status).toBe(200);
    expect(response.body.posts).toHaveLength(2);
    expect(response.body.totalCount).toBeGreaterThanOrEqual(3);
    expect(response.body.hasMore).toBe(true);
  });

  it('deletes a post owned by the caller', async () => {
    const user = await createTestUser();
    const created = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload());

    const del = await request(app)
      .delete(`/api/posts/${created.body.postId}`)
      .set('Authorization', `Bearer ${user.token}`);
    expect(del.status).toBe(204);

    const getAfter = await request(app).get(`/api/posts/${created.body.postId}`);
    expect(getAfter.status).toBe(404);
  });
});

describe('Comment scenarios', () => {
  it('rejects a comment on a post that does not exist', async () => {
    const user = await createTestUser();

    const response = await request(app)
      .post('/api/posts/00000000-0000-0000-0000-000000000000/comments')
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: 'Comment on nothing' });

    expect(response.status).toBe(404);
  });

  it('rejects an empty comment body', async () => {
    const user = await createTestUser();
    const post = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload());

    const response = await request(app)
      .post(`/api/posts/${post.body.postId}/comments`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: '' });

    expect(response.status).toBe(400);
  });

  it('requires authentication to comment', async () => {
    const user = await createTestUser();
    const post = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload());

    const response = await request(app)
      .post(`/api/posts/${post.body.postId}/comments`)
      .send({ content: 'Anonymous comment' });

    expect(response.status).toBe(401);
  });

  it('returns comments in chronological order with a total count', async () => {
    const user = await createTestUser();
    const post = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload());

    await request(app)
      .post(`/api/posts/${post.body.postId}/comments`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: 'First' });
    await request(app)
      .post(`/api/posts/${post.body.postId}/comments`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: 'Second' });

    const response = await request(app).get(`/api/posts/${post.body.postId}/comments`);

    expect(response.status).toBe(200);
    expect(response.body.totalCount).toBe(2);
    expect(response.body.comments.map((c: { content: string }) => c.content)).toEqual(['First', 'Second']);
  });
});
