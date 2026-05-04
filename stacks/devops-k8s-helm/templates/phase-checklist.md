# Phase Checklist: Helm Chart Development

Use this checklist to track progress through chart development phases. Copy it into your feature PR description.

---

## Phase 0 — Skeleton

- [ ] Chart directory structure created (`Chart.yaml`, `values.yaml`, `templates/`, `NOTES.txt`)
- [ ] `helm lint` passes with zero warnings and zero errors
- [ ] `helm template` renders valid YAML (no Go template errors)
- [ ] `kubeconform` passes on rendered output (no schema violations)
- [ ] ArgoCD Application manifest created in `gitops/` or `argocd/`

---

## Phase 1 — Implement

- [ ] All resources have standard labels from `{{ include "chart.labels" . }}` in `_helpers.tpl`
- [ ] All resource names use `{{ include "chart.fullname" . }}` — no hardcoded release names
- [ ] Resource requests and limits set on every container
- [ ] Liveness probe configured (`livenessProbe`) — triggers restart on deadlock
- [ ] Readiness probe configured (`readinessProbe`) — different endpoint from liveness
- [ ] Security context set on pod (`runAsNonRoot: true`, `runAsUser`) and container (`allowPrivilegeEscalation: false`)
- [ ] `helm unittest` written for any non-trivial template logic (conditionals, value-driven naming)
- [ ] Ingress resource disabled by default (`ingress.enabled: false` in `values.yaml`)
- [ ] `values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml` created

---

## Handoff

- [ ] `checkov` scan passes with no HIGH severity findings (MEDIUM findings documented if not fixed)
- [ ] Values files for staging and prod use explicit image tags (no `latest`)
- [ ] ArgoCD sync verified in dev environment — Application shows `Synced` and `Healthy`
- [ ] `helm lint` passes for all environment values file combinations
- [ ] `kubeconform` passes for all environment renders
- [ ] `NOTES.txt` explains post-deploy verification steps clearly
- [ ] Chart `version` bumped in `Chart.yaml`
- [ ] PR description references this checklist with all items checked

---

## Environment-Specific Reminders

| Check | Dev | Staging | Prod |
|---|---|---|---|
| Auto-sync in ArgoCD | Yes | Yes | **No — manual** |
| Image tag must be explicit | No (dev-latest ok) | **Yes** | **Yes** |
| `imagePullPolicy` | Always | IfNotPresent | IfNotPresent |
| Replicas | 1 | 2 | 3+ |
| Resource limits | Relaxed ok | Match prod | Tuned to workload |
