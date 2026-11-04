# Phase 05 grader: search (q), tag filter and sort on GET /api/posts
# Variables: base_url, run_id (lowercase letters and digits)
# Filters combine with AND. sort is one of -createdAt (default), createdAt, title, -title.

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "xs_{{run_id}}", "email": "xs_{{run_id}}@example.com", "password": "correct-horse-14"}
HTTP 201   # A-01 setup: register the author
[Captures]
author_id: jsonpath "$.id"

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "xs_{{run_id}}", "password": "correct-horse-14"}
HTTP 200   # A-10 setup: log in
[Captures]
token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Banana bread", "content": "Uses the zebra{{run_id}} method", "tags": ["baking-{{run_id}}"]}
HTTP 201   # X-01 setup: post B (match in content)
[Captures]
pb: jsonpath "$.id"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
[Options]
delay: 20
{"title": "Apple pie ZEBRA{{run_id}}", "content": "Plain text", "tags": ["baking-{{run_id}}"]}
HTTP 201   # X-01 setup: post A (match in title, upper case)
[Captures]
pa: jsonpath "$.id"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
[Options]
delay: 20
{"title": "Carrot cake", "content": "No match here", "tags": ["baking-{{run_id}}"]}
HTTP 201   # X-01 setup: post C (no match)
[Captures]
pc: jsonpath "$.id"

# X-01 q is a case-insensitive substring match on title OR content
GET {{base_url}}/api/posts?q=zebra{{run_id}}
HTTP 200   # X-01 search must return 200
[Asserts]
jsonpath "$.total" == 2   # X-01 two posts match (one by title, one by content)
jsonpath "$.items[*].id" contains "{{pa}}"   # X-01 title match found, ignoring case
jsonpath "$.items[*].id" contains "{{pb}}"   # X-01 content match found
jsonpath "$.items[*].id" not contains "{{pc}}"   # X-01 non-matching post excluded

# X-02 tag filter on /api/posts, combined with sort=title
GET {{base_url}}/api/posts?tag=baking-{{run_id}}&sort=title
HTTP 200   # X-02 tag filter plus sort
[Asserts]
jsonpath "$.total" == 3   # X-02 all three posts carry the tag
jsonpath "$.items[0].id" == "{{pa}}"   # X-02 sort=title is A to Z: Apple first
jsonpath "$.items[1].id" == "{{pb}}"   # X-02 Banana second
jsonpath "$.items[2].id" == "{{pc}}"   # X-02 Carrot third

GET {{base_url}}/api/posts?authorId={{author_id}}&sort=-title
HTTP 200   # X-03 sort=-title is Z to A
[Asserts]
jsonpath "$.items[0].id" == "{{pc}}"   # X-03 Carrot first
jsonpath "$.items[2].id" == "{{pa}}"   # X-03 Apple last

GET {{base_url}}/api/posts?authorId={{author_id}}&sort=createdAt
HTTP 200   # X-04 sort=createdAt is oldest first
[Asserts]
jsonpath "$.items[0].id" == "{{pb}}"   # X-04 oldest first
jsonpath "$.items[2].id" == "{{pc}}"   # X-04 newest last

GET {{base_url}}/api/posts?authorId={{author_id}}
HTTP 200   # X-05 default sort is -createdAt
[Asserts]
jsonpath "$.items[0].id" == "{{pc}}"   # X-05 newest first by default

# X-06 filters combine with AND
GET {{base_url}}/api/posts?q=zebra{{run_id}}&tag=baking-{{run_id}}&sort=title&pageSize=1
HTTP 200   # X-06 q + tag + sort + pageSize together
[Asserts]
jsonpath "$.total" == 2   # X-06 AND of q and tag
jsonpath "$.items[0].id" == "{{pa}}"   # X-06 sorted by title, first page
jsonpath "$.totalPages" == 2   # X-06 pagination applies after filtering

# X-07 invalid sort: 422
GET {{base_url}}/api/posts?sort=popularity
HTTP 422   # X-07 an unknown sort key must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "sort"   # X-07 fields[] names sort
