# Data Scientist Persona: Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. Cursor

Install **Cursor IDE**: https://cursor.sh

Verify it launches and can open the course repo directory.

## 2. Python 3.11+

This persona requires Python 3.11 or later. If you pick the r-tidyverse stack, also install R (see that stack's README).

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

If you are unsure, install PyTorch. It is the most common in course exercises.

## 6. jq CLI tool

The `seed-check.sh` and `notebook-lint.sh` hooks parse `.ipynb` files using `jq`.

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

## 8. Smoke test

Open the repo in Cursor and run in the chat:

```
/set-persona add data-scientist
/setup-stack data-scientist
```

After the first command you should see a confirmation listing the DS commands, subagents, hooks, MCP servers and the new `workspaces/data-scientist/` folder. Pick `python-datascience` at the second; the `## Persona: data-scientist` block in `.cursor/context.md` should then show that stack.

If either step fails, contact the instructor before class.
