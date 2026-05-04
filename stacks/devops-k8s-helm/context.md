# Project Context: Kubernetes + Helm + GitOps

## Tech Stack
- Orchestration: Kubernetes 1.28+
- Packaging: Helm 3.x
- GitOps CD: ArgoCD 2.x
- Secrets: Sealed Secrets or External Secrets Operator
- Linting: helm lint, kubeval/kubeconform, checkov
- Testing: helm unittest (unit), kind/k3d (integration)

## Architecture Shape
GitOps Platform — Helm packages Kubernetes apps; ArgoCD syncs them from Git.
Not an application. Not a build system. The deliverable is a running Kubernetes workload.

## Vibe & Style
- Single source of truth: Git is the desired state. Cluster should always match Git.
- Chart design: one chart per application or service group. Values files per environment.
- No kubectl apply by hand: all changes go through Git → ArgoCD sync.

## Key Rules
- Never `kubectl apply` manually in production. All changes via Git PR + ArgoCD.
- Separate values files per environment (values-dev.yml, values-staging.yml, values-prod.yml).
- Secrets are never in Git — use Sealed Secrets or External Secrets Operator.
- Every chart must have a NOTES.txt explaining post-install steps.
- Image tags must be explicit (never `latest` in Helm values for staging/prod).

## Active Phase
- Current: Phase 0 (Skeleton)
