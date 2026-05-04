# Session 10 — New Stack: `devops-k8s-helm`

**Phase:** 3 — Group B (devops persona)
**Parallel with:** Sessions 7, 8, 9, 11, 12
**Depends on:** Sessions 1–6 complete
**Client fit:** Platform engineering teams, any team running Kubernetes in production

## Architecture Shape
GitOps Platform — Helm charts + ArgoCD for Kubernetes application delivery.

---

## Files to Create

```
stacks/devops-k8s-helm/
├── context.md
├── rules/
│   ├── 000-gitops-workflow.mdc
│   ├── 100-helm-architecture.mdc
│   ├── 200-k8s-testing.mdc
│   └── 300-k8s-style.mdc
├── templates/
│   ├── helm-starter.md
│   ├── phase-checklist.md
│   └── argocd-app.yaml
├── vibe/
│   ├── vibe_architecture.md
│   └── vibe_development_lifecycle.md
└── examples/
    └── webapp-chart/
        ├── Chart.yaml
        ├── values.yaml
        ├── values-staging.yaml
        ├── values-prod.yaml
        └── templates/
            ├── deployment.yaml
            ├── service.yaml
            ├── ingress.yaml
            └── _helpers.tpl
```

---

## File Specifications

### `context.md`

```markdown
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
```

### `rules/000-gitops-workflow.mdc`

- **Git is truth**: the Kubernetes cluster state is always derived from Git. Manual `kubectl apply` is an emergency procedure, never a workflow.
- **PR gate**: chart changes require `helm lint` + `helm template` + `kubeconform` all passing before merge.
- **ArgoCD sync policy**: auto-sync for dev/staging (ArgoCD auto-deploys on merge). Manual sync for production (requires explicit operator approval in ArgoCD UI or CLI).
- **No `latest` tag**: values files for staging and prod must specify explicit image tags. CI pushes the new tag; GitOps pulls it.
- **Branch strategy**: one branch per environment OR environment-specific values files on `main`. Choose one; don't mix.

### `rules/100-helm-architecture.mdc`

- **Chart structure**: `Chart.yaml` (metadata), `values.yaml` (defaults), `templates/` (manifests), `NOTES.txt` (post-install help). All required.
- **`_helpers.tpl`**: define reusable template helpers. `{{ include "chart.fullname" . }}` for all resource names. Never hardcode release name.
- **Values layering**: `values.yaml` has safe defaults for local/dev. `values-{env}.yaml` overrides for each environment. Never put secrets in any values file.
- **Resource naming**: all resources use `{{ include "chart.fullname" . }}` as name prefix. Prevents collision when multiple releases in same namespace.
- **Labels**: every resource has `helm.sh/chart`, `app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/managed-by` labels from `_helpers.tpl`.
- **Requests and limits**: every container in every Deployment must have resource requests AND limits. No unbounded pods.
- **Liveness vs readiness**: every Deployment has both `livenessProbe` and `readinessProbe`. Different endpoints: readiness blocks traffic, liveness triggers restart.
- **ApplicationSet for multi-env**: use ArgoCD ApplicationSet to generate per-environment Applications from a single template. DRY.

### `rules/200-k8s-testing.mdc`

- **`helm lint`**: runs before every commit. Zero warnings allowed.
- **`helm template`**: render chart locally to inspect output. Catch YAML syntax errors before pushing.
- **`kubeconform`**: validate rendered manifests against Kubernetes API schemas. Run in CI.
- **`helm unittest`**: unit test chart template logic with `helm plugin install https://github.com/helm-unittest/helm-unittest`. Test value overrides produce correct manifests.
- **`kind` or `k3d` for integration**: spin up a local cluster in CI, `helm install`, run smoke tests. Use for PRs touching chart templates.
- **checkov for security**: `checkov -d . --framework helm` in CI. Catch missing security contexts, privileged containers, missing resource limits.

### `rules/300-k8s-style.mdc`

- **YAML formatting**: 2-space indent. No tabs. Consistent spacing around `:`.
- **Template comments**: `{{- /* comment */ -}}` for template logic comments. Document non-obvious template decisions.
- **Whitespace control**: use `{{-` and `-}}` to control whitespace in rendered output. Avoid extra blank lines in rendered YAML.
- **Security context**: every Deployment sets `securityContext.runAsNonRoot: true`, `securityContext.allowPrivilegeEscalation: false`. No exceptions without explicit justification.
- **Image pull policy**: `IfNotPresent` for staging/prod (explicit tags). `Always` for dev with floating tags (dev only).

### `templates/helm-starter.md`

