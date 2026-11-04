# Phase 02 grader: GET, PUT, DELETE /api/posts/{id} and author-only rules
# Variables: base_url, run_id
# Error precedence for PUT and DELETE: 401 (no or bad token) > 404 (no such post) > 403 (not the author) > 422 (bad body)

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "pa_{{run_id}}", "email": "pa_{{run_id}}@example.com", "password": "correct-horse-5"}
HTTP 201   # A-01 setup: register the author

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "pa_{{run_id}}", "password": "correct-horse-5"}
HTTP 200   # A-10 setup: log in the author
[Captures]
author_token: jsonpath "$.accessToken"

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "pb_{{run_id}}", "email": "pb_{{run_id}}@example.com", "password": "correct-horse-6"}
HTTP 201   # A-01 setup: register a second user

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "pb_{{run_id}}", "password": "correct-horse-6"}
HTTP 200   # A-10 setup: log in the second user
[Captures]
other_token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{author_token}}
Content-Type: application/json
{"title": "Original {{run_id}}", "content": "Original body"}
HTTP 201   # P-02 setup: create a post
[Captures]
post_id: jsonpath "$.id"

# P-10 unknown ids return 404 with the error envelope, whatever their format
GET {{base_url}}/api/posts/00000000-0000-0000-0000-000000000000
HTTP 404   # P-10 an unknown UUID-shaped id must return 404
[Asserts]
jsonpath "$.error.code" == "NOT_FOUND"   # P-10 error.code is NOT_FOUND

GET {{base_url}}/api/posts/not-a-real-id
HTTP 404   # P-10 a non-numeric, non-UUID id must return 404 (not 400, not 500)
[Asserts]
jsonpath "$.error.code" == "NOT_FOUND"   # P-10 error.code is NOT_FOUND

# P-11 PUT without a token: 401
PUT {{base_url}}/api/posts/{{post_id}}
Content-Type: application/json
{"title": "Hijack", "content": "nope"}
HTTP 401   # P-11 PUT without a token must return 401

# P-12 PUT by someone who is not the author: 403 FORBIDDEN
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{other_token}}
Content-Type: application/json
{"title": "Hijack", "content": "nope"}
HTTP 403   # P-12 only the author may update a post
[Asserts]
jsonpath "$.error.code" == "FORBIDDEN"   # P-12 error.code is FORBIDDEN

# P-13 precedence: a non-author with an invalid body still gets 403, not 422
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{other_token}}
Content-Type: application/json
{"title": ""}
HTTP 403   # P-13 ownership is checked before the body is validated

# P-14 PUT on a missing post: 404
PUT {{base_url}}/api/posts/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{author_token}}
Content-Type: application/json
{"title": "Ghost", "content": "Ghost"}
HTTP 404   # P-14 PUT on an unknown post must return 404

# P-15 PUT by the author with an invalid body: 422
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{author_token}}
Content-Type: application/json
{"title": "Only a title"}
HTTP 422   # P-15 PUT is a full replacement: content is required
[Asserts]
jsonpath "$.error.fields[*].field" contains "content"   # P-15 fields[] names content

# P-16 PUT by the author: 200 and the change is persisted
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{author_token}}
Content-Type: application/json
{"title": "Edited {{run_id}}", "content": "Edited body"}
HTTP 200   # P-16 the author can update the post
[Asserts]
jsonpath "$.title" == "Edited {{run_id}}"   # P-16 title updated
jsonpath "$.content" == "Edited body"   # P-16 content updated

GET {{base_url}}/api/posts/{{post_id}}
HTTP 200   # P-16 the edit is persisted
[Asserts]
jsonpath "$.title" == "Edited {{run_id}}"   # P-16 GET shows the new title

# P-17 DELETE by a non-author: 403, and the post survives
DELETE {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{other_token}}
HTTP 403   # P-17 only the author may delete a post

GET {{base_url}}/api/posts/{{post_id}}
HTTP 200   # P-17 the post still exists after a refused delete

# P-18 DELETE without a token: 401
DELETE {{base_url}}/api/posts/{{post_id}}
HTTP 401   # P-18 DELETE without a token must return 401

# P-19 DELETE by the author: 204, then the post is gone
DELETE {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{author_token}}
HTTP 204   # P-19 the author can delete the post (204, empty body)

GET {{base_url}}/api/posts/{{post_id}}
HTTP 404   # P-19 a deleted post returns 404

DELETE {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{author_token}}
HTTP 404   # P-19 deleting twice returns 404
