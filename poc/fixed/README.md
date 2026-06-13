# Auto-Fixed Kubernetes Manifests
This folder contains a collection of auto-fixed Kubernetes manifests. The manifests were scanned for various violations and fixed accordingly. The fixes were applied based on a set of predefined policies, including resource limits, image tags, required labels, and security context. The table below provides a summary of the files, violations found, and fixes applied.

| File | Violations Found | Fix Applied | File Type |
| --- | --- | --- | --- |
| sample-manifests/job.yaml | 7 | resource-limits, image-tag, required-labels, security-context | manifest |
| sample-charts/my-app/values.yaml | 1 | image-tag | values.yaml |
| sample-charts/my-app/templates/deployment.yaml | 6 | resource-limits, required-labels, security-context | template |

## Policies Enforced
The following policies were enforced on the Kubernetes manifests:
* resource-limits: Containers must have resource limits defined for CPU and memory.
* image-tag: Containers must use a specific image tag instead of the latest tag.
* required-labels: Pod templates must have required labels, such as app and env.
* security-context: Containers must have a security context defined with allowPrivilegeEscalation set to false and runAsNonRoot set to true.

Note: For Helm charts, value-driven violations (e.g., image tag) are fixed in the values.yaml file, while structural violations are fixed in the template files.