Scaffold for a new Helm chart:
```
{chart-name}/
  Chart.yaml          (name, description, version, appVersion)
  values.yaml         (all defaults; every value has a comment)
  values-dev.yaml     (dev overrides)
  values-staging.yaml (staging overrides; explicit image tag)
  values-prod.yaml    (prod overrides; explicit image tag; higher replicas)
  NOTES.txt           (post-install instructions)
  templates/
    _helpers.tpl      (fullname, labels, selectorLabels helpers)
    deployment.yaml
    service.yaml
    ingress.yaml      (disabled by default via ingress.enabled: false)
    hpa.yaml          (disabled by default)
    serviceaccount.yaml
```

Show example `_helpers.tpl` with standard label helpers.
Show example `values.yaml` with `image.repository`, `image.tag`, `replicaCount`, `resources`, `ingress.enabled`.

### `templates/argocd-app.yaml`

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {app-name}-{env}
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/{org}/{repo}
    targetRevision: main
    path: charts/{chart-name}
    helm:
      valueFiles:
        - values.yaml
        - values-{env}.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: {app-namespace}
  syncPolicy:
    automated:        # remove for prod (manual sync)
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] Chart directory structure created
- [ ] `helm lint` passes
- [ ] `helm template` renders valid YAML
- [ ] `kubeconform` passes on rendered output
- [ ] ArgoCD Application manifest created

**Phase 1 — Implement:**
- [ ] All resources have standard labels from `_helpers.tpl`
- [ ] Resource requests and limits set
- [ ] Liveness + readiness probes configured
- [ ] Security context set (`runAsNonRoot: true`)
- [ ] `helm unittest` written for any non-trivial template logic

**Handoff:**
- [ ] `checkov` scan passes (no HIGH findings)
- [ ] Values files per environment with explicit image tags
- [ ] ArgoCD sync verified in dev environment
- [ ] `NOTES.txt` explains post-deploy verification steps

### `vibe/vibe_architecture.md`

- **GitOps principle**: Git is the single source of truth for what should be running. If it's not in Git, it doesn't exist. Drift from Git is a bug.
- **Helm vs Kustomize vs raw YAML**: Helm wins for complex apps with many configurable values (environment-specific config). Kustomize wins for simple overlay patterns without templating. Raw YAML for extremely simple, never-changing resources.
- **Helm vs ArgoCD**: Helm packages and templates. ArgoCD deploys and reconciles. They are complementary. Don't use `helm install` in production — let ArgoCD do it.
- **ApplicationSet patterns**: one ApplicationSet can generate Applications for dev/staging/prod from a single template with environment-specific values. Use it. Don't maintain three separate Application manifests.
- **Sealed Secrets vs External Secrets**: Sealed Secrets encrypts secrets for Git (no external dependency). External Secrets syncs from Vault/AWS SSM/GCP Secret Manager (requires external dependency, more flexible). Choose Sealed Secrets for simplicity; External Secrets for large-scale secret management.
- **Progressive delivery**: canary and blue-green deployments use Argo Rollouts (not standard Kubernetes Deployments). Consider Rollouts when zero-downtime deploys matter more than operational simplicity.

### `vibe/vibe_development_lifecycle.md`

References `stacks/shared/`. Adds K8s/Helm-specific:
- Chart versioning: bump `version` in `Chart.yaml` on every chart change; `appVersion` tracks the app version
- Image tag flow: CI builds image → pushes to registry with git SHA tag → updates values file via PR
- ArgoCD sync workflow: auto in dev/staging; manual approval in prod

### `examples/webapp-chart/`

Eight files — a complete, working Helm chart for a generic web application:
- `Chart.yaml` — metadata, version 0.1.0
- `values.yaml` — complete defaults with comments on every value
- `values-staging.yaml` — explicit image tag, 2 replicas
- `values-prod.yaml` — explicit image tag, 3 replicas, higher resource limits
- `templates/_helpers.tpl` — fullname, chart, labels, selectorLabels helpers
- `templates/deployment.yaml` — with resource requests/limits, liveness+readiness probes, security context
- `templates/service.yaml` — ClusterIP service
- `templates/ingress.yaml` — disabled by default, enabled via values

---

## Acceptance Criteria

- [ ] `ls stacks/devops-k8s-helm/rules/` shows 4 files
- [ ] `ls stacks/devops-k8s-helm/templates/` shows `helm-starter.md`, `phase-checklist.md`, `argocd-app.yaml`
- [ ] `ls stacks/devops-k8s-helm/vibe/` shows 2 docs
- [ ] `ls stacks/devops-k8s-helm/examples/webapp-chart/templates/` shows 4 template files + `_helpers.tpl`
- [ ] `context.md` Architecture Shape = "GitOps Platform"
- [ ] `rules/000-gitops-workflow.mdc` contains "Never `kubectl apply` manually" rule
- [ ] `rules/100-helm-architecture.mdc` contains resource requests/limits rule
- [ ] `vibe_architecture.md` contains "Helm vs Kustomize vs raw YAML" decision section
