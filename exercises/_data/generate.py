#!/usr/bin/env python3
"""Northwind Co. synthetic data generator (expense claims and reimbursement).

One seeded generator feeds every persona exercise (engineer, pm, designer,
data-scientist, accountant) so the numbers agree across personas.

Stdlib only. Deterministic: the same --seed always produces byte-identical files.

Usage:
    python3 exercises/_data/generate.py                    # writes exercises/_data/northwind/ + README.md
    python3 exercises/_data/generate.py --seed 7 --out /tmp/nw
    python3 exercises/_data/generate.py --only gl_journal

Everything is fictional: Northwind Co., its people, merchants, vendors and customers.
Merchant descriptor strings imitate card statement text but name invented merchants.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import random
from decimal import ROUND_HALF_UP, Decimal

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(SCRIPT_DIR, "northwind")
DEFAULT_README = os.path.join(SCRIPT_DIR, "README.md")

D = dt.date
ONE = dt.timedelta(days=1)
CLAIMS_START = D(2026, 8, 1)
AS_OF = D(2026, 10, 31)          # claims snapshot: end of day Oct 31 2026
GL_START = D(2026, 9, 1)
SEP_CLOSE = D(2026, 10, 6)       # 4th business day after Sep month end
OCT_CLOSE = D(2026, 11, 5)       # 4th business day after Oct month end
GL_EXTRACT = D(2026, 11, 12)     # GL extract date (after the late entries)
HOLIDAYS = {D(2026, 9, 7): "Labor Day", D(2026, 10, 12): "Indigenous Peoples' Day"}
SEP, OCT = "2026-09", "2026-10"

N_CLAIMS = 4000
N_DRAFTS = 110
THRESH_DOLLAR = 1_000_000   # $10,000.00 flux threshold
THRESH_PCT = 0.10
JE_APPROVAL_LIMIT = 1_000_000   # MANUAL JEs of $10,000.00 or more need the Controller

# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------


def is_bd(d):
    return d.weekday() < 5 and d not in HOLIDAYS


def add_bd(d, n):
    while n > 0:
        d += ONE
        if is_bd(d):
            n -= 1
    return d


def roll_fwd(d):
    while not is_bd(d):
        d += ONE
    return d


def prev_weekday(d):
    while d.weekday() >= 5:
        d -= ONE
    return d


def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += ONE


def period_of(d):
    return f"{d.year}-{d.month:02d}"


def to_usd(cents, rate):
    return int((Decimal(cents) * Decimal(rate)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def from_usd(usd, rate):
    return int((Decimal(usd) / Decimal(rate)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def money(c):
    sign = "-" if c < 0 else ""
    c = abs(c)
    return f"{sign}${c // 100:,}.{c % 100:02d}"


def fmt_dt(x):
    return x.strftime("%Y-%m-%dT%H:%M:%S")


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def split_parts(total, n, rng):
    shares = [rng.uniform(0.7, 1.3) for _ in range(n)]
    s = sum(shares)
    parts = [int(total * x / s) for x in shares[:-1]]
    parts.append(total - sum(parts))
    return parts


def split_by_weights(total, weights):
    keys = sorted(k for k, v in weights.items() if v > 0)
    wsum = sum(weights[k] for k in keys)
    out = []
    acc = 0
    for k in keys[:-1]:
        part = total * weights[k] // wsum
        out.append((k, part))
        acc += part
    out.append((keys[-1], total - acc))
    return out


def first_thursday_on_or_after(d):
    return d + dt.timedelta(days=(3 - d.weekday()) % 7)


# ----------------------------------------------------------------------------
# reference data
# ----------------------------------------------------------------------------

FIRST_NAMES = ["Avery", "Blake", "Casey", "Dana", "Elliot", "Finley", "Gray", "Harper", "Indy",
               "Jordan", "Kai", "Logan", "Morgan", "Noel", "Oakley", "Parker", "Quinn", "Reese",
               "Sage", "Taylor", "Umi", "Vale", "Wren", "Xen", "Yael", "Zion", "Arden", "Briar",
               "Cove", "Dell", "Ember", "Fern", "Glen", "Hollis", "Ira", "Jules", "Kit", "Lark",
               "Marlo", "Nova"]
LAST_NAMES = ["Ashdown", "Brightwater", "Copperfield", "Dunmore", "Eastlake", "Fairholm",
              "Greystone", "Hollowell", "Ironwood", "Juniper", "Kestrel", "Larkspur", "Millbrook",
              "Northcote", "Oakhurst", "Pennywhistle", "Quarrystone", "Ravensworth", "Silverton",
              "Thistledown", "Underhill", "Vantwood", "Westerly", "Yarrowby", "Zephyrine",
              "Amberlyn", "Birchmont", "Coldharbor", "Driftwood", "Elmstead", "Foxglove",
              "Glimmerton", "Hearthstone", "Inglewick", "Jasperly", "Kingsmere", "Lowmarsh",
              "Mossgrove", "Nettlefield", "Orchardly"]

DEPTS = [
    ("Sales", "CC-SAL", 30, 3, "Account Executive"),
    ("Engineering", "CC-ENG", 32, 3, "Software Engineer"),
    ("Finance", "CC-FIN", 12, 2, None),
    ("Marketing", "CC-MKT", 14, 2, "Marketing Specialist"),
    ("Support", "CC-SUP", 18, 2, "Support Specialist"),
    ("Operations", "CC-OPS", 14, 2, "Operations Analyst"),
]
FIN_IC_TITLES = ["Senior Accountant", "Staff Accountant", "Staff Accountant", "AP Specialist",
                 "AP Specialist", "Payroll Specialist", "Financial Analyst", "Financial Analyst"]
LIMITS = {"IC": 0, "Manager": 250000, "Director": 1000000, "VP": 5000000}
DEPT_TRAVEL = {"Sales": 3.0, "Support": 1.4, "Engineering": 1.0, "Marketing": 1.6,
               "Finance": 0.6, "Operations": 0.9}
ROLE_TRAVEL = {"IC": 1.0, "Manager": 1.2, "Director": 1.3, "VP": 1.4}

CATEGORY_ACCOUNT = {"Meals": "6100", "Lodging": "6110", "Airfare": "6120",
                    "Ground transport": "6130", "Software": "6140", "Office supplies": "6150",
                    "Training": "6160", "Client entertainment": "6170"}
UNCATEGORIZED_ACCOUNT = "6190"

BOXMART = ("Boxmart Marketplace", ["BOXMART MKTP US*2K4", "BOXMART MKTPLACE"])
MERCH = {
    "Meals": [("Basil & Rye", ["BASIL & RYE #112", "SQ *BASIL AND RYE"]),
              ("Corner Deli Co", ["CORNER DELI CO", "TST* CORNER DELI CO"]),
              ("Lumen Cafe", ["LUMEN CAFE 0381", "SQ *LUMEN CAFE"]),
              ("Harbor Noodle House", ["HARBOR NOODLE HSE", "HARBOR NOODLE 22"]),
              ("Greenfield Kitchen", ["GREENFIELD KITCHEN", "GFK*GREENFIELD KTCHN"]),
              ("Northside Bistro", ["NORTHSIDE BISTRO", "TST* NORTHSIDE BSTRO"])],
    "Lodging": [("Stayline Hotels", ["STAYLINE HOTEL 4421", "STAYLINE HTL FOLIO"]),
                ("Meridian Suites", ["MERIDIAN SUITES 207", "MERIDIAN STES"]),
                ("Parkway Inn", ["PARKWAY INN 88", "PARKWAY INN & SUITES"])],
    "Airfare": [("Skylark Air", ["SKYLARK AIR 0062", "SKYLARK AIR 0067 ETKT"]),
                ("Bluejet Airways", ["BLUEJET AIR 2793", "BLUEJET AIRWAYS"]),
                ("Northstar Airlines", ["NORTHSTAR AIRL 0164", "NORTHSTAR AIR TKT"])],
    "Software": [BOXMART, ("Pixelforge", ["PIXELFORGE *SUBSCR", "PIXELFORGE.IO"]),
                 ("Notably", ["NOTABLY.APP", "NOTABLY *ANNUAL"]),
                 ("Diagramly", ["DIAGRAMLY.COM", "DIAGRAMLY *PRO"])],
    "Office supplies": [BOXMART, ("Paper & Pine Supply", ["PAPER&PINE SUPPLY", "PAPER & PINE #31"]),
                        ("Deskworks", ["DESKWORKS STORE 88", "DESKWORKS ONLINE"])],
    "Training": [("Summit Learning", ["SUMMIT LEARNING INC", "SUMMIT LRNG"]),
                 ("CodeCamp Academy", ["CODECAMP ACADEMY", "CODECAMP*COURSE"]),
                 ("ProCert Institute", ["PROCERT INST", "PROCERT EXAM FEE"])],
    "Client entertainment": [("Skyline Steakhouse", ["SKYLINE STEAKHSE", "TST* SKYLINE STEAK"]),
                             ("Ballpark Suites", ["BALLPARK SUITES TIX", "BALLPARK SUITES"]),
                             ("Riverside Grill", ["RIVERSIDE GRILL", "SQ *RIVERSIDE GRILL"])],
}
GROUND = [
    ("Rideo", ["RIDEO *TRIP", "RIDEO *TRIP HELP.RIDEO"],
     ["Ride to airport", "Ride from airport", "Ride to customer site"], 900, 6500),
    ("Swift Cab Co", ["SWIFT CAB 3321", "SWIFTCAB*FARE"],
     ["Taxi to customer site", "Taxi from airport"], 1200, 5500),
    ("Metro Transit", ["METRO TRANSIT FARE", "METRO TRNST"], ["Train fare", "Transit fare"], 275, 1250),
    ("ParkRight Garage", ["PARKRIGHT GARAGE 12", "PARKRIGHT*AIRPORT"],
     ["Airport parking", "Parking at customer site"], 1500, 4800),
    ("Roadrunner Car Rental", ["ROADRUNNER RENT A CAR", "ROADRUNNER RAC"], ["Rental car"], 6500, 14500),
]
DESC = {
    "Meals1": ["Lunch while traveling", "Dinner while traveling", "Breakfast before client visit",
               "Working lunch", "Dinner after site visit"],
    "MealsN": ["Team lunch", "Team dinner during onsite", "Working lunch with team"],
    "Lodging": ["Hotel night, customer visit", "Hotel night, regional meeting", "Hotel night, onsite"],
    "Airfare": ["Round trip, customer visit", "Round trip, regional meeting", "Round trip, onsite"],
    "AirfareConf": ["Round trip, conference"],
    "Software": ["Design tool monthly seat", "Note-taking app annual plan", "Diagram tool license",
                 "Browser testing add-on", "Screen recorder license"],
    "Office supplies": ["Printer paper and toner", "USB-C adapters", "Notebooks and pens",
                        "Monitor stand", "Headset for support calls", "Whiteboard markers"],
    "Training": ["Online course", "Certification exam fee", "Workshop registration"],
    "TrainingConf": ["Conference registration"],
    "Client entertainment": ["Client dinner", "Event tickets with client", "Client lunch"],
}
ALCOHOL_DESCS = ["Team dinner, includes wine", "Client dinner with beer and appetizers",
                 "Drinks after offsite, cocktails", "Dinner, bar tab included",
                 "Celebration dinner with wine pairing"]
ALCOHOL_KEYWORDS = ["wine", "beer", "cocktail", "bar tab", "brewery", "whiskey"]
TAPROOM = ("Copper Kettle Taproom", ["COPPER KETTLE TAPROOM"])

FX = {"EUR": {"2026-08": "1.0921", "2026-09": "1.0874", "2026-10": "1.0812"},
      "GBP": {"2026-08": "1.2764", "2026-09": "1.2709", "2026-10": "1.2655"},
      "CAD": {"2026-08": "0.7318", "2026-09": "0.7296", "2026-10": "0.7342"}}

POLICY_LIMITS = {"Lodging": 30000, "Airfare": 150000, "Ground transport": 15000,
                 "Software": 50000, "Office supplies": 50000, "Training": 250000}

GL_ACCOUNTS = [
    ("1010", "Operating Cash", "asset", "debit"),
    ("1020", "Operating Cash (NW-CA)", "asset", "debit"),
    ("1050", "Petty Cash", "asset", "debit"),
    ("1200", "Accounts Receivable", "asset", "debit"),
    ("1310", "Intercompany Receivable", "asset", "debit"),
    ("1400", "Prepaid Expenses", "asset", "debit"),
    ("1500", "Fixed Assets", "asset", "debit"),
    ("1510", "Accumulated Depreciation", "asset", "credit"),
    ("1900", "Suspense", "asset", "debit"),
    ("2010", "Accounts Payable", "liability", "credit"),
    ("2100", "Accrued Liabilities", "liability", "credit"),
    ("2150", "Accrued Reimbursements", "liability", "credit"),
    ("2200", "Payroll Liabilities", "liability", "credit"),
    ("2310", "Intercompany Payable", "liability", "credit"),
    ("2400", "Corporate Card Payable", "liability", "credit"),
    ("2500", "Deferred Revenue", "liability", "credit"),
    ("3000", "Common Stock", "equity", "credit"),
    ("3100", "Retained Earnings", "equity", "credit"),
    ("3900", "Opening Balance Equity", "equity", "credit"),
    ("4000", "Subscription Revenue", "revenue", "credit"),
    ("4100", "Services Revenue", "revenue", "credit"),
    ("4910", "Interest Income", "revenue", "credit"),
    ("4990", "FX Gain or Loss", "revenue", "credit"),
    ("6000", "Salaries and Wages", "expense", "debit"),
    ("6010", "Payroll Taxes", "expense", "debit"),
    ("6020", "Employee Benefits", "expense", "debit"),
    ("6100", "Meals", "expense", "debit"),
    ("6110", "Lodging", "expense", "debit"),
    ("6120", "Airfare", "expense", "debit"),
    ("6130", "Ground Transport", "expense", "debit"),
    ("6140", "Software Subscriptions", "expense", "debit"),
    ("6150", "Office Supplies", "expense", "debit"),
    ("6160", "Training", "expense", "debit"),
    ("6170", "Client Entertainment", "expense", "debit"),
    ("6180", "Conferences and Events", "expense", "debit"),
    ("6190", "Other Travel and Expense (Uncategorized)", "expense", "debit"),
    ("6200", "Rent", "expense", "debit"),
    ("6210", "Utilities", "expense", "debit"),
    ("6300", "Professional Fees", "expense", "debit"),
    ("6310", "Legal Fees", "expense", "debit"),
    ("6400", "Marketing Programs", "expense", "debit"),
    ("6500", "Depreciation", "expense", "debit"),
    ("6600", "Bank and Merchant Fees", "expense", "debit"),
    ("6700", "Hosting and Cloud", "expense", "debit"),
    ("6800", "Insurance", "expense", "debit"),
    ("6900", "Charitable Contributions", "expense", "debit"),
    ("6950", "Penalties and Fines", "expense", "debit"),
    ("6990", "Miscellaneous Expense", "expense", "debit"),
]
ACCT_NAME = {a: n for a, n, _, _ in GL_ACCOUNTS}

BUDGET_ACCTS = ["6000", "6010", "6020", "6100", "6110", "6120", "6130", "6140", "6150", "6160",
                "6170", "6180", "6190", "6200", "6210", "6300", "6310", "6400", "6500", "6600",
                "6700", "6800"]
TE_ACCTS = {"6100", "6110", "6120", "6130", "6150", "6160", "6170", "6190"}
# class, base flex amount (cents), designed Oct delta (cents) for non-"under" classes
DESIGN = {
    "6000": ("dollar_only", 115_000_000, 3_842_617),
    "6010": ("under", 8_800_000, None),
    "6020": ("under", 14_000_000, None),
    "6100": ("under", 500_000, None),
    "6110": ("under", 1_500_000, None),
    "6120": ("under", 2_000_000, None),
    "6130": ("under", 300_000, None),
    "6140": ("under", 5_500_000, None),
    "6150": ("pct_only", 600_000, 850_000),
    "6160": ("both", 1_800_000, 3_214_050),
    "6170": ("under", 400_000, None),
    "6180": ("both", 2_500_000, 4_862_511),
    "6190": ("under", 250_000, None),
    "6200": ("under", 9_641_250, None),
    "6210": ("pct_only", 740_000, 165_043),
    "6300": ("both", 3_200_000, 2_745_033),
    "6310": ("under", 1_800_000, None),
    "6400": ("both", 12_000_000, 3_630_977),
    "6500": ("under", 2_100_000, None),
    "6600": ("under", 4_800_000, None),
    "6700": ("dollar_only", 31_000_000, 1_912_345),
    "6800": ("pct_only", 560_000, 214_088),
}
VENDORS = {
    "6100": "Basil & Rye Catering", "6110": "Wayfinder Travel Desk", "6120": "Wayfinder Travel Desk",
    "6130": "Citywide Car Service", "6140": "Pixelforge Software", "6150": "Paper & Pine Supply",
    "6160": "Summit Learning", "6170": "Ballpark Suites", "6180": "Lakeside Lodge Events",
    "6190": "Wayfinder Travel Desk", "6200": "Harborview Properties", "6210": "Metro Power & Water",
    "6300": "Granite Ridge Advisory", "6310": "Calder & Moss LLP", "6400": "Brightbeam Media",
    "6700": "Stratus Cloud Hosting", "6800": "Keystone Mutual Insurance",
}
DRIVERS = {
    "6160": ("CC-ENG", "Engineering fall training cohort, 40 seats"),
    "6180": ("CC-SAL", "Sales offsite Oct 20 to 22, venue and catering"),
    "6400": ("CC-MKT", "Q4 brand campaign, launch flight"),
    "6300": ("CC-FIN", "Advisory services, October"),
}
EXPLANATION = {
    "6160": ("explained", "Engineering note: fall training cohort ran in October, planned for Q1 2027"),
    "6180": ("explained", "Sales note: Q4 offsite moved from November to October"),
    "6400": ("explained", "Marketing note: Q4 campaign launched three weeks early"),
    "6300": ("owner_to_explain", "No note covers it. Finance owns 6300 and its note says nothing unusual"),
    "6000": ("explained", "People note: merit increases effective Oct 1"),
    "6700": ("no_note", "No note. Not required: under the 10% threshold"),
    "6150": ("no_note", "No note. Driven by the $9,800.00 office supplies outlier line"),
    "6210": ("no_note", "No note. Under the $10,000 threshold"),
    "6800": ("no_note", "No note. Under the $10,000 threshold"),
}


# ----------------------------------------------------------------------------
# employees
# ----------------------------------------------------------------------------


def gen_employees(rng):
    pairs = [(f, l) for f in FIRST_NAMES for l in LAST_NAMES]
    rng.shuffle(pairs)
    emps = []
    counter = [0]
    span = (D(2026, 6, 30) - D(2015, 1, 5)).days

    def new(dept, cc, role, title, mgr):
        f, l = pairs[counter[0]]
        counter[0] += 1
        e = {"id": f"E{counter[0]:04d}", "name": f"{f} {l}", "department": dept, "role": role,
             "title": title, "manager_id": mgr, "limit": LIMITS[role], "cost_center": cc,
             "hire_date": D(2015, 1, 5) + dt.timedelta(days=rng.randint(0, span))}
        emps.append(e)
        return e

    for dept, cc, size, n_mgr, ic_title in DEPTS:
        vp = new(dept, cc, "VP", "Chief Financial Officer" if dept == "Finance" else f"VP of {dept}", "")
        di = new(dept, cc, "Director", "Controller" if dept == "Finance" else f"Director of {dept}", vp["id"])
        if dept == "Finance":
            am = new(dept, cc, "Manager", "Accounting Manager", di["id"])
            apm = new(dept, cc, "Manager", "AP Manager", di["id"])
            for t in FIN_IC_TITLES:
                mgr = apm if t in ("AP Specialist", "Payroll Specialist") else am
                new(dept, cc, "IC", t, mgr["id"])
        else:
            mgrs = [new(dept, cc, "Manager", f"{dept} Manager", di["id"]) for _ in range(n_mgr)]
            for k in range(size - 2 - n_mgr):
                new(dept, cc, "IC", ic_title, mgrs[k % n_mgr]["id"])
    return emps


# ----------------------------------------------------------------------------
# expense claims and lines
# ----------------------------------------------------------------------------


class ClaimBook:
    def __init__(self, rng, emps):
        self.rng = rng
        self.emps = emps
        self.emp_by_id = {e["id"]: e for e in emps}
        self.used = set()       # (emp, merchant, date)
        self.meal_days = set()  # (emp, date)
        self.seq = 0
        self.claims = []

    # -- line construction -------------------------------------------------
    def make_line(self, cat, date, conf=False):
        rng = self.rng
        att = ""
        if cat == "Ground transport":
            m, texts, descs, lo, hi = rng.choice(GROUND)
            usd = rng.randint(lo, hi)
            desc = rng.choice(descs)
        else:
            m, texts = rng.choice(MERCH[cat])
            if cat == "Meals":
                if rng.random() < 0.85:
                    att = 1
                    usd = rng.randint(1200, 6800)
                    desc = rng.choice(DESC["Meals1"])
                else:
                    att = rng.randint(2, 5)
                    usd = att * rng.randint(1800, 6500)
                    desc = rng.choice(DESC["MealsN"])
            elif cat == "Lodging":
                usd = rng.randint(13900, 29400)
                desc = rng.choice(DESC["Lodging"])
            elif cat == "Airfare":
                usd = rng.randint(25000, 98000) if conf else rng.randint(18900, 89000)
                desc = rng.choice(DESC["AirfareConf"] if conf else DESC["Airfare"])
            elif cat == "Software":
                usd = rng.randint(900, 29900)
                desc = rng.choice(DESC["Software"])
            elif cat == "Office supplies":
                usd = rng.randint(500, 24000)
                desc = rng.choice(DESC["Office supplies"])
            elif cat == "Training":
                usd = rng.randint(90000, 220000) if conf else rng.randint(19900, 150000)
                desc = rng.choice(DESC["TrainingConf"] if conf else DESC["Training"])
            else:  # Client entertainment
                att = rng.randint(2, 6)
                usd = att * rng.randint(3500, 13500)
                desc = rng.choice(DESC["Client entertainment"])
        receipt = True if usd > 7500 else rng.random() < 0.65
        return {"date": date, "merchant": m, "mtext": rng.choice(texts), "category": cat,
                "usd": usd, "desc": desc, "att": att, "receipt": receipt, "flag": None,
                "currency": None, "amount": None, "seq": None, "claim": None}

    def place(self, claim, line, shift=True):
        emp = claim["emp"]["id"]
        d = line["date"]
        for _ in range(4):
            key = (emp, line["merchant"], d)
            meal_ok = line["category"] != "Meals" or (emp, d) not in self.meal_days
            if key not in self.used and meal_ok:
                line["date"] = d
                self.used.add(key)
                if line["category"] == "Meals":
                    self.meal_days.add((emp, d))
                self.attach(claim, line)
                return True
            if not shift:
                return False
            d = prev_weekday(d - ONE)
        return False

    def attach(self, claim, line):
        self.seq += 1
        line["seq"] = self.seq
        line["claim"] = claim
        claim["lines"].append(line)

    # -- claim construction ------------------------------------------------
    def gen_trip(self, claim, ref, conf):
        rng = self.rng
        end = prev_weekday(ref - rng.randint(1, 10) * ONE)
        n = rng.choice([2, 3, 3, 4]) if conf else rng.choice([1, 1, 2, 2, 2, 3, 3, 4])
        n = min(n, end.weekday())
        start = end - n * ONE
        self.place(claim, self.make_line("Airfare", start, conf))
        if conf:
            self.place(claim, self.make_line("Training", start, conf=True))
        m, texts = rng.choice(MERCH["Lodging"])
        for k in range(n):
            ln = self.make_line("Lodging", start + k * ONE)
            ln["merchant"], ln["mtext"] = m, rng.choice(texts)
            self.place(claim, ln, shift=False)
        for d in daterange(start, end):
            if rng.random() < 0.4:
                self.place(claim, self.make_line("Meals", d), shift=False)
        self.place(claim, self.make_line("Ground transport", start), shift=False)
        if rng.random() < 0.5 and end != start:
            self.place(claim, self.make_line("Ground transport", end), shift=False)

    def gen_single(self, claim, ref):
        rng = self.rng
        cat = rng.choices(["Software", "Office supplies", "Ground transport", "Meals", "Training",
                           "Client entertainment"], [20, 18, 20, 17, 10, 15])[0]
        d = prev_weekday(ref - rng.randint(0, 20) * ONE)
        self.place(claim, self.make_line(cat, d))

    def gen_multi(self, claim, ref):
        rng = self.rng
        for _ in range(rng.choice([2, 2, 3])):
            cat = rng.choice(["Ground transport", "Meals", "Client entertainment", "Office supplies",
                              "Software"])
            d = prev_weekday(ref - rng.randint(1, 15) * ONE)
            self.place(claim, self.make_line(cat, d))

    def generate(self):
        rng = self.rng
        weights = [DEPT_TRAVEL[e["department"]] * ROLE_TRAVEL[e["role"]] for e in self.emps]
        days = list(daterange(CLAIMS_START, AS_OF))
        day_w = [1.0 if d.weekday() < 5 else 0.25 for d in days]
        oct_days = list(daterange(D(2026, 10, 12), AS_OF))
        raw = []
        for i in range(N_CLAIMS):
            emp = rng.choices(self.emps, weights)[0]
            draft = i < N_DRAFTS
            if draft:
                day = rng.choice(oct_days)
            else:
                day = rng.choices(days, day_w)[0]
            created = dt.datetime(day.year, day.month, day.day, rng.randint(7, 21), rng.randint(0, 59))
            r = rng.random()
            cur = "USD" if r < 0.92 else ("EUR" if r < 0.95 else ("GBP" if r < 0.98 else "CAD"))
            fx = "1.0000" if cur == "USD" else FX[cur][period_of(day)]
            kind = "draft" if draft else rng.choices(["trip", "conf", "single", "multi"], [17, 5, 50, 28])[0]
            claim = {"idx": i, "emp": emp, "created": created, "submitted": None if draft else created,
                     "kind": kind, "currency": cur, "fx": fx, "lines": [], "status": None,
                     "dec": None, "paid": None, "approver": "", "flag": None, "id": None}
            if kind == "trip":
                self.gen_trip(claim, day, False)
            elif kind == "conf":
                self.gen_trip(claim, day, True)
            elif kind == "multi":
                self.gen_multi(claim, day)
            elif kind == "draft":
                if rng.random() < 0.6:
                    self.gen_single(claim, day)
                else:
                    self.gen_multi(claim, day)
            else:
                self.gen_single(claim, day)
            tries = 0
            while not claim["lines"]:
                tries += 1
                self.gen_single(claim, day - tries * ONE)
            raw.append(claim)
        raw.sort(key=lambda c: (c["created"], c["idx"]))
        for n, c in enumerate(raw, 1):
            c["id"] = f"C-{n:05d}"
        self.claims = raw
        self.timeline()

    def timeline(self):
        rng = self.rng
        for c in self.claims:
            if c["kind"] == "draft":
                c["status"] = "draft"
                continue
            sub = c["submitted"].date()
            lag = rng.choices([1, 2, 3, 4, 5, 6], [25, 25, 20, 15, 10, 5])[0]
            dec = add_bd(sub, lag)
            if dec > AS_OF:
                c["status"] = "submitted"
                continue
            c["dec"] = dt.datetime(dec.year, dec.month, dec.day, rng.randint(8, 18), rng.randint(0, 59))
            if rng.random() < 0.04:
                c["status"] = "rejected"
                continue
            run = first_thursday_on_or_after(dec + 2 * ONE)
            if run <= AS_OF:
                c["status"] = "paid"
                c["paid"] = run
            else:
                c["status"] = "approved"

    # -- anomaly helpers ---------------------------------------------------
    def key_free(self, emp_id, merchant, d):
        return (emp_id, merchant, d) not in self.used

    def move_line(self, line, new_date=None, new_merchant=None):
        emp = line["claim"]["emp"]["id"]
        old_key = (emp, line["merchant"], line["date"])
        nd = new_date or line["date"]
        nm = new_merchant or line["merchant"]
        new_key = (emp, nm, nd)
        if new_key != old_key and new_key in self.used:
            return False
        if line["category"] == "Meals" and nd != line["date"] and (emp, nd) in self.meal_days:
            return False
        self.used.discard(old_key)
        self.used.add(new_key)
        if line["category"] == "Meals":
            self.meal_days.discard((emp, line["date"]))
            self.meal_days.add((emp, nd))
        line["date"], line["merchant"] = nd, nm
        return True


def near_dup_pairs(lines_iter, amount_key):
    """Return sorted list of (a, b, kind) near-duplicate pairs among lines."""
    groups = {}
    for ln in lines_iter:
        groups.setdefault((ln["emp_id"], ln["merchant"], ln["currency"]), []).append(ln)
    out = []
    for _, g in sorted(groups.items()):
        if len(g) < 2:
            continue
        g = sorted(g, key=lambda x: x["sortkey"])
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                a, b = g[i], g[j]
                dd = abs((a["date"] - b["date"]).days)
                da = abs(amount_key(a) - amount_key(b))
                if dd == 0 and da == 1:
                    out.append((a, b, "amount_1_cent"))
                elif dd == 1 and da == 0:
                    out.append((a, b, "date_1_day"))
    return out


def build_claims(rng, emps):
    book = ClaimBook(rng, emps)
    book.generate()
    claims = book.claims
    emp_by_id = book.emp_by_id

    def all_lines():
        for c in claims:
            for ln in c["lines"]:
                yield ln

    # 1. remove accidental near-duplicates among normal lines (USD amounts)
    for _ in range(5):
        tmp = [{"emp_id": ln["claim"]["emp"]["id"], "merchant": ln["merchant"], "currency": "X",
                "date": ln["date"], "usd": ln["usd"], "sortkey": ln["seq"], "ref": ln} for ln in all_lines()]
        pairs = near_dup_pairs(tmp, lambda x: x["usd"])
        if not pairs:
            break
        for a, b, _ in pairs:
            b["ref"]["usd"] += 7
            if b["ref"]["usd"] > 7500:
                b["ref"]["receipt"] = True

    protected = set()

    def eligible_claim(c):
        return c["kind"] != "draft" and c["currency"] == "USD" and c["id"] not in protected

    # 2. transposition claim (paid Oct 22, total exactly 123456)
    trans = None
    cands = [c for c in claims if c["status"] == "paid" and c["paid"] == D(2026, 10, 22)
             and c["currency"] == "USD"]
    rng.shuffle(cands)
    for c in cands:
        tot = sum(ln["usd"] for ln in c["lines"])
        if not 60000 <= tot <= 123000:
            continue
        for ln in c["lines"]:
            if ln["category"] in ("Airfare", "Training"):
                new = ln["usd"] + 123456 - tot
                lim = POLICY_LIMITS[ln["category"]]
                if new <= lim - 1000:
                    ln["usd"] = new
                    ln["receipt"] = True
                    ln["flag"] = "special"
                    trans = c
                    break
        if trans:
            break
    assert trans, "no transposition claim"
    protected.add(trans["id"])

    # 3. outlier: a $9,800.00 office supplies line in an Oct-approved claim
    outlier = None
    cands = [c for c in claims if c["status"] in ("approved", "paid") and c["dec"].date() >= D(2026, 10, 1)
             and c["currency"] == "USD" and c["kind"] == "single" and c["id"] not in protected
             and c["lines"][0]["category"] == "Office supplies"]
    rng.shuffle(cands)
    for c in cands:
        ln = c["lines"][0]
        if book.move_line(ln, new_merchant="Deskworks"):
            ln["usd"] = 980000
            ln["mtext"] = "DESKWORKS ONLINE"
            ln["desc"] = "Ergonomic chairs, bulk order of 12"
            ln["receipt"] = True
            ln["flag"] = "outlier"
            outlier = ln
            break
    assert outlier
    protected.add(outlier["claim"]["id"])

    # 4. mixed currency without fx_rate (3 pending claims)
    mixed = []
    cands = [c for c in claims if c["status"] == "submitted" and c["currency"] == "USD"
             and len(c["lines"]) >= 2 and c["id"] not in protected]
    rng.shuffle(cands)
    for c in cands:
        opts = [ln for ln in c["lines"] if ln["usd"] < 7000 and ln["category"] != "Meals" and ln["flag"] is None]
        if not opts:
            continue
        ln = opts[0]
        ln["flag"] = "mixed_currency"
        ln["mixed_to"] = ["EUR", "GBP", "CAD"][len(mixed)]
        c["flag"] = "missing_fx"
        protected.add(c["id"])
        mixed.append(ln)
        if len(mixed) == 3:
            break
    assert len(mixed) == 3

    def pool(pred, kinds=None):
        out = []
        for c in claims:
            if not eligible_claim(c):
                continue
            if kinds and c["kind"] not in kinds:
                continue
            for ln in c["lines"]:
                if ln["flag"] is None and pred(ln):
                    out.append(ln)
        return out

    seeded = {"outlier": [outlier], "mixed_currency": mixed}

    # 5. line-level anomalies
    def take(name, cands, n, action):
        rng.shuffle(cands)
        got = []
        for ln in cands:
            if len(got) == n:
                break
            if ln["flag"] is not None:
                continue
            if action(ln):
                ln["flag"] = name
                got.append(ln)
        assert len(got) == n, name
        seeded[name] = got

    def meals_over(ln):
        ln["usd"] = rng.randint(8200, 14500)
        ln["receipt"] = True
        return True
    take("meals_over_limit", pool(lambda l: l["category"] == "Meals" and l["att"] == 1), 5, meals_over)

    def alcohol(ln):
        if len(seeded.get("_alc", [])) < 6:
            if not book.move_line(ln, new_merchant=TAPROOM[0]):
                return False
            ln["mtext"] = TAPROOM[1][0]
            seeded.setdefault("_alc", []).append(ln)
        ln["desc"] = rng.choice(ALCOHOL_DESCS)
        return True
    take("alcohol", pool(lambda l: l["category"] == "Meals"), 25, alcohol)
    seeded.pop("_alc", None)

    def lodging_over(ln):
        ln["usd"] = rng.randint(31500, 42000)
        ln["receipt"] = True
        return True
    take("lodging_over_limit", pool(lambda l: l["category"] == "Lodging"), 4, lodging_over)

    def no_receipt(ln):
        ln["receipt"] = False
        return True
    take("missing_receipt_over_threshold",
         pool(lambda l: l["usd"] > 7500 and l["category"] not in ("Meals", "Lodging")), 10, no_receipt)

    def weekend(ln):
        d = ln["date"]
        back = d.weekday() + (2 if rng.random() < 0.5 else 1)
        nd = d - back * ONE
        sub = ln["claim"]["submitted"].date()
        if (sub - nd).days > 55:
            return False
        return book.move_line(ln, new_date=nd)
    take("weekend", pool(lambda l: l["category"] in ("Ground transport", "Office supplies", "Software",
                                                     "Client entertainment", "Meals"),
                         kinds=("single", "multi")), 30, weekend)

    def stale(ln):
        sub = ln["claim"]["submitted"].date()
        nd = prev_weekday(sub - rng.randint(62, 80) * ONE)
        return book.move_line(ln, new_date=nd)
    take("stale_over_60_days", pool(lambda l: l["category"] != "Meals", kinds=("single",)), 4, stale)

    def missing_cat(ln):
        ln["category"] = ""
        return True
    take("missing_category", pool(lambda l: l["category"] in ("Ground transport", "Office supplies",
                                                              "Software", "Client entertainment")), 8,
         missing_cat)

    # 6. exact and near duplicates across claims of the same employee
    claims_by_emp = {}
    for c in claims:
        if eligible_claim(c):
            claims_by_emp.setdefault(c["emp"]["id"], []).append(c)

    def targets_for(ln, nd):
        out = []
        for c in claims_by_emp.get(ln["claim"]["emp"]["id"], []):
            if c is ln["claim"] or c["submitted"] <= ln["claim"]["submitted"]:
                continue
            sub = c["submitted"].date()
            if sub >= nd and (sub - nd).days <= 55:
                out.append(c)
        return out

    def dup_ok(ln):
        return ln["category"] not in ("Meals", "") and not 5900 <= ln["usd"] <= 7600

    def copy_line(ln, target, nd, usd, flag):
        new = dict(ln)
        new["date"], new["usd"], new["flag"] = nd, usd, flag
        new["orig"] = ln
        book.attach(target, new)
        return new

    exact = []
    cands = pool(dup_ok)
    rng.shuffle(cands)
    for ln in cands:
        if len(exact) == 90:
            break
        if ln["flag"] is not None:
            continue
        tg = targets_for(ln, ln["date"])
        if not tg:
            continue
        ln["flag"] = "dup_original"
        new = copy_line(ln, rng.choice(tg), ln["date"], ln["usd"], "exact_duplicate")
        exact.append(new)
    assert len(exact) == 90
    seeded["exact_duplicate"] = exact

    near = []
    cands = pool(dup_ok)
    rng.shuffle(cands)
    kinds = ["amount_1_cent", "date_1_day"]
    for ln in cands:
        if len(near) == 45:
            break
        if ln["flag"] is not None:
            continue
        kind = kinds[len(near) % 2]
        emp = ln["claim"]["emp"]["id"]
        if kind == "amount_1_cent":
            nd = ln["date"]
            usd = ln["usd"] + (1 if rng.random() < 0.5 else -1)
        else:
            nd = ln["date"] + ONE
            if nd.weekday() >= 5:
                nd = ln["date"] - ONE
            if nd.weekday() >= 5 or not book.key_free(emp, ln["merchant"], nd):
                continue
            if (ln["date"] - nd).days == 1 and (ln["claim"]["submitted"].date() - nd).days > 55:
                continue
            usd = ln["usd"]
        tg = targets_for(ln, max(nd, ln["date"]))
        if not tg:
            continue
        if kind == "date_1_day":
            book.used.add((emp, ln["merchant"], nd))
        ln["flag"] = "near_original"
        new = copy_line(ln, rng.choice(tg), nd, usd, "near_duplicate")
        new["near_kind"] = kind
        if new["usd"] > 7500 and not new["receipt"]:
            new["receipt"] = True
        near.append(new)
    assert len(near) == 45
    seeded["near_duplicate"] = near

    # 7. split claims just under the 7500 receipt threshold
    splits = []
    emp_ids = sorted(claims_by_emp)
    rng.shuffle(emp_ids)
    used_emps = set()
    for eid in emp_ids:
        if len(splits) == 6:
            break
        cl = sorted(claims_by_emp[eid], key=lambda c: c["submitted"])
        pair = None
        for i in range(len(cl) - 1):
            gap = (cl[i + 1]["submitted"] - cl[i]["submitted"]).days
            if 1 <= gap <= 21:
                pair = (cl[i], cl[i + 1])
                break
        if not pair:
            continue
        a, b = pair
        nd = prev_weekday(a["submitted"].date() - rng.randint(0, 4) * ONE)
        cat = ["Office supplies", "Software", "Client entertainment"][len(splits) % 3]
        m, texts = MERCH[cat][1] if cat != "Client entertainment" else MERCH[cat][2]
        if not book.key_free(eid, m, nd):
            continue
        k = 3 if len(splits) % 2 == 0 else 2
        amts = []
        while len(amts) < k:
            x = rng.randint(7005, 7495)
            if all(abs(x - y) >= 50 for y in amts):
                amts.append(x)
        book.used.add((eid, m, nd))
        group = []
        for j, amt in enumerate(amts):
            line = {"date": nd, "merchant": m, "mtext": rng.choice(texts), "category": cat, "usd": amt,
                    "desc": rng.choice(DESC[cat]), "att": 2 if cat == "Client entertainment" else "",
                    "receipt": False, "flag": "split", "currency": None, "amount": None, "seq": None,
                    "claim": None}
            book.attach(a if j == 0 else b, line)
            group.append(line)
        splits.append(group)
        used_emps.add(eid)
    assert len(splits) == 6
    seeded["split"] = splits

    # 8. finalize amounts, ids, totals
    for c in claims:
        c["lines"].sort(key=lambda ln: (ln["date"], ln["seq"]))
        for ln in c["lines"]:
            ln["currency"] = c["currency"]
            ln["amount"] = ln["usd"] if c["currency"] == "USD" else from_usd(ln["usd"], c["fx"])
    for ln in mixed:
        ln["currency"] = ln["mixed_to"]
        ln["claim"]["fx"] = ""
    n = 0
    for c in claims:
        for ln in c["lines"]:
            n += 1
            ln["id"] = f"L-{n:06d}"
            ln["amount_usd"] = None if not c["fx"] else to_usd(ln["amount"], c["fx"])
        c["total_cents"] = sum(ln["amount"] for ln in c["lines"])
        c["total_usd"] = None if not c["fx"] else sum(ln["amount_usd"] for ln in c["lines"])

    # 9. approvers
    cfo = next(e for e in emps if e["title"] == "Chief Financial Officer")
    vp_ops = next(e for e in emps if e["title"] == "VP of Operations")

    def normal_approver(emp, total):
        cur = emp
        while cur["manager_id"]:
            cur = emp_by_id[cur["manager_id"]]
            if cur["limit"] >= total:
                return cur["id"]
        return vp_ops["id"] if emp is cfo else cfo["id"]

    for c in claims:
        if c["status"] in ("approved", "paid", "rejected"):
            c["approver"] = normal_approver(c["emp"], c["total_usd"])

    def approved_in_gl(c):
        return c["status"] in ("approved", "paid") and c["dec"].date() >= GL_START

    cands = [c for c in claims if approved_in_gl(c) and c["emp"]["role"] != "IC" and c["id"] not in protected
             and c["total_usd"] <= c["emp"]["limit"]]
    rng.shuffle(cands)
    self_appr = cands[:5]
    for c in self_appr:
        c["approver"] = c["emp"]["id"]
        c["flag"] = "self_approved"
        protected.add(c["id"])
    seeded["self_approved"] = self_appr

    cands = [c for c in claims if approved_in_gl(c) and c["emp"]["role"] == "IC" and c["id"] not in protected
             and 250000 < c["total_usd"] <= 1000000]
    rng.shuffle(cands)
    over = cands[:5]
    assert len(over) == 5
    for c in over:
        c["approver"] = c["emp"]["manager_id"]
        c["flag"] = "above_limit"
        protected.add(c["id"])
    seeded["above_limit"] = over
    seeded["transposition_claim"] = trans
    return claims, seeded, emp_by_id


def audit_lines(claims, emp_by_id):
    """Apply the documented detection rules to the final data. Returns dict of results."""
    lines = []
    for c in claims:
        for ln in c["lines"]:
            lines.append({"id": ln["id"], "claim_id": c["id"], "emp_id": c["emp"]["id"],
                          "merchant": ln["merchant"], "date": ln["date"], "amount": ln["amount"],
                          "currency": ln["currency"], "usd": ln["amount_usd"], "category": ln["category"],
                          "receipt": ln["receipt"], "desc": ln["desc"], "att": ln["att"],
                          "sub": c["submitted"].date() if c["submitted"] else None, "sortkey": ln["id"],
                          "claim_currency": c["currency"], "fx": c["fx"]})
    res = {}
    groups = {}
    for ln in lines:
        groups.setdefault((ln["emp_id"], ln["merchant"], ln["date"], ln["amount"], ln["currency"]), []).append(ln)
    exact = []
    for _, g in sorted(groups.items(), key=lambda kv: kv[1][0]["id"]):
        if len(g) >= 2 and len({x["claim_id"] for x in g}) >= 2:
            exact.append((g[0]["id"], g[1]["id"]))
    res["exact_duplicate"] = sorted(exact)
    res["near_duplicate"] = sorted((a["id"], b["id"], k) for a, b, k in near_dup_pairs(lines, lambda x: x["amount"]))
    sg = {}
    for ln in lines:
        if ln["usd"] is not None and 6000 <= ln["usd"] < 7500:
            sg.setdefault((ln["emp_id"], ln["merchant"], ln["date"]), []).append(ln)
    res["split"] = sorted(tuple(x["id"] for x in g) for g in sg.values()
                          if len(g) >= 2 and sum(x["usd"] for x in g) > 7500)
    res["weekend"] = sorted(ln["id"] for ln in lines if ln["date"].weekday() >= 5)
    res["missing_category"] = sorted(ln["id"] for ln in lines if ln["category"] == "")
    res["mixed_currency"] = sorted(ln["id"] for ln in lines if ln["currency"] != ln["claim_currency"])
    res["missing_fx_claims"] = sorted(c["id"] for c in claims if c["fx"] == "")
    res["alcohol"] = sorted(ln["id"] for ln in lines if any(k in ln["desc"].lower() for k in ALCOHOL_KEYWORDS))
    res["missing_receipt_over_threshold"] = sorted(ln["id"] for ln in lines
                                                   if ln["usd"] is not None and ln["usd"] > 7500 and not ln["receipt"])
    res["stale_over_60_days"] = sorted(ln["id"] for ln in lines if ln["sub"] and (ln["sub"] - ln["date"]).days > 60)
    over = []
    meals = {}
    for ln in lines:
        if ln["usd"] is None:
            continue
        cat = ln["category"]
        if cat in POLICY_LIMITS and ln["usd"] > POLICY_LIMITS[cat]:
            over.append((ln["id"], cat))
        if cat == "Client entertainment" and ln["usd"] > 15000 * int(ln["att"]):
            over.append((ln["id"], cat))
        if cat == "Meals":
            meals.setdefault((ln["emp_id"], ln["date"]), []).append(ln)
    for g in meals.values():
        if sum(x["usd"] for x in g) > 7500 * max(int(x["att"]) for x in g):
            for x in g:
                over.append((x["id"], "Meals"))
    res["over_policy_limit"] = sorted(over)
    res["self_approved"] = sorted(c["id"] for c in claims if c["approver"] and c["approver"] == c["emp"]["id"])
    res["above_limit"] = sorted(c["id"] for c in claims if c["status"] in ("approved", "paid")
                                and emp_by_id[c["approver"]]["limit"] < c["total_usd"])
    return res


# ----------------------------------------------------------------------------
# general ledger
# ----------------------------------------------------------------------------


class Ledger:
    def __init__(self):
        self.jes = []

    def add(self, entity, posting, source, preparer, approver, desc, lines, entry=None, flag=None,
            bank=None, tag=None):
        dr = sum(x[2] for x in lines)
        cr = sum(x[3] for x in lines)
        assert dr == cr and dr > 0, (desc, dr, cr)
        je = {"entity": entity, "posting": posting, "entry": entry or posting, "source": source,
              "preparer": preparer, "approver": approver, "desc": desc, "lines": lines, "flag": flag,
              "bank": bank, "tag": tag, "seq": len(self.jes), "id": None}
        self.jes.append(je)
        return je


def DR(acct, amt, cc=""):
    return (acct, cc, amt, 0)


def CR(acct, amt, cc=""):
    return (acct, cc, 0, amt)


SOURCE_ORDER = {"SYSTEM": 0, "PAYROLL": 1, "AP": 2, "EXP": 3, "MANUAL": 4}


def build_gl(rng, emps, claims, seeded):
    L = Ledger()
    by_title = {}
    for e in emps:
        by_title.setdefault(e["title"], []).append(e["id"])
    controller = by_title["Controller"][0]
    acct_mgr = by_title["Accounting Manager"][0]
    ap_mgr = by_title["AP Manager"][0]
    staff = by_title["Senior Accountant"] + by_title["Staff Accountant"]
    ap_specs = by_title["AP Specialist"]
    payroll_spec = by_title["Payroll Specialist"][0]
    finance_ids = sorted(e["id"] for e in emps if e["department"] == "Finance")

    def man_approver(total):
        return controller if total >= JE_APPROVAL_LIMIT else acct_mgr

    def cents(lo, hi):
        while True:
            x = rng.randint(lo, hi)
            if x % 100000 != 0 and not 950000 <= x < 1000000:
                return x

    headcount = {}
    travel_w = {}
    for e in emps:
        headcount[e["cost_center"]] = headcount.get(e["cost_center"], 0) + 1
        travel_w[e["cost_center"]] = travel_w.get(e["cost_center"], 0) + int(DEPT_TRAVEL[e["department"]] * 10)
    cc_weights = {a: travel_w for a in TE_ACCTS}
    cc_weights.update({a: headcount for a in ("6000", "6010", "6020")})
    cc_weights.update({
        "6140": {"CC-ENG": 50, "CC-FIN": 10, "CC-MKT": 15, "CC-SAL": 10, "CC-SUP": 10, "CC-OPS": 5},
        "6180": {"CC-SAL": 70, "CC-MKT": 30},
        "6200": {"CC-OPS": 1}, "6210": {"CC-OPS": 1}, "6800": {"CC-OPS": 1}, "6500": {"CC-OPS": 1},
        "6300": {"CC-FIN": 1}, "6310": {"CC-FIN": 1}, "6600": {"CC-FIN": 1},
        "6400": {"CC-MKT": 1}, "6700": {"CC-ENG": 1},
    })

    # --- expense claims: approvals and payouts --------------------------------
    paid = sorted([c for c in claims if c["status"] == "paid"], key=lambda c: (c["paid"], c["id"]))
    run_seq = {}
    for n, c in enumerate(paid, 1):
        c["payout_id"] = f"PO-{n:06d}"
        k = run_seq.get(c["paid"], 0) + 1
        run_seq[c["paid"]] = k
        c["bank_ref"] = f"NWR{c['paid']:%y%m%d}{k:04d}"
        c["method"] = "ACH"
    oct_paid = [c for c in paid if c["paid"].month == 10]
    trans = seeded["transposition_claim"]
    # duplicate payment candidate (Oct 15 run) and checks
    pool15 = [c for c in oct_paid if c["paid"] == D(2026, 10, 15) and c is not trans
              and 40000 <= c["total_usd"] <= 150000]
    dup_pay = rng.choice(pool15)
    checks = []
    check_no = 10231
    plan = [(D(2026, 10, 8), D(2026, 10, 13)), (D(2026, 10, 15), D(2026, 10, 20)),
            (D(2026, 10, 22), None), (D(2026, 10, 29), None), (D(2026, 10, 29), None)]
    for run, clear in plan:
        opts = [c for c in oct_paid if c["paid"] == run and c is not trans and c is not dup_pay
                and c["method"] == "ACH" and c["currency"] == "USD"]
        c = rng.choice(opts)
        c["method"] = "CHECK"
        c["bank_ref"] = f"CHK {check_no:06d}"
        c["check_clear"] = clear
        check_no += rng.randint(3, 40)
        checks.append(c)

    for c in claims:
        if c["status"] in ("approved", "paid") and c["dec"].date() >= GL_START:
            agg = {}
            for ln in c["lines"]:
                acct = CATEGORY_ACCOUNT.get(ln["category"], UNCATEGORIZED_ACCOUNT)
                agg[acct] = agg.get(acct, 0) + ln["amount_usd"]
            cc = c["emp"]["cost_center"]
            lines = [DR(a, agg[a], cc) for a in sorted(agg)] + [CR("2150", c["total_usd"])]
            L.add("NW-US", c["dec"].date(), "EXP", "SVC-EXPENSE", "",
                  f"Expense claim {c['id']} approved {c['emp']['id']}", lines, tag=("claim", c["id"]))
    trans_je = dup_je = None
    for c in paid:
        if c["paid"] < GL_START:
            continue
        amt = c["total_usd"]
        gl_amt = 124356 if c is trans else amt
        if c["method"] == "ACH":
            bank = {"date": c["paid"], "desc": f"ACH CREDIT NWREIMB {c['emp']['id']}", "ref": c["bank_ref"],
                    "amount": -amt}
        elif c.get("check_clear"):
            bank = {"date": c["check_clear"], "desc": "CHECK PAID", "ref": c["bank_ref"], "amount": -amt}
        else:
            bank = None
        je = L.add("NW-US", c["paid"], "EXP", "SVC-EXPENSE", "",
                   f"Reimbursement {c['payout_id']} {c['id']} {c['bank_ref']}",
                   [DR("2150", gl_amt), CR("1010", gl_amt)], bank=bank, tag=("payout", c["id"]))
        if c is trans:
            je["flag"] = "transposition"
            trans_je = je
        if c is dup_pay:
            dup_orig = je
            dup_je = L.add("NW-US", c["paid"], "EXP", "SVC-EXPENSE", "", je["desc"], list(je["lines"]),
                           entry=add_bd(c["paid"], 1), flag="duplicate", bank=None, tag=("payout_dup", c["id"]))
            dup_je["dup_of"] = je
    assert trans_je and dup_je

    # --- revenue, receipts, interest ------------------------------------------
    customers = [f"Customer {n:04d}" for n in rng.sample(range(100, 999), 40)]
    for d in list(daterange(D(2026, 9, 1), D(2026, 10, 31))):
        if d.weekday() == 2 and is_bd(d):
            amt = cents(70_000_000, 80_000_000)
            L.add("NW-US", d, "SYSTEM", "SVC-GL", "", f"Subscription billing run {d:%Y%m%d}",
                  [DR("1200", amt), CR("4000", amt)], tag="billing")
    rcpt_no = 260101
    dit = []
    for month_days in (list(daterange(D(2026, 9, 1), D(2026, 9, 30))),
                       list(daterange(D(2026, 10, 1), D(2026, 10, 29)))):
        bds = [d for d in month_days if is_bd(d)]
        for d in sorted(rng.choices(bds, k=22)):
            amt = cents(4_000_000, 26_000_000)
            cust = rng.choice(customers)
            ref = f"RCPT-{rcpt_no}"
            rcpt_no += 1
            L.add("NW-US", d, "SYSTEM", "SVC-GL", "", f"Customer receipt {ref} {cust}",
                  [DR("1010", amt), CR("1200", amt)],
                  bank={"date": d, "desc": f"DEPOSIT {cust.upper()}", "ref": ref, "amount": amt})
    for _ in range(2):
        amt = cents(600_000, 2_400_000)
        cust = rng.choice(customers)
        ref = f"RCPT-{rcpt_no}"
        rcpt_no += 1
        dit.append(L.add("NW-US", D(2026, 10, 30), "SYSTEM", "SVC-GL", "", f"Customer receipt {ref} {cust}",
                         [DR("1010", amt), CR("1200", amt)], bank=None, flag="deposit_in_transit"))
    L.add("NW-US", D(2026, 9, 30), "MANUAL", staff[0], acct_mgr, "Record September bank interest per statement",
          [DR("1010", 1203), CR("4910", 1203)], entry=D(2026, 10, 1),
          bank=None)  # September item, cleared on the September statement
    for d in (D(2026, 9, 18), D(2026, 10, 16)):
        amt = cents(40_000, 180_000)
        L.add("NW-US", d, "SYSTEM", "SVC-GL", "", "Late payment interest billed to customers",
              [DR("1200", amt), CR("4910", amt)])

    # --- recurring manual entries ---------------------------------------------
    sep_accr = cents(600_000, 890_000)
    oct_accr = cents(600_000, 890_000)
    L.add("NW-US", D(2026, 9, 30), "MANUAL", staff[1], acct_mgr, "Accrue professional fees, September",
          [DR("6300", sep_accr, "CC-FIN"), CR("2100", sep_accr)], entry=D(2026, 10, 2))
    L.add("NW-US", D(2026, 10, 1), "MANUAL", staff[1], acct_mgr, "Reverse September professional fees accrual",
          [DR("2100", sep_accr), CR("6300", sep_accr, "CC-FIN")])
    L.add("NW-US", D(2026, 10, 30), "MANUAL", staff[1], acct_mgr, "Accrue professional fees, October",
          [DR("6300", oct_accr, "CC-FIN"), CR("2100", oct_accr)], entry=D(2026, 11, 3))
    for d, entry in ((D(2026, 9, 30), D(2026, 10, 1)), (D(2026, 10, 30), D(2026, 11, 2))):
        ins = 412_377
        sw = cents(1_480_000, 1_560_000)
        L.add("NW-US", d, "MANUAL", staff[2], acct_mgr, "Amortize prepaid insurance",
              [DR("6800", ins, "CC-OPS"), CR("1400", ins)], entry=entry)
        L.add("NW-US", d, "MANUAL", staff[2], controller, "Amortize prepaid software licenses",
              [DR("6140", sw, "CC-ENG"), CR("1400", sw)], entry=entry)
    for d in (D(2026, 9, 16), D(2026, 10, 14)):
        amt = cents(30_000, 90_000)
        L.add("NW-US", d, "MANUAL", staff[1], acct_mgr, "Reclass uncategorized T&E to Lodging",
              [DR("6110", amt, "CC-SAL"), CR("6190", amt, "CC-SAL")])
    # intercompany shared services recharges (NW-US bills NW-CA)
    ic_dates = [D(2026, 9, 10), D(2026, 9, 17), D(2026, 9, 24), D(2026, 10, 8), D(2026, 10, 22), D(2026, 10, 29)]
    ic_unmatched = None
    for k, d in enumerate(ic_dates):
        ref = f"IC-{d:%y%m}-{k + 1:02d}"
        amt = cents(1_200_000, 1_900_000)
        us = L.add("NW-US", d, "MANUAL", staff[0], man_approver(amt), f"IC shared services recharge {ref} to NW-CA",
                   [DR("1310", amt), CR("4100", amt)], tag=("ic", ref))
        if k == 5:
            us["flag"] = "ic_unmatched"
            ic_unmatched = us
            continue
        L.add("NW-CA", d, "MANUAL", staff[0], man_approver(amt), f"IC shared services recharge {ref} from NW-US",
              [DR("6300", amt, "CC-FIN"), CR("2310", amt)], tag=("ic", ref))
    ca_rent = 1_840_215
    for d in (D(2026, 9, 1), D(2026, 10, 1)):
        L.add("NW-CA", d, "AP", ap_specs[0], ap_mgr, f"Northgate Realty Ltd INV-NG-{d:%m}01 office rent",
              [DR("6200", ca_rent, "CC-OPS"), CR("2010", ca_rent)])

    # --- seeded JE-test anomalies -------------------------------------------
    S = {}

    def seed(name, entity, d, preparer, approver, desc, lines, entry=None):
        je = L.add(entity, d, "MANUAL", preparer, approver, desc, lines, entry=entry, flag=name)
        S.setdefault(name, []).append(je)
        return je

    seed("weekend_or_holiday", "NW-US", D(2026, 9, 19), staff[1], acct_mgr, "Accrue car service invoice",
         [DR("6130", 137_422, "CC-SAL"), CR("2100", 137_422)])
    seed("weekend_or_holiday", "NW-US", D(2026, 10, 18), staff[2], acct_mgr, "Reclass accrued vendor bill to AP",
         [DR("2100", 381_240), CR("2010", 381_240)])
    seed("weekend_or_holiday", "NW-US", D(2026, 9, 7), staff[0], acct_mgr, "Accrue client event deposit",
         [DR("6170", 220_815, "CC-SAL"), CR("2100", 220_815)])
    seed("weekend_or_holiday", "NW-US", D(2026, 10, 12), staff[1], acct_mgr, "Record prepaid maintenance contract",
         [DR("1400", 447_690), CR("2010", 447_690)])
    sales_vp = by_title["VP of Sales"][0]
    eng_mgr = by_title["Engineering Manager"][0]
    mkt_ic = by_title["Marketing Specialist"][0]
    seed("preparer_never_posts", "NW-US", D(2026, 10, 6), sales_vp, acct_mgr, "Reclass client dinner to entertainment",
         [DR("6170", 195_037, "CC-SAL"), CR("6100", 195_037, "CC-SAL")])
    seed("preparer_never_posts", "NW-US", D(2026, 9, 22), eng_mgr, acct_mgr, "Accrue tooling subscription",
         [DR("6140", 268_411, "CC-ENG"), CR("2100", 268_411)])
    seed("preparer_never_posts", "NW-US", D(2026, 10, 26), mkt_ic, acct_mgr, "Accrue sponsorship booth",
         [DR("6400", 412_066, "CC-MKT"), CR("2100", 412_066)])
    seed("post_close", "NW-US", D(2026, 10, 30), staff[0], acct_mgr, "Record prepaid conference booth",
         [DR("1400", 318_544), CR("2010", 318_544)], entry=D(2026, 11, 6))
    seed("post_close", "NW-US", D(2026, 10, 30), staff[1], acct_mgr, "Reclass October accrual to AP",
         [DR("2100", 274_903), CR("2010", 274_903)], entry=D(2026, 11, 9))
    seed("post_close", "NW-US", D(2026, 10, 30), staff[2], acct_mgr, "Late invoice adjustment, October billing",
         [DR("1200", 586_210), CR("4000", 586_210)], entry=D(2026, 11, 12))
    seed("round_amount", "NW-US", D(2026, 10, 23), staff[0], controller, "Reclass accrued liabilities to AP",
         [DR("2100", 5_000_000), CR("2010", 5_000_000)])
    seed("round_amount", "NW-US", D(2026, 9, 25), staff[2], controller, "Prepaid deposit, event venue",
         [DR("1400", 2_500_000), CR("2100", 2_500_000)])
    seed("round_amount", "NW-US", D(2026, 10, 27), staff[1], controller, "Prepay annual conference sponsorship",
         [DR("1400", 10_000_000), CR("2010", 10_000_000)])
    seed("just_under_limit", "NW-US", D(2026, 9, 28), staff[1], acct_mgr, "Accrue outside counsel fees",
         [DR("6310", 999_900, "CC-FIN"), CR("2100", 999_900)])
    seed("just_under_limit", "NW-US", D(2026, 10, 9), staff[0], acct_mgr, "Accrue advisory retainer",
         [DR("6300", 999_500, "CC-FIN"), CR("2100", 999_500)])
    seed("just_under_limit", "NW-US", D(2026, 10, 27), staff[2], acct_mgr, "Accrue software true-up",
         [DR("6140", 998_750, "CC-ENG"), CR("2100", 998_750)])
    seed("seldom_used_account", "NW-US", D(2026, 10, 14), staff[2], acct_mgr, "Park unidentified customer receipt",
         [DR("1900", 742_118), CR("1200", 742_118)])
    seed("seldom_used_account", "NW-US", D(2026, 9, 23), staff[0], acct_mgr, "State late filing penalty",
         [DR("6950", 61_250, "CC-FIN"), CR("2100", 61_250)])
    seed("seldom_used_account", "NW-US", D(2026, 10, 20), staff[1], acct_mgr, "Clean up opening balance difference",
         [DR("6990", 383_317, "CC-FIN"), CR("3900", 383_317)])
    seed("self_approved", "NW-US", D(2026, 9, 15), acct_mgr, acct_mgr, "Accrue tax advisory fees",
         [DR("6300", 431_508, "CC-FIN"), CR("2100", 431_508)])
    seed("self_approved", "NW-US", D(2026, 10, 21), controller, controller, "Release legal accrual",
         [DR("2100", 670_294), CR("6310", 670_294, "CC-FIN")])
    d1 = L.add("NW-US", D(2026, 9, 10), "AP", ap_specs[1], ap_mgr, "Pixelforge Software INV-PF-20931 annual license",
               [DR("1400", 342_960), CR("2010", 342_960)], tag="ap_dup_orig")
    d2 = L.add("NW-US", D(2026, 9, 10), "AP", ap_specs[1], ap_mgr, "Pixelforge Software INV-PF-20931 annual license",
               [DR("1400", 342_960), CR("2010", 342_960)], entry=D(2026, 9, 11), flag="duplicate")
    d2["dup_of"] = d1

    # --- flex solver: hit the designed budget variance classes --------------
    fixed = {a: {SEP: 0, OCT: 0} for a in BUDGET_ACCTS}
    for je in L.jes:
        p = period_of(je["posting"])
        for acct, _, dr, cr in je["lines"]:
            if acct in fixed and p in (SEP, OCT):
                fixed[acct][p] += dr - cr
    design = {}
    for a in BUDGET_ACCTS:
        cls, base_c, dd = DESIGN[a]
        fs, fo = fixed[a][SEP], fixed[a][OCT]
        base = base_c + (max(fs, 0) * 35 // 100 if a in TE_ACCTS else 0) + rng.randint(1, 9999)
        s_target = fs + base
        if cls == "under":
            delta = int(s_target * rng.uniform(-0.03, 0.03))
            delta = max(-600_000, min(600_000, delta))
            bdev = int(s_target * rng.uniform(-0.01, 0.01))
            bdev = max(-200_000, min(200_000, bdev))
        elif cls == "dollar_only":
            delta = dd
            bdev = int(s_target * rng.uniform(-0.004, 0.004))
        else:
            delta = dd
            bdev = int(s_target * rng.uniform(-0.008, 0.008))
        o_target = s_target + delta
        driver = dd if cls == "both" else 0
        xs, xo = s_target - fs, o_target - fo - driver
        assert xs >= 20_000 and xo >= 20_000, (a, xs, xo)
        design[a] = {"class": cls, "sep": s_target, "oct": o_target, "budget_oct": s_target + bdev,
                     "flex": {SEP: xs, OCT: xo}, "driver": driver}

    sep_bds = [d for d in daterange(D(2026, 9, 1), D(2026, 9, 25)) if is_bd(d)]
    oct_bds = [d for d in daterange(D(2026, 10, 1), D(2026, 10, 28)) if is_bd(d)]
    ap_invoices = []
    inv_no = {}
    for a in BUDGET_ACCTS:
        if a in ("6000", "6010", "6020", "6500", "6600"):
            continue
        vendor = VENDORS[a]
        code = "".join(w[0] for w in vendor.split() if w[0].isalpha()).upper()[:3]
        for p, bds in ((SEP, sep_bds), (OCT, oct_bds)):
            for part, d in zip(split_parts(design[a]["flex"][p], 2, rng), sorted(rng.sample(bds, 2))):
                inv_no[code] = inv_no.get(code, rng.randint(10000, 60000)) + rng.randint(3, 90)
                inv = f"INV-{code}-{inv_no[code]}"
                lines = [DR(a, amt, cc) for cc, amt in split_by_weights(part, cc_weights[a]) if amt]
                tot = sum(x[2] for x in lines)
                lines.append(CR("2010", tot))
                je = L.add("NW-US", d, "AP", rng.choice(ap_specs), ap_mgr, f"{vendor} {inv} {ACCT_NAME[a].lower()}",
                           lines)
                ap_invoices.append((je, vendor, inv, tot))
            if p == OCT and design[a]["driver"]:
                cc, what = DRIVERS[a]
                inv_no[code] = inv_no.get(code, 50000) + rng.randint(3, 90)
                inv = f"INV-{code}-{inv_no[code]}"
                amt = design[a]["driver"]
                d = rng.choice([x for x in oct_bds if x >= D(2026, 10, 19)])
                je = L.add("NW-US", d, "AP", rng.choice(ap_specs), ap_mgr, f"{vendor} {inv} {what}",
                           [DR(a, amt, cc), CR("2010", amt)])
                je["driver"] = a
    # payroll runs
    runs = {SEP: [D(2026, 9, 15), D(2026, 9, 30)], OCT: [D(2026, 10, 15), D(2026, 10, 30)]}
    for p, dates in runs.items():
        halves = {a: split_parts(design[a]["flex"][p], 2, rng) for a in ("6000", "6010", "6020")}
        for k, d in enumerate(dates):
            lines = []
            for a in ("6000", "6010", "6020"):
                for cc, amt in split_by_weights(halves[a][k], cc_weights[a]):
                    lines.append(DR(a, amt, cc))
            tot = sum(x[2] for x in lines)
            lines.append(CR("1010", tot))
            ref = f"PR-{d:%Y%m%d}"
            L.add("NW-US", d, "PAYROLL", payroll_spec, controller, f"Payroll run {ref} net pay, taxes and benefits",
                  lines, bank={"date": d, "desc": "NWPAY PAYROLL FUNDING", "ref": ref, "amount": -tot})
    # depreciation and merchant fees
    for p, d in ((SEP, D(2026, 9, 30)), (OCT, D(2026, 10, 30))):
        a, b = split_parts(design["6500"]["flex"][p], 2, rng)
        L.add("NW-US", d, "SYSTEM", "SVC-GL", "", "Depreciation, computer equipment",
              [DR("6500", a, "CC-OPS"), CR("1510", a)])
        L.add("NW-US", d, "SYSTEM", "SVC-GL", "", "Depreciation, furniture and fixtures",
              [DR("6500", b, "CC-OPS"), CR("1510", b)])
    fee_dates = {SEP: [D(2026, 9, 4), D(2026, 9, 11), D(2026, 9, 18), D(2026, 9, 25)],
                 OCT: [D(2026, 10, 2), D(2026, 10, 9), D(2026, 10, 16), D(2026, 10, 23), D(2026, 10, 30)]}
    for p, dates in fee_dates.items():
        for d, amt in zip(dates, split_parts(design["6600"]["flex"][p], len(dates), rng)):
            ref = f"MSF-{d:%m%d}"
            L.add("NW-US", d, "SYSTEM", "SVC-GL", "", f"Merchant processing fees {ref}",
                  [DR("6600", amt, "CC-FIN"), CR("1010", amt)],
                  bank={"date": d, "desc": "MERCHANT SVCS FEE", "ref": ref, "amount": -amt})

    # --- AP payments ---------------------------------------------------------
    opening_ap_parts = [cents(3_000_000, 15_000_000) for _ in range(10)]
    open_vendors = sorted(set(VENDORS.values()))
    for k, (amt, d) in enumerate(zip(opening_ap_parts, sorted(rng.sample(sep_bds, 10)))):
        vendor = rng.choice(open_vendors)
        inv = f"INV-AUG-{4100 + k * 7}"
        L.add("NW-US", d, "AP", rng.choice(ap_specs), ap_mgr, f"AP payment {vendor} {inv}",
              [DR("2010", amt), CR("1010", amt)])
    payables = [(d1, "Pixelforge Software", "INV-PF-20931", 342_960)] + \
               [x for x in ap_invoices if x[0]["posting"].month == 9]
    for je, vendor, inv, amt in sorted(payables, key=lambda x: x[0]["seq"]):
        pay = roll_fwd(je["posting"] + 30 * ONE)
        if pay > D(2026, 10, 30):
            continue
        L.add("NW-US", pay, "AP", rng.choice(ap_specs), ap_mgr, f"AP payment {vendor} {inv}",
              [DR("2010", amt), CR("1010", amt)],
              bank={"date": pay, "desc": f"ACH DEBIT {vendor.upper()}", "ref": inv, "amount": -amt})

    # --- assign ids ------------------------------------------------------------
    L.jes.sort(key=lambda j: (j["posting"], SOURCE_ORDER[j["source"]], j["seq"]))
    for n, je in enumerate(L.jes, 1):
        je["id"] = f"JE-{n:06d}"
    for je in L.jes:
        assert je["posting"] >= GL_START
    ctx = {"ledger": L, "design": design, "cc_weights": cc_weights, "seeded_je": S, "dup_ap": (d1, d2),
           "dup_pay": (dup_orig, dup_je), "trans_je": trans_je, "dit": dit, "checks": checks,
           "ic_unmatched": ic_unmatched, "finance_ids": finance_ids, "opening_ap": sum(opening_ap_parts),
           "dup_pay_claim": dup_pay, "controller": controller, "acct_mgr": acct_mgr}
    return ctx


def audit_gl(L, emps, finance_ids):
    res = {}
    authorized = set(finance_ids) | {"SVC-EXPENSE", "SVC-GL"}
    res["weekend_or_holiday"] = sorted(j["id"] for j in L.jes if not is_bd(j["posting"]))
    res["preparer_never_posts"] = sorted(j["id"] for j in L.jes if j["preparer"] not in authorized)
    res["post_close"] = sorted(j["id"] for j in L.jes if
                               (period_of(j["posting"]) == OCT and j["entry"] > OCT_CLOSE) or
                               (period_of(j["posting"]) == SEP and j["entry"] > SEP_CLOSE))
    res["round_amount"] = sorted(j["id"] for j in L.jes if j["source"] == "MANUAL" and
                                 any(max(x[2], x[3]) % 100000 == 0 for x in j["lines"]))
    res["just_under_limit"] = sorted(j["id"] for j in L.jes if j["source"] == "MANUAL" and
                                     950000 <= sum(x[2] for x in j["lines"]) < JE_APPROVAL_LIMIT)
    usage = {}
    for j in L.jes:
        for acct in {x[0] for x in j["lines"]}:
            usage.setdefault(acct, set()).add(j["id"])
    seldom_accts = sorted(a for a, s in usage.items() if len(s) <= 2)
    res["seldom_accounts"] = seldom_accts
    res["seldom_used_account"] = sorted({jid for a in seldom_accts for jid in usage[a]})
    res["self_approved"] = sorted(j["id"] for j in L.jes if j["approver"] and j["preparer"] == j["approver"])
    sig = {}
    for j in L.jes:
        k = (j["entity"], j["posting"], j["desc"], tuple(sorted(j["lines"])))
        sig.setdefault(k, []).append(j["id"])
    res["duplicate"] = sorted(tuple(v) for v in sig.values() if len(v) > 1)
    ic = {}
    for j in L.jes:
        if j["tag"] and j["tag"][0] == "ic":
            ic.setdefault(j["tag"][1], []).append(j)
    res["ic_unmatched"] = sorted(v[0]["id"] for v in ic.values() if len({x["entity"] for x in v}) < 2)
    res["unused_accounts"] = sorted(a for a, _, _, _ in GL_ACCOUNTS if a not in usage)
    return res


# ----------------------------------------------------------------------------
# PM data
# ----------------------------------------------------------------------------

USAGE = [
    ("Receipt photo capture with auto-fill", "receipts", 41200, 168, "9.4"),
    ("Corporate card auto-match", "receipts", 27900, 61, "6.1"),
    ("Approval reminders and escalation", "approvals", 12300, 142, "7.8"),
    ("Bulk approve for managers", "approvals", 4100, 18, "7.1"),
    ("Mobile offline drafts", "mobile", 19800, 97, "11.2"),
    ("Multi-currency conversion at entry", "currency", 6400, 72, "13.6"),
    ("Inline policy hints", "policy", 38500, 83, "8.7"),
    ("Mileage tracker", "other", 8900, 12, "5.2"),
]
TICKET_COUNTS = [("receipts", 21), ("approvals", 15), ("mobile", 9), ("currency", 7), ("policy", 7), ("other", 1)]
TICKET_TEXT = {
    "receipts": ["Receipt photo came out blurry and the app rejected it twice before I gave up.",
                 "The app did not read the total from my hotel folio, I had to type every line.",
                 "Receipt upload spun for a minute and then said it failed. Tried on wifi too.",
                 "I lost a paper receipt for a {amt} dinner. What do I do now?",
                 "Card transaction shows up but the receipt I emailed in is not matched to it.",
                 "Uploaded a PDF receipt and the app says file type not supported.",
                 "Auto-fill picked the tip line as the total, so my claim was {amt} short."],
    "approvals": ["My claim from {n} days ago is still waiting on my manager.",
                  "Manager is on leave and nobody else can approve my claims.",
                  "I approved a claim but the employee still sees it as pending.",
                  "Got rejected with no comment, not sure what to fix.",
                  "Approval reminder emails go to my old manager.",
                  "I have {n} claims to approve and opening each one takes forever."],
    "mobile": ["App crashes when I open the camera on my phone.",
               "Lost my draft on mobile when I switched apps.",
               "Cannot add attendees from the mobile app.",
               "Mobile app logs me out every day.",
               "Submit button is hidden behind the keyboard on small phones."],
    "currency": ["Paid in EUR and the app converted at a rate that does not match my card statement.",
                 "I cannot pick GBP on a claim line, only on the whole claim.",
                 "My CAD hotel showed up as USD and I got reimbursed the wrong amount.",
                 "Where do I enter the exchange rate my card used?"],
    "policy": ["Why was my team dinner flagged? It was under the limit per person.",
               "The policy says receipts over $75 but the app asked for one on a {amt} lunch.",
               "I did not know weekend expenses need extra review.",
               "Is a client lunch Meals or Client entertainment?",
               "Claim rejected for being too old, but I was traveling for two months."],
    "other": ["How do I change the bank account my reimbursement goes to?"],
}

INTERVIEWS = """# Northwind Expense: user interview notes (October 2026)

