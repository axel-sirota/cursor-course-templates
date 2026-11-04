# Phase 03 grader: POST and GET /api/posts/{id}/comments
# Variables: base_url, run_id

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "ca_{{run_id}}", "email": "ca_{{run_id}}@example.com", "password": "correct-horse-8"}
HTTP 201   # A-01 setup: register the post author

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "ca_{{run_id}}", "password": "correct-horse-8"}
HTTP 200   # A-10 setup: log in the post author
[Captures]
author_token: jsonpath "$.accessToken"

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "cb_{{run_id}}", "email": "cb_{{run_id}}@example.com", "password": "correct-horse-9"}
HTTP 201   # A-01 setup: register a commenter
[Captures]
commenter_id: jsonpath "$.id"

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "cb_{{run_id}}", "password": "correct-horse-9"}
HTTP 200   # A-10 setup: log in the commenter
[Captures]
commenter_token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{author_token}}
Content-Type: application/json
{"title": "Comment target {{run_id}}", "content": "Talk to me"}
HTTP 201   # P-02 setup: create a post
[Captures]
post_id: jsonpath "$.id"

# C-01 commenting needs a token
POST {{base_url}}/api/posts/{{post_id}}/comments
Content-Type: application/json
{"content": "anonymous"}
HTTP 401   # C-01 POST comment without a token must return 401

# C-02 commenting on a missing post: 404
POST {{base_url}}/api/posts/00000000-0000-0000-0000-000000000000/comments
Authorization: Bearer {{commenter_token}}
Content-Type: application/json
{"content": "hello?"}
HTTP 404   # C-02 POST comment on an unknown post must return 404
[Asserts]
jsonpath "$.error.code" == "NOT_FOUND"   # C-02 error.code is NOT_FOUND

# C-03 validation: blank content
POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{commenter_token}}
Content-Type: application/json
{"content": "  "}
HTTP 422   # C-03 a whitespace-only comment must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "content"   # C-03 fields[] names content

# C-04 any logged-in user can comment; authorId comes from the token
POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{commenter_token}}
Content-Type: application/json
{"content": "First!", "authorId": "someone-else"}
HTTP 201   # C-04 POST comment with a token must return 201
[Captures]
c1: jsonpath "$.id"
[Asserts]
jsonpath "$.id" isString   # C-04 id is a string
jsonpath "$.postId" == "{{post_id}}"   # C-04 postId is the parent post
jsonpath "$.authorId" == "{{commenter_id}}"   # C-04 authorId is the token owner, body value ignored
jsonpath "$.authorUsername" == "cb_{{run_id}}"   # C-04 authorUsername is included
jsonpath "$.content" == "First!"   # C-04 content stored
jsonpath "$.createdAt" isString   # C-04 createdAt present

POST {{base_url}}/api/posts/{{post_id}}/comments
Authorization: Bearer {{author_token}}
Content-Type: application/json
[Options]
delay: 20
{"content": "Thanks for reading"}
HTTP 201   # C-04 the post author can comment too
[Captures]
c2: jsonpath "$.id"

# C-05 listing is public, oldest first, in the pagination envelope
GET {{base_url}}/api/posts/{{post_id}}/comments
HTTP 200   # C-05 GET comments is public
[Asserts]
jsonpath "$.total" == 2   # C-05 total is 2
jsonpath "$.items" count == 2   # C-05 both comments listed
jsonpath "$.items[0].id" == "{{c1}}"   # C-05 oldest comment first (reading order)
jsonpath "$.items[1].id" == "{{c2}}"   # C-05 newest comment last

GET {{base_url}}/api/posts/{{post_id}}/comments?pageSize=1&page=2
HTTP 200   # C-06 comments use the same page/pageSize rules as posts
[Asserts]
jsonpath "$.items" count == 1   # C-06 one item on page 2
jsonpath "$.items[0].id" == "{{c2}}"   # C-06 page 2 holds the second comment
jsonpath "$.totalPages" == 2   # C-06 totalPages = 2

# C-07 listing comments of a missing post: 404, not an empty list
GET {{base_url}}/api/posts/00000000-0000-0000-0000-000000000000/comments
HTTP 404   # C-07 GET comments of an unknown post must return 404
