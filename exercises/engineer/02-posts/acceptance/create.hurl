# Phase 02 grader: POST /api/posts
# Variables: base_url, run_id

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "pc_{{run_id}}", "email": "pc_{{run_id}}@example.com", "password": "correct-horse-4"}
HTTP 201   # A-01 setup: register the author
[Captures]
author_id: jsonpath "$.id"

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "pc_{{run_id}}", "password": "correct-horse-4"}
HTTP 200   # A-10 setup: log in the author
[Captures]
token: jsonpath "$.accessToken"

# P-01 creating a post needs a token: 401 without one
POST {{base_url}}/api/posts
Content-Type: application/json
{"title": "No token", "content": "Should be refused"}
HTTP 401   # P-01 POST /api/posts without a token must return 401
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # P-01 error.code is UNAUTHORIZED

# P-02 create returns 201; authorId comes from the TOKEN, never from the body
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "First post {{run_id}}", "content": "Hello from the grader.", "authorId": "someone-else"}
HTTP 201   # P-02 create post with a valid token must return 201
[Captures]
post_id: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isString   # P-02 id is a string
jsonpath "$.title" == "First post {{run_id}}"   # P-02 title is stored
jsonpath "$.content" == "Hello from the grader."   # P-02 content is stored
jsonpath "$.authorId" == "{{author_id}}"   # P-03 authorId is the token owner; a client-sent authorId is ignored
jsonpath "$.authorUsername" == "pc_{{run_id}}"   # P-02 authorUsername is included
jsonpath "$.createdAt" isString   # P-02 createdAt is present
jsonpath "$.updatedAt" isString   # P-02 updatedAt is present

# P-04 the created post is readable by anyone
GET {{base_url}}/api/posts/{{post_id}}
HTTP 200   # P-04 GET /api/posts/{id} is public
[Asserts]
jsonpath "$.id" == "{{post_id}}"   # P-04 returns the same post
jsonpath "$.authorId" == "{{author_id}}"   # P-04 authorId persisted

# P-05 validation: missing title and content
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{}
HTTP 422   # P-05 empty body must return 422
[Asserts]
jsonpath "$.error.code" == "VALIDATION_FAILED"   # P-05 error.code is VALIDATION_FAILED
jsonpath "$.error.fields[*].field" contains "title"   # P-05 fields[] names title
jsonpath "$.error.fields[*].field" contains "content"   # P-05 fields[] names content

# P-06 validation: blank strings are not valid
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "   ", "content": "ok"}
HTTP 422   # P-06 a whitespace-only title must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "title"   # P-06 fields[] names title

# P-07 validation: title max 200 characters
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", "content": "ok"}
HTTP 422   # P-07 a 201-character title must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "title"   # P-07 fields[] names title

# P-08 validation: wrong JSON type
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": 42, "content": "ok"}
HTTP 422   # P-08 a number where a string is expected must return 422 (no silent coercion)
[Asserts]
jsonpath "$.error.fields[*].field" contains "title"   # P-08 fields[] names title
