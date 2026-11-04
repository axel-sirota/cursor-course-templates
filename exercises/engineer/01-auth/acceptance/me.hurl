# Phase 01 grader: GET /api/auth/me and bearer token checks
# Variables: base_url, run_id

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "me_{{run_id}}", "email": "me_{{run_id}}@example.com", "password": "correct-horse-3"}
HTTP 201   # A-01 setup: register a user
[Captures]
user_id: jsonpath "$.id"

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "me_{{run_id}}", "password": "correct-horse-3"}
HTTP 200   # A-10 setup: log in
[Captures]
token: jsonpath "$.accessToken"

# A-20 a valid token returns the caller's User
GET {{base_url}}/api/auth/me
Authorization: Bearer {{token}}
HTTP 200   # A-20 GET /api/auth/me with a valid token must return 200
[Asserts]
jsonpath "$.id" == "{{user_id}}"   # A-20 me returns the token owner
jsonpath "$.username" == "me_{{run_id}}"   # A-20 me returns the username
body not contains "assword"   # A-02 me never returns password material

# A-21 no Authorization header: 401 UNAUTHORIZED
GET {{base_url}}/api/auth/me
HTTP 401   # A-21 missing token must return 401, not 403
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # A-21 error.code is UNAUTHORIZED

# A-22 garbage token: 401
GET {{base_url}}/api/auth/me
Authorization: Bearer not-a-jwt
HTTP 401   # A-22 a malformed token must return 401, not 500
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # A-22 error.code is UNAUTHORIZED

# A-23 tampered signature: 401
GET {{base_url}}/api/auth/me
Authorization: Bearer {{token}}x
HTTP 401   # A-23 a token with a modified signature must return 401
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # A-23 error.code is UNAUTHORIZED

# A-24 HS256 token signed with a different secret (sub "1", exp year 2100): 401
GET {{base_url}}/api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjo0MTAyNDQ0ODAwfQ.DMmurm4_zeE5mMwnOcjj-pWTxa1QEnaGH9rNlgaFqy8
HTTP 401   # A-24 a token signed with another key must return 401 (verify the signature)
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # A-24 error.code is UNAUTHORIZED

# A-25 unsigned token with alg "none": 401
GET {{base_url}}/api/auth/me
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwiZXhwIjo0MTAyNDQ0ODAwfQ.
HTTP 401   # A-25 alg=none tokens must be rejected with 401 (pin the algorithm to HS256)
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # A-25 error.code is UNAUTHORIZED

# A-26 wrong scheme: 401
GET {{base_url}}/api/auth/me
Authorization: Basic {{token}}
HTTP 401   # A-26 only the Bearer scheme is accepted
[Asserts]
jsonpath "$.error.code" == "UNAUTHORIZED"   # A-26 error.code is UNAUTHORIZED
