# Phase 05 grader: error handling, request ids and CORS
# Variables: base_url, run_id
# CORS: the server reads allowed origins from CORS_ORIGINS; http://localhost:3000 must be allowed by default.

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "xe_{{run_id}}", "email": "xe_{{run_id}}@example.com", "password": "correct-horse-15"}
HTTP 201   # A-01 setup: register

POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "xe_{{run_id}}", "password": "correct-horse-15"}
HTTP 200   # A-10 setup: log in
[Captures]
token: jsonpath "$.accessToken"

POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "Errors {{run_id}}", "content": "x"}
HTTP 201   # P-02 setup: a post
[Captures]
post_id: jsonpath "$.id"

# X-10 unknown routes answer with the JSON error envelope
GET {{base_url}}/api/does-not-exist
HTTP 404   # X-10 an unknown route must return 404
[Asserts]
header "Content-Type" contains "application/json"   # X-10 even framework 404s are JSON
jsonpath "$.error.code" == "NOT_FOUND"   # X-10 error.code is NOT_FOUND

# X-11 malformed JSON is a 400, not a 422 and not a 500, with no stack trace
POST {{base_url}}/api/posts
Authorization: Bearer {{token}}
Content-Type: application/json
```
{"title": "broken",
```
HTTP 400   # X-11 a body that is not valid JSON must return 400
[Asserts]
jsonpath "$.error.code" == "MALFORMED_JSON"   # X-11 error.code is MALFORMED_JSON
body not contains "Traceback"   # X-12 no Python stack trace in error bodies
body not contains "Exception"   # X-12 no Java or Node exception class names in error bodies
body not contains "goroutine"   # X-12 no Go panic output in error bodies

# X-13 a known path with an unsupported method: 405 with Allow
PATCH {{base_url}}/api/posts/{{post_id}}
Authorization: Bearer {{token}}
Content-Type: application/json
{"title": "patch is not in the contract"}
HTTP 405   # X-13 PATCH on /api/posts/{id} must return 405 (the contract uses PUT)
[Asserts]
header "Allow" contains "PUT"   # X-13 the Allow header lists the supported methods
jsonpath "$.error.code" == "METHOD_NOT_ALLOWED"   # X-13 error.code is METHOD_NOT_ALLOWED

# X-14 every response carries X-Request-Id; a client-sent id is echoed back
GET {{base_url}}/health
X-Request-Id: grader-{{run_id}}
HTTP 200   # X-14 health with a client request id
[Asserts]
header "X-Request-Id" == "grader-{{run_id}}"   # X-14 the client X-Request-Id is echoed

GET {{base_url}}/api/posts/{{post_id}}
HTTP 200   # X-15 a request without an id still gets one
[Asserts]
header "X-Request-Id" exists   # X-15 the server generates an X-Request-Id when none is sent

GET {{base_url}}/api/posts/00000000-0000-0000-0000-000000000000
HTTP 404   # X-15 error responses carry the id too
[Asserts]
header "X-Request-Id" exists   # X-15 X-Request-Id is present on errors

# X-16 CORS preflight from the default allowed origin
OPTIONS {{base_url}}/api/posts
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization, Content-Type
HTTP *
[Asserts]
status >= 200   # X-16 preflight must succeed (200 or 204)
status < 300   # X-16 preflight must succeed (200 or 204)
header "Access-Control-Allow-Origin" == "http://localhost:3000"   # X-16 the allowed origin is echoed

# X-17 a simple request from an allowed origin gets the CORS header
GET {{base_url}}/api/posts?pageSize=1
Origin: http://localhost:3000
HTTP 200   # X-17 GET with an Origin header
[Asserts]
header "Access-Control-Allow-Origin" == "http://localhost:3000"   # X-17 allowed origin echoed on real responses

# X-18 an origin that is not allowed gets no CORS header
GET {{base_url}}/api/posts?pageSize=1
Origin: https://evil.example
HTTP 200   # X-18 the request itself still succeeds
[Asserts]
header "Access-Control-Allow-Origin" not exists   # X-18 never echo an origin that is not in CORS_ORIGINS (no "*")
