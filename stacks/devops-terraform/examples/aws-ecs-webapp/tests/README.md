# Tests: aws-ecs-webapp

## Layers

| Layer | Location | Costs Money? | Command |
|-------|----------|--------------|---------|
| Static | (n/a, tool-driven) | No | `terraform fmt -check -recursive && terraform validate` |
| Lint | (n/a, tool-driven) | No | `tflint` |
| Policy | `tests/policy/` | No | `checkov -d . --external-checks-dir tests/policy` |
| Script unit | `tests/scripts/` | No (mocked via Stubber/moto) | `pytest tests/scripts/ -v` |
| Integration / e2e | `tests/integration/` | **Yes** (real apply/destroy) | `pytest tests/integration/ -v -m e2e` |

## Run Everything Except e2e (Default, Safe, Free)

```bash
terraform fmt -check -recursive
terraform validate
tflint
checkov -d . --external-checks-dir tests/policy
.venv/bin/python3 -m pytest tests/ -v -m "not e2e"
```

## Run the e2e Suite (Manual Only, Costs Money)

```bash
.venv/bin/python3 -m pytest tests/integration/ -v -m e2e
```

This applies real infrastructure into a throwaway workspace and destroys it in a `finally` block. Run manually, or on a scheduled/nightly CI job — never in the default PR pipeline.

## Test Files

- `tests/policy/check_alb_https_redirect.py` — checkov custom check, the validation-first check for the ALB HTTP listener
- `tests/scripts/conftest.py` — shared moto/Stubber fixtures
- `tests/scripts/test_verify_deployment.py` — HP/UP unit tests for `scripts/verify_deployment.py`
- `tests/integration/test_e2e_stack.py` — full ephemeral apply/destroy cycle
