# Accountant Persona: Pre-Class Setup

Complete every item below before class. The instructor cannot wait for installs during the session. You do not need to be a programmer; each step is one or two commands to copy and paste.

## 1. Cursor

Install Cursor: https://cursor.com

Open the course repo folder in Cursor and confirm the chat panel opens.

## 2. Python 3.11+

```bash
python3 --version
# Should print: Python 3.11.x or higher
```

Windows: use `py --version`. If Python is missing, install it from https://www.python.org/downloads/ and tick "Add Python to PATH".

## 3. A virtual environment (pick one)

**Option A: uv (faster)**

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

uv --version
```

**Option B: venv (built into Python)**

```bash
python3 -m venv --help
```

You will create the environment in step 6.

## 4. Node.js 18+ (for the filesystem MCP)

The pack's only MCP server runs with `npx`.

```bash
node --version
# Should print v18 or higher
```

If Node is missing, install the LTS version from https://nodejs.org. Without it, the commands still work; only the MCP server is skipped.

## 5. Excel (optional)

Excel or any spreadsheet app is useful for viewing CSV and XLSX files. It is not required. When you change a workbook that the assistant should read, save it first; the assistant reads saved files only.

## 6. Smoke test

**Spreadsheet stack (`sheets-accounting`, the default).** No install needed. Open `stacks/sheets-accounting/examples/bank-rec-toy/working/recon-1010-2026-03.csv` in Excel or Google Sheets, filter the `section` column to `TIE-OUT`, and confirm eight rows that read 0.00 or 0 with status PASS. If the file opens with every value in one column, import it as comma separated (Excel: Data > From Text/CSV; Sheets: File > Import).

**Scripted stack (`python-accounting`, optional).** Only if you plan to use Python. Steps 2 and 3 above are needed for this one only. From the repo root:

```bash
cd stacks/python-accounting/examples/bank-rec

# Option A: uv
uv venv && uv pip install -r requirements.txt
.venv/bin/python src/reconcile.py
.venv/bin/python -m pytest -q

# Option B: venv
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
.venv/bin/python3 src/reconcile.py
.venv/bin/python3 -m pytest -q
```

Windows: replace `.venv/bin/python3` with `.venv\Scripts\python`.

You should see `difference: 0.00` and `17 passed`. Generated files in `output/` are git-ignored, so the repo stays clean. `/setup-stack` later copies a fresh example into your workspace.

## 7. Persona install

In Cursor chat, from the repo root:

```
/set-persona accountant
/setup-stack accountant
```

The first prints the commands, agents, hooks and MCP server it installed. The second shows the stack menu: press Enter for `sheets-accounting` (copies its templates and `examples/bank-rec-toy/` into `workspaces/accountant/`), or pick `python-accounting` (copies its templates and `examples/bank-rec/`).

If either step fails, contact the instructor before class.

## Data rules for this course

- Synthetic Northwind Co. data only. Never load real company data, real bank statements or real employee details.
- Source files go in `workspaces/accountant/data/raw/` and are never edited after that.
