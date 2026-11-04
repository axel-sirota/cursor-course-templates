# Phase 04 grader: tags on posts (normalization, validation, replacement on PUT)
# Variables: base_url, run_id (lowercase letters and digits)
# Rule: each tag is trimmed and lowercased, then must match ^[a-z0-9][a-z0-9-]{0,29}$.
#       Duplicates after normalization collapse. At most 5 tags. Post.tags is sorted A to Z.

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "tr_{{run_id}}", "email": "tr_{{run_id}}@example.com", "password": "correct-horse-12"}
HTTP 201   # A-01 setup: register the author

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "tr_{{run_id}}", "password": "correct-horse-12"}
HTTP 200   # A-10 setup: log in
[Captures]
token: jsonpath "$.accessToken"

# T-01 tags are normalized, deduplicated and sorted
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Tagged {{run_id}}", "content": "tags!", "tags": ["Web-{{run_id}}", " api-{{run_id}} ", "API-{{run_id}}"]}
HTTP 201   # T-01 create post with tags must return 201
[Captures]
post_id: jsonpath "$.id"
[Asserts]
jsonpath "$.tags" count == 2   # T-01 "API-x" and " api-x " collapse into one tag
jsonpath "$.tags[0]" == "api-{{run_id}}"   # T-01 tags are lowercased, trimmed and sorted A to Z
jsonpath "$.tags[1]" == "web-{{run_id}}"   # T-01 second tag after sorting

GET {{base_url}}/api/posts/{{post_id}}
HTTP 200   # T-01 tags are persisted
[Asserts]
jsonpath "$.tags" count == 2   # T-01 GET returns the same two tags

# T-02 a post without tags has tags: []
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Untagged {{run_id}}", "content": "no tags"}
HTTP 201   # T-02 create post without tags
[Asserts]
jsonpath "$.tags" isCollection   # T-02 tags is still an array
jsonpath "$.tags" isEmpty   # T-02 and it is empty

# T-03 invalid tag characters: 422 on field tags
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Bad tag", "content": "x", "tags": ["no spaces!"]}
HTTP 422   # T-03 a tag with spaces or punctuation must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "tags"   # T-03 fields[] names tags

# T-04 more than 5 distinct tags: 422
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Too many", "content": "x", "tags": ["a1", "a2", "a3", "a4", "a5", "a6"]}
HTTP 422   # T-04 six distinct tags must return 422 (max 5)
[Asserts]
jsonpath "$.error.fields[*].field" contains "tags"   # T-04 fields[] names tags

# T-05 tags must be an array of strings
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Wrong type", "content": "x", "tags": "api"}
HTTP 422   # T-05 a string instead of an array must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "tags"   # T-05 fields[] names tags

# T-06 PUT with tags replaces the whole set
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Tagged {{run_id}}", "content": "tags!", "tags": ["web-{{run_id}}"]}
HTTP 200   # T-06 PUT with tags must return 200
[Asserts]
jsonpath "$.tags" count == 1   # T-06 the new set replaces the old one
jsonpath "$.tags[0]" == "web-{{run_id}}"   # T-06 only the new tag remains

# T-07 PUT without a tags field leaves tags unchanged
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Retitled {{run_id}}", "content": "tags!"}
HTTP 200   # T-07 PUT without tags must return 200
[Asserts]
jsonpath "$.tags" count == 1   # T-07 omitting tags keeps the current tags
jsonpath "$.tags[0]" == "web-{{run_id}}"   # T-07 same tag as before

# T-08 PUT with tags: [] clears them
PUT {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Retitled {{run_id}}", "content": "tags!", "tags": []}
HTTP 200   # T-08 PUT with an empty array must return 200
[Asserts]
jsonpath "$.tags" isEmpty   # T-08 an empty array removes every tag
