# Choose Your Adventure

This course has multiple paths. Pick the one that matches what you're building — or what you want to learn.

---

## How to Choose

Answer two questions:
1. **What is your role?** → Pick a persona
2. **What are you building?** → Pick a stack (engineer / data-scientist / devops only — designer + pm skip this)

Then run the full SDD pipeline in order:
```
/set-persona     (pick your role — MANDATORY first step)
/setup-stack     (pick your stack; designer + pm skip)
/architect "..."  (design the phases + session plan for what you want to build)
/start-session   (execute the first session)
/next-session    (wrap up and hand off to next time)
```

Use `/undo persona` / `/undo stack` / `/undo all` to roll back installs cleanly when experimenting.

For brownfield (existing repo), substitute `/detect-stack` for `/setup-stack` — it scans your code and generates the stack from observed patterns.

---

## The Paths

### Path 1 — Backend Engineer (REST API)
**You are:** A software engineer building HTTP services
**You want:** A production-quality API with tests, migrations, and CI

| Stack | Language | Best for | Client fit |
|---|---|---|---|
| `python-fastapi` | Python | ML-adjacent APIs, async services | General / Intuit data teams |
| `go-gin` | Go | High-throughput REST, microservices | Intuit platform |
| `java-spring` | Java | Enterprise CRUD, Spring ecosystem | Salesforce, Travelers |
| `node-express` | TypeScript | Lightweight APIs, rapid prototyping | General |
| `node-nestjs` | TypeScript | Enterprise Node, DI, Swagger-first | Salesforce, Travelers |

**Setup:**
```
/set-persona engineer
/setup-stack python-fastapi   # (or your stack of choice)
```

---

### Path 2 — Backend Engineer (gRPC / Internal Services)
**You are:** A backend engineer building inter-service communication
**You want:** Protocol Buffers, strongly-typed service contracts, streaming

| Stack | Language | Best for | Client fit |
|---|---|---|---|
| `go-grpc` | Go | Internal gRPC services, Intuit platform | Intuit |

**Setup:**
```
/set-persona engineer
/setup-stack go-grpc
```

---

### Path 3 — DevOps / Platform Engineer
**You are:** A platform engineer, SRE, or DevOps practitioner
**You want:** Infrastructure as code, config management, or Kubernetes

| Stack | Best for | Client fit |
|---|---|---|
| `devops-terraform` | Cloud infrastructure (AWS/GCP/Azure), IaC | All clients |
| `devops-ansible` | Server config management, post-Terraform provisioning | All clients |
| `devops-k8s-helm` | Kubernetes workloads, GitOps with ArgoCD | Platform teams |

**Setup:**
```
/set-persona devops
/setup-stack devops-terraform   # (or ansible, k8s-helm)
```

---

### Path 4 — Data Scientist (Notebooks + Classical ML)
**You are:** A data scientist doing EDA, feature engineering, and model prototyping
**You want:** Reproducible experiments, model cards, MLflow tracking

| Stack | Best for | Client fit |
|---|---|---|
| `python-datascience` | sklearn, pandas, Jupyter, experiment notebooks | General DS teams |
| `r-tidyverse` | Actuarial / statistical analysis, Quarto reports, Plumber APIs | Travelers, academic |

**Setup:**
```
/set-persona data-scientist
/setup-stack python-datascience   # or r-tidyverse
```

---

### Path 5 — Data Engineer / Analytics Engineer
**You are:** A data engineer building pipelines or an analytics engineer defining metrics
**You want:** Distributed data processing or SQL-first transformation

| Stack | Best for | Client fit |
|---|---|---|
| `python-spark` | Large-scale ETL, Databricks, Delta Lake, feature pipelines | Databricks / enterprise |
| `python-dbt-snowflake` | SQL-first transformations, Snowflake/BigQuery, BI layer | Analytics engineering teams |

**Setup:**
```
/set-persona data-scientist
/setup-stack python-spark   # or python-dbt-snowflake
```

---

### Path 6 — MLOps Engineer
**You are:** A data scientist or ML engineer shipping models to production
**You want:** End-to-end ML pipelines: training → registry → serving

| Stack | Best for | Client fit |
|---|---|---|
| `python-mlops` | MLflow-based training pipeline + FastAPI model serving | Databricks, Intuit ML teams |

**Setup:**
```
/set-persona data-scientist
/setup-stack python-mlops
```

---

### Path 7 — Product Manager
**You are:** A PM who wants to collaborate better with engineering
**You want:** PRD templates, story decomposition, sprint planning tools

No stack needed. The PM persona gives you:
- `/start-project` — guided PRD creation
- `/architect` — translate PRDs into technical specs
- `/read` — summarize active sprint state

**Setup:**
```
/set-persona pm
/start-session
```

---

### Path 8 — Designer
**You are:** A UI/UX designer working in code or alongside engineering
**You want:** Design token management, component specs, Figma handoff docs

No stack needed.

**Setup:**
```
/set-persona designer
/start-session
```

---

## Quick Decision Tree

```
Are you writing code?
├── Yes — what kind?
│   ├── HTTP API → Path 1 (REST) or Path 2 (gRPC)
│   ├── Infrastructure → Path 3 (DevOps)
│   ├── Data analysis / notebooks → Path 4 (Data Science)
│   ├── Data pipelines / warehouses → Path 5 (Data Engineering)
│   └── ML in production → Path 6 (MLOps)
└── No — what's your role?
    ├── Product Manager → Path 7
    └── Designer → Path 8
```

---

## Client-to-Path Quick Reference

| Client | Recommended paths |
|---|---|
| **Intuit** | Path 1 (go-gin), Path 2 (go-grpc), Path 6 (python-mlops) |
| **Salesforce** | Path 1 (java-spring, node-nestjs) |
| **Travelers** | Path 1 (java-spring), Path 4 (r-tidyverse) |
| **Databricks / ML teams** | Path 5 (python-spark), Path 6 (python-mlops) |
| **Analytics engineering** | Path 5 (python-dbt-snowflake) |
| **Platform / DevOps teams** | Path 3 (all devops stacks) |

---

## What Happens After You Choose

Once you run `/set-persona` and `/setup-stack`, the AI knows:
- What language and framework you're using
- What architecture pattern to scaffold (`/architect`)
- What rules to enforce during code review (`/code-review`)
- What testing strategy applies (`/start-session`)

You don't need to explain your stack to the AI. It already knows.

---

## Can I Switch Paths Mid-Course?

Yes. Run `/set-persona` again to switch. The previous persona's files are removed and the new one is installed. Your code is never touched — only the AI context changes.

To see what's currently active:
```
/read
```
