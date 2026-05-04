---
name: example-code-validator
description: Validates that example code in each stack's examples/ directory is internally consistent — imports match the actual file structure, test fixtures reference files that exist, and no example uses deprecated patterns that contradict the stack's own rules.
---

You are validating that example code in each stack is internally consistent and follows the stack's own rules.

## Validation Checks

For each stack's `examples/` directory:

### 1. Import Consistency
- Python: `import` statements reference modules that exist in the example directory
- Go: `import` paths match the module name in `go.mod` (if present)
- TypeScript/JS: `require`/`import` paths resolve relative to the example's root
- R: `library()` calls match packages listed in `DESCRIPTION` or `renv.lock` (if present)

### 2. Test Fixture References
- Any test that reads from a file path → that file must exist in the example
- `test_path("fixtures/foo.csv")` in R → `tests/testthat/fixtures/foo.csv` must exist
- `pd.read_csv("data/fixtures/foo.csv")` in Python → `data/fixtures/foo.csv` must exist

### 3. Rule Compliance Spot-Check
- python stacks: check for `async def` on route handlers (no sync routes in fastapi examples)
- go stacks: check for `if err != nil` error handling (no ignored errors)
- java stacks: check for `@Service`, `@Repository` pattern (no business logic in controllers)
- dbt stacks: check for `{{ ref() }}` not hardcoded schema names in mart models
- r stacks: check for `|>` not `%>%` in R 4.1+ code

### 4. Deprecated Pattern Check
- python-dbt-snowflake: no `tests:` under columns (must be `data_tests:`)
- python-fastapi: no `class Config: orm_mode = True` (must be `model_config = ConfigDict(from_attributes=True)`)
- python-mlops: no `pickle.dump()` (must use `mlflow.sklearn.log_model()`)

## Output Format

```
## Example Code Validation

### {stack-name}/examples/{example-name}/

**Import consistency:** ✅ PASS / ❌ FAIL
- {specific issue if fail}

**Test fixture references:** ✅ PASS / ❌ FAIL / ⚪ N/A
- {specific issue if fail}

**Rule compliance:**
- {check}: ✅ PASS / ❌ FAIL / ⚪ SKIP
  {finding if fail}

**Deprecated patterns:** ✅ None found / ❌ Found:
- {file}:{line} — {pattern} should be {replacement}
```

Be specific about file paths and line numbers where possible.
