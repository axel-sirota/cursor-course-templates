# Close Workbook Starter

Use this to start a new workpaper in `workspaces/accountant/`. All paths below are relative to that folder.

## 1. Folders

```
data/raw/        put source extracts here, then never touch them again
data/interim/    work copies (add to .gitignore)
src/             one module per workpaper
tests/           one test file per workpaper
output/          generated reports only
docs/            close plan, materiality, notes
```

## 2. Environment

```bash
uv venv && uv pip install -r requirements.txt
# or
python -m venv .venv && .venv/bin/python3 -m pip install -r requirements.txt
```

`requirements.txt`:

```
pandas==2.3.3
numpy==2.3.4
openpyxl==3.1.5
pytest==8.4.2
# pandera==0.26.1   optional, for schema contracts
```

## 3. Close plan (write it before any code)

Create `docs/close-plan.md`:

```markdown
# Close plan: Northwind Co., period <YYYY-MM>

Entity: Northwind Co. (synthetic)
Period: <YYYY-MM-01> to <YYYY-MM-DD>
Materiality: <amount> overall, <amount or %> for flux lines
Accounts in scope: <list>

## Sources
| File | Rows | Control total | Received |
|---|---:|---:|---|

## Workpapers
| Workpaper | Command | Output | Owner |
|---|---|---|---|
| Bank rec 1010 | /acct-reconcile | output/recon-1010-<period>.md | |
| Flux | /acct-variance | output/flux-<period>.md | |
| JE testing | /acct-je-test | output/je-test-<period>.md | |
| Close memo | /acct-close-handoff | output/close-memo-<period>.md | |
```

## 4. Step module skeleton

`src/bank_rec.py`:

```python
from pathlib import Path
import pandas as pd

PERIOD = "2026-10"
MATERIALITY_CENTS = 50_000  # from docs/close-plan.md

def load_sources(raw_dir: Path) -> dict[str, pd.DataFrame]:
    return {"gl": pd.DataFrame(columns=["je_id", "amount_cents", "source_file", "source_row"]),
            "bank": pd.DataFrame(columns=["bank_txn_id", "amount_cents", "source_file", "source_row"])}

def validate(sources: dict[str, pd.DataFrame]) -> list[str]:
    return []

def reconcile(sources: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {"matched": pd.DataFrame(), "unmatched": pd.DataFrame()}

def write_report(result: dict[str, pd.DataFrame], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return []
```

## 5. Tie-out test skeleton

`tests/test_bank_rec.py`:

```python
import pytest
import bank_rec

def test_pipeline_runs_on_empty_sources(tmp_path):
    sources = bank_rec.load_sources(tmp_path)
    assert bank_rec.validate(sources) == []

@pytest.mark.xfail(reason="Phase 2", strict=True)
def test_reconciliation_difference_is_zero(tmp_path):
    result = bank_rec.reconcile(bank_rec.load_sources(tmp_path))
    assert result["summary"]["difference"] == 0  # KeyError until Phase 2 builds the summary
```

Add `pytest.ini` with `pythonpath = src` so tests import step modules directly.

## 6. First run

```bash
pytest -q tests/
```

Then copy patterns from `examples/bank-rec/` as each phase lands.