Six short interviews run by the Northwind Expense product team. Participants are users at customer
companies and at Northwind itself. Names are withheld; participants are labeled P1 to P6.

## P1: Field sales rep, travels 3 weeks a month
- Keeps receipts in a jacket pocket and submits "when the pocket is full", often 4 to 6 weeks later.
- Lost two receipts last quarter and had to write a missing-receipt memo for each.
- "If I could snap the receipt at the table and be done, I would submit the same day."
- Has had a claim bounced for being older than 60 days.

## P2: Engineering manager, approves for 9 people
- Gets approval emails in a batch and approves on Friday afternoons.
- Opens each claim to check the receipt; says it takes "a minute or two each, more on trips".
- Wants to approve the clean ones in bulk and only look at the flagged ones.
- Did not know there is a delegate setting for vacations.

## P3: Support specialist, rarely travels
- Submits a few small claims a month (parking, a headset, a training course).
- Mostly uses the phone app. The camera crashed twice this month and the draft was lost.
- "I just retype everything on the laptop now, it is slower but it does not lose my work."

## P4: Finance AP specialist (internal user at Northwind)
- Spends the first two days after each payout run answering "where is my money" emails.
- Sees duplicate submissions every week: same taxi, same amount, a second claim a few days later.
- Foreign currency claims are the worst: employees type the converted amount, the card statement
  shows another, and AP fixes it by hand.

