# Data Scientist Persona — Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. AI code assistant

Install one of:
- **Cursor IDE:** https://cursor.sh
- **Claude Code:** https://docs.anthropic.com/en/docs/claude-code/overview

Verify it launches and can open the course repo directory.

## 2. Python 3.11+

This persona requires Python 3.11 or later.

```bash
python3 --version
# Should print: Python 3.11.x or higher
```

Also verify `pip` and `venv` are available:

```bash
python3 -m pip --version
python3 -m venv --help
```

## 3. Jupyter

Install JupyterLab and the classic notebook interface:

```bash
pip install jupyterlab notebook
```

Verify:

```bash
jupyter lab --version
```

## 4. Core DS libraries

```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

Verify:

```bash
python3 -c "import pandas, numpy, sklearn, matplotlib, seaborn; print('OK')"
```

## 5. Optional: Deep learning

Install whichever framework you plan to use during class:

```bash
# PyTorch
pip install torch

# TensorFlow
pip install tensorflow
```

If you are unsure, install PyTorch — it is the most common in course exercises.

## 6. jq CLI tool

The `notebook-lint.sh` hook parses `.ipynb` files using `jq`. This tool must be installed on your system.

**macOS:**
```bash
brew install jq
```

**Ubuntu / Debian:**
```bash
apt install jq
```

**Windows (Git Bash or WSL):**
```bash
# WSL (Ubuntu)
sudo apt install jq

# Or download from: https://stedolan.github.io/jq/download/
```

Verify:

```bash
jq --version
# Should print: jq-1.6 or higher
```

## 7. Repository access

Clone the course repo:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

If your instructor provided a `client-config.zip`, unzip it into the repo root:

```bash
unzip ~/client-config.zip
# should create client-config/ in the repo root
```

## 8. Smoke test

In the repo root, open your AI tool and run:

- **Cursor:** `@set-persona`
- **Claude Code:** `/set-persona`

Pick `data-scientist`. You should see a confirmation listing the DS commands, subagents, hooks, and MCP servers.

Then run `/setup-stack python-datascience`. You should see a confirmation that the DS stack is configured alongside the data scientist persona.

If either step fails, contact the instructor before class.
