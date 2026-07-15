# Research Export: [Problem Title]

## Export Information
- Date: [YYYY-MM-DD]
- Phase: Phase N - [module-name]
- Severity: [Low/Medium/High/Blocking]
- Exported By: [Your Name]

## Problem Statement

### Brief Description
[One paragraph describing the problem in plain language]

### Impact
- What is blocked: [Module/Resource/Pipeline stage]
- Workaround available: [Yes/No - describe if yes]
- Production impact: [Yes/No - describe if yes, e.g. state locked, resource in a failed state]

## Context

### Current Phase
- Phase Number: N
- Module Being Implemented: modules/[module-name]
- Step Where Problem Occurred: [Validation-first check / terraform plan / terraform apply / post-apply verification / etc.]

### Related Phases
- Dependencies on previous phases: [List, e.g. "depends on module.vpc outputs"]
- Impact on future phases: [List]

### System State
- Environment: [dev/staging/prod]
- Terraform version: [x.y.z]
- AWS provider version: [x.y.z]
- State backend: [S3 bucket + key, locking mode]
- Other relevant tool versions: [tflint, checkov]

## What We Tried

### Attempt 1
**Approach:**
[Describe what was tried]

**Result:**
[What happened]

**Why it didn't work:**
[Analysis of why this approach failed]

**Code snippets:**
```hcl
# Include relevant HCL that was tried
```

```bash
# Include relevant CLI commands that were tried
```

### Attempt 2
**Approach:**
[Describe what was tried]

**Result:**
[What happened]

**Why it didn't work:**
[Analysis of why this approach failed]

**Code snippets:**
```hcl
# Include relevant HCL that was tried
```

### Attempt 3
**Approach:**
[Describe what was tried]

**Result:**
[What happened]

**Why it didn't work:**
[Analysis of why this approach failed]

**Code snippets:**
```hcl
# Include relevant HCL that was tried
```

## Error Messages

### Primary Error
```
[Full terraform plan/apply error output, including stack trace]
```

### Secondary Errors
```
[Any related provider warnings or errors]
```

### Log Output
```
[Relevant TF_LOG=debug output, or CloudTrail/CloudWatch log entries showing the problem]
```

## Current Code

### Problematic Code
**File:** [modules/module-name/main.tf]
**Lines:** [XX-YY]

```hcl
# Include the problematic resource/data block
```

### Related Code
**File:** [modules/module-name/variables.tf]
**Lines:** [XX-YY]

```hcl
# Include related variable/output definitions that might be relevant
```

### Configuration
**terraform.tfvars (redacted) / TF_VAR_* env vars set:**
```
[Relevant non-secret variable values]
```

**backend.tf:**
```hcl
# Relevant backend configuration
```

## Research Questions

### Primary Questions
1. [Main question about the problem]
2. [Secondary question]
3. [Follow-up question]

### Technical Questions
1. [Specific provider resource-argument behavior to research]
2. [AWS API behavior question]
3. [Best-practice question]

### Architecture Questions
1. [Module boundary / blast-radius question]
2. [State-management question]
3. [Alternative approach question]

## Hypotheses

### Hypothesis 1
**Theory:**
[What might be causing the problem — e.g. eventual-consistency lag in the AWS API, a provider version bug, an IAM permission gap]

**Evidence:**
- [Supporting evidence]
- [Related observations]

**Test:**
[How to test this hypothesis — e.g. re-run plan after a delay, check CloudTrail for AccessDenied]

### Hypothesis 2
**Theory:**
[Alternative explanation]

**Evidence:**
- [Supporting evidence]
- [Related observations]

**Test:**
[How to test this hypothesis]

## Documentation References

### Official Documentation Consulted
- [registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/... link] - [What was checked]
- [Terraform language docs link] - [What was checked]
- [AWS service docs link] - [What was checked]

### GitHub Issues / Provider Changelog
- [hashicorp/terraform-provider-aws issue link] - [Summary of what was found]
- [Link] - [Summary of what was found]

### Blog Posts / Tutorials
- [Link] - [Summary of content]
- [Link] - [Summary of content]

## Environment Details

### Provider/State Info
```bash
terraform version
# Terraform v1.9.8
# + provider registry.terraform.io/hashicorp/aws v5.68.0

terraform state list | head -20
```

### AWS Resource State
```bash
# Relevant aws cli describe/list output
aws ecs describe-services --cluster acme-dev-cluster --services acme-dev-web
```

### Tooling Versions
```bash
tflint --version
checkov --version
```

## Constraints and Requirements

### Must Have
- [Requirement that cannot be compromised, e.g. "no downtime during fix"]
- [Requirement that cannot be compromised]

### Nice to Have
- [Preference but can be adjusted]
- [Preference but can be adjusted]

### Cannot Do
- [Approaches that are not options, e.g. "cannot hand-edit .tfstate"]
- [Approaches that are not options, e.g. "cannot run terraform destroy on this module"]

## Success Criteria

### How We'll Know It's Fixed
- [ ] [terraform plan shows "No changes" after fix]
- [ ] [Specific validation-first check passes]
- [ ] [Post-apply verification confirms healthy resource]

### Acceptance Check
```python
def test_solution():
    """This check should pass when the problem is solved."""
    # pytest+boto3 or checkov check
```

## Additional Context

### Similar Issues Encountered
- Phase X: [Similar problem and how it was solved]
- Phase Y: [Related issue]

### Working Code References
**File:** [modules/other-module/main.tf]
```hcl
# Working HCL that might provide hints
```

### Related Phase Summaries
- Phase N-1 Summary: [Key points that might be relevant]
- Phase N-2 Summary: [Key points that might be relevant]

## Next Steps After Research

### Information Needed
- [ ] [Specific information to gather]
- [ ] [Documentation to review]
- [ ] [Expertise to consult, e.g. AWS support case]

### Potential Solutions to Test
1. [Solution idea from research]
2. [Alternative solution]
3. [Fallback solution]

### Timeline
- Time spent so far: [X] hours
- Maximum time to allocate: [Y] hours
- Decision point: [When to escalate or pivot]

## Notes for Future Reference

### Lessons Learned
[Document insights even if problem not yet solved]

### Documentation Gaps
[Note where official provider docs were unclear, stale, or missing an example]

### Process Improvements
[Note how this could have been prevented or caught earlier — e.g. a tflint custom rule, a checkov check, a variable validation block]

---

## Research Results (To Be Filled After External Research)

### Solution Found
[Describe the solution]

### Why It Works
[Explain the underlying issue and why this solution addresses it]

### Implementation Plan
1. [Step to implement solution]
2. [Step to verify solution via terraform plan]
3. [Step to prevent recurrence, e.g. add a tflint/checkov rule]

### Code Changes Required
```hcl
# New/changed HCL to implement
```

### Testing Strategy
```python
# Checks to verify the solution
```

### Documentation Updates Needed
- [What needs to be documented]
- [Where to document it — module README, plan/architecture/resources.md]
