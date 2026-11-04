# Phase 02 grader: GET /api/posts pagination (page, pageSize) and the authorId filter
# Variables: base_url, run_id
# Order: newest first (createdAt descending). The small delays keep createdAt values distinct.

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "pp_{{run_id}}", "email": "pp_{{run_id}}@example.com", "password": "correct-horse-7"}
HTTP 201   # A-01 setup: register the author
[Captures]
author_id: jsonpath "$.id"

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "pp_{{run_id}}", "password": "correct-horse-7"}
HTTP 200   # A-10 setup: log in
[Captures]
token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Page post 1", "content": "one"}
HTTP 201   # P-02 setup: post 1
[Captures]
p1: jsonpath "$.id"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
[Options]
delay: 20
{"title": "Page post 2", "content": "two"}
HTTP 201   # P-02 setup: post 2
[Captures]
p2: jsonpath "$.id"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
[Options]
delay: 20
{"title": "Page post 3", "content": "three"}
HTTP 201   # P-02 setup: post 3
[Captures]
p3: jsonpath "$.id"

# P-20 defaults: page=1, pageSize=10; authorId filters to one author
GET {{base_url}}/api/posts?authorId={{author_id}}
HTTP 200   # P-20 list posts is public
[Asserts]
jsonpath "$.page" == 1   # P-20 default page is 1
jsonpath "$.pageSize" == 10   # P-20 default pageSize is 10
jsonpath "$.total" == 3   # P-20 total counts only this author's posts
jsonpath "$.totalPages" == 1   # P-20 totalPages = ceil(total / pageSize)
jsonpath "$.items" count == 3   # P-20 all three posts on page 1

# P-21 page 1 of size 2 holds the two newest posts, newest first
GET {{base_url}}/api/posts?authorId={{author_id}}&pageSize=2&page=1
HTTP 200   # P-21 explicit page and pageSize
[Asserts]
jsonpath "$.items" count == 2   # P-21 page 1 has pageSize items
jsonpath "$.items[0].id" == "{{p3}}"   # P-21 newest post first
jsonpath "$.items[1].id" == "{{p2}}"   # P-21 second newest next
jsonpath "$.total" == 3   # P-21 total does not depend on the page
jsonpath "$.totalPages" == 2   # P-21 ceil(3 / 2) = 2

# P-22 page 2 holds the remainder
GET {{base_url}}/api/posts?authorId={{author_id}}&pageSize=2&page=2
HTTP 200   # P-22 page 2
[Asserts]
jsonpath "$.items" count == 1   # P-22 last page has the remainder
jsonpath "$.items[0].id" == "{{p1}}"   # P-22 oldest post last
jsonpath "$.page" == 2   # P-22 page echoes the request

# P-23 a page past the end is empty, not an error
GET {{base_url}}/api/posts?authorId={{author_id}}&pageSize=2&page=3
HTTP 200   # P-23 a page past the end returns 200
[Asserts]
jsonpath "$.items" count == 0   # P-23 and an empty items[]
jsonpath "$.total" == 3   # P-23 total is still reported

# P-24 bad paging parameters: 422 with the field named
GET {{base_url}}/api/posts?pageSize=0
HTTP 422   # P-24 pageSize=0 must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "pageSize"   # P-24 fields[] names pageSize

GET {{base_url}}/api/posts?pageSize=101
HTTP 422   # P-24 pageSize=101 must return 422 (max is 100)
[Asserts]
jsonpath "$.error.fields[*].field" contains "pageSize"   # P-24 fields[] names pageSize

GET {{base_url}}/api/posts?page=0
HTTP 422   # P-24 page=0 must return 422 (pages start at 1)
[Asserts]
jsonpath "$.error.fields[*].field" contains "page"   # P-24 fields[] names page

GET {{base_url}}/api/posts?page=abc
HTTP 422   # P-24 a non-numeric page must return 422, not 400 or 500
[Asserts]
jsonpath "$.error.fields[*].field" contains "page"   # P-24 fields[] names page