## P5: Marketing specialist, books events in Europe
- Pays in EUR and GBP. Does not know which exchange rate to use and guesses.
- Got reimbursed short on a GBP hotel and gave up chasing the difference.
- Wants the app to read the currency from the receipt and show the USD amount before submitting.

## P6: Operations analyst, new hire (2 months)
- Read the policy once during onboarding and does not remember the limits.
- Was surprised a team dinner was flagged ("I thought the limit was per dinner, not per person").
- Asked whether a client lunch is Meals or Client entertainment. Nobody on the team agreed.
- "Tell me while I am filling it in, not two days later in a rejection."
"""


def build_pm(rng):
    usage = csv_text(["feature", "area", "monthly_active_users", "support_tickets_per_month",
                      "avg_minutes_to_submit_claim"], [list(r) for r in USAGE])
    tickets = []
    for cat, n in TICKET_COUNTS:
        for _ in range(n):
            d = D(2026, 10, rng.randint(1, 31))
            t = dt.datetime(d.year, d.month, d.day, rng.randint(7, 20), rng.randint(0, 59))
            text = rng.choice(TICKET_TEXT[cat]).format(amt=money(rng.randint(3000, 14000)),
                                                       n=rng.randint(6, 30))
            tickets.append([t, cat, text])
    tickets.sort(key=lambda x: (x[0], x[1], x[2]))
    rows = [[f"T-{1000 + i}", fmt_dt(t), cat, text] for i, (t, cat, text) in enumerate(tickets, 1)]
    return {"usage_metrics.csv": usage,
            "support_tickets.csv": csv_text(["ticket_id", "created_at", "category", "text"], rows),
            "interview_notes.md": INTERVIEWS}


# ----------------------------------------------------------------------------
# assemble
# ----------------------------------------------------------------------------


def build(seed):
    rng = random.Random(seed)
    emps = gen_employees(rng)
    claims, seeded, emp_by_id = build_claims(rng, emps)
    audit = audit_lines(claims, emp_by_id)

    # --- check line/claim rules against the seeded set ---------------------
    def ids(lst):
        return sorted(x["id"] for x in lst)
    exp_exact = sorted((ln["orig"]["id"], ln["id"]) if ln["orig"]["id"] < ln["id"] else (ln["id"], ln["orig"]["id"])
                       for ln in seeded["exact_duplicate"])
    assert audit["exact_duplicate"] == exp_exact, "exact dup mismatch"
    exp_near = sorted(tuple(sorted((ln["orig"]["id"], ln["id"]))) for ln in seeded["near_duplicate"])
    assert sorted((a, b) for a, b, _ in audit["near_duplicate"]) == exp_near, "near dup mismatch"
    assert audit["split"] == sorted(tuple(sorted(x["id"] for x in g)) for g in seeded["split"]), "split mismatch"
    assert audit["weekend"] == ids(seeded["weekend"]), "weekend mismatch"
    assert audit["missing_category"] == ids(seeded["missing_category"])
    assert audit["mixed_currency"] == ids(seeded["mixed_currency"])
    assert audit["alcohol"] == ids(seeded["alcohol"])
    assert audit["missing_receipt_over_threshold"] == ids(seeded["missing_receipt_over_threshold"])
    assert audit["stale_over_60_days"] == ids(seeded["stale_over_60_days"])
    exp_over = sorted([(x["id"], "Meals") for x in seeded["meals_over_limit"]] +
                      [(x["id"], "Lodging") for x in seeded["lodging_over_limit"]] +
                      [(seeded["outlier"][0]["id"], "Office supplies")])
    assert audit["over_policy_limit"] == exp_over, (audit["over_policy_limit"], exp_over)
    assert audit["self_approved"] == ids(seeded["self_approved"])
    assert audit["above_limit"] == ids(seeded["above_limit"])

    g = build_gl(rng, emps, claims, seeded)
    L = g["ledger"]
    ga = audit_gl(L, emps, g["finance_ids"])
    S = g["seeded_je"]
    for name in ("weekend_or_holiday", "preparer_never_posts", "post_close", "round_amount", "just_under_limit",
                 "seldom_used_account", "self_approved"):
        assert ga[name] == ids(S[name]), (name, ga[name], ids(S[name]))
    assert ga["seldom_accounts"] == ["1900", "3900", "6950", "6990"], ga["seldom_accounts"]
    exp_dups = sorted([(g["dup_ap"][0]["id"], g["dup_ap"][1]["id"]), (g["dup_pay"][0]["id"], g["dup_pay"][1]["id"])])
    assert ga["duplicate"] == exp_dups, (ga["duplicate"], exp_dups)
    assert ga["ic_unmatched"] == [g["ic_unmatched"]["id"]]

    files = {}
    # employees
    files["employees.csv"] = csv_text(
        ["employee_id", "name", "department", "role", "title", "manager_id", "approval_limit_cents",
         "cost_center", "hire_date"],
        [[e["id"], e["name"], e["department"], e["role"], e["title"], e["manager_id"], e["limit"],
          e["cost_center"], e["hire_date"].isoformat()] for e in emps])
    # policy
    policy = {
        "company": "Northwind Co.",
        "policy_version": "2026.1",
        "effective_date": "2026-01-01",
        "base_currency": "USD",
        "amounts_in": "cents",
        "category_limits": {
            "Meals": {"limit_cents": 7500, "per": "person_per_day",
                      "note": "Sum of Meals lines for one employee on one date, divided by attendees_count"},
            "Lodging": {"limit_cents": 30000, "per": "night", "note": "One line per night"},
            "Airfare": {"limit_cents": 150000, "per": "ticket", "note": "Economy class"},
            "Ground transport": {"limit_cents": 15000, "per": "line"},
            "Software": {"limit_cents": 50000, "per": "line"},
            "Office supplies": {"limit_cents": 50000, "per": "line"},
            "Training": {"limit_cents": 250000, "per": "line"},
            "Client entertainment": {"limit_cents": 15000, "per": "attendee"},
        },
        "receipt_required_over_cents": 7500,
        "max_age_days": 60,
        "max_age_rule": "submitted_at date minus expense_date must be 60 days or less",
        "weekend_expenses": "flag_for_review",
        "non_reimbursable": ["alcohol", "personal entertainment", "traffic and parking fines"],
        "approval": {
            "rule": "Approver must be in the submitter's management chain with approval_limit_cents at least "
                    "the claim total in USD. Nobody approves their own claim.",
            "limits_cents": LIMITS,
            "top_of_chain": "VP claims are approved by the Chief Financial Officer; the CFO's claims by the VP of "
                            "Operations.",
        },
        "foreign_currency": "Claims in EUR, GBP or CAD carry fx_rate = USD per 1 unit of claim currency. "
                            "USD value = amount_cents x fx_rate, rounded half up to the cent, per line. "
                            "All lines on a claim must be in the claim currency.",
        "payment": "Approved claims are paid in the weekly Thursday payout run at least 2 days after approval.",
    }
    files["expense_policy.json"] = json.dumps(policy, indent=2) + "\n"

    def iso_or_blank(x):
        return fmt_dt(x) if x else ""
    files["expense_claims.csv"] = csv_text(
        ["claim_id", "employee_id", "submitted_at", "status", "approver_id", "approved_at", "total_cents",
         "currency", "fx_rate", "paid_at"],
        [[c["id"], c["emp"]["id"], iso_or_blank(c["submitted"]), c["status"], c["approver"],
          iso_or_blank(c["dec"]) if c["status"] in ("approved", "paid") else "", c["total_cents"], c["currency"],
          c["fx"], c["paid"].isoformat() if c["paid"] else ""] for c in claims])
    rows = []
    for c in claims:
        for ln in c["lines"]:
            rows.append([ln["id"], c["id"], ln["date"].isoformat(), ln["merchant"], ln["mtext"], ln["category"],
                         ln["amount"], ln["currency"], "true" if ln["receipt"] else "false", ln["desc"], ln["att"],
                         CATEGORY_ACCOUNT.get(ln["category"], "")])
    files["expense_lines.csv"] = csv_text(
        ["line_id", "claim_id", "expense_date", "merchant", "merchant_category_text", "category", "amount_cents",
         "currency", "receipt_attached", "description", "attendees_count", "gl_account_hint"], rows)

    files["gl_accounts.csv"] = csv_text(["account", "name", "type", "normal_balance"], [list(x) for x in GL_ACCOUNTS])

    # GL journal
    rows = []
    for je in L.jes:
        for n, (acct, cc, dr, cr) in enumerate(je["lines"], 1):
            rows.append([je["id"], n, je["entity"], je["posting"].isoformat(), je["entry"].isoformat(),
                         period_of(je["posting"]), acct, cc, dr, cr, je["desc"], je["source"], je["preparer"],
                         je["approver"]])
    files["gl_journal.csv"] = csv_text(
        ["je_id", "line_no", "entity", "posting_date", "entry_date", "period", "account", "cost_center",
         "debit_cents", "credit_cents", "description", "source", "preparer_id", "approver_id"], rows)

    # opening balances (Sep 1)
    open_accrual = sum(c["total_usd"] for c in claims if c["status"] in ("approved", "paid")
                       and c["dec"].date() < GL_START and (c["paid"] is None or c["paid"] >= GL_START))
    ob_us = {"1010": 425_187_342, "1200": 348_621_077, "1400": 41_288_015, "1500": 210_455_000,
             "1510": -64_122_931, "2010": -g["opening_ap"], "2100": -18_344_720, "2150": -open_accrual,
             "3000": -100_000_000}
    ob_us["3100"] = -sum(ob_us.values())
    ob_ca = {"1020": 50_000_000, "3100": -50_000_000}
    ob_rows = [["NW-US", a, ACCT_NAME[a], v] for a, v in sorted(ob_us.items())] + \
              [["NW-CA", a, ACCT_NAME[a], v] for a, v in sorted(ob_ca.items())]
    files["gl_opening_balances_2026-09-01.csv"] = csv_text(["entity", "account", "name", "balance_cents"], ob_rows)

    def balance(acct, entity, upto):
        b = ob_us.get(acct, 0) if entity == "NW-US" else ob_ca.get(acct, 0)
        for je in L.jes:
            if je["entity"] != entity or je["posting"] > upto:
                continue
            for a, _, dr, cr in je["lines"]:
                if a == acct:
                    b += dr - cr
        return b

    je_policy = {
        "company": "Northwind Co.",
        "entities": {"NW-US": "Northwind Co. (United States)", "NW-CA": "Northwind Co. Canada (reports in USD)"},
        "reporting_currency": "USD",
        "close_calendar": {"2026-09": {"period_end": "2026-09-30", "close_date": SEP_CLOSE.isoformat()},
                           "2026-10": {"period_end": "2026-10-31", "close_date": OCT_CLOSE.isoformat()}},
        "close_rule": "Entries for a period must be entered (entry_date) on or before that period's close_date.",
        "company_holidays": {d.isoformat(): n for d, n in sorted(HOLIDAYS.items())},
        "posting_days": "Entries post on business days (Monday to Friday, excluding company holidays).",
        "manual_je_approval": {"limit_cents": JE_APPROVAL_LIMIT,
                               "rule": "MANUAL entries with total debits of 1000000 cents ($10,000.00) or more "
                                       "need the Controller. Smaller entries can be approved by the Accounting "
                                       "Manager or the Controller. Preparer and approver must be different people."},
        "preparers": "Journal entries are prepared by Finance staff. System sources post as service accounts "
                     "SVC-EXPENSE (expense claims and payouts) and SVC-GL (billing, receipts, fees, depreciation).",
        "sources": {"AP": "Vendor invoices and vendor payments", "EXP": "Expense claim approvals and payouts",
                    "PAYROLL": "Payroll runs", "MANUAL": "Manual journal entries",
                    "SYSTEM": "Automated postings"},
        "intercompany": "Every NW-US entry to 1310 Intercompany Receivable must have an NW-CA entry to 2310 "
                        "Intercompany Payable with the same IC reference and amount.",
        "gl_extract_date": GL_EXTRACT.isoformat(),
    }
    files["je_policy.json"] = json.dumps(je_policy, indent=2) + "\n"

    # --- bank statement Oct ----------------------------------------------------
    oct_cash = []
    for je in L.jes:
        if je["entity"] == "NW-US" and je["posting"].month == 10:
            for a, _, dr, cr in je["lines"]:
                if a == "1010":
                    oct_cash.append((je, dr - cr))
    bank_rows = []
    for je, amt in oct_cash:
        b = je["bank"]
        if b is None:
            continue
        bank_rows.append((b["date"], 0, je["seq"], b["desc"], b["amount"], b["ref"]))
    fee = {"date": D(2026, 10, 21), "desc": "WIRE SVC CHARGE", "ref": "BKFEE-1021", "amount": -3500}
    interest = {"date": D(2026, 10, 30), "desc": "INTEREST CREDIT", "ref": "INT-1030", "amount": 1287}
    for x in (fee, interest):
        bank_rows.append((x["date"], 1, 0, x["desc"], x["amount"], x["ref"]))
    bank_rows.sort(key=lambda r: (r[0], r[1], r[2]))
    gl_open_oct = balance("1010", "NW-US", D(2026, 9, 30))
    gl_close_oct = balance("1010", "NW-US", D(2026, 10, 31))
    bal = gl_open_oct
    out = []
    for d, _, _, desc, amt, ref in bank_rows:
        bal += amt
        out.append([d.isoformat(), desc, amt, ref, bal])
    bank_close = bal
    files["bank_statement_2026-10.csv"] = csv_text(["date", "description", "amount_cents", "reference", "balance_cents"],
                                                   out)
    gl_open_sep = ob_us["1010"]
    files["gl_balance_1010_2026-10.csv"] = csv_text(["metric", "amount_cents"], [
        ["gl_1010_opening_2026-09-01", gl_open_sep],
        ["gl_1010_opening_2026-10-01", gl_open_oct],
        ["gl_1010_closing_2026-10-31", gl_close_oct],
        ["bank_opening_2026-10-01", gl_open_oct],
        ["bank_closing_2026-10-31", bank_close],
    ])
    dup_amt = g["dup_pay"][1]["lines"][0][2]
    trans_diff = 124356 - 123456
    dit_total = sum(j["lines"][0][2] for j in g["dit"])
    outstanding = [c for c in g["checks"] if not c.get("check_clear")]
    os_total = sum(c["total_usd"] for c in outstanding)
    adj_bank = bank_close + dit_total - os_total
    adj_book = gl_close_oct + fee["amount"] + interest["amount"] + dup_amt + trans_diff
    assert adj_bank == adj_book, (adj_bank, adj_book)

    # --- accrual 2150 ---------------------------------------------------------
    accr_claims = [c for c in claims if c["status"] == "approved"]
    accrual = sum(c["total_usd"] for c in accr_claims)
    gl_2150 = -balance("2150", "NW-US", D(2026, 10, 31))
    assert gl_2150 == accrual - dup_amt - trans_diff, (gl_2150, accrual, dup_amt)

    # --- payouts Oct -----------------------------------------------------------
    oct_po = [c for c in claims if c["status"] == "paid" and c["paid"].month == 10]
    oct_po.sort(key=lambda c: c["payout_id"])
    files["payouts_2026-10.csv"] = csv_text(
        ["payout_id", "claim_id", "employee_id", "amount_cents", "currency", "method", "paid_at", "status",
         "bank_reference"],
        [[c["payout_id"], c["id"], c["emp"]["id"], c["total_usd"], "USD", c["method"], c["paid"].isoformat(), "sent",
          c["bank_ref"]] for c in oct_po])

    # --- budget ----------------------------------------------------------------
    design = g["design"]
    actual = {a: {SEP: 0, OCT: 0} for a in BUDGET_ACCTS}
    for je in L.jes:
        p = period_of(je["posting"])
        for a, _, dr, cr in je["lines"]:
            if a in actual:
                actual[a][p] += dr - cr
    month_factor = {"2026-08": 0.985, "2026-09": 0.995, "2026-10": 1.0, "2026-11": 1.01, "2026-12": 1.02}
    nov_extra = {"6180": ("CC-SAL", 4_500_000), "6400": ("CC-MKT", 3_500_000)}
    brows = []
    for m, f in month_factor.items():
        for a in BUDGET_ACCTS:
            total = design[a]["budget_oct"] if m == OCT else int(design[a]["budget_oct"] * f)
            parts = dict(split_by_weights(total, g["cc_weights"][a]))
            if m == "2026-11" and a in nov_extra:
                cc, extra = nov_extra[a]
                parts[cc] = parts.get(cc, 0) + extra
            for cc, amt in parts.items():
                brows.append([m, cc, a, amt])
    brows.sort(key=lambda r: (r[0], r[1], r[2]))
    files["budget_2026.csv"] = csv_text(["month", "cost_center", "account", "budget_cents"], brows)

    def classify(act, base):
        diff = act - base
        pct = abs(diff) / abs(base)
        assert not 950_000 <= abs(diff) <= 1_050_000, ("too close to $ threshold", diff)
        assert not 0.09 <= pct <= 0.11, ("too close to % threshold", pct)
        over_d, over_p = abs(diff) > THRESH_DOLLAR, pct > THRESH_PCT
        return {(True, True): "both", (False, True): "pct_only", (True, False): "dollar_only",
                (False, False): "under"}[(over_d, over_p)], diff, pct

    variance = []
    for a in BUDGET_ACCTS:
        assert actual[a][SEP] == design[a]["sep"] and actual[a][OCT] == design[a]["oct"], a
        b = design[a]["budget_oct"]
        c1, d1, p1 = classify(actual[a][OCT], b)
        c2, d2, p2 = classify(actual[a][OCT], actual[a][SEP])
        assert c1 == c2 == design[a]["class"], (a, c1, c2, design[a]["class"])
        expl = EXPLANATION.get(a, ("not_flagged", ""))
        variance.append({"account": a, "name": ACCT_NAME[a], "class": c1, "budget_oct_cents": b,
                         "actual_sep_cents": actual[a][SEP], "actual_oct_cents": actual[a][OCT],
                         "var_vs_budget_cents": d1, "var_vs_budget_pct": round(d1 / b * 100, 1),
                         "var_vs_sep_cents": d2, "var_vs_sep_pct": round(d2 / actual[a][SEP] * 100, 1),
                         "explanation_status": expl[0], "explanation": expl[1]})

    vp = {e["department"]: e for e in emps if e["role"] == "VP"}
    di = {e["department"]: e for e in emps if e["role"] == "Director"}
    notes = f"""# October 2026 department notes

