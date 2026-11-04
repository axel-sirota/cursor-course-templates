# Phase 04 grader: GET /api/tags and GET /api/tags/{tag}/posts
# Variables: base_url, run_id (lowercase letters and digits)

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "tq_{{run_id}}", "email": "tq_{{run_id}}@example.com", "password": "correct-horse-13"}
HTTP 201   # A-01 setup: register the author

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "tq_{{run_id}}", "password": "correct-horse-13"}
HTTP 200   # A-10 setup: log in
[Captures]
token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Shared tag one", "content": "x", "tags": ["shared-{{run_id}}", "solo-{{run_id}}"]}
HTTP 201   # T-10 setup: post with two tags
[Captures]
p1: jsonpath "$.id"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
[Options]
delay: 20
{"title": "Shared tag two", "content": "x", "tags": ["shared-{{run_id}}"]}
HTTP 201   # T-10 setup: second post with the shared tag
[Captures]
p2: jsonpath "$.id"

# T-10 GET /api/tags lists each tag once with its post count, sorted by name
GET {{base_url}}/api/tags
HTTP 200   # T-10 list tags is public
[Asserts]
jsonpath "$.items[*].name" contains "shared-{{run_id}}"   # T-10 the shared tag is listed
jsonpath "$.items[?(@.name=='shared-{{run_id}}')].postCount" == 2   # T-10 postCount counts posts that carry the tag (a duplicate entry also fails here)
jsonpath "$.items[?(@.name=='solo-{{run_id}}')].postCount" == 1   # T-10 postCount for a single-use tag

# T-11 posts by tag: pagination envelope, newest first
GET {{base_url}}/api/tags/shared-{{run_id}}/posts
HTTP 200   # T-11 posts by tag is public
[Asserts]
jsonpath "$.total" == 2   # T-11 both posts carry the tag
jsonpath "$.items[0].id" == "{{p2}}"   # T-11 newest first
jsonpath "$.items[1].id" == "{{p1}}"   # T-11 oldest last

GET {{base_url}}/api/tags/shared-{{run_id}}/posts?pageSize=1
HTTP 200   # T-12 posts by tag honours pageSize
[Asserts]
jsonpath "$.items" count == 1   # T-12 one item per page
jsonpath "$.totalPages" == 2   # T-12 two pages

# T-13 the tag in the path is normalized like stored tags
GET {{base_url}}/api/tags/SHARED-{{run_id}}/posts
HTTP 200   # T-13 tag lookup is case-insensitive
[Asserts]
jsonpath "$.total" == 2   # T-13 upper-case path finds the same posts

# T-14 an unknown tag is an empty page, not a 404
GET {{base_url}}/api/tags/missing-{{run_id}}/posts
HTTP 200   # T-14 unknown tag returns 200
[Asserts]
jsonpath "$.total" == 0   # T-14 total is 0
jsonpath "$.items" isEmpty   # T-14 items is empty

# T-15 counts follow edits: removing a tag from its only post removes it from /api/tags
PUT {{base_url}}/api/posts/{{p1}}
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Shared tag one", "content": "x", "tags": ["shared-{{run_id}}"]}
HTTP 200   # T-15 drop solo tag from post 1

GET {{base_url}}/api/tags
HTTP 200   # T-15 list tags after the edit
[Asserts]
jsonpath "$.items[*].name" not contains "solo-{{run_id}}"   # T-15 tags with zero posts are not listed

# T-16 counts follow deletes
DELETE {{base_url}}/api/posts/{{p2}}
Authorization: Bearer {{token}}
HTTP 204   # T-16 delete post 2

GET {{base_url}}/api/tags
HTTP 200   # T-16 list tags after the delete
[Asserts]
jsonpath "$.items[?(@.name=='shared-{{run_id}}')].postCount" == 1   # T-16 postCount drops when a post is deleted
