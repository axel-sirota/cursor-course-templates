"""Generate synthetic October 2026 cash data for Northwind Co.

Writes three CSV files into data/raw/ (or --out-dir):

    gl_journal_2026-10.csv     GL journal lines (every JE balances: debits = credits)
    bank_statement_2026-10.csv bank statement lines for the operating account
    balances_2026-10.csv       opening and closing balances (bank statement + GL)

All data is fictional. Seeded, so two runs produce identical bytes.

Three exceptions are planted on purpose so the reconciliation has work to do:
    1. Timing difference: a customer deposit booked on 2026-10-31 that the
       bank credits on 2026-11-02 (deposit in transit).
    2. Bank fee not booked: a 35.00 monthly service fee on the statement
       with no GL entry.
    3. Duplicate GL entry: one vendor payment JE posted twice.

Usage (from the example folder):
    python scripts/generate_data.py
    python scripts/generate_data.py --out-dir /tmp/check
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20261031
PERIOD = "2026-10"
PERIOD_START = date(2026, 10, 1)
LAST_NORMAL_POSTING = date(2026, 10, 27)
PERIOD_END = date(2026, 10, 31)

CASH_ACCOUNT = ("1010", "Cash - Operating")
AR_ACCOUNT = ("1200", "Accounts Receivable")
AP_ACCOUNT = ("2000", "Accounts Payable")

OPENING_BALANCE_CENTS = 25_000_000  # 250,000.00 per September close
NORMAL_TXN_COUNT = 24
DUPLICATE_TXN_INDEX = 7  # which vendor payment gets posted twice (see build_dataset)
IN_TRANSIT_CENTS = 1_275_000  # 12,750.00
BANK_FEE_CENTS = -3_500  # -35.00

CUSTOMERS = [
    "Alder Street Cafe",
    "Bluefin Outfitters",
    "Cedar Hill Clinics",
    "Driftwood Supply",
    "Elm Grove Schools",
    "Foxglove Studios",
]
VENDORS = [
    "Granite Office Leasing",
    "Harbor Freight Lines",
    "Ironwood IT Services",
    "Juniper Utilities",
    "Kestrel Insurance Group",
]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "raw"

GL_FILE = f"gl_journal_{PERIOD}.csv"
BANK_FILE = f"bank_statement_{PERIOD}.csv"
BALANCES_FILE = f"balances_{PERIOD}.csv"

GL_COLUMNS = [
    "je_id",
    "line",
    "posting_date",
    "account",
    "account_name",
    "description",
    "debit",
    "credit",
    "reference",
]
BANK_COLUMNS = ["bank_txn_id", "value_date", "description", "amount", "reference"]
BALANCE_COLUMNS = ["source", "account", "period", "opening_balance", "closing_balance"]


def fmt_cents(cents: int) -> str:
    """Integer cents to a plain decimal string: -3500 -> '-35.00'."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def _business_day(rng: random.Random, start: date, end: date) -> date:
    while True:
        day = start + timedelta(days=rng.randint(0, (end - start).days))
        if day.weekday() < 5:
            return day


def build_transactions(rng: random.Random) -> list[dict]:
    """Normal cash transactions that appear in both the GL and the bank."""
    txns = []
    for i in range(NORMAL_TXN_COUNT):
        posting = _business_day(rng, PERIOD_START, LAST_NORMAL_POSTING)
        clearing_lag = rng.randint(0, 2)
        if i % 2 == 0:
            party = rng.choice(CUSTOMERS)
            cents = rng.randint(50_000, 1_800_000)
            reference = f"DEP-{1001 + i}"
            description = f"Customer receipt {party}"
        else:
            party = rng.choice(VENDORS)
            cents = -rng.randint(25_000, 1_200_000)
            reference = f"ACH-{5001 + i}"
            description = f"Vendor payment {party}"
        txns.append(
            {
                "posting_date": posting,
                "value_date": posting + timedelta(days=clearing_lag),
                "cents": cents,
                "reference": reference,
                "description": description,
            }
        )
    txns.sort(key=lambda t: (t["posting_date"], t["reference"]))
    return txns


