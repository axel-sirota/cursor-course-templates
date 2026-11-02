"""Tie-out tests for the Northwind Co. bank reconciliation.

Each test generates fresh synthetic data into a temp folder, so the suite never
reads or writes the real data/raw/ folder.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

import generate_data
import reconcile


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    raw = tmp_path / "data" / "raw"
    generate_data.generate(raw)
    return raw


@pytest.fixture
def result(raw_dir: Path) -> reconcile.ReconResult:
    return reconcile.reconcile(raw_dir)


def _hashes(folder: Path) -> dict[str, str]:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir())}


# ---------------------------------------------------------------- sources
def test_generator_is_seeded(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    generate_data.generate(first)
    generate_data.generate(second)
    assert _hashes(first) == _hashes(second)


def test_every_je_balances_debits_equal_credits(raw_dir: Path) -> None:
    gl = reconcile.load_gl(raw_dir / reconcile.GL_FILE)
    by_je = gl.groupby("je_id")[["debit_cents", "credit_cents"]].sum()
    assert (by_je["debit_cents"] == by_je["credit_cents"]).all()
    assert gl["debit_cents"].sum() == gl["credit_cents"].sum()


def test_bank_lines_tie_to_statement_closing(raw_dir: Path) -> None:
    bank = reconcile.load_bank(raw_dir / reconcile.BANK_FILE)
    bal = reconcile.load_balances(raw_dir / reconcile.BALANCES_FILE).loc["bank_statement"]
    assert bal["opening_cents"] + bank["amount_cents"].sum() == bal["closing_cents"]


def test_gl_cash_lines_tie_to_ledger_closing(raw_dir: Path) -> None:
    gl = reconcile.load_gl(raw_dir / reconcile.GL_FILE)
    cash = reconcile.gl_cash_lines(gl)
    bal = reconcile.load_balances(raw_dir / reconcile.BALANCES_FILE).loc["general_ledger"]
    assert bal["opening_cents"] + cash["amount_cents"].sum() == bal["closing_cents"]


# ---------------------------------------------------------------- reconcile
def test_matched_plus_unmatched_equals_source_totals(result: reconcile.ReconResult) -> None:
    u = result.unmatched
    gl_unmatched = u[u["side"] == "GL"]
    bank_unmatched = u[u["side"] == "bank"]
    # Row counts
    assert len(result.matched) + len(gl_unmatched) == len(result.gl_cash)
    assert len(result.matched) + len(bank_unmatched) == len(result.bank)
    # Amounts in cents
    matched_cents = result.matched["amount_cents"].sum()
    assert matched_cents + gl_unmatched["amount_cents"].sum() == result.gl_cash["amount_cents"].sum()
    assert matched_cents + bank_unmatched["amount_cents"].sum() == result.bank["amount_cents"].sum()


def test_every_unmatched_source_row_is_listed(result: reconcile.ReconResult) -> None:
    matched_gl_rows = set(result.matched["source_row_gl"].astype(int))
    matched_bank_rows = set(result.matched["source_row_bank"].astype(int))
    expected_gl = set(result.gl_cash["source_row"]) - matched_gl_rows
    expected_bank = set(result.bank["source_row"]) - matched_bank_rows
    u = result.unmatched
    assert set(u.loc[u["side"] == "GL", "source_row"]) == expected_gl
    assert set(u.loc[u["side"] == "bank", "source_row"]) == expected_bank


def test_seeded_exceptions_are_classified(result: reconcile.ReconResult) -> None:
    by_cat = result.unmatched.groupby("category")["amount_cents"].agg(["count", "sum"])
    assert by_cat.loc[reconcile.CAT_IN_TRANSIT, "count"] == 1
    assert by_cat.loc[reconcile.CAT_IN_TRANSIT, "sum"] == generate_data.IN_TRANSIT_CENTS
    assert by_cat.loc[reconcile.CAT_BANK_FEE, "count"] == 1
    assert by_cat.loc[reconcile.CAT_BANK_FEE, "sum"] == generate_data.BANK_FEE_CENTS
    assert by_cat.loc[reconcile.CAT_DUPLICATE, "count"] == 1
    assert len(result.unmatched) == 3


def test_reconciliation_difference_is_zero(result: reconcile.ReconResult) -> None:
    assert result.summary["difference"] == 0
    assert result.summary["adjusted_bank"] == result.summary["adjusted_book"]


def test_proposed_entries_balance(result: reconcile.ReconResult) -> None:
    pje = result.proposed_je
    by_je = pje.groupby("proposed_je")[["debit_cents", "credit_cents"]].sum()
    assert (by_je["debit_cents"] == by_je["credit_cents"]).all()
    assert (pje["status"] == "PROPOSED - NOT POSTED").all()


# ---------------------------------------------------------------- outputs
def test_outputs_cite_source_file_and_row(result: reconcile.ReconResult, tmp_path: Path) -> None:
    out = tmp_path / "output"
    reconcile.write_outputs(result, out)
    unmatched = pd.read_csv(out / f"unmatched_items_{reconcile.PERIOD}.csv", dtype={"source_row": "int64"})
    assert unmatched["source_file"].ne("").all()
    assert (unmatched["source_row"] >= 2).all()
    report = (out / f"bank_rec_{reconcile.PERIOD}.md").read_text(encoding="utf-8")
    assert "**Difference** | **0.00**" in report
    for r in result.unmatched.itertuples():
        assert f"{r.source_file} row {r.source_row}" in report


def test_raw_files_are_not_modified(raw_dir: Path, tmp_path: Path) -> None:
    before = _hashes(raw_dir)
    reconcile.write_outputs(reconcile.reconcile(raw_dir), tmp_path / "output")
    assert _hashes(raw_dir) == before


def test_unbalanced_source_is_rejected(raw_dir: Path) -> None:
    path = raw_dir / reconcile.GL_FILE
    gl = pd.read_csv(path, dtype=str, keep_default_na=False)
    gl.loc[0, "debit"] = "1.00" if gl.loc[0, "debit"] == "0.00" else "0.00"
    gl.to_csv(path, index=False)
    with pytest.raises(ValueError, match="does not balance"):
        reconcile.reconcile(raw_dir)


# ---------------------------------------------------------------- money
@pytest.mark.parametrize("text, cents", [("1234.56", 123456), ("-35.00", -3500), ("1,000.10", 100010), ("", 0)])
def test_to_cents_parses_exact_amounts(text: str, cents: int) -> None:
    assert reconcile.to_cents(text) == cents


def test_to_cents_rejects_fraction_of_a_cent() -> None:
    with pytest.raises(ValueError):
        reconcile.to_cents("10.005")
