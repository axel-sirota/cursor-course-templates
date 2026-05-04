# Development Lifecycle: Kubernetes + Helm + GitOps

See also: `stacks/shared/` for the general development lifecycle patterns shared across all stacks.

This document covers K8s/Helm-specific additions to the standard workflow.

---

## Chart Versioning

Every change to chart templates, values defaults, or helpers requires a `version` bump in `Chart.yaml`. This is mandatory, not optional.

- `version` — the chart's own version. Bump when chart structure, templates, or default values change. Follows semver: patch for fixes, minor for new optional features, major for breaking changes.
- `appVersion` — the version of the application the chart deploys. Bump when the deployed application version changes (e.g., a new release of your service). This does NOT require a chart version bump on its own.

```yaml
# Chart.yaml
version: 0.3.1      # chart changed: bumped patch
appVersion: "2.1.0" # app released 2.1.0
```

Chart version changes must be in the same PR as the template/values change. Never merge a template change without bumping the chart version.

---

## Image Tag Flow

CI/CD pipeline for updating a deployed service:

1. **Developer merges feature PR** → CI triggers on `main`
2. **CI builds Docker image** → tags it with git SHA: `ghcr.io/org/myapp:abc1234`
3. **CI pushes image to registry**
4. **CI opens an automated PR** that updates `values-staging.yaml`:
   ```yaml
   image:
     tag: "abc1234"  # was: "prev1234"
   ```
5. **PR is reviewed and merged** (can be auto-merged with a trusted CI bot for dev/staging)
6. **ArgoCD detects the values file change** → syncs automatically (dev/staging) or waits for manual approval (prod)
7. **ArgoCD deploys** the new image tag to the cluster
8. **ArgoCD reports** Synced + Healthy once pods are running and passing readiness probes

This flow ensures every deployed image is traceable to a git commit. No image is ever deployed without a Git trail.

---

## ArgoCD Sync Workflow

### Dev Environment
- ArgoCD Application has `automated.prune: true` and `automated.selfHeal: true`
- Every merge to `main` triggers an automatic sync within seconds
- No human intervention required
- Failures alert the team via Slack/PagerDuty

### Staging Environment
- Same as dev: auto-sync enabled
- Consider adding a post-sync health check that runs smoke tests
- Failures block promotion to prod (if using a promotion gate)

### Production Environment
- ArgoCD Application has NO `automated` block — manual sync only
- Operator reviews the diff in ArgoCD UI (`argocd app diff myapp-prod`)
- Operator approves sync: `argocd app sync myapp-prod --prune`
- ArgoCD performs a rolling deploy and waits for health checks
- Operator confirms in the ArgoCD UI that Application is `Synced` and `Healthy`
- Rollback if needed: `argocd app rollback myapp-prod <previous-revision>`

---

## Local Development Workflow

```bash
# 1. Make changes to chart templates or values
vim charts/myapp/templates/deployment.yaml

# 2. Lint immediately
helm lint ./charts/myapp

# 3. Render and inspect
helm template my-release ./charts/myapp \
  -f charts/myapp/values.yaml \
  -f charts/myapp/values-staging.yaml \
  > /tmp/rendered.yaml
cat /tmp/rendered.yaml

# 4. Validate against Kubernetes schema
helm template my-release ./charts/myapp \
  -f charts/myapp/values.yaml \
  -f charts/myapp/values-staging.yaml \
  | kubeconform -strict -summary

# 5. Run unit tests
helm unittest ./charts/myapp

# 6. Test in local cluster (kind or k3d)
kind create cluster --name local-dev
helm install my-release ./charts/myapp --wait
kubectl get pods
kind delete cluster --name local-dev

# 7. Commit and open PR
git add charts/myapp/
git commit -m "feat(myapp): add readiness probe to deployment"
```

---

## Promotion Gate Checklist

Before promoting a change from staging to prod:

- [ ] ArgoCD shows staging Application as `Synced` and `Healthy`
- [ ] Smoke tests pass on staging (health endpoint responds, key flows work)
- [ ] `checkov` scan has no HIGH findings
- [ ] Image tag is explicit and matches the SHA deployed to staging
- [ ] `helm diff` reviewed: `argocd app diff myapp-prod` shows only the intended change
- [ ] On-call engineer is aware of the deploy window
- [ ] Rollback plan documented (previous chart version + previous image tag)
