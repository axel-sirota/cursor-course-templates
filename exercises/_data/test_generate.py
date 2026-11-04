#!/usr/bin/env python3
"""Self-check for the Northwind generator. No pytest needed.

    python3 exercises/_data/test_generate.py

Checks: determinism, committed files match a fresh run, row counts, every JE balances,
seeded anomalies are present (recomputed from the CSVs, independent of the generator),
bank rec ties to 0, the 2150 accrual tie-out and the budget variance classes.
"""
import csv
import datetime as dt
import importlib.util
import io
import json
import os
import sys
import tempfile

sys.dont_write_bytecode = True  # keep __pycache__ out of exercises/_data
HERE = os.path.dirname(os.path.abspath(__file__))
spec =importlib.util.spec_from_file_location("nw_generate", os.path.join(HERE, "generate.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail and not cond else ''}")


def read_csv(folder, name):
    with open(os.path.join(folder, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def snapshot(folder):
    out = {}
    for name in sorted(os.listdir(folder)):
        with open(os.path.join(folder, name), "rb") as f:
            out[name] = f.read()
    return out


def run_into(folder):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        gen.main(["--out", folder, "--readme", os.path.join(folder, "README.md")])
    finally:
        sys.stdout = old


def main():
    with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
        run_into(t1)
        run_into(t2)
        s1, s2 = snapshot(t1), snapshot(t2)
        check("determinism: two runs with seed 2026 are byte-identical", s1 == s2,
              str([k for k in s1 if s1.get(k) != s2.get(k)]))
        committed = os.path.join(HERE, "northwind")
        if os.path.isdir(committed):
            c = snapshot(committed)
            fresh = {k: v for k, v in s1.items() if k != "README.md"}
            check("committed northwind/ matches a fresh run", c == fresh,
                  str(sorted(set(c) ^ set(fresh)) + [k for k in c if c.get(k) != fresh.get(k)]))
            with open(os.path.join(HERE, "README.md"), "rb") as f:
                check("committed README.md matches a fresh run", f.read() == s1["README.md"])
        else:
            check("committed northwind/ exists", False)
        verify(t1)
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


def verify(d):
    key = json.load(open(os.path.join(d, "answer_key.json"), encoding="utf-8"))
    emps = read_csv(d, "employees.csv")
    claims = read_csv(d, "expense_claims.csv")
    lines = read_csv(d, "expense_lines.csv")
    gl = read_csv(d, "gl_journal.csv")
    bank = read_csv(d, "bank_statement_2026-10.csv")
    payouts = read_csv(d, "payouts_2026-10.csv")
    budget = read_csv(d, "budget_2026.csv")
    tickets = read_csv(d, "support_tickets.csv")
    accts = read_csv(d, "gl_accounts.csv")

    # row counts
    check("employees ~120", len(emps) == 120, str(len(emps)))
    check("claims ~4000", 3900 <= len(claims) <= 4100, str(len(claims)))
    check("lines ~9000", 8500 <= len(lines) <= 9800, str(len(lines)))
    check("gl accounts ~40", 38 <= len(accts) <= 50, str(len(accts)))
    check("support tickets ~60", len(tickets) == 60, str(len(tickets)))
    check("usage metrics 8 features", len(read_csv(d, "usage_metrics.csv")) == 8)
    check("budget covers Aug to Dec", sorted({r["month"] for r in budget}) ==
          ["2026-08", "2026-09", "2026-10", "2026-11", "2026-12"])
    for name in ("expense_policy.json", "je_policy.json", "context_notes_2026-10.md", "interview_notes.md"):
        check(f"{name} present", os.path.getsize(os.path.join(d, name)) > 200)

    # every JE balances
    tot = {}
    for r in gl:
        t = tot.setdefault(r["je_id"], [0, 0])
        t[0] += int(r["debit_cents"])
        t[1] += int(r["credit_cents"])
    bad = [k for k, (a, b) in tot.items() if a != b]
    check(f"all {len(tot)} JEs balance (debits = credits)", not bad, str(bad[:5]))

    # claim totals = sum of lines; claim and line joins
    claim_by_id = {c["claim_id"]: c for c in claims}
    sums = {}
    for ln in lines:
        sums[ln["claim_id"]] = sums.get(ln["claim_id"], 0) + int(ln["amount_cents"])
    check("claim total_cents = sum of line amount_cents",
          all(sums.get(c["claim_id"], 0) == int(c["total_cents"]) for c in claims))
    check("every line joins a claim", all(ln["claim_id"] in claim_by_id for ln in lines))
    emp_by_id = {e["employee_id"]: e for e in emps}
    check("every claim joins an employee", all(c["employee_id"] in emp_by_id for c in claims))

    # --- independent anomaly recomputation ---------------------------------
    EL = key["expense_lines"]
    groups = {}
    for ln in lines:
        k = (claim_by_id[ln["claim_id"]]["employee_id"], ln["merchant"], ln["expense_date"], ln["amount_cents"],
             ln["currency"])
        groups.setdefault(k, []).append(ln)
    exact = sorted((g[0]["line_id"], g[1]["line_id"]) for g in groups.values()
                   if len(g) >= 2 and len({x["claim_id"] for x in g}) >= 2)
    want = sorted((x["original_line_id"], x["duplicate_line_id"]) for x in EL["exact_duplicates"])
    check(f"exact duplicate lines present ({len(want)})", exact == want and len(want) >= 80)
    check(f"near duplicates listed ({len(EL['near_duplicates'])})", len(EL["near_duplicates"]) >= 40)
    weekend = sorted(ln["line_id"] for ln in lines
                     if dt.date.fromisoformat(ln["expense_date"]).weekday() >= 5)
    check(f"weekend lines present ({len(weekend)})",
          weekend == sorted(x["line_id"] for x in EL["weekend_expenses"]) and weekend)
    check("missing category lines present", sorted(ln["line_id"] for ln in lines if ln["category"] == "") ==
          sorted(x["line_id"] for x in EL["missing_category"]) and EL["missing_category"])
    mixed = sorted(ln["line_id"] for ln in lines if ln["currency"] != claim_by_id[ln["claim_id"]]["currency"])
    check("3 mixed currency lines, claims without fx_rate",
          len(mixed) == 3 and mixed == sorted(x["line_id"] for x in EL["mixed_currency_without_fx"]) and
          sorted(c["claim_id"] for c in claims if c["fx_rate"] == "") == EL["claims_missing_fx_rate"])
    out = [ln for ln in lines if ln["category"] == "Office supplies" and int(ln["amount_cents"]) == 980000]
    check("$9,800 office supplies outlier present", len(out) == 1 and out[0]["line_id"] == EL["outliers"][0]["line_id"])
    hint_map = {}
    for ln in lines:
        hint_map.setdefault(ln["category"], set()).add(ln["gl_account_hint"])
    check("leakage: gl_account_hint maps 1:1 to category", all(len(v) == 1 for v in hint_map.values()) and
          len({next(iter(v)) for v in hint_map.values()}) == len(hint_map))
    alc = sorted(ln["line_id"] for ln in lines if ln["category"] == "Meals" and
                 any(w in ln["description"].lower() for w in gen.ALCOHOL_KEYWORDS))
    check(f"alcohol lines in Meals ({len(alc)})", alc == sorted(x["line_id"] for x in EL["alcohol_in_meals"]) and alc)
    check("split groups present (6)", len(EL["split_under_receipt_threshold"]) == 6 and
          all(all(6000 <= a < 7500 for a in g["amounts_cents"]) and g["total_cents"] > 7500
              for g in EL["split_under_receipt_threshold"]))
    sa = sorted(c["claim_id"] for c in claims if c["approver_id"] and c["approver_id"] == c["employee_id"])
    check("5 self-approved claims", len(sa) == 5 and sa == [x["claim_id"] for x in key["expense_claims"]["self_approved"]])
    al = [x for x in key["expense_claims"]["approved_above_limit"]]
    ok = len(al) == 5 and all(int(emp_by_id[claim_by_id[x["claim_id"]]["approver_id"]]["approval_limit_cents"]) <
                              x["total_usd_cents"] for x in al)
    check("5 claims approved above approver limit", ok)

    # JE tests
    G = key["gl_journal"]
    je_first = {}
    for r in gl:
        je_first.setdefault(r["je_id"], r)
    hol = {"2026-09-07", "2026-10-12"}
    wk = sorted(k for k, r in je_first.items() if dt.date.fromisoformat(r["posting_date"]).weekday() >= 5
                or r["posting_date"] in hol)
    check(f"weekend/holiday JEs ({len(wk)})", wk == [x["je_id"] for x in G["weekend_or_holiday"]] and wk)
    pc = sorted(k for k, r in je_first.items() if r["period"] == "2026-10" and r["entry_date"] > "2026-11-05")
    check(f"post-close JEs ({len(pc)})", pc == [x["je_id"] for x in G["post_close"]] and pc)
    fin = {e["employee_id"] for e in emps if e["department"] == "Finance"} | {"SVC-GL", "SVC-EXPENSE"}
    npost = sorted(k for k, r in je_first.items() if r["preparer_id"] not in fin)
    check(f"JEs by people who never post ({len(npost)})", npost == [x["je_id"] for x in G["preparer_never_posts"]] and npost)
    rnd = sorted({r["je_id"] for r in gl if r["source"] == "MANUAL" and
                  max(int(r["debit_cents"]), int(r["credit_cents"])) % 100000 == 0})
    check(f"round-amount manual JEs ({len(rnd)})", rnd == [x["je_id"] for x in G["round_amount_manual"]] and rnd)
    ju = sorted(k for k, (a, _) in tot.items() if je_first[k]["source"] == "MANUAL" and 950000 <= a < 1000000)
    check(f"just-under-limit JEs ({len(ju)})", ju == [x["je_id"] for x in G["just_under_approval_limit"]] and ju)
    selfje = sorted(k for k, r in je_first.items() if r["approver_id"] and r["approver_id"] == r["preparer_id"])
    check(f"self-approved manual JEs ({len(selfje)})", selfje == [x["je_id"] for x in G["self_approved_manual"]] and selfje)
    use = {}
    for r in gl:
        use.setdefault(r["account"], set()).add(r["je_id"])
    seldom = sorted(a for a, s in use.items() if len(s) <= 2)
    check("seldom-used accounts", seldom == G["seldom_used_accounts"] and seldom, str(seldom))
    sig = {}
    for k in tot:
        pass
    by_je = {}
    for r in gl:
        by_je.setdefault(r["je_id"], []).append((r["account"], r["cost_center"], r["debit_cents"], r["credit_cents"]))
    for k, ls in by_je.items():
        r = je_first[k]
        sig.setdefault((r["entity"], r["posting_date"], r["description"], tuple(sorted(ls))), []).append(k)
    dups = sorted(tuple(v) for v in sig.values() if len(v) > 1)
    check(f"duplicate JEs ({len(dups)})", [list(x) for x in dups] ==
          [[x["original_je_id"], x["duplicate_je_id"]] for x in G["duplicate_entries"]] and dups)
    ic_ca = {r["description"].split()[4] for r in gl if r["entity"] == "NW-CA" and r["account"] == "2310"}
    ic_us = sorted(r["je_id"] for r in gl if r["entity"] == "NW-US" and r["account"] == "1310"
                   and r["description"].split()[4] not in ic_ca)
    check("1 intercompany entry without NW-CA offset", ic_us == [x["je_id"] for x in G["intercompany_unmatched"]]
          and len(ic_us) == 1)

    # bank rec
    B = key["bank_rec_2026_10"]
    bal = {r["metric"]: int(r["amount_cents"]) for r in read_csv(d, "gl_balance_1010_2026-10.csv")}
    gl1010 = bal["gl_1010_opening_2026-10-01"] + sum(int(r["debit_cents"]) - int(r["credit_cents"]) for r in gl
                                                       if r["account"] == "1010" and r["period"] == "2026-10"
                                                       and r["entity"] == "NW-US")
    check("GL 1010 closing recomputes", gl1010 == bal["gl_1010_closing_2026-10-31"])
    bank_close = bal["bank_opening_2026-10-01"] + sum(int(r["amount_cents"]) for r in bank)
    check("bank running balance ties", bank_close == bal["bank_closing_2026-10-31"] ==
          int(bank[-1]["balance_cents"]))
    adj_bank = bank_close + sum(x["amount_cents"] for x in B["deposits_in_transit"]) - \
        sum(x["amount_cents"] for x in B["outstanding_payments"])
    adj_book = gl1010 + B["bank_fee_not_booked"]["amount_cents"] + B["interest_not_booked"]["amount_cents"] + \
        B["gl_duplicate_payment"]["amount_cents"] + B["transposition"]["difference_cents"]
    check("bank rec ties to 0.00 after documented items", adj_bank == adj_book)
    check("bank rec item counts (2 DIT, 3 outstanding)", len(B["deposits_in_transit"]) == 2 and
          len(B["outstanding_payments"]) == 3)
    check("transposition is 1,243.56 vs 1,234.56", B["transposition"]["gl_amount_cents"] == 124356 and
          B["transposition"]["bank_amount_cents"] == 123456)

    # accrual
    A = key["accrual_2150"]
    usd = {}
    rate = {c["claim_id"]: c["fx_rate"] for c in claims}
    for ln in lines:
        if rate[ln["claim_id"]]:
            usd[ln["claim_id"]] = usd.get(ln["claim_id"], 0) + gen.to_usd(int(ln["amount_cents"]), rate[ln["claim_id"]])
    accr = sum(usd[c["claim_id"]] for c in claims if c["status"] == "approved")
    check("expected accrual = approved unpaid claims in USD", accr == A["expected_accrual_cents"])
    ob = {(r["entity"], r["account"]): int(r["balance_cents"]) for r in read_csv(d, "gl_opening_balances_2026-09-01.csv")}
    g2150 = -(ob[("NW-US", "2150")] + sum(int(r["debit_cents"]) - int(r["credit_cents"]) for r in gl
                                         if r["account"] == "2150"))
    check("GL 2150 balance matches answer key", g2150 == A["gl_2150_credit_balance_cents"])
    check("accrual gap = duplicate payment + transposition",
          accr - g2150 == B["gl_duplicate_payment"]["amount_cents"] + B["transposition"]["difference_cents"])
    po_ok = all(usd[p["claim_id"]] == int(p["amount_cents"]) and claim_by_id[p["claim_id"]]["status"] == "paid"
                for p in payouts)
    check("payouts tie to paid claims", po_ok and payouts)
    for name, side in (("opening balances sum to 0 per entity", None),):
        ents = {}
        for (e, _), v in ob.items():
            ents[e] = ents.get(e, 0) + v
        check(name, all(v == 0 for v in ents.values()))

    # budget variance classes
    act = {}
    for r in gl:
        if r["account"].startswith("6"):
            k = (r["account"], r["period"])
            act[k] = act.get(k, 0) + int(r["debit_cents"]) - int(r["credit_cents"])
    bud = {}
    for r in budget:
        if r["month"] == "2026-10":
            bud[r["account"]] = bud.get(r["account"], 0) + int(r["budget_cents"])
    counts = {}
    for a, b in bud.items():
        o, s = act.get((a, "2026-10"), 0), act.get((a, "2026-09"), 0)
        cls = set()
        for base in (b, s):
            diff = o - base
            cls.add((abs(diff) > 1_000_000, abs(diff) > 0.10 * abs(base)))
        check(f"account {a} same class vs budget and vs Sep", len(cls) == 1)
        c = {(True, True): "both", (False, True): "pct_only", (True, False): "dollar_only",
             (False, False): "under"}[cls.pop()]
        counts[c] = counts.get(c, 0) + 1
    check("variance classes 4 both / 3 pct-only / 2 dollar-only", counts.get("both") == 4 and
          counts.get("pct_only") == 3 and counts.get("dollar_only") == 2, str(counts))

    # writing rules
    banned = ["—", "delve", "leverage", "robust", "seamless", "unlock", "elevate", "empower", "harness",
              "game-changer", "cutting-edge", "transformative"]
    text = open(os.path.join(d, "README.md"), encoding="utf-8").read().lower()
    for name in ("context_notes_2026-10.md", "interview_notes.md"):
        text += open(os.path.join(d, name), encoding="utf-8").read().lower()
    hits = [w for w in banned if w in text]
    check("no em dashes or banned words in prose", not hits, str(hits))
    total = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d))
    check(f"total size under 5 MB ({total:,} bytes)", total < 5_000_000)


if __name__ == "__main__":
    raise SystemExit(main())
