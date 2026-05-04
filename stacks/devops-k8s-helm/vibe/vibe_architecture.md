# Architecture Vibe: Kubernetes + Helm + GitOps

## GitOps Principle

Git is the single source of truth for what should be running in the cluster. If it's not in Git, it does not exist. Drift from Git is a bug that must be corrected by either committing the intent or reverting the cluster to match Git.

This is not just a workflow preference — it's an operational invariant. Teams that allow manual kubectl changes in production will eventually have untracked changes, unreviewed changes, and incidents with unclear root causes.

## Helm vs Kustomize vs Raw YAML

**Choose Helm when:**
- The app has many configurable values that differ by environment (image tags, replica counts, resource limits, feature flags)
- You want to package the app for reuse across teams or clusters
- You need chart versioning and rollback semantics (`helm rollback`)
- The chart will be shared on a Helm registry (ArtifactHub, internal registry)

**Choose Kustomize when:**
- The app has a simple base with lightweight environment overlays
- You don't need templating — just patching specific fields
- You want to avoid the Go template language
- You're managing cluster-level infrastructure that doesn't change often

**Choose raw YAML when:**
- The resource is extremely simple and never changes (e.g., a static Namespace or ClusterRole)
- You want zero abstraction overhead for a one-off resource

**The rule:** Helm wins for complex apps with many configurable values. Kustomize wins for simple overlay patterns without templating. Raw YAML for extremely simple, never-changing resources. Don't mix Helm and Kustomize in the same chart — pick one per service.

## Helm vs ArgoCD Responsibilities

Helm and ArgoCD have distinct, complementary responsibilities:

- **Helm** packages and templates Kubernetes manifests. It knows how to render a chart with values into valid Kubernetes YAML. It handles chart versioning, dependencies, and rollback.
- **ArgoCD** deploys and reconciles. It watches Git, detects drift between the cluster and Git, and syncs (or alerts). It handles deployment history, health checks, and rollback at the GitOps layer.

Do NOT use `helm install` in production. Let ArgoCD call Helm under the hood. Running `helm install` directly bypasses ArgoCD's reconciliation loop and creates drift.

## ApplicationSet Patterns

One ArgoCD ApplicationSet can generate Applications for dev/staging/prod from a single template with environment-specific substitutions. This is far better than maintaining three separate Application manifests — they will drift.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: dev
            namespace: myapp-dev
            autoSync: "true"
          - env: staging
            namespace: myapp-staging
            autoSync: "true"
          - env: prod
            namespace: myapp-prod
            autoSync: "false"
  template:
    metadata:
      name: "myapp-{{env}}"
    spec:
      source:
        path: charts/myapp
        helm:
          valueFiles:
            - values.yaml
            - "values-{{env}}.yaml"
      destination:
        namespace: "{{namespace}}"
```

Use ApplicationSet for any app deployed to more than one environment. Single-environment apps can use a plain Application manifest.

## Sealed Secrets vs External Secrets

**Sealed Secrets:**
- Encrypts Kubernetes Secret objects into a `SealedSecret` CRD that is safe to commit to Git
- Decryption happens in-cluster via the Sealed Secrets controller
- Simple setup: one controller, one CLI tool (`kubeseal`)
- No external dependency — works fully offline
- Best for: teams with simple secret needs, small-scale deployments, teams new to secrets management

**External Secrets Operator:**
- Syncs secrets from external stores: AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, Azure Key Vault, 1Password
- Secrets never live in Git — External Secrets CR describes what to fetch and where to put it
- More complex setup: requires external secret store, IAM/RBAC to the store, ESO controller
- Best for: large-scale deployments, teams already using a secret manager, multi-cluster setups

**Rule:** Choose Sealed Secrets for simplicity when starting out. Migrate to External Secrets Operator when you need centralized secret management across multiple clusters or when your team already uses a cloud secret manager.

## Progressive Delivery

Standard Kubernetes Deployments do rolling updates: gradually replacing old pods with new ones. This is sufficient for most workloads.

For zero-downtime deploys where the risk of a bad release is high, consider **Argo Rollouts**:
- **Canary**: send 10% of traffic to the new version, observe metrics, gradually increase
- **Blue-green**: spin up the new version alongside the old, switch traffic atomically

Argo Rollouts integrates with ArgoCD and supports automated analysis (metric-based promotion or rollback). Add it when:
- The application handles significant traffic and a bad deploy would cause measurable user impact
- You have metrics (error rate, latency) that can drive automated rollback decisions
- Operational simplicity matters less than deployment safety

Do not add Argo Rollouts prematurely. A standard Deployment with a proper readiness probe and a `maxSurge`/`maxUnavailable` strategy is often sufficient.
