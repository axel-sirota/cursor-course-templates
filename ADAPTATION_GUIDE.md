# Adaptation Guide: Porting to New Stacks

This repository is designed to be a **Master Template**. While it comes with a Python FastAPI stack out of the box, it is built to support *any* language or framework.

## How to Add a New Stack

You want to use this workflow for **Node.js + Express**? Here is how.

### 1. Create the Stack Folder
Create a directory in `stacks/`:
```bash
mkdir -p stacks/node-express/rules
mkdir -p stacks/node-express/templates
```

### 2. Define the Context
Create `stacks/node-express/context.md`. This tells the AI how to behave.

```markdown
# Project Context: Node.js Express

## Tech Stack
- Language: TypeScript
- Framework: Express
- Test Runner: Jest
- Linting: ESLint

## Key Rules
- Use `async/await`, no callbacks.
- Use Zod for validation.
```

### 3. Define the Rules
Create `.mdc` files in `stacks/node-express/rules/`.
- `style.mdc`: Coding standards (camelCase, etc.).
- `testing.mdc`: How to write Jest tests (describe/it blocks).

### 4. Use It
Run `@setup-stack` in Cursor. Your new stack will appear in the list.

---

## Adopting into Brownfield (Legacy) Projects

You have an existing massive repo?

1.  **Copy the `.cursor` folder** from this repo into your legacy repo.
2.  Run `@setup-stack`.
3.  Select **"3. Analyze Code"**.
4.  The AI will scan your files and generate a custom `context.md`.
5.  **Edit the Context**: Open `.cursor/context.md` and set `Strictness: Low`.
    - This tells the AI: "Don't refactor everything. Just write clean *new* code."

## Concept Mapping

When porting, map the core concepts:

| Concept | Python (Ref) | Node.js | Java Spring | Go Gin | DevOps |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Skeleton** | Mock Routes | Mock Routes | Mock Controllers | Mock Handlers | `terraform plan` |
| **Models** | Pydantic | Zod | JPA Entities | Go Structs | `variables.tf` |
| **Repo** | SQLAlchemy | Prisma | JpaRepository | GORM | Modules |
| **Tests** | Pytest | Jest | JUnit 5 | `testing` | `tflint` / `checkov` |
| **Entry** | `main.py` | `server.ts` | `Application.java` | `main.go` | `main.tf` |

