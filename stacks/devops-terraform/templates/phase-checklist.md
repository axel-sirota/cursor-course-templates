# Phase N Checklist: [module-name]

## Phase Information
- Phase Number: N
- Module: modules/[module-name]
- Goal: [One sentence description]
- Dependencies: [List previous phases / module outputs required]
- Estimated Time: [X] minutes
- Start Time: [YYYY-MM-DD HH:MM]

## Pre-Phase Setup
- [ ] Previous phase summary reviewed
- [ ] Upstream module outputs identified (terraform_remote_state keys)
- [ ] Dependencies understood
- [ ] Phase requirements clear
- [ ] Backend reachable (`terraform init` succeeds)

## Step 1: Validation-First Check (5-10 min)
- [ ] Check file created: tests/policy/check_[name].py or tests/scripts/test_[name].py
- [ ] Check written against skeleton's placeholder state
- [ ] Check includes the success case
- [ ] Check includes the failure/error case
- [ ] Check run and confirmed FAILING
- [ ] Check failure makes sense (no real resource yet)

## Step 2: Backend / State Readiness (2-5 min)
- [ ] `terraform init` succeeds against the remote backend
- [ ] `terraform state list` shows expected prior-session resources (no drift)
- [ ] Upstream `terraform_remote_state` data source resolves

## Step 3: Variable/Output Contract (5 min)
- [ ] variables.tf matches plan/architecture/variables-outputs.md
- [ ] outputs.tf matches plan/architecture/variables-outputs.md
- [ ] type and description present on every variable
- [ ] sensitive = true on any secret-bearing variable
- [ ] validation blocks added where constraints exist

## Step 4: Resource Blocks (10-20 min)
- [ ] Skeleton placeholder identified and located
- [ ] Real resource arguments filled in
- [ ] No hardcoded ARNs/account IDs (use data sources or variables)
- [ ] for_each used for named resource sets (not count, unless simple repetition)
- [ ] locals extracted for repeated expressions
- [ ] Tags applied via local.common_tags / default_tags
- [ ] lifecycle { prevent_destroy = true } added for stateful resources

## Step 5: `terraform plan` Review (5-10 min)
- [ ] `terraform fmt -check -recursive` passes
- [ ] `terraform validate` passes
- [ ] `tflint` passes
- [ ] `checkov -d .` clean (or skips justified with a comment/`.checkov.yaml` entry)
- [ ] `terraform plan -out=terraform_plans/<ts>.tfplan` run
- [ ] Plan diff reviewed line by line — matches this phase's scope only
- [ ] No unexpected destroy/replace on resources from other phases

## Step 6: `terraform apply` From Saved Plan (2-5 min)
- [ ] `terraform apply terraform_plans/<ts>.tfplan` run (never a fresh, unreviewed apply)
- [ ] Apply completed with no errors
- [ ] `terraform plan` re-run immediately after — shows "No changes"

## Step 7: Post-Apply Verification (5 min)
- [ ] boto3/aws-cli check confirms the real resource exists
- [ ] Resource is in the expected healthy state (e.g. ECS service steady, ALB target healthy)
- [ ] Validation-first check from Step 1 re-run — now PASSING

## Step 8: Code Quality (5 min)
- [ ] `terraform fmt -recursive` applied
- [ ] `terraform validate` clean
- [ ] `tflint` clean
- [ ] `checkov -d .` clean
- [ ] Python script changes: `mypy scripts/` clean, `pytest tests/scripts/ -v` passing
- [ ] Code reviewed for best practices (no `-target`, no manual state edits)

## Step 9: Phase Transition (5-10 min)
- [ ] Phase summary generated: plan/sessions/session-N-summary.md
- [ ] Resources created/modified documented (with resource addresses)
- [ ] State changes documented
- [ ] Shared module outputs documented
- [ ] Cost impact noted
- [ ] Rollback notes provided
- [ ] Known limitations noted
- [ ] Next phase recommendations provided
- [ ] Files changed list complete
- [ ] Time actual vs. estimate noted

## Final Checklist
- [ ] All validation-first checks passing
- [ ] terraform plan shows "No changes" on re-plan
- [ ] Code formatted and linted
- [ ] No hardcoded values
- [ ] Secrets properly managed
- [ ] Error handling comprehensive (variable validation, preconditions)
- [ ] Logging appropriate in any script changes
- [ ] Documentation complete
- [ ] Ready for next phase

## Time Tracking
- Estimated Time: [X] minutes
- Actual Time: [Y] minutes
- Variance: [+/-Z] minutes
- Notes on variance: [Why it took longer/shorter]

## Notes and Learnings
[Document any issues encountered, provider quirks, solutions found, or learnings for future phases]