def gl_lines_for(je_id: str, txn: dict) -> list[dict]:
    """Two-line JE: cash against AR (receipt) or AP (payment)."""
    cents = txn["cents"]
    offset = AR_ACCOUNT if cents > 0 else AP_ACCOUNT
    amount = fmt_cents(abs(cents))
    zero = "0.00"
    cash_debit, cash_credit = (amount, zero) if cents > 0 else (zero, amount)
    common = {
        "je_id": je_id,
        "posting_date": txn["posting_date"].isoformat(),
        "description": txn["description"],
        "reference": txn["reference"],
    }
    return [
        {**common, "line": "1", "account": CASH_ACCOUNT[0], "account_name": CASH_ACCOUNT[1],
         "debit": cash_debit, "credit": cash_credit},
        {**common, "line": "2", "account": offset[0], "account_name": offset[1],
         "debit": cash_credit, "credit": cash_debit},
    ]


def build_dataset(seed: int = SEED) -> dict[str, list[dict]]:
    rng = random.Random(seed)
    txns = build_transactions(rng)
    payments = [t for t in txns if t["cents"] < 0]
    duplicate_txn = payments[DUPLICATE_TXN_INDEX % len(payments)]

    # Exception 1: deposit booked on the last day, cleared by the bank in November.
    in_transit = {
        "posting_date": PERIOD_END,
        "value_date": PERIOD_END + timedelta(days=2),
        "cents": IN_TRANSIT_CENTS,
        "reference": "DEP-1099",
        "description": f"Customer receipt {CUSTOMERS[2]}",
    }

    gl_rows: list[dict] = []
    je_number = 1

    def next_je() -> str:
        nonlocal je_number
        je_id = f"JE-{PERIOD}-{je_number:04d}"
        je_number += 1
        return je_id

    for txn in txns:
        gl_rows.extend(gl_lines_for(next_je(), txn))
        if txn is duplicate_txn:
            # Exception 3: same payment posted a second time.
            gl_rows.extend(gl_lines_for(next_je(), txn))
    gl_rows.extend(gl_lines_for(next_je(), in_transit))

    bank_rows = [
        {
            "value_date": t["value_date"],
            "description": t["description"].upper(),
            "cents": t["cents"],
            "reference": t["reference"],
        }
        for t in txns
    ]
    # Exception 2: bank fee on the statement, never booked in the GL.
    bank_rows.append(
        {
            "value_date": PERIOD_END,
            "description": "MONTHLY SERVICE FEE",
            "cents": BANK_FEE_CENTS,
            "reference": "",
        }
    )
    bank_rows.sort(key=lambda r: (r["value_date"], r["reference"]))
    bank_out = [
        {
            "bank_txn_id": f"BK-{PERIOD}-{n:04d}",
            "value_date": r["value_date"].isoformat(),
            "description": r["description"],
            "amount": fmt_cents(r["cents"]),
            "reference": r["reference"],
        }
        for n, r in enumerate(bank_rows, start=1)
    ]

    bank_closing = OPENING_BALANCE_CENTS + sum(r["cents"] for r in bank_rows)
    gl_cash_activity = 0
    for row in gl_rows:
        if row["account"] == CASH_ACCOUNT[0]:
            gl_cash_activity += _to_cents(row["debit"]) - _to_cents(row["credit"])
    gl_closing = OPENING_BALANCE_CENTS + gl_cash_activity

    balances = [
        {"source": "bank_statement", "account": CASH_ACCOUNT[0], "period": PERIOD,
         "opening_balance": fmt_cents(OPENING_BALANCE_CENTS),
         "closing_balance": fmt_cents(bank_closing)},
        {"source": "general_ledger", "account": CASH_ACCOUNT[0], "period": PERIOD,
         "opening_balance": fmt_cents(OPENING_BALANCE_CENTS),
         "closing_balance": fmt_cents(gl_closing)},
    ]
    return {GL_FILE: gl_rows, BANK_FILE: bank_out, BALANCES_FILE: balances}


def _to_cents(text: str) -> int:
    whole, _, frac = text.lstrip("-").partition(".")
    cents = int(whole) * 100 + int((frac + "00")[:2])
    return -cents if text.startswith("-") else cents


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row[c] for c in columns})


def generate(out_dir: Path, seed: int = SEED) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    data = build_dataset(seed)
    columns = {GL_FILE: GL_COLUMNS, BANK_FILE: BANK_COLUMNS, BALANCES_FILE: BALANCE_COLUMNS}
    written = []
    for name, rows in data.items():
        path = out_dir / name
        write_csv(path, columns[name], rows)
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    for path in generate(args.out_dir, args.seed):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
