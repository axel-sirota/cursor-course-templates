# Phase 00 grader: every route in contract/openapi.yaml answers with the contract SHAPE.
# Mock data is fine. A finished app must also pass this file (it is the regression floor).
# Variables: base_url, run_id

# S-01 health: GET /health returns 200 and {"status":"ok"}
GET {{base_url}}/health
HTTP 200   # S-01 GET /health must return 200
[Asserts]
header "Content-Type" contains "application/json"   # S-01 responses are JSON
jsonpath "$.status" == "ok"   # S-01 body is {"status":"ok"}

# S-02 register: POST /api/auth/register returns 201 and a User
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "skel_{{run_id}}", "email": "skel_{{run_id}}@example.com", "password": "skeleton-pass-1"}
HTTP 201   # S-02 register must return 201 Created
[Asserts]
jsonpath "$.id" isString   # S-02 User.id is a string (even if the DB key is a number)
jsonpath "$.username" isString   # S-02 User.username is a string
jsonpath "$.email" isString   # S-02 User.email is a string
jsonpath "$.createdAt" isString   # S-02 User.createdAt is an RFC 3339 string

# S-03 login: POST /api/auth/login returns 200 and a TokenResponse
POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "skel_{{run_id}}", "password": "skeleton-pass-1"}
HTTP 200   # S-03 login must return 200
[Captures]
token: jsonpath "$.accessToken"
[Asserts]
jsonpath "$.accessToken" isString   # S-03 accessToken is a string
jsonpath "$.tokenType" == "Bearer"   # S-03 tokenType is exactly "Bearer"
jsonpath "$.expiresIn" isInteger   # S-03 expiresIn is an integer number of seconds
jsonpath "$.user.id" isString   # S-03 login embeds the User

# S-04 me: GET /api/auth/me returns 200 and a User
GET {{base_url}}/api/auth/me
Authorization: Bearer {{token}}
HTTP 200   # S-04 GET /api/auth/me must return 200 with a valid token
[Asserts]
jsonpath "$.id" isString   # S-04 me returns a User

# S-05 create post: POST /api/posts returns 201 and a Post
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Skeleton walk {{run_id}}", "content": "Checking the contract shape."}
HTTP 201   # S-05 create post must return 201 Created
[Captures]
post_id: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isString   # S-05 Post.id is a string
jsonpath "$.title" isString   # S-05 Post.title is a string
jsonpath "$.content" isString   # S-05 Post.content is a string
jsonpath "$.authorId" isString   # S-05 Post.authorId is a string
jsonpath "$.tags" isCollection   # S-05 Post.tags is always an array (may be empty before phase 04)
jsonpath "$.createdAt" isString   # S-05 Post.createdAt is a string

# S-06 list posts: GET /api/posts returns the pagination envelope
GET {{base_url}}/api/posts
HTTP 200   # S-06 list posts must return 200 without a token
[Asserts]
jsonpath "$.items" isCollection   # S-06 envelope has items[]
jsonpath "$.page" isInteger   # S-06 envelope has page
jsonpath "$.pageSize" isInteger   # S-06 envelope has pageSize
jsonpath "$.total" isInteger   # S-06 envelope has total
jsonpath "$.totalPages" isInteger   # S-06 envelope has totalPages

# S-07 get post: GET /api/posts/{id} returns 200 and a Post
GET {{base_url}}/api/posts/{{post_id}}
HTTP 200   # S-07 get post must return 200
[Asserts]
jsonpath "$.id" isString   # S-07 returns a Post

# S-08 update post: PUT /api/posts/{id} returns 200 and a Post
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Skeleton walk {{run_id}} (edited)", "content": "Still checking the shape."}
HTTP 200   # S-08 update post must return 200
[Asserts]
jsonpath "$.id" isString   # S-08 returns a Post

# S-09 add comment: POST /api/posts/{id}/comments returns 201 and a Comment
POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{token}}
Content-Type: application/json
{"content": "Skeleton comment"}
HTTP 201   # S-09 add comment must return 201 Created
[Captures]
comment_id: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isString   # S-09 Comment.id is a string
jsonpath "$.postId" isString   # S-09 Comment.postId is a string
jsonpath "$.content" isString   # S-09 Comment.content is a string

# S-10 list comments: GET /api/posts/{id}/comments returns the pagination envelope
GET {{base_url}}/api/posts/{{post_id}}/comments
HTTP 200   # S-10 list comments must return 200
[Asserts]
jsonpath "$.items" isCollection   # S-10 envelope has items[]
jsonpath "$.total" isInteger   # S-10 envelope has total

# S-11 delete comment: DELETE /api/comments/{id} returns 204
DELETE {{base_url}}/api/comments/{{comment_id}}
Authorization: Bearer {{token}}
HTTP 204   # S-11 delete comment must return 204 No Content

# S-12 list tags: GET /api/tags returns {"items":[TagSummary]}
GET {{base_url}}/api/tags
HTTP 200   # S-12 list tags must return 200
[Asserts]
jsonpath "$.items" isCollection   # S-12 body has items[]

# S-13 posts by tag: GET /api/tags/{tag}/posts returns the pagination envelope
GET {{base_url}}/api/tags/skeleton/posts
HTTP 200   # S-13 posts by tag must return 200 (empty list for an unknown tag)
[Asserts]
jsonpath "$.items" isCollection   # S-13 envelope has items[]
jsonpath "$.totalPages" isInteger   # S-13 envelope has totalPages

# S-14 delete post: DELETE /api/posts/{id} returns 204
DELETE {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{token}}
HTTP 204   # S-14 delete post must return 204 No Content
