"""Bank reconciliation for Northwind Co. operating cash (account 1010).

Pipeline: Sources -> Validate -> Reconcile -> Tie-out -> Report.

Reads data/raw/ (never writes there). Writes to output/:
    bank_rec_<period>.md          reconciliation report, every number cites its source
    matched_pairs_<period>.csv    GL line <-> bank line pairs
    unmatched_items_<period>.csv  every unmatched item, classified
    proposed_je_<period>.csv      proposed adjusting entries (NOT posted)

Money is held as integer cents (int64). Never float.

Usage (from the example folder):
    python src/reconcile.py
    python src/reconcile.py --raw-dir data/raw --out-dir output
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------- config
# Named settings, stated once. Change them here, never inline.
PERIOD = "2026-10"
PERIOD_END = pd.Timestamp("2026-10-31")
CASH_ACCOUNT = "1010"
BANK_FEE_ACCOUNT = "6110"
TIMING_WINDOW_DAYS = 3  # GL receipts in the last N days may be in transit
MATERIALITY_CENTS = 50_000  # 500.00 per the close plan; items above it are flagged

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "data" / "raw"
DEFAULT_OUT_DIR = ROOT / "output"

GL_FILE = f"gl_journal_{PERIOD}.csv"
BANK_FILE = f"bank_statement_{PERIOD}.csv"
BALANCES_FILE = f"balances_{PERIOD}.csv"

GL_REQUIRED = {"je_id", "line", "posting_date", "account", "description", "debit", "credit", "reference"}
BANK_REQUIRED = {"bank_txn_id", "value_date", "description", "amount", "reference"}
BALANCES_REQUIRED = {"source", "account", "period", "opening_balance", "closing_balance"}

# Unmatched item categories
CAT_DUPLICATE = "possible duplicate GL entry"
CAT_IN_TRANSIT = "deposit in transit (timing)"
CAT_OUTSTANDING = "outstanding payment (timing)"
CAT_BANK_FEE = "bank fee not booked"
CAT_BANK_OTHER = "bank item not booked, investigate"
CAT_GL_OTHER = "GL item not on statement, investigate"


# ---------------------------------------------------------------- money
def to_cents(value: object) -> int:
    """Parse a decimal string into integer cents. Rejects fractions of a cent."""
    text = str(value).strip().replace(",", "")
    if text == "":
        return 0
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"not a money amount: {value!r}") from exc
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"fraction of a cent: {value!r}")
    return int(cents)


def fmt_money(cents: int) -> str:
    """Integer cents to '1,234.56' or '(1,234.56)' for negatives."""
    text = f"{abs(cents) // 100:,}.{abs(cents) % 100:02d}"
    return f"({text})" if cents < 0 else text


# ---------------------------------------------------------------- sources
def _read(path: Path, required: set[str]) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
    df["source_file"] = path.name
    df["source_row"] = range(2, len(df) + 2)  # line number in the file; header is line 1
    return df


def load_gl(path: Path) -> pd.DataFrame:
    df = _read(path, GL_REQUIRED)
    df["posting_date"] = pd.to_datetime(df["posting_date"], format="%Y-%m-%d")
    df["debit_cents"] = df["debit"].map(to_cents).astype("int64")
    df["credit_cents"] = df["credit"].map(to_cents).astype("int64")
    return df


def load_bank(path: Path) -> pd.DataFrame:
    df = _read(path, BANK_REQUIRED)
    df["value_date"] = pd.to_datetime(df["value_date"], format="%Y-%m-%d")
    df["amount_cents"] = df["amount"].map(to_cents).astype("int64")
    return df


def load_balances(path: Path) -> pd.DataFrame:
    df = _read(path, BALANCES_REQUIRED)
    df["opening_cents"] = df["opening_balance"].map(to_cents).astype("int64")
    df["closing_cents"] = df["closing_balance"].map(to_cents).astype("int64")
    return df.set_index("source")


# ---------------------------------------------------------------- validate
def validate(gl: pd.DataFrame, bank: pd.DataFrame, balances: pd.DataFrame) -> list[str]:
    """Return a list of validation failures. Empty list means the sources are usable."""
    problems = []
    by_je = gl.groupby("je_id")[["debit_cents", "credit_cents"]].sum()
    unbalanced = by_je[by_je["debit_cents"] != by_je["credit_cents"]]
    for je_id in unbalanced.index:
        problems.append(f"{GL_FILE}: {je_id} does not balance")
    bank_row = balances.loc["bank_statement"]
    bank_calc = int(bank_row["opening_cents"]) + int(bank["amount_cents"].sum())
    if bank_calc != int(bank_row["closing_cents"]):
        problems.append(
            f"{BANK_FILE}: opening + lines = {fmt_money(bank_calc)}, "
            f"statement closing = {fmt_money(int(bank_row['closing_cents']))}"
        )
    gl_row = balances.loc["general_ledger"]
    cash = gl_cash_lines(gl)
    gl_calc = int(gl_row["opening_cents"]) + int(cash["amount_cents"].sum())
    if gl_calc != int(gl_row["closing_cents"]):
        problems.append(
            f"{GL_FILE}: opening + cash lines = {fmt_money(gl_calc)}, "
            f"ledger closing = {fmt_money(int(gl_row['closing_cents']))}"
        )
    return problems


def gl_cash_lines(gl: pd.DataFrame) -> pd.DataFrame:
    cash = gl[gl["account"] == CASH_ACCOUNT].copy()
    cash["amount_cents"] = (cash["debit_cents"] - cash["credit_cents"]).astype("int64")
    return cash


# ---------------------------------------------------------------- reconcile
@dataclass
class ReconResult:
    gl_cash: pd.DataFrame
    bank: pd.DataFrame
    balances: pd.DataFrame
    matched: pd.DataFrame
    unmatched: pd.DataFrame
    proposed_je: pd.DataFrame
    summary: dict = field(default_factory=dict)


def match_items(gl_cash: pd.DataFrame, bank: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """One-to-one match on (reference, amount). Returns matched, unmatched GL, unmatched bank.

    The nth GL line with a given key pairs with the nth bank line with the same key.
    Extra lines on either side stay unmatched, so a duplicate GL posting surfaces.
    """
    key = ["reference", "amount_cents"]
    g = gl_cash.copy()
    b = bank.copy()
    g["occurrence"] = g.groupby(key).cumcount()
    b["occurrence"] = b.groupby(key).cumcount()
    merged = g.merge(b, on=key + ["occurrence"], how="outer", suffixes=("_gl", "_bank"), indicator=True)
    matched = merged[merged["_merge"] == "both"]
    unmatched_gl_idx = merged.loc[merged["_merge"] == "left_only", "source_row_gl"].astype("int64")
    unmatched_bank_idx = merged.loc[merged["_merge"] == "right_only", "source_row_bank"].astype("int64")
    unmatched_gl = g[g["source_row"].isin(unmatched_gl_idx)]
    unmatched_bank = b[b["source_row"].isin(unmatched_bank_idx)]
    return matched, unmatched_gl, unmatched_bank


def classify(unmatched_gl: pd.DataFrame, unmatched_bank: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    matched_keys = set(zip(matched["reference"], matched["amount_cents"]))
    rows = []
    for r in unmatched_gl.itertuples():
        if (r.reference, r.amount_cents) in matched_keys:
            category = CAT_DUPLICATE
        elif r.amount_cents > 0 and (PERIOD_END - r.posting_date).days < TIMING_WINDOW_DAYS:
            category = CAT_IN_TRANSIT
        elif r.amount_cents < 0:
            category = CAT_OUTSTANDING
        else:
            category = CAT_GL_OTHER
        rows.append(
            {"side": "GL", "category": category, "item_id": r.je_id, "date": r.posting_date.date().isoformat(),
             "description": r.description, "reference": r.reference, "amount_cents": int(r.amount_cents),
             "source_file": r.source_file, "source_row": int(r.source_row)}
        )
    for r in unmatched_bank.itertuples():
        category = CAT_BANK_FEE if r.amount_cents < 0 and "FEE" in r.description.upper() else CAT_BANK_OTHER
        rows.append(
            {"side": "bank", "category": category, "item_id": r.bank_txn_id, "date": r.value_date.date().isoformat(),
             "description": r.description, "reference": r.reference, "amount_cents": int(r.amount_cents),
             "source_file": r.source_file, "source_row": int(r.source_row)}
        )
    df = pd.DataFrame(rows, columns=["side", "category", "item_id", "date", "description", "reference",
                                     "amount_cents", "source_file", "source_row"])
    df["amount_cents"] = df["amount_cents"].astype("int64")
    df["above_materiality"] = df["amount_cents"].abs() > MATERIALITY_CENTS
    return df


def propose_entries(unmatched: pd.DataFrame) -> pd.DataFrame:
    """Draft adjusting entries for book-side items. These are proposals, never posted."""
    rows = []
    n = 1
    for r in unmatched.itertuples():
        if r.category == CAT_BANK_FEE:
            amount = -r.amount_cents
            lines = [(BANK_FEE_ACCOUNT, amount, 0), (CASH_ACCOUNT, 0, amount)]
            memo = f"Book bank service fee per {r.source_file} row {r.source_row}"
        elif r.category == CAT_DUPLICATE:
            # Reverse the duplicate cash line; the offset goes back to AP / AR.
            offset = "2000" if r.amount_cents < 0 else "1200"
            amount = abs(r.amount_cents)
            if r.amount_cents < 0:
                lines = [(CASH_ACCOUNT, amount, 0), (offset, 0, amount)]
            else:
                lines = [(offset, amount, 0), (CASH_ACCOUNT, 0, amount)]
            memo = f"Reverse duplicate {r.item_id} per {r.source_file} row {r.source_row}"
        else:
            continue
        for line_no, (account, debit, credit) in enumerate(lines, start=1):
            rows.append({"proposed_je": f"PJE-{PERIOD}-{n:02d}", "line": line_no, "account": account,
                         "debit_cents": debit, "credit_cents": credit, "memo": memo,
                         "status": "PROPOSED - NOT POSTED"})
        n += 1
    return pd.DataFrame(rows, columns=["proposed_je", "line", "account", "debit_cents", "credit_cents",
                                       "memo", "status"])


def reconcile(raw_dir: Path) -> ReconResult:
    gl = load_gl(raw_dir / GL_FILE)
    bank = load_bank(raw_dir / BANK_FILE)
    balances = load_balances(raw_dir / BALANCES_FILE)
    problems = validate(gl, bank, balances)
    if problems:
        raise ValueError("source validation failed:\n" + "\n".join(problems))

    gl_cash = gl_cash_lines(gl)
    matched, unmatched_gl, unmatched_bank = match_items(gl_cash, bank)
    unmatched = classify(unmatched_gl, unmatched_bank, matched)
    proposed = propose_entries(unmatched)

    def total(category: str) -> int:
        return int(unmatched.loc[unmatched["category"] == category, "amount_cents"].sum())

    bank_closing = int(balances.loc["bank_statement", "closing_cents"])
    book_closing = int(balances.loc["general_ledger", "closing_cents"])
    in_transit = total(CAT_IN_TRANSIT)
    outstanding = total(CAT_OUTSTANDING)
    bank_only = int(unmatched.loc[unmatched["side"] == "bank", "amount_cents"].sum())
    duplicates = total(CAT_DUPLICATE)
    gl_other = total(CAT_GL_OTHER)

    adjusted_bank = bank_closing + in_transit + outstanding + gl_other
    adjusted_book = book_closing + bank_only - duplicates
    summary = {
        "bank_closing": bank_closing,
        "book_closing": book_closing,
        "deposits_in_transit": in_transit,
        "outstanding_payments": outstanding,
        "gl_items_to_investigate": gl_other,
        "bank_items_not_booked": bank_only,
        "duplicate_gl_entries": duplicates,
        "adjusted_bank": adjusted_bank,
        "adjusted_book": adjusted_book,
        "difference": adjusted_bank - adjusted_book,
        "gl_cash_lines": len(gl_cash),
        "bank_lines": len(bank),
        "matched_pairs": len(matched),
        "unmatched_items": len(unmatched),
    }
    return ReconResult(gl_cash, bank, balances, matched, unmatched, proposed, summary)


# ---------------------------------------------------------------- report
def _cite(balances: pd.DataFrame, source: str) -> str:
    return f"{BALANCES_FILE} row {int(balances.loc[source, 'source_row'])}"


def render_report(result: ReconResult) -> str:
    s = result.summary
    u = result.unmatched
    lines = [
        f"# Bank reconciliation: Northwind Co. cash {CASH_ACCOUNT}, period {PERIOD}",
        "",
        f"Materiality threshold: {fmt_money(MATERIALITY_CENTS)} (from the close plan).",
        "Synthetic data. Proposed entries are NOT posted.",
        "",
        "## Reconciliation",
        "",
        "| Line | Amount | Source / formula |",
        "|---|---:|---|",
        f"| Balance per bank statement | {fmt_money(s['bank_closing'])} | {_cite(result.balances, 'bank_statement')} |",
        f"| Add: deposits in transit | {fmt_money(s['deposits_in_transit'])} | unmatched_items: category = '{CAT_IN_TRANSIT}' |",
        f"| Less: outstanding payments | {fmt_money(s['outstanding_payments'])} | unmatched_items: category = '{CAT_OUTSTANDING}' |",
        f"| GL items to investigate | {fmt_money(s['gl_items_to_investigate'])} | unmatched_items: category = '{CAT_GL_OTHER}' |",
        f"| **Adjusted bank balance** | **{fmt_money(s['adjusted_bank'])}** | sum of the four lines above |",
        f"| Balance per GL | {fmt_money(s['book_closing'])} | {_cite(result.balances, 'general_ledger')} |",
        f"| Add/less: bank items not booked | {fmt_money(s['bank_items_not_booked'])} | unmatched_items: side = 'bank' |",
        f"| Reverse: duplicate GL entries | {fmt_money(-s['duplicate_gl_entries'])} | unmatched_items: category = '{CAT_DUPLICATE}', sign reversed |",
        f"| **Adjusted book balance** | **{fmt_money(s['adjusted_book'])}** | sum of the three lines above |",
        f"| **Difference** | **{fmt_money(s['difference'])}** | adjusted bank - adjusted book; must be 0.00 |",
        "",
        "## Tie-out",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| GL cash lines = matched + unmatched GL | {s['gl_cash_lines']} = {s['matched_pairs']} + {int((u['side'] == 'GL').sum())} |",
        f"| Bank lines = matched + unmatched bank | {s['bank_lines']} = {s['matched_pairs']} + {int((u['side'] == 'bank').sum())} |",
        f"| Difference is zero | {'PASS' if s['difference'] == 0 else 'FAIL'} |",
        "",
        "## Unmatched items",
        "",
        "| Side | Category | Item | Date | Amount | Above materiality | Source |",
        "|---|---|---|---|---:|---|---|",
    ]
    for r in u.itertuples():
        lines.append(
            f"| {r.side} | {r.category} | {r.item_id} | {r.date} | {fmt_money(r.amount_cents)} | "
            f"{'yes' if r.above_materiality else 'no'} | {r.source_file} row {r.source_row} |"
        )
    lines += ["", "## Proposed entries (not posted)", ""]
    if result.proposed_je.empty:
        lines.append("None.")
    else:
        lines += ["| Proposed JE | Line | Account | Debit | Credit | Memo |", "|---|---|---|---:|---:|---|"]
        for r in result.proposed_je.itertuples():
            lines.append(
                f"| {r.proposed_je} | {r.line} | {r.account} | {fmt_money(r.debit_cents)} | "
                f"{fmt_money(r.credit_cents)} | {r.memo} |"
            )
    return "\n".join(lines) + "\n"


def write_outputs(result: ReconResult, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "report": out_dir / f"bank_rec_{PERIOD}.md",
        "matched": out_dir / f"matched_pairs_{PERIOD}.csv",
        "unmatched": out_dir / f"unmatched_items_{PERIOD}.csv",
        "proposed": out_dir / f"proposed_je_{PERIOD}.csv",
    }
    paths["report"].write_text(render_report(result), encoding="utf-8")
    matched_cols = ["reference", "amount_cents", "je_id", "posting_date", "source_file_gl", "source_row_gl",
                    "bank_txn_id", "value_date", "source_file_bank", "source_row_bank"]
    result.matched[matched_cols].to_csv(paths["matched"], index=False, date_format="%Y-%m-%d")
    result.unmatched.to_csv(paths["unmatched"], index=False)
    result.proposed_je.to_csv(paths["proposed"], index=False)
    return list(paths.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="Northwind Co. bank reconciliation")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    result = reconcile(args.raw_dir)
    for path in write_outputs(result, args.out_dir):
        print(f"wrote {path}")
    print(f"difference: {fmt_money(result.summary['difference'])}")


if __name__ == "__main__":
    main()
