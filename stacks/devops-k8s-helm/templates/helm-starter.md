# Helm Chart Starter Template

Use this scaffold whenever you create a new Helm chart. Replace `{chart-name}` with your chart's name (lowercase, hyphens only).

## Directory Structure

```
{chart-name}/
  Chart.yaml            (name, description, version, appVersion)
  values.yaml           (all defaults; every value has a comment)
  values-dev.yaml       (dev overrides; imagePullPolicy: Always)
  values-staging.yaml   (staging overrides; explicit image tag)
  values-prod.yaml      (prod overrides; explicit image tag; higher replicas)
  NOTES.txt             (post-install instructions)
  templates/
    _helpers.tpl        (fullname, labels, selectorLabels helpers)
    deployment.yaml
    service.yaml
    ingress.yaml        (disabled by default via ingress.enabled: false)
    hpa.yaml            (disabled by default via autoscaling.enabled: false)
    serviceaccount.yaml
```

---

## `Chart.yaml`

```yaml
apiVersion: v2
name: {chart-name}
description: A Helm chart for {chart-name}
type: application
version: 0.1.0        # Chart version — bump on every chart change
appVersion: "1.0.0"   # Application version — tracks the app being deployed
```

---

## `values.yaml`

```yaml
# Number of pod replicas
replicaCount: 1

image:
  # Container image repository
  repository: nginx
  # Image pull policy: IfNotPresent for staging/prod, Always for dev
  pullPolicy: IfNotPresent
  # Image tag — must be explicit for staging/prod, never "latest"
  tag: "1.25.3"

# Image pull secrets for private registries
imagePullSecrets: []

# Override the chart name for resource naming
nameOverride: ""
# Override the full resource name prefix
fullnameOverride: ""

serviceAccount:
  # Create a dedicated ServiceAccount for this release
  create: true
  # Annotations to add to the ServiceAccount (e.g., for IRSA)
  annotations: {}
  # Name override; defaults to chart fullname
  name: ""

# Annotations added to the pod template
podAnnotations: {}

# Pod-level security context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault

# Container-level security context
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL

service:
  # Service type: ClusterIP, NodePort, or LoadBalancer
  type: ClusterIP
  # Port the Service exposes
  port: 80
  # Port the container listens on
  targetPort: 8080

ingress:
  # Enable Ingress resource creation
  enabled: false
  # Ingress class name (e.g., nginx, traefik, alb)
  className: ""
  # Ingress annotations (e.g., cert-manager.io/cluster-issuer)
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix
  # TLS configuration
  tls: []

# Resource requests and limits — tune these for your workload
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"

# Liveness probe — restarts the container if it fails
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 15
  failureThreshold: 3

# Readiness probe — removes pod from Service endpoints if it fails
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3

autoscaling:
  # Enable HorizontalPodAutoscaler
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

# Node selector for pod scheduling
nodeSelector: {}

# Tolerations for pod scheduling
tolerations: []

# Affinity rules for pod scheduling
affinity: {}
```

---

## `_helpers.tpl` — Standard Helpers

```
{{/*
Expand the name of the chart.
*/}}
{{- define "chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
Truncated to 63 characters because Kubernetes DNS names have limits.
If release name contains the chart name it will be used as a full name.
*/}}
{{- define "chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the Helm chart label.
*/}}
{{- define "chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels — applied to all resources.
*/}}
{{- define "chart.labels" -}}
helm.sh/chart: {{ include "chart.chart" . }}
{{ include "chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels — used in spec.selector.matchLabels and pod template labels.
Only stable labels that don't change between releases.
*/}}
{{- define "chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the ServiceAccount to use.
*/}}
{{- define "chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

---

## `NOTES.txt`

```
1. Get the application URL by running:
{{- if .Values.ingress.enabled }}
{{- range $host := .Values.ingress.hosts }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}
{{- end }}
{{- else if contains "NodePort" .Values.service.type }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "chart.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if contains "LoadBalancer" .Values.service.type }}
  NOTE: It may take a few minutes for the LoadBalancer IP to be available.
  export SERVICE_IP=$(kubectl get svc --namespace {{ .Release.Namespace }} {{ include "chart.fullname" . }} --template "{{"{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}"}}")
  echo http://$SERVICE_IP:{{ .Values.service.port }}
{{- else if contains "ClusterIP" .Values.service.type }}
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "{{ include "chart.selectorLabels" . }}" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:{{ .Values.service.targetPort }}
  echo "Visit http://127.0.0.1:8080 to use your application"
{{- end }}

2. Verify all pods are running:
  kubectl get pods --namespace {{ .Release.Namespace }} -l "{{ include "chart.selectorLabels" . }}"
```