Collected by FP&A for the October 2026 close. Notes are as submitted by each department head and have not
been checked against the ledger.

## Sales ({vp['Sales']['name']}, {vp['Sales']['title']})
The Q4 sales offsite moved from November to October (Oct 20 to 22). Venue and catering invoices from
Lakeside Lodge Events landed in October, about $48,600. November conferences spend will come in under
budget by roughly the same amount.

## Engineering ({di['Engineering']['name']}, {di['Engineering']['title']})
We ran the fall training cohort for 40 engineers with Summit Learning in October, about $32,100. It was
planned for Q1 2027 and is not in the 2026 budget. Expect nothing similar in November or December.

## Marketing ({vp['Marketing']['name']}, {vp['Marketing']['title']})
The Q4 brand campaign with Brightbeam Media launched three weeks early to line up with the October trade
show, about $36,300 of spend that was planned for November.

## People and payroll ({di['Finance']['name']}, Controller)
Merit increases took effect October 1, about 3.3% on base salary. Salaries will run at the new level
for the rest of the year.

## Operations ({vp['Operations']['name']}, {vp['Operations']['title']})
Planning for the office move continues. No spend yet; the first invoices are expected in December.

## Finance ({vp['Finance']['name']}, {vp['Finance']['title']})
Nothing unusual this month.

