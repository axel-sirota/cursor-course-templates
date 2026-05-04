# Project Context: Python Data Science

## Tech Stack
- **Language**: Python 3.11+
- **Notebook**: JupyterLab / Jupyter Notebook
- **Data manipulation**: pandas 2.x, numpy 1.x
- **ML**: scikit-learn (default), pytorch / tensorflow (optional)
- **Visualization**: matplotlib, seaborn
- **Testing**: pytest (pipeline tests), nbval (notebook tests)
- **Linting**: ruff, nbqa (applies ruff to notebooks)

## Vibe & Style
- **Coding Style**: snake_case, PEP 8
- **Architecture**: Notebook-first for exploration; .py modules for reusable pipelines
- **Data flow**: raw → processed → features → model → evaluation

## Key Rules
- Seed every experiment before any random operation
- No raw data committed — paths and hashes only
- Notebooks run top-to-bottom (clear + re-run before handoff)
- Log every experiment with params, metrics, seed, and artifact paths
- Model card required before handoff

## Active Phase
- Current: Explore (EDA)

## Active Persona
- (set by /set-persona)
