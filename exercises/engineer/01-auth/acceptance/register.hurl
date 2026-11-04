# Phase 01 grader: POST /api/auth/register
# Variables: base_url, run_id

# A-01 register returns 201 and the User, with no password material
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "Reg_{{run_id}}", "email": "reg_{{run_id}}@example.com", "password": "correct-horse-1"}
HTTP 201   # A-01 register must return 201 Created
[Asserts]
jsonpath "$.id" isString   # A-01 User.id is a string
jsonpath "$.username" == "Reg_{{run_id}}"   # A-01 username is stored as sent (case kept)
jsonpath "$.email" == "reg_{{run_id}}@example.com"   # A-01 email is returned
jsonpath "$.createdAt" isString   # A-01 createdAt is present
body not contains "assword"   # A-02 the response never contains password or passwordHash fields

# A-03 usernames are unique, case-insensitive: 409 USERNAME_TAKEN
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "reg_{{run_id}}", "email": "other_{{run_id}}@example.com", "password": "correct-horse-1"}
HTTP 409   # A-03 same username in different case must return 409
[Asserts]
jsonpath "$.error.code" == "USERNAME_TAKEN"   # A-03 error.code is USERNAME_TAKEN

# A-04 emails are unique, case-insensitive: 409 EMAIL_TAKEN
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "regtwo_{{run_id}}", "email": "REG_{{run_id}}@example.com", "password": "correct-horse-1"}
HTTP 409   # A-04 same email in different case must return 409
[Asserts]
jsonpath "$.error.code" == "EMAIL_TAKEN"   # A-04 error.code is EMAIL_TAKEN

# A-05 missing fields: 422 VALIDATION_FAILED with one entry per bad field
POST {{base_url}}/api/auth/register
Content-Type: application/json
{}
HTTP 422   # A-05 empty body must return 422, not 400 and not 500
[Asserts]
jsonpath "$.error.code" == "VALIDATION_FAILED"   # A-05 error.code is VALIDATION_FAILED
jsonpath "$.error.fields[*].field" contains "username"   # A-05 fields[] names username
jsonpath "$.error.fields[*].field" contains "email"   # A-05 fields[] names email
jsonpath "$.error.fields[*].field" contains "password"   # A-05 fields[] names password

# A-06 username rules: 3 to 30 of [A-Za-z0-9_]
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "no spaces allowed", "email": "a6_{{run_id}}@example.com", "password": "correct-horse-1"}
HTTP 422   # A-06 username with spaces must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "username"   # A-06 fields[] names username

# A-07 email must look like an email
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "a7_{{run_id}}", "email": "not-an-email", "password": "correct-horse-1"}
HTTP 422   # A-07 bad email must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "email"   # A-07 fields[] names email

# A-08 password must be 8 to 72 bytes (72 is the bcrypt input limit)
POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "a8_{{run_id}}", "email": "a8_{{run_id}}@example.com", "password": "short"}
HTTP 422   # A-08 password under 8 characters must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "password"   # A-08 fields[] names password

POST {{base_url}}/api/auth/register
Content-Type: application/json
{"username": "a8b_{{run_id}}", "email": "a8b_{{run_id}}@example.com", "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
HTTP 422   # A-08 password of 73 bytes must return 422
[Asserts]
jsonpath "$.error.fields[*].field" contains "password"   # A-08 fields[] names password
