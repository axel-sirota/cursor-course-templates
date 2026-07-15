# Infrastructure Phase Plan

## Project Overview
- Project Name: [Project Name]
- Terraform Version: >= 1.9, < 2.0.0
- AWS Provider Version: ~> 5.0
- Total Modules: [Number]
- Estimated Total Time: [Hours/Days]

## Phase 0: Skeleton

**Goal:** Scaffold the full module tree with valid-but-inert HCL; `terraform plan` succeeds, nothing is applied.

**Deliverables:**
- Complete root + module directory structure
- Backend + provider configuration (pinned versions)
- Every module's variables.tf/outputs.tf matching the drafted contract
- terraform.tfvars.example
- Development tooling configured (tflint, checkov, terraform-docs)

**Success Criteria:**
- terraform fmt -check -recursive passes
- terraform validate passes
- tflint passes
- terraform plan succeeds with expected (placeholder) resource count

**Estimated Time:** 45-60 minutes

**Dependencies:** Backend bucket (and lock table, if used) bootstrapped by hand

---

## Phase 1: [module-name]

**Goal:** [One sentence description of what this module provisions]

**Module:** modules/[module-name]

**Priority:** High/Medium/Low

**Deliverables:**
- Real resource blocks replacing skeleton placeholders
- Validation-first check (checkov/tflint/pytest+boto3) written and initially failing
- terraform plan reviewed and applied from a saved plan file
- Post-apply verification (boto3/aws-cli check)
- Session summary document

**Success Criteria:**
- terraform plan shows "No changes" on immediate re-plan
- Validation-first check now passing
- checkov/tflint clean
- Post-apply verification confirms real resource exists and is healthy

**Estimated Time:** 45-60 minutes

**Dependencies:** Phase 0

**Shared Modules/Outputs Created:**
- module.[module-name].outputs.[output] (available for downstream modules via terraform_remote_state)

---

## Phase 2: [module-name]

**Goal:** [One sentence description]

**Module:** modules/[module-name]

**Priority:** High/Medium/Low

**Deliverables:**
- [List new resources, or "Extends Phase 1 module outputs only"]
- Validation-first check
- Real resource blocks applied
- Session summary document

**Success Criteria:**
- terraform plan diff matches session scope only
- Integration with Phase 1 outputs works (terraform_remote_state resolves)
- Error handling comprehensive (variable validation, preconditions)

**Estimated Time:** 30-45 minutes

**Dependencies:** Phase 1 (module.[module-name].outputs.[output] available)

**Shared Modules/Outputs Created:**
- Extended outputs from [module-name]
- [Additional outputs if any]

---

## Phase 3: [module-name]

**Goal:** [One sentence description]

**Module:** modules/[module-name]

**Priority:** High/Medium/Low

**Deliverables:**
- New resource group (e.g. RDS, CloudFront)
- Validation-first check
- Real resource blocks applied
- Session summary document

**Success Criteria:**
- New resources created successfully
- Cross-module references resolve correctly
- terraform plan/apply clean

**Estimated Time:** 45-60 minutes

**Dependencies:** Phase 1, Phase 2

**Shared Modules/Outputs Created:**
- module.[module-name].outputs.[output]

---

## Phase Priority Matrix

### Must Have (Phase 0-3)
Critical infrastructure required for MVP:
- Phase 0: Skeleton
- Phase 1: [Networking foundation, e.g. VPC]
- Phase 2: [Core compute, e.g. ECS + ALB]
- Phase 3: [Data layer, e.g. RDS, or static asset delivery]

### Should Have (Phase 4-6)
Important but not blocking:
- Phase 4: [CI/CD pipeline wiring]
- Phase 5: [Observability — CloudWatch dashboards/alarms]
- Phase 6: [Autoscaling policies]

### Nice to Have (Phase 7+)
Enhancement features:
- Phase 7: [WAF / edge security]
- Phase 8: [Cost optimization — Savings Plans, Spot for non-prod]
- Phase 9: [Multi-region / DR]

## Implementation Strategy

### Week 1
- Phase 0: Skeleton (Day 1)
- Phase 1-2: Networking + compute (Day 2-3)
- Phase 3: Data/static layer (Day 4-5)

### Week 2
- Phase 4-5: CI/CD + observability (Day 1-2)
- Phase 6+: Enhancements (Day 3-5)

## Risk Assessment

### High Risk Phases
- [Phase N]: [Reason — e.g. RDS resize triggers replacement, or NAT gateway change affects all subnets]

### Dependencies Between Phases
```
Phase 1 (VPC) -> Phase 2 (ALB + ECS) -> Phase 3 (RDS)
                                    \-> Phase 4 (Static site)
```

### Blocking Issues
- Remote state backend (S3 bucket + optional DynamoDB table) must exist before the first `terraform init`
- VPC module must be applied before ECS/RDS modules can reference its subnet outputs
- IAM OIDC trust for CI/CD must exist before the pipeline can assume a deploy role
- ACM certificate validation (DNS) can block ALB HTTPS listener creation if not pre-provisioned

## Testing Strategy

### Per Phase
- Validation-first check written before real resource blocks
- Check must fail initially (proves it validates something)
- Implementation makes the check pass
- Script unit tests added for any new automation logic

### Integration Testing
After Phase 2: Test cross-module references (VPC -> ECS)
After Phase 3: Test full request path (ALB -> ECS -> RDS, if applicable)
After Phase 6: Full ephemeral-workspace e2e apply/destroy cycle

## Quality Gates

### Before Completing Each Phase
- [ ] terraform plan shows "No changes" on re-plan
- [ ] terraform fmt -check -recursive passes
- [ ] terraform validate passes
- [ ] tflint passes
- [ ] checkov -d . clean (or skips justified)
- [ ] Session summary generated
- [ ] Changes committed

### Before Moving to Production
- [ ] All phases complete
- [ ] Full validation suite passing
- [ ] Security review complete (checkov + manual IAM review)
- [ ] Cost estimate reviewed (Infracost or manual)
- [ ] Documentation updated (terraform-docs)

## Rollback Plan

### If a Phase's Apply Fails or Needs Reverting
1. Never delete or hand-edit the `.tfstate` file
2. Pull a state backup first: `terraform state pull > backup-phase-N.tfstate`
3. Prefer reverting the HCL (`git revert`) and re-applying the previous configuration over manual `state rm`/`import`
4. Review what went wrong before re-attempting; split into smaller phases if the blast radius was too large

### State Safety
- Remote state is versioned (S3 bucket versioning enabled) — a previous state version can be restored from S3 if absolutely necessary, as a last resort, with human approval only
- Every module's stateful resources (RDS, S3 with data) carry `lifecycle { prevent_destroy = true }`

## Notes

### Design Decisions
- [Key architectural decisions made during design, e.g. "single NAT gateway for dev, one-per-AZ for prod"]
- [Trade-offs considered]
- [Alternative approaches rejected and why]

### Assumptions
- [Assumptions about traffic volume]
- [Assumptions about environment count — dev/staging/prod as separate state or separate directories]
- [Assumptions about team size / who has apply access]

### Future Considerations
- [Multi-region expansion]
- [Cost optimization opportunities]
- [Additional environments]