## Support ({vp['Support']['name']}, {vp['Support']['title']})
Headcount flat. No unusual spend.
"""
    files["context_notes_2026-10.md"] = notes
    files.update(build_pm(rng))

    # --- answer key -----------------------------------------------------------
    line_by_id = {ln["id"]: ln for c in claims for ln in c["lines"]}

    def line_info(lid):
        ln = line_by_id[lid]
        c = ln["claim"]
        return {"line_id": lid, "claim_id": c["id"], "employee_id": c["emp"]["id"], "merchant": ln["merchant"],
                "expense_date": ln["date"].isoformat(), "amount_cents": ln["amount"], "currency": ln["currency"],
                "category": ln["category"]}

    je_by_id = {j["id"]: j for j in L.jes}

    def je_info(jid, extra=None):
        j = je_by_id[jid]
        d = {"je_id": jid, "entity": j["entity"], "posting_date": j["posting"].isoformat(),
             "entry_date": j["entry"].isoformat(), "source": j["source"], "preparer_id": j["preparer"],
             "approver_id": j["approver"], "total_debit_cents": sum(x[2] for x in j["lines"]),
             "accounts": sorted({x[0] for x in j["lines"]}), "description": j["desc"]}
        if extra:
            d.update(extra)
        return d

    emp_name = {e["id"]: e for e in emps}
    key = {
        "seed": seed,
        "expense_lines": {
            "exact_duplicates": [{"original_line_id": a, "duplicate_line_id": b, **{k: v for k, v in line_info(b).items()
                                                                                  if k != "line_id"}}
                                 for a, b in audit["exact_duplicate"]],
            "near_duplicates": [{"line_id_a": a, "line_id_b": b, "kind": k,
                                 "employee_id": line_info(a)["employee_id"], "merchant": line_info(a)["merchant"],
                                 "date_a": line_info(a)["expense_date"], "date_b": line_info(b)["expense_date"],
                                 "amount_a": line_info(a)["amount_cents"], "amount_b": line_info(b)["amount_cents"]}
                                for a, b, k in audit["near_duplicate"]],
            "split_under_receipt_threshold": [{"line_ids": list(grp), "employee_id": line_info(grp[0])["employee_id"],
                                               "merchant": line_info(grp[0])["merchant"],
                                               "expense_date": line_info(grp[0])["expense_date"],
                                               "claim_ids": sorted({line_info(x)["claim_id"] for x in grp}),
                                               "amounts_cents": [line_info(x)["amount_cents"] for x in grp],
                                               "total_cents": sum(line_info(x)["amount_cents"] for x in grp)}
                                              for grp in audit["split"]],
            "weekend_expenses": [line_info(x) for x in audit["weekend"]],
            "missing_category": [line_info(x) for x in audit["missing_category"]],
            "mixed_currency_without_fx": [line_info(x) for x in audit["mixed_currency"]],
            "claims_missing_fx_rate": audit["missing_fx_claims"],
            "outliers": [line_info(seeded["outlier"][0]["id"])],
            "alcohol_in_meals": [line_info(x) for x in audit["alcohol"]],
            "over_policy_limit": [{**line_info(x), "rule": cat} for x, cat in audit["over_policy_limit"]],
            "missing_receipt_over_threshold": [line_info(x) for x in audit["missing_receipt_over_threshold"]],
            "stale_over_60_days": [line_info(x) for x in audit["stale_over_60_days"]],
            "leakage_column": "gl_account_hint",
        },
        "expense_claims": {
            "self_approved": [{"claim_id": c["id"], "employee_id": c["emp"]["id"], "approver_id": c["approver"],
                               "total_usd_cents": c["total_usd"], "status": c["status"]}
                              for c in sorted(seeded["self_approved"], key=lambda c: c["id"])],
            "approved_above_limit": [{"claim_id": c["id"], "employee_id": c["emp"]["id"], "approver_id": c["approver"],
                                      "approver_limit_cents": emp_name[c["approver"]]["limit"],
                                      "total_usd_cents": c["total_usd"], "status": c["status"]}
                                     for c in sorted(seeded["above_limit"], key=lambda c: c["id"])],
            "status_counts": {s: sum(1 for c in claims if c["status"] == s)
                              for s in ("draft", "submitted", "approved", "rejected", "paid")},
        },
        "gl_journal": {
            "weekend_or_holiday": [je_info(x) for x in ga["weekend_or_holiday"]],
            "preparer_never_posts": [je_info(x, {"preparer_department": emp_name[je_by_id[x]["preparer"]]["department"]})
                                     for x in ga["preparer_never_posts"]],
            "post_close": [je_info(x) for x in ga["post_close"]],
            "round_amount_manual": [je_info(x) for x in ga["round_amount"]],
            "just_under_approval_limit": [je_info(x) for x in ga["just_under_limit"]],
            "seldom_used_accounts": ga["seldom_accounts"],
            "seldom_used_account_entries": [je_info(x) for x in ga["seldom_used_account"]],
            "self_approved_manual": [je_info(x) for x in ga["self_approved"]],
            "duplicate_entries": [{"original_je_id": a, "duplicate_je_id": b, "description": je_by_id[a]["desc"],
                                   "total_debit_cents": sum(x[2] for x in je_by_id[a]["lines"])}
                                  for a, b in ga["duplicate"]],
            "intercompany_unmatched": [je_info(x) for x in ga["ic_unmatched"]],
            "unused_accounts": ga["unused_accounts"],
            "je_count": len(L.jes),
            "line_count": sum(len(j["lines"]) for j in L.jes),
        },
        "bank_rec_2026_10": {
            "gl_1010_opening_2026_10_01": gl_open_oct,
            "gl_1010_closing": gl_close_oct,
            "bank_opening": gl_open_oct,
            "bank_closing": bank_close,
            "deposits_in_transit": [{"je_id": j["id"], "date": j["posting"].isoformat(),
                                     "description": j["desc"], "amount_cents": j["lines"][0][2]} for j in g["dit"]],
            "outstanding_payments": [{"payout_id": c["payout_id"], "claim_id": c["id"], "check": c["bank_ref"],
                                      "paid_at": c["paid"].isoformat(), "amount_cents": c["total_usd"],
                                      "je_id": next(j["id"] for j in L.jes if j["tag"] == ("payout", c["id"]))}
                                     for c in outstanding],
            "cleared_checks_not_outstanding": [{"payout_id": c["payout_id"], "check": c["bank_ref"],
                                                "issued": c["paid"].isoformat(), "cleared": c["check_clear"].isoformat(),
                                                "amount_cents": c["total_usd"]}
                                               for c in g["checks"] if c.get("check_clear")],
            "bank_fee_not_booked": {"date": fee["date"].isoformat(), "description": fee["desc"],
                                    "reference": fee["ref"], "amount_cents": fee["amount"]},
            "interest_not_booked": {"date": interest["date"].isoformat(), "description": interest["desc"],
                                    "reference": interest["ref"], "amount_cents": interest["amount"]},
            "gl_duplicate_payment": {"original_je_id": g["dup_pay"][0]["id"], "duplicate_je_id": g["dup_pay"][1]["id"],
                                     "payout_id": g["dup_pay_claim"]["payout_id"], "amount_cents": dup_amt},
            "transposition": {"je_id": g["trans_je"]["id"], "payout_id": seeded["transposition_claim"]["payout_id"],
                              "claim_id": seeded["transposition_claim"]["id"], "gl_amount_cents": 124356,
                              "bank_amount_cents": 123456, "difference_cents": trans_diff},
            "adjusted_bank_balance": adj_bank,
            "adjusted_book_balance": adj_book,
            "unreconciled_difference": adj_bank - adj_book,
        },
        "accrual_2150": {
            "as_of": "2026-10-31",
            "approved_unpaid_claim_count": len(accr_claims),
            "expected_accrual_cents": accrual,
            "gl_2150_credit_balance_cents": gl_2150,
            "difference_cents": accrual - gl_2150,
            "difference_explained_by": {"gl_duplicate_payment_cents": dup_amt, "transposition_cents": trans_diff},
            "opening_2150_2026_09_01_cents": open_accrual,
            "approved_unpaid_claim_ids": sorted(c["id"] for c in accr_claims),
        },
        "budget_variance_2026_10": {
            "level": "account (sum of all cost centers and both entities)",
            "thresholds": {"dollar_cents": THRESH_DOLLAR, "pct": THRESH_PCT},
            "counts": {k: sum(1 for v in variance if v["class"] == k) for k in ("both", "pct_only", "dollar_only", "under")},
            "accounts": variance,
        },
        "pm": {"ticket_counts": dict(TICKET_COUNTS), "ticket_sample_rate": "about 1 in 11 of October tickets"},
    }
    assert key["budget_variance_2026_10"]["counts"] == {"both": 4, "pct_only": 3, "dollar_only": 2, "under": 13}
    files["answer_key.json"] = json.dumps(key, indent=2, default=str) + "\n"
    readme = render_readme(key, files, emps, claims)
    return files, readme


# ----------------------------------------------------------------------------
# README
# ----------------------------------------------------------------------------

DATASETS = {
    "employees": ["employees.csv"],
    "expense_policy": ["expense_policy.json"],
    "expense_claims": ["expense_claims.csv", "expense_lines.csv"],
    "gl_accounts": ["gl_accounts.csv"],
    "gl_journal": ["gl_journal.csv", "gl_opening_balances_2026-09-01.csv", "je_policy.json"],
    "bank": ["bank_statement_2026-10.csv", "gl_balance_1010_2026-10.csv"],
    "budget": ["budget_2026.csv", "context_notes_2026-10.md"],
    "pm": ["usage_metrics.csv", "interview_notes.md", "support_tickets.csv"],
    "payouts": ["payouts_2026-10.csv"],
    "answer_key": ["answer_key.json"],
}

PURPOSE = {
    "employees.csv": "People, org chart and approval limits",
    "expense_policy.json": "Expense policy rules the claims are tested against",
    "expense_claims.csv": "Claim headers, Aug to Oct 2026",
    "expense_lines.csv": "Claim lines (one row per expense)",
    "gl_accounts.csv": "Chart of accounts",
    "gl_journal.csv": "General ledger journal lines, Sep and Oct 2026",
    "gl_opening_balances_2026-09-01.csv": "Balance sheet opening balances at Sep 1 2026",
    "je_policy.json": "Close calendar, holidays and manual JE approval rules",
    "bank_statement_2026-10.csv": "Operating bank account statement, October 2026",
    "gl_balance_1010_2026-10.csv": "GL 1010 and bank opening and closing balances",
    "budget_2026.csv": "Monthly expense budget Aug to Dec 2026 by cost center and account",
    "context_notes_2026-10.md": "Department head notes for the October flux review",
    "usage_metrics.csv": "Northwind Expense product metrics per candidate feature",
    "interview_notes.md": "Six synthetic user interviews",
    "support_tickets.csv": "Sample of October 2026 support tickets",
    "payouts_2026-10.csv": "Reimbursement payouts made in October 2026",
    "answer_key.json": "Machine-readable answer key (same content as the tables below)",
}

COLUMNS = {
    "employees.csv": [
        ("employee_id", "string", "E0001 to E0120"),
        ("name", "string", "Fictional first and last name"),
        ("department", "string", "Sales, Engineering, Finance, Marketing, Support or Operations"),
        ("role", "string", "IC, Manager, Director or VP"),
        ("title", "string", "Job title. Finance titles identify the JE preparers and approvers"),
        ("manager_id", "string", "employee_id of the direct manager; blank for VPs"),
        ("approval_limit_cents", "int", "Max claim total in USD cents this person can approve: IC 0, Manager 250000, Director 1000000, VP 5000000"),
        ("cost_center", "string", "CC-SAL, CC-ENG, CC-FIN, CC-MKT, CC-SUP, CC-OPS (one per department)"),
        ("hire_date", "date", "ISO date"),
    ],
    "expense_claims.csv": [
        ("claim_id", "string", "C-00001 onward, ordered by submitted_at (drafts by creation time)"),
        ("employee_id", "string", "Submitter, joins employees.csv"),
        ("submitted_at", "datetime", "ISO local datetime; blank for drafts"),
        ("status", "string", "draft, submitted (pending approval), approved (not yet paid), rejected, paid"),
        ("approver_id", "string", "Who approved or rejected; blank for draft and submitted"),
        ("approved_at", "datetime", "Approval datetime for approved and paid; blank otherwise"),
        ("total_cents", "int", "Sum of line amount_cents, in the claim currency"),
        ("currency", "string", "USD, EUR, GBP or CAD"),
        ("fx_rate", "decimal string", "USD per 1 unit of claim currency, 4 decimals; 1.0000 for USD; blank means missing (seeded anomaly)"),
        ("paid_at", "date", "Payout run date for paid claims"),
    ],
    "expense_lines.csv": [
        ("line_id", "string", "L-000001 onward, grouped by claim"),
        ("claim_id", "string", "Joins expense_claims.csv"),
        ("expense_date", "date", "Date the expense happened"),
        ("merchant", "string", "Clean merchant name"),
        ("merchant_category_text", "string", "Raw card descriptor text (for example RIDEO *TRIP, SKYLARK AIR 0062, BOXMART MKTP US*2K4)"),
        ("category", "string", "Policy category label; blank for a few seeded lines"),
        ("amount_cents", "int", "Amount in currency"),
        ("currency", "string", "Line currency; equals the claim currency except 3 seeded lines"),
        ("receipt_attached", "bool", "true or false"),
        ("description", "string", "Employee free text"),
        ("attendees_count", "int", "People covered, Meals and Client entertainment only; blank otherwise"),
        ("gl_account_hint", "string", "GL account for the category (LEAKAGE: a 1:1 copy of the label, see answer key)"),
    ],
    "gl_accounts.csv": [
        ("account", "string", "4-digit account number"),
        ("name", "string", "Account name"),
        ("type", "string", "asset, liability, equity, revenue or expense"),
        ("normal_balance", "string", "debit or credit"),
    ],
    "gl_journal.csv": [
        ("je_id", "string", "JE-000001 onward, ordered by posting_date then source"),
        ("line_no", "int", "Line number within the entry"),
        ("entity", "string", "NW-US or NW-CA"),
        ("posting_date", "date", "Accounting date"),
        ("entry_date", "date", "Date the entry was keyed"),
        ("period", "string", "YYYY-MM of posting_date"),
        ("account", "string", "Joins gl_accounts.csv"),
        ("cost_center", "string", "Set on expense lines; blank on balance sheet and revenue lines"),
        ("debit_cents", "int", "Debit amount, USD cents (0 when the line is a credit)"),
        ("credit_cents", "int", "Credit amount, USD cents (0 when the line is a debit)"),
        ("description", "string", "Entry description; carries the claim, payout, invoice or bank reference"),
        ("source", "string", "AP, EXP, PAYROLL, MANUAL or SYSTEM"),
        ("preparer_id", "string", "employee_id, or SVC-EXPENSE / SVC-GL for system postings"),
        ("approver_id", "string", "employee_id; blank for EXP and SYSTEM postings"),
    ],
    "gl_opening_balances_2026-09-01.csv": [
        ("entity", "string", "NW-US or NW-CA"),
        ("account", "string", "Balance sheet account"),
        ("name", "string", "Account name"),
        ("balance_cents", "int", "Signed balance, debit positive, credit negative. Sums to 0 per entity"),
    ],
    "bank_statement_2026-10.csv": [
        ("date", "date", "Bank posting date"),
        ("description", "string", "Bank text"),
        ("amount_cents", "int", "Signed: deposits positive, withdrawals negative"),
        ("reference", "string", "Bank reference. Matches the token in the GL description (RCPT-, NWR, CHK, INV-, PR-, MSF-)"),
        ("balance_cents", "int", "Running balance after the row"),
    ],
    "gl_balance_1010_2026-10.csv": [
        ("metric", "string", "Which balance"),
        ("amount_cents", "int", "Balance, USD cents"),
    ],
    "budget_2026.csv": [
        ("month", "string", "YYYY-MM, 2026-08 to 2026-12"),
        ("cost_center", "string", "Cost center"),
        ("account", "string", "Expense account (6000 to 6800)"),
        ("budget_cents", "int", "Budget, USD cents"),
    ],
    "payouts_2026-10.csv": [
        ("payout_id", "string", "PO-000001 onward across Aug to Oct; this file holds October only"),
        ("claim_id", "string", "Joins expense_claims.csv"),
        ("employee_id", "string", "Payee"),
        ("amount_cents", "int", "USD amount paid (claim total converted per line at the claim fx_rate)"),
        ("currency", "string", "Always USD"),
        ("method", "string", "ACH or CHECK"),
        ("paid_at", "date", "Payout run date (Thursdays)"),
        ("status", "string", "sent (the payout system does not know bank clearing)"),
        ("bank_reference", "string", "ACH trace (NWR...) or check number (CHK ...)"),
    ],
    "usage_metrics.csv": [
        ("feature", "string", "Candidate feature for the Northwind Expense app"),
        ("area", "string", "Pain area: receipts, approvals, mobile, currency, policy, other"),
        ("monthly_active_users", "int", "Users who touch this workflow area in a month today"),
        ("support_tickets_per_month", "int", "Tickets per month in this area today"),
        ("avg_minutes_to_submit_claim", "decimal", "Average minutes to submit a claim that touches this area"),
    ],
    "support_tickets.csv": [
        ("ticket_id", "string", "T-1001 onward"),
        ("created_at", "datetime", "ISO local datetime, October 2026"),
        ("category", "string", "receipts, approvals, mobile, currency, policy, other"),
        ("text", "string", "Ticket text"),
    ],
}


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def count_rows(text, name):
    if name.endswith(".csv"):
        return str(text.count("\n") - 1)
    return ""


def render_readme(key, files, emps, claims):
    E = key["expense_lines"]
    C = key["expense_claims"]
    G = key["gl_journal"]
    B = key["bank_rec_2026_10"]
    A = key["accrual_2150"]
    V = key["budget_variance_2026_10"]
    p = []
    w = p.append
    w("# Northwind Co. synthetic dataset (expense claims and reimbursement)\n")
    w("One dataset for every persona. Engineers, PMs, designers, data scientists and accountants all work on the "
      "same fictional company, Northwind Co., so a number one persona finds is the same number another persona "
      "sees. Northwind sells an expense app (Northwind Expense) and runs its own employee reimbursements on it.\n")
    w("Everything here is synthetic. Company, people, merchants, vendors and customers are invented. Merchant "
      "descriptor strings imitate card statement text but name made-up merchants. There are no real card numbers.\n")
    w("This README is the answer key for exercise authors. Every seeded anomaly is listed with its exact row "
      "identifiers. The same content is in `northwind/answer_key.json`.\n")
    w("## Regenerate\n")
    w("```bash\npython3 exercises/_data/generate.py                 # default seed 2026, writes northwind/ and this README\n"
      "python3 exercises/_data/generate.py --seed 7 --out /tmp/nw   # another seed, README goes into /tmp/nw\n"
      "python3 exercises/_data/generate.py --only gl_journal        # write one dataset only\n"
      "python3 exercises/_data/test_generate.py                     # self-check\n```\n")
    w("Python 3.11 or newer, standard library only. The same seed gives byte-identical files. The pre-generated "
      "files in `northwind/` use seed 2026; students do not need to run anything. The answer key below is for "
      "seed 2026 only. Another seed moves every identifier.\n")
    w("Dataset names for `--only`: " + ", ".join(f"`{k}`" for k in DATASETS) + ".\n")
    w("## Conventions\n")
    w("- Money is integer cents in columns ending `_cents`. GL, bank, budget and payouts are USD. Claims and lines "
      "are in their `currency`.\n"
      "- USD value of a claim line = `amount_cents x fx_rate` from its claim, rounded half up to the cent. A claim's "
      "USD total is the sum of its line USD values. Approval limits, policy limits, the GL and payouts all use "
      "this USD value.\n"
      "- Dates are ISO 8601 (`2026-10-31`). Datetimes are local time without a zone (`2026-10-30T14:05:00`).\n"
      "- Close month is October 2026 (`2026-10`). Prior month is September 2026 (`2026-09`).\n"
      "- Claims snapshot: end of day 2026-10-31. Claims cover submissions from 2026-08-01 to 2026-10-31.\n"
      "- GL covers postings from 2026-09-01 to 2026-10-31, extracted on 2026-11-12 (so it includes late entries).\n"
      f"- Close dates: September closes {SEP_CLOSE.isoformat()}, October closes {OCT_CLOSE.isoformat()}.\n"
      "- Company holidays: 2026-09-07 (Labor Day) and 2026-10-12 (Indigenous Peoples' Day). Business days are "
      "Monday to Friday excluding these.\n"
      "- Payout runs are every Thursday. An approved claim is paid in the first run at least 2 days after approval.\n"
      "- Entities: NW-US (all claims, cash, payroll) and NW-CA (a small Canadian entity, reported in USD).\n")
    w("## Files\n")
    rows = []
    for name in sorted(files):
        rows.append([f"`{name}`", count_rows(files[name], name), PURPOSE.get(name, "")])
    w(md_table(["file", "rows", "purpose"], rows) + "\n")
    w("## Column reference\n")
    for name, cols in COLUMNS.items():
        w(f"### {name}\n")
        w(md_table(["column", "type", "meaning"], [[f"`{c}`", t, m] for c, t, m in cols]) + "\n")
    w("### expense_policy.json\n")
    w("Category limits (`limit_cents` and `per`), `receipt_required_over_cents` (7500), `max_age_days` (60), "
      "`weekend_expenses` (`flag_for_review`), `non_reimbursable` (includes alcohol), approval chain rules and "
      "limits, foreign currency rule, payout rule.\n")
    w("### je_policy.json\n")
    w("Entities, close calendar and close rule, company holidays, manual JE approval limit (1000000 cents: "
      "Controller needed at or above it), preparer rule, source codes, intercompany rule, GL extract date.\n")
    w("### Markdown files\n")
    w("- `context_notes_2026-10.md`: memo-style notes from department heads for the October flux review.\n"
      "- `interview_notes.md`: six short user interviews (P1 to P6) about receipts, slow approvals, mobile, "
      "currency and policy confusion.\n")

    # --- answer key ----------------------------------------------------------
    w("# Answer key (seed 2026)\n")
    w("## Summary\n")
    summary = [
        ["Exact duplicate lines across claims", len(E["exact_duplicates"]), "expense_lines.csv", "A1"],
        ["Near-duplicate lines (1 cent or 1 day)", len(E["near_duplicates"]), "expense_lines.csv", "A2"],
        ["Split groups just under receipt threshold", len(E["split_under_receipt_threshold"]), "expense_lines.csv", "A3"],
        ["Weekend expense lines", len(E["weekend_expenses"]), "expense_lines.csv", "A4"],
        ["Lines with missing category", len(E["missing_category"]), "expense_lines.csv", "A5"],
        ["Mixed currency lines, claim fx_rate blank", len(E["mixed_currency_without_fx"]), "expense_lines.csv", "A6"],
        ["Outlier ($9,800 office supplies)", len(E["outliers"]), "expense_lines.csv", "A7"],
        ["Alcohol lines in Meals", len(E["alcohol_in_meals"]), "expense_lines.csv", "A8"],
        ["Over policy limit lines", len(E["over_policy_limit"]), "expense_lines.csv", "A9"],
        ["Missing receipt over $75", len(E["missing_receipt_over_threshold"]), "expense_lines.csv", "A10"],
        ["Older than 60 days at submission", len(E["stale_over_60_days"]), "expense_lines.csv", "A11"],
        ["Leakage column", 1, "expense_lines.csv", "A12"],
        ["Self-approved claims", len(C["self_approved"]), "expense_claims.csv", "B1"],
        ["Claims approved above approver limit", len(C["approved_above_limit"]), "expense_claims.csv", "B2"],
        ["JE weekend or holiday postings", len(G["weekend_or_holiday"]), "gl_journal.csv", "C1"],
        ["JE by people who never post", len(G["preparer_never_posts"]), "gl_journal.csv", "C2"],
        ["JE entered after close", len(G["post_close"]), "gl_journal.csv", "C3"],
        ["Round-amount manual JEs", len(G["round_amount_manual"]), "gl_journal.csv", "C4"],
        ["Manual JEs just under $10,000", len(G["just_under_approval_limit"]), "gl_journal.csv", "C5"],
        ["JEs to seldom-used accounts", len(G["seldom_used_account_entries"]), "gl_journal.csv", "C6"],
        ["Self-approved manual JEs", len(G["self_approved_manual"]), "gl_journal.csv", "C7"],
        ["Duplicate JEs (pairs)", len(G["duplicate_entries"]), "gl_journal.csv", "C8"],
        ["Intercompany entry with no NW-CA offset", len(G["intercompany_unmatched"]), "gl_journal.csv", "C9"],
        ["Bank rec reconciling items", 9, "bank_statement_2026-10.csv", "D"],
        ["Reimbursement accrual tie-out", 1, "payouts, claims, GL 2150", "E"],
        ["Budget accounts over both thresholds", V["counts"]["both"], "budget_2026.csv", "F"],
        ["Budget accounts over % only", V["counts"]["pct_only"], "budget_2026.csv", "F"],
        ["Budget accounts over $ only", V["counts"]["dollar_only"], "budget_2026.csv", "F"],
    ]
    w(md_table(["anomaly", "count", "file", "section"], summary) + "\n")
    w("Every list below was produced by running the stated detection rule over the final files, and the "
      "generator asserts that the rule finds exactly the seeded rows and nothing else.\n")

    def lt(items, cols):
        return md_table(cols, [[x[c] for c in cols] for x in items]) + "\n"

    sc = C["status_counts"]
    w(f"Claim status counts: draft {sc['draft']}, submitted {sc['submitted']}, approved {sc['approved']}, "
      f"rejected {sc['rejected']}, paid {sc['paid']}.\n")
    w("## A. Expense lines\n")
    w("### A1. Exact duplicates across different claims\n")
    w("Rule: same employee (via claim), `merchant`, `expense_date`, `amount_cents` and `currency`, on two "
      "different claims. The later line_id is the duplicate.\n")
    w(lt(E["exact_duplicates"], ["original_line_id", "duplicate_line_id", "claim_id", "employee_id", "merchant",
                                 "expense_date", "amount_cents"]))
    w("`claim_id` is the claim holding the duplicate line.\n")
    w("### A2. Near-duplicates\n")
    w("Rule: same employee, `merchant` and `currency`, and either the same date with amounts 1 cent apart "
      "(`amount_1_cent`) or the same amount with dates 1 day apart (`date_1_day`). Pairs are on different claims.\n")
    w(lt(E["near_duplicates"], ["line_id_a", "line_id_b", "kind", "employee_id", "merchant", "date_a", "date_b",
                                "amount_a", "amount_b"]))
    w("### A3. Split claims just under the receipt threshold\n")
    w("Rule: same employee, `merchant` and `expense_date`, two or more lines each between 6000 and 7499 USD "
      "cents, summing to more than 7500. None has a receipt. Each group spans two claims.\n")
    rows = [[", ".join(x["line_ids"]), x["employee_id"], x["merchant"], x["expense_date"], ", ".join(x["claim_ids"]),
             ", ".join(str(a) for a in x["amounts_cents"]), x["total_cents"]] for x in E["split_under_receipt_threshold"]]
    w(md_table(["line_ids", "employee_id", "merchant", "expense_date", "claim_ids", "amounts_cents", "total_cents"],
               rows) + "\n")
    w("### A4. Weekend expenses\n")
    w("Rule: `expense_date` is a Saturday or Sunday. Normal lines are all on weekdays, so every weekend line is "
      "seeded.\n")
    w(lt(E["weekend_expenses"], ["line_id", "claim_id", "employee_id", "expense_date", "merchant", "category",
                                 "amount_cents"]))
    w("### A5. Missing category\n")
    w("Rule: `category` is blank (and so is `gl_account_hint`). If approved, these post to 6190 Other Travel and "
      "Expense (Uncategorized).\n")
    w(lt(E["missing_category"], ["line_id", "claim_id", "employee_id", "merchant", "amount_cents"]))
    w("### A6. Mixed currency without fx_rate\n")
    w("Rule: line `currency` differs from its claim `currency`. Each of these claims has a blank `fx_rate` and a "
      "`total_cents` that naively adds amounts in two currencies. All three claims are still `submitted`, so they "
      "are not in the GL.\n")
    w(lt(E["mixed_currency_without_fx"], ["line_id", "claim_id", "employee_id", "currency", "amount_cents"]))
    w("Claims with blank fx_rate: " + ", ".join(E["claims_missing_fx_rate"]) + ".\n")
    w("### A7. Outlier\n")
    o = E["outliers"][0]
    w(f"`{o['line_id']}` on claim `{o['claim_id']}` ({o['employee_id']}): Office supplies at {o['merchant']}, "
      f"{money(o['amount_cents'])} on {o['expense_date']}. Normal office supplies lines are under $240. It was "
      "approved in October and posted to 6150, which is why 6150 is a %-only flux item. It also breaks the "
      "$500 per line Office supplies limit (A9).\n")
    w("### A8. Alcohol in Meals\n")
    w("Rule: `description` contains one of " + ", ".join(f"`{k}`" for k in ALCOHOL_KEYWORDS) +
      " (case-insensitive). All are Meals lines; 6 are at the merchant Copper Kettle Taproom. Alcohol is not "
      "reimbursable.\n")
    w(lt(E["alcohol_in_meals"], ["line_id", "claim_id", "employee_id", "merchant", "expense_date", "amount_cents"]))
    w("### A9. Over policy limit\n")
    w("Rule: per `expense_policy.json` on USD values. Meals: sum per employee per date above 7500 x attendees. "
      "Lodging above 30000 per line (one line per night). Office supplies above 50000 per line.\n")
    w(lt(E["over_policy_limit"], ["line_id", "claim_id", "employee_id", "rule", "amount_cents"]))
    w("### A10. Missing receipt over the threshold\n")
    w("Rule: USD value above 7500 and `receipt_attached` is false.\n")
    w(lt(E["missing_receipt_over_threshold"], ["line_id", "claim_id", "employee_id", "category", "amount_cents"]))
    w("### A11. Older than 60 days\n")
    w("Rule: claim `submitted_at` date minus `expense_date` is more than 60 days.\n")
    w(lt(E["stale_over_60_days"], ["line_id", "claim_id", "employee_id", "expense_date", "category"]))
    w("### A12. Leakage column (data science trap)\n")
    w("`gl_account_hint` is filled from `category` after labeling (Meals 6100, Lodging 6110, Airfare 6120, Ground "
      "transport 6130, Software 6140, Office supplies 6150, Training 6160, Client entertainment 6170; blank when "
      "category is blank). A classifier that predicts `category` with this column as a feature scores close to "
      "100% and is useless in production, where the hint does not exist yet. Drop it. Also note that Boxmart "
      "Marketplace appears under both Software and Office supplies, so merchant alone is not enough.\n")

    w("## B. Expense claims\n")
    w("### B1. Self-approved claims\n")
    w("Rule: `approver_id` equals `employee_id`.\n")
    w(lt(C["self_approved"], ["claim_id", "employee_id", "approver_id", "total_usd_cents", "status"]))
    w("### B2. Approved above the approver's limit\n")
    w("Rule: claim USD total above the approver's `approval_limit_cents`. In each case an IC's own Manager "
      "(limit 250000) approved a claim that needed a Director.\n")
    w(lt(C["approved_above_limit"], ["claim_id", "employee_id", "approver_id", "approver_limit_cents",
                                     "total_usd_cents", "status"]))

    w("## C. Journal entry testing (gl_journal.csv)\n")
    w(f"{G['je_count']} entries, {G['line_count']} lines. Every `je_id` balances (sum of debits equals sum of "
      "credits). Each seeded entry carries one flag only.\n")
    jcols = ["je_id", "entity", "posting_date", "entry_date", "source", "preparer_id", "approver_id",
             "total_debit_cents", "description"]
    w("### C1. Weekend or holiday postings\n")
    w("Rule: `posting_date` is a Saturday, Sunday or company holiday.\n")
    w(lt(G["weekend_or_holiday"], jcols))
    w("### C2. Entries by people who normally never post\n")
    w("Rule: `preparer_id` is not a Finance employee and not a service account. Each of these people appears as "
      "preparer exactly once.\n")
    w(lt(G["preparer_never_posts"], jcols + ["preparer_department"]))
    w("### C3. Entered after period close\n")
    w(f"Rule: period 2026-10 with `entry_date` after {OCT_CLOSE.isoformat()} (or period 2026-09 after "
      f"{SEP_CLOSE.isoformat()}; there are none). All three are balance sheet or revenue entries, so they do not "
      "move the expense flux.\n")
    w(lt(G["post_close"], jcols))
    w("### C4. Round-amount manual entries\n")
    w("Rule: source MANUAL and a line amount that is a whole multiple of $1,000.00.\n")
    w(lt(G["round_amount_manual"], jcols))
    w("### C5. Just under the manual JE approval limit\n")
    w("Rule: source MANUAL with total debits from $9,500.00 to $9,999.99. All were approved by the Accounting "
      "Manager; at $10,000.00 they would have needed the Controller.\n")
    w(lt(G["just_under_approval_limit"], jcols))
    w("### C6. Entries to seldom-used accounts\n")
    w("Rule: accounts used by 1 or 2 entries in the two months: " + ", ".join(G["seldom_used_accounts"]) +
      ". Accounts in the chart with no activity at all: " + ", ".join(G["unused_accounts"]) + ".\n")
    w(lt(G["seldom_used_account_entries"], jcols + ["accounts"]))
    w("### C7. Self-approved manual entries\n")
    w("Rule: `preparer_id` equals `approver_id`.\n")
    w(lt(G["self_approved_manual"], jcols))
    w("### C8. Duplicate entries\n")
    w("Rule: same entity, `posting_date`, `description` and identical lines on two `je_id`s. The second is the "
      "duplicate. The AP one double-books a vendor invoice to Prepaid; the EXP one double-books a reimbursement "
      "payout and is also a bank rec item (D).\n")
    w(lt(G["duplicate_entries"], ["original_je_id", "duplicate_je_id", "total_debit_cents", "description"]))
    w("### C9. Intercompany entry with no offset\n")
    w("Rule: an IC reference (IC-YYMM-NN in the description) booked in NW-US with no NW-CA entry for the same "
      "reference. Five IC references are paired; this one is not. NW-US 1310 will not agree with NW-CA 2310 by "
      "this amount.\n")
    w(lt(G["intercompany_unmatched"], jcols))

    w("## D. Bank reconciliation, October 2026 (account 1010, NW-US)\n")
    w(md_table(["item", "amount"], [
        ["GL 1010 opening 2026-10-01 (equals bank opening; September reconciled with no open items)",
         money(B["gl_1010_opening_2026_10_01"])],
        ["GL 1010 closing 2026-10-31", money(B["gl_1010_closing"])],
        ["Bank closing 2026-10-31", money(B["bank_closing"])],
    ]) + "\n")
    w("Reconciling items:\n")
    rows = []
    for x in B["deposits_in_transit"]:
        rows.append(["Deposit in transit (bank side, add)", x["je_id"], x["description"], money(x["amount_cents"])])
    for x in B["outstanding_payments"]:
        rows.append(["Outstanding check (bank side, subtract)", x["je_id"],
                     f"{x['payout_id']} {x['claim_id']} {x['check']} issued {x['paid_at']}", money(-x["amount_cents"])])
    f_ = B["bank_fee_not_booked"]
    i_ = B["interest_not_booked"]
    rows.append(["Bank fee not booked (book side, subtract)", "", f"{f_['date']} {f_['description']} {f_['reference']}",
                 money(f_["amount_cents"])])
    rows.append(["Interest not booked (book side, add)", "", f"{i_['date']} {i_['description']} {i_['reference']}",
                 money(i_["amount_cents"])])
    dp = B["gl_duplicate_payment"]
    rows.append(["GL duplicate payment (book side, add back)", dp["duplicate_je_id"],
                 f"duplicate of {dp['original_je_id']}, {dp['payout_id']}", money(dp["amount_cents"])])
    t = B["transposition"]
    rows.append(["Transposition (book side, add back)", t["je_id"],
                 f"{t['payout_id']} {t['claim_id']}: GL {money(t['gl_amount_cents'])}, bank {money(t['bank_amount_cents'])}",
                 money(t["difference_cents"])])
    w(md_table(["item", "je_id", "detail", "amount"], rows) + "\n")
    w(f"Adjusted bank = bank closing + deposits in transit - outstanding checks = {money(B['adjusted_bank_balance'])}.\n\n"
      f"Adjusted book = GL closing - fee + interest + duplicate + transposition = {money(B['adjusted_book_balance'])}.\n\n"
      f"Unreconciled difference: {money(B['unreconciled_difference'])}.\n")
    cc = B["cleared_checks_not_outstanding"]
    w("Distractors: two other October checks cleared a few days after issue and are not reconciling items: " +
      "; ".join(f"{x['payout_id']} {x['check']} issued {x['issued']}, cleared {x['cleared']}" for x in cc) +
      ". Every other bank row matches one GL 1010 line by reference and amount.\n")

    w("## E. Reimbursement accrual (2150 Accrued Reimbursements) at 2026-10-31\n")
    w(md_table(["item", "value"], [
        ["Approved but unpaid claims (status approved)", A["approved_unpaid_claim_count"]],
        ["Expected accrual (sum of their USD totals)", money(A["expected_accrual_cents"])],
        ["GL 2150 credit balance at 2026-10-31 (opening + Sep and Oct activity)", money(A["gl_2150_credit_balance_cents"])],
        ["Difference (expected minus GL)", money(A["difference_cents"])],
        ["Explained by GL duplicate payment (D)", money(A["difference_explained_by"]["gl_duplicate_payment_cents"])],
        ["Explained by transposition (D)", money(A["difference_explained_by"]["transposition_cents"])],
        ["2150 opening balance 2026-09-01", money(A["opening_2150_2026_09_01_cents"])],
    ]) + "\n")
    w("The approved-unpaid claim ids are listed in `answer_key.json` under `accrual_2150`. October payouts in "
      "`payouts_2026-10.csv` tie to the EXP payout entries in the GL except the duplicate and the transposition. "
      "All three outstanding checks are paid in the payout system, so they are not in the accrual.\n")

    w("## F. Budget variance, October 2026\n")
    w("Level: account, summing all cost centers and both entities. Actual = sum(debit - credit) in "
      "`gl_journal.csv` for the period. Thresholds: more than $10,000.00 AND more than 10%. The same "
      "classification holds for Oct actual vs Oct budget and for Oct actual vs Sep actual. Classes: `both` "
      "(over $ and %), `pct_only` (small accounts), `dollar_only` (large accounts), `under`. The classification "
      "is on the GL as given, before any correcting entries. Unbudgeted accounts with activity (6950, 6990, "
      "revenue and balance sheet) are outside the budget file.\n")
    rows = []
    for v in V["accounts"]:
        rows.append([v["account"], v["name"], v["class"], money(v["budget_oct_cents"]), money(v["actual_sep_cents"]),
                     money(v["actual_oct_cents"]), money(v["var_vs_budget_cents"]), f"{v['var_vs_budget_pct']}%",
                     money(v["var_vs_sep_cents"]), f"{v['var_vs_sep_pct']}%", v["explanation_status"]])
    w(md_table(["account", "name", "class", "budget Oct", "actual Sep", "actual Oct", "vs budget", "%", "vs Sep", "%",
                "explanation"], rows) + "\n")
    w("Explanations using `context_notes_2026-10.md`:\n")
    for v in V["accounts"]:
        if v["explanation"]:
            w(f"- {v['account']} {v['name']} ({v['class']}): {v['explanation']}.")
    w("")
    w("Expected student result: explain 6160, 6180 and 6400 from the notes; flag 6300 Professional Fees as "
      "\"owner to explain\". The Operations note (office move) and the Support note do not match any variance. "
      "The November budget carries the offsite (6180, CC-SAL, +$45,000.00) and the campaign (6400, CC-MKT, "
      "+$35,000.00) that moved into October.\n")
    w("## G. PM data\n")
    w("`support_tickets.csv` is a sample of about 1 in 11 October tickets. Counts by category: " +
      ", ".join(f"{k} {v}" for k, v in key["pm"]["ticket_counts"].items()) + ". `usage_metrics.csv` totals per "
      "area roughly match the sample ratio. Interview themes map to the same areas: receipts (P1, P4), approvals "
      "(P2), mobile (P3), currency (P4, P5), policy confusion (P6). The claims data backs this up: duplicate "
      "submissions (A1, A2), missing fx (A6) and policy misses (A9, A10) are the problems the interviews "
      "describe.\n")
    text = "\n".join(p) + "\n"
    assert "—" not in text
    return text


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate the Northwind Co. synthetic dataset.")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", choices=sorted(DATASETS), default=None)
    ap.add_argument("--readme", default=None, help="README path (default: next to generate.py for the default "
                                                   "--out, otherwise inside --out)")
    args = ap.parse_args(argv)
    files, readme = build(args.seed)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    names = DATASETS[args.only] if args.only else sorted(files)
    for name in names:
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="") as f:
            f.write(files[name])
    if args.only in (None, "answer_key"):
        readme_path = args.readme or (DEFAULT_README if out == os.path.abspath(DEFAULT_OUT)
                                      else os.path.join(out, "README.md"))
        with open(readme_path, "w", encoding="utf-8", newline="") as f:
            f.write(readme)
    for name in names:
        size = os.path.getsize(os.path.join(out, name))
        print(f"{name:40s} {size:>10,d} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
