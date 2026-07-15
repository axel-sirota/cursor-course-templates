/**
 * E2E API Smoke Tests
 * Basic happy-path coverage for every route. See tests/scenarios.test.ts
 * for detailed input/output documented scenarios per entity.
 */
import request from 'supertest';
import app from '../src/app';
import { createTestUser, buildPostPayload } from './setup';

describe('GET /health', () => {
  it('returns healthy status', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('healthy');
  });
});

describe('POST /api/auth/register', () => {
  it('registers a new user', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({ email: 'testuser@example.com', password: 'testpass123', fullName: 'Test User' });

    expect(response.status).toBe(201);
    expect(response.body.user).toHaveProperty('userId');
    expect(response.body.user.email).toBe('testuser@example.com');
  });
});

describe('POST /api/auth/login', () => {
  it('logs in a registered user', async () => {
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'loginuser@example.com', password: 'testpass123', fullName: 'Login User' });

    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'loginuser@example.com', password: 'testpass123' });

    expect(response.status).toBe(200);
    expect(response.body.user.email).toBe('loginuser@example.com');
  });
});

describe('POST /api/posts', () => {
  it('creates a blog post', async () => {
    const user = await createTestUser();

    const response = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload({ title: 'My First Post', content: 'This is the content of my first post.' }));

    expect(response.status).toBe(201);
    const data = response.body;
    expect(data).toHaveProperty('postId');
    expect(data.title).toBe('My First Post');
    expect(data.content).toBe('This is the content of my first post.');
    expect(data.authorId).toBe(user.userId);
    expect(data).toHaveProperty('createdAt');
  });
});

describe('GET /api/posts/:postId', () => {
  it('retrieves a blog post', async () => {
    const user = await createTestUser();
    const created = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload({ title: 'Test Post', content: 'Test content' }));
    const postId = created.body.postId;

    const response = await request(app).get(`/api/posts/${postId}`);

    expect(response.status).toBe(200);
    expect(response.body.postId).toBe(postId);
    expect(response.body.title).toBe('Test Post');
    expect(response.body.content).toBe('Test content');
  });
});

describe('POST /api/posts/:postId/comments', () => {
  it('creates a comment on a post', async () => {
    const user = await createTestUser();
    const post = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload({ title: 'Post with Comments', content: 'Content here' }));
    const postId = post.body.postId;

    const response = await request(app)
      .post(`/api/posts/${postId}/comments`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: 'Great post!' });

    expect(response.status).toBe(201);
    const data = response.body;
    expect(data).toHaveProperty('commentId');
    expect(data.postId).toBe(postId);
    expect(data.content).toBe('Great post!');
    expect(data.authorId).toBe(user.userId);
    expect(data).toHaveProperty('createdAt');
  });
});

describe('GET /api/posts/:postId/comments', () => {
  it('lists comments for a post in creation order', async () => {
    const user = await createTestUser();
    const post = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${user.token}`)
      .send(buildPostPayload({ title: 'Post with Multiple Comments', content: 'Content' }));
    const postId = post.body.postId;

    await request(app)
      .post(`/api/posts/${postId}/comments`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: 'First comment' });
    await request(app)
      .post(`/api/posts/${postId}/comments`)
      .set('Authorization', `Bearer ${user.token}`)
      .send({ content: 'Second comment' });

    const response = await request(app).get(`/api/posts/${postId}/comments`);

    expect(response.status).toBe(200);
    expect(response.body.comments).toHaveLength(2);
    expect(response.body.comments[0].content).toBe('First comment');
    expect(response.body.comments[1].content).toBe('Second comment');
  });
});
