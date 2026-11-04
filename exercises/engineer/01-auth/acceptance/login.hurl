# Phase 01 grader: POST /api/auth/login
# Variables: base_url, run_id

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "login_{{run_id}}", "email": "login_{{run_id}}@example.com", "password": "correct-horse-2"}
HTTP 201   # A-01 setup: register a user for the login checks
[Captures]
user_id: jsonpath "$.id"

# A-10 login returns 200 with a JWT, tokenType Bearer, expiresIn seconds and the User
POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "login_{{run_id}}", "password": "correct-horse-2"}
HTTP 200   # A-10 correct credentials must return 200
[Asserts]
jsonpath "$.accessToken" matches /^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/   # A-10 accessToken is a signed JWT (three base64url parts)
jsonpath "$.tokenType" == "Bearer"   # A-10 tokenType is exactly "Bearer"
jsonpath "$.expiresIn" isInteger   # A-10 expiresIn is an integer
jsonpath "$.expiresIn" > 0   # A-10 expiresIn is positive
jsonpath "$.user.id" == "{{user_id}}"   # A-10 user.id is the registered user
body not contains "assword"   # A-02 login never returns password material

# A-11 wrong password: 401 INVALID_CREDENTIALS
POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "login_{{run_id}}", "password": "wrong-password"}
HTTP 401   # A-11 wrong password must return 401
[Asserts]
jsonpath "$.error.code" == "INVALID_CREDENTIALS"   # A-11 error.code is INVALID_CREDENTIALS

# A-12 unknown user gets the SAME answer as a wrong password (no user enumeration)
POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "ghost_{{run_id}}", "password": "correct-horse-2"}
HTTP 401   # A-12 unknown username must return 401, not 404
[Asserts]
jsonpath "$.error.code" == "INVALID_CREDENTIALS"   # A-12 same error.code as a wrong password

# A-13 missing fields: 422
POST {{base_url}}/api/auth/login
Content-Type: application/json
{"username": "login_{{run_id}}"}
HTTP 422   # A-13 login without password must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "password"   # A-13 fields[] names password
