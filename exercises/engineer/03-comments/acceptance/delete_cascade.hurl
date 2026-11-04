# Phase 03 grader: DELETE /api/comments/{id} (author only) and cascade on post delete
# Variables: base_url, run_id

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "cd_{{run_id}}", "email": "cd_{{run_id}}@example.com", "password": "correct-horse-10"}
HTTP 201   # A-01 setup: register the post author

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "cd_{{run_id}}", "password": "correct-horse-10"}
HTTP 200   # A-10 setup: log in the post author
[Captures]
author_token: jsonpath "$.accessToken"

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "ce_{{run_id}}", "email": "ce_{{run_id}}@example.com", "password": "correct-horse-11"}
HTTP 201   # A-01 setup: register a commenter

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "ce_{{run_id}}", "password": "correct-horse-11"}
HTTP 200   # A-10 setup: log in the commenter
[Captures]
commenter_token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{author_token}}
Content-Type: application/json
{"title": "Delete target {{run_id}}", "content": "Comments come and go"}
HTTP 201   # P-02 setup: create a post
[Captures]
post_id: jsonpath "$.id"

POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{commenter_token}}
Content-Type: application/json
{"content": "Keep me"}
HTTP 201   # C-04 setup: comment 1
[Captures]
keep_id: jsonpath "$.id"

POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{commenter_token}}
Content-Type: application/json
{"content": "Delete me"}
HTTP 201   # C-04 setup: comment 2
[Captures]
drop_id: jsonpath "$.id"

# C-10 deleting needs a token
DELETE {{base_url}}/api/comments/{{drop_id}}
HTTP 401   # C-10 DELETE comment without a token must return 401

# C-11 only the comment author may delete it (the post author may not)
DELETE {{base_url}}/api/comments/{{drop_id}}
Authorization: Bearer {{author_token}}
HTTP 403   # C-11 a non-author (even the post author) gets 403
[Asserts]
jsonpath "$.error.code" == "FORBIDDEN"   # C-11 error.code is FORBIDDEN

# C-12 the comment author deletes: 204, list shrinks, second delete is 404
DELETE {{base_url}}/api/comments/{{drop_id}}
Authorization: Bearer {{commenter_token}}
HTTP 204   # C-12 the comment author can delete the comment

GET {{base_url}}/api/posts/{{post_id}}/comments
HTTP 200   # C-12 list after delete
[Asserts]
jsonpath "$.total" == 1   # C-12 one comment left
jsonpath "$.items[*].id" not contains "{{drop_id}}"   # C-12 the deleted comment is gone
jsonpath "$.items[0].id" == "{{keep_id}}"   # C-12 the other comment is untouched

DELETE {{base_url}}/api/comments/{{drop_id}}
Authorization: Bearer {{commenter_token}}
HTTP 404   # C-12 deleting a deleted comment returns 404

# C-13 unknown comment id: 404
DELETE {{base_url}}/api/comments/00000000-0000-0000-0000-000000000000
Authorization: Bearer {{commenter_token}}
HTTP 404   # C-13 DELETE on an unknown comment must return 404

# C-14 deleting the post removes its comments
DELETE {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{author_token}}
HTTP 204   # C-14 the post author deletes a post that has comments (no FK error, no 500)

GET {{base_url}}/api/posts/{{post_id}}/comments
HTTP 404   # C-14 comments of a deleted post: the post is gone, so 404

DELETE {{base_url}}/api/comments/{{keep_id}}
Authorization: Bearer {{commenter_token}}
HTTP 404   # C-14 the orphaned comment no longer exists (cascade delete)
