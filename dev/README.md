# dev/

Template-maintenance agents for the people who edit this course, not for students. `dev/agents/` holds verifiers that audit stacks, persona commands, `/setup-stack` routing, `/architect` inputs and example code (`architect-hook-verifier`, `example-code-validator`, `persona-command-verifier`, `setup-stack-routing-verifier`, `stack-completeness-auditor`). They live here so they do not show up in a student's Cursor. To use one, copy it into `.cursor/agents/` and run it there, then delete the copy before you ship the template.
