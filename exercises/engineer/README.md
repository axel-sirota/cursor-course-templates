# Engineer exercises: the Blog API, in your stack

Every engineer builds the same Blog API from the same contract. You build it in the language you use at work: Python, Go, Java or TypeScript. Grading is done over HTTP, so it does not care which stack you picked.

**Requirements:** your stack's toolchain (see [STACK_NOTES.md](STACK_NOTES.md)) plus [Hurl](https://hurl.dev) 7 or newer. go-grpc also needs grpcurl. You do not need Python to run the graders.

| Tool | macOS | Windows | Linux |
|---|---|---|---|
| hurl | `brew install hurl` | `winget install hurl` (or scoop, choco) | packages and tarballs at https://hurl.dev/docs/installation.html |
| grpcurl (go-grpc only) | `brew install grpcurl` | release zip from https://github.com/fullstorydev/grpcurl/releases | `go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest` |

On Windows, run the `.sh` scripts from Git Bash or WSL.

## The flow

```
/set-persona add engineer
/setup-stack engineer                 # python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs
/architect engineer exercises/engineer/00-skeleton/README.md
/start-session engineer               # then /engineer-tasks and /engineer-implement
exercises/engineer/run-acceptance.sh 00
/next-session                         # repeat start-session ... next-session for each phase
```

Your code goes in `workspaces/engineer/`. The exercise folders are read-only briefs and graders.

## Phases

The phases are the ones the course has always used. `/architect` runs once (on 00-skeleton); each phase is one `/start-session` to `/next-session` cycle.

| Folder | Phase | Time | You build | Rules |
|---|---|---|---|---|
| [00-skeleton](00-skeleton/README.md) | 0 Skeleton | 60 to 90 min | Every route stubbed with mock data in the contract shape | S-01 to S-14 |
| [01-auth](01-auth/README.md) | 1 Authentication | 90 to 120 min | Register, login with JWT, me, password hashing | A-01 to A-26 |
| [02-posts](02-posts/README.md) | 2 Posts CRUD | 120 min | Posts CRUD, author-only update and delete, pagination | P-01 to P-24 |
| [03-comments](03-comments/README.md) | 3 Comments | 60 to 90 min | Nested comments, author-only delete, cascade | C-01 to C-14 |
| [04-tags](04-tags/README.md) | 4 Tags | 90 min | Many-to-many tags, tag list, posts by tag | T-01 to T-16 |
| [05-polish](05-polish/README.md) | 5 Polish and deploy | 90 to 120 min | Search, sort, error handling, request ids, CORS, Docker | X-01 to X-18 |

Total: about 9 to 11 hours. A one-day workshop usually covers 00 to 02; 03 to 05 make good homework.

## Files

| Path | Purpose |
|---|---|
| `contract/openapi.yaml` | OpenAPI 3.1 contract for all 14 operations. The single source of truth. |
| `contract/grpc/blog.proto` | Same operations for the go-grpc stack, with the HTTP to gRPC status mapping |
| `contract/grpc/grpc_smoke.sh` | grpcurl grader for go-grpc |
| `run-acceptance.sh` | Wrapper that runs one phase (or all) and checks that hurl is installed |
| `<phase>/README.md` | Scenario, task, rules, done-when checklist, in-session commands, stretch goals |
| `<phase>/acceptance/*.hurl` | The grader for that phase, one file per contract area |
| `<phase>/SOLUTION.md` | Instructor notes: design decisions and common mistakes. No implementation. |
| `STACK_NOTES.md` | Ports, file locations, test commands and traps per stack |

## How grading works

1. Start your server. By default the graders call `http://localhost:8000`. Set `BASE_URL` for anything else.
2. Run the phase:

   ```bash
   exercises/engineer/run-acceptance.sh 02                 # just phase 02
   exercises/engineer/run-acceptance.sh 02 --cumulative    # phases 00, 01 and 02
   exercises/engineer/run-acceptance.sh all                # everything
   BASE_URL=http://localhost:8080 exercises/engineer/run-acceptance.sh 01
   GRPC_ADDR=localhost:50051 exercises/engineer/run-acceptance.sh 02 --grpc   # go-grpc
   ```

3. Read the failures. Every request and assert line ends with a comment naming the rule it checks, and Hurl prints that line when it fails:

   ```
   error: Assert status code
     --> 02-posts/acceptance/read_update_delete.hurl:59:6
      |
   59 | HTTP 403   # P-12 only the author may update a post
      |      ^^^ actual value is <200>
   ```

   Look up `P-12` in the phase README.

Each run creates its own users, posts and tags with a fresh `run_id`, so you can run the graders as often as you like against the same database. Graders never delete data they did not create.

To run Hurl by hand, pass the two variables the wrapper sets:

```bash
hurl --test --variable base_url=$BASE_URL --variable run_id=r$RANDOM exercises/engineer/02-posts/acceptance/*.hurl
```

`run_id` must be lowercase letters and digits; it ends up in usernames and tag names.

Passing the grader means the HTTP behaviour matches the contract. Your own unit and integration tests, written test-first with `/engineer-implement`, are still part of "done" in every phase.

## Picking a stack

Any of the six works for every phase. Choose the one your team ships. [STACK_NOTES.md](STACK_NOTES.md) covers each stack's port, where the contract copy goes, how to run your own tests and the framework defaults that break the contract (validation status codes, coercion, 403 vs 401, typed path ids).

go-grpc teams implement `contract/grpc/blog.proto` and grade with `--grpc`. The phase 05 HTTP rules (CORS, request ids, 405) apply only if you add an HTTP gateway, which is a stretch goal.

## Stretch: schema conformance with Schemathesis

The Hurl graders check the rules. Schemathesis generates many requests from `openapi.yaml` and flags responses that do not match the schema. It runs in Docker, so you still need no local Python:

```bash
docker run --rm -v "$PWD/exercises/engineer/contract:/contract" schemathesis/schemathesis:stable \
  run /contract/openapi.yaml --url http://host.docker.internal:8000
```

On Linux add `--add-host=host.docker.internal:host-gateway` to `docker run`.
