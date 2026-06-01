# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Kubernetes AI platform that runs a [kind](https://kind.sigs.k8s.io/) cluster with Envoy Gateway and Envoy AI Gateway to proxy requests to LLM providers (AWS Bedrock, Anthropic). There is no application code — the repository is entirely Kubernetes manifests and Helm values.

## Cluster Bootstrap

- Create Kind cluster.
- Install Envoy Gateway and Envoy AI Gateway (in order).
- There is no load balancer and we use port-forward to access any kubernetes service.

## Architecture

### Request Routing

Requests reach the cluster through the `envoy-ai-gateway-basic` Gateway. The AI Gateway routes by the `x-ai-eg-model` header value to the appropriate `AIServiceBackend`:

| Header value | Backend | Schema |
|---|---|---|
| `us.meta.llama3-3-70b-instruct-v1:0` | AWS Bedrock (Meta) | `AWSBedrock` |
| `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | AWS Bedrock (Anthropic) | `AWSAnthropic` |

### Key CRD types (`aigateway.envoyproxy.io/v1beta1`)

- **`AIGatewayRoute`** — matches on `x-ai-eg-model` header, selects a named `AIServiceBackend`
- **`AIServiceBackend`** — declares the schema (protocol translation) and points to an Envoy Gateway `Backend`
- **`BackendSecurityPolicy`** — attaches AWS credentials (file-based secret or IRSA) to one or more `AIServiceBackend` resources
- **`Backend`** (gateway.envoyproxy.io/v1alpha1) — the actual FQDN/port endpoint (e.g. `bedrock-runtime.us-east-1.amazonaws.com:443`)
- **`BackendTLSPolicy`** — enforces TLS with system CA verification for the upstream endpoint

### AWS Credentials

Credentials are stored in a Kubernetes `Secret` (`envoy-ai-gateway-basic-aws-credentials`) using the standard AWS credentials file format and referenced by `BackendSecurityPolicy`. Replace the placeholder key values in `templates/aws-bedrock/sample.yaml` before applying. For EKS, use IRSA instead.

### Rate Limiting

Redis (`templates/redis.yaml`, namespace `redis-system`, port 6379) is required only when the Envoy Gateway rate-limit add-on is enabled via Helm values.

## Goal

- Deploy sample Gateway manifests to create gateway api to connect with AWS Bedrock [achieved].
- Create a sample agent which connects to AWS bedrock using envoy AI gateway.
- Create another agent to try failover from AWS Bedrock to Anthropic model directly.
- Enforce token based rate limiting for this agent.